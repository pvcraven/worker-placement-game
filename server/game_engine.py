"""Core game logic: worker placement, resource collection, quest completion, scoring."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from server.lobby import _filter_state_for_player
from server.models.game import ActionSpace, GameLog
import random

from shared.card_models import ContractCard, ResourceCost
from shared.constants import BONUS_WORKER_ROUND, GamePhase
from shared.constants import FACE_UP_QUEST_COUNT
from shared.messages import (
    BonusWorkersGrantedResponse,
    BuildingMarketUpdateResponse,
    ContractAcquiredResponse,
    ErrorResponse,
    FaceUpQuestsUpdatedResponse,
    FinalPlayerScore,
    GameOverResponse,
    IntrigueEffectResolvedResponse,
    IntrigueTargetPromptResponse,
    PlacementCancelledResponse,
    QuestCardSelectedResponse,
    QuestCompletedResponse,
    QuestCompletionPromptResponse,
    QuestRewardChoicePromptResponse,
    QuestRewardChoiceResolvedResponse,
    QuestSkippedResponse,
    QuestsResetResponse,
    ReassignmentPhaseStartResponse,
    ResourceChoicePromptResponse,
    ResourceChoiceResolvedResponse,
    RoundEndResponse,
    TurnTimeoutResponse,
    WorkerPlacedBackstageResponse,
    WorkerPlacedResponse,
    WorkerReassignedResponse,
)

if TYPE_CHECKING:
    from server.network import ClientConnection, GameServer

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _get_game_state(server: GameServer, conn: ClientConnection):
    """Look up the game state for a connection, or None."""
    if not conn.game_code:
        return None
    return server.session_manager.get_session(conn.game_code)


def _validate_turn(server, conn, state):
    """Check it's this player's turn. Returns True if valid."""
    if state.phase != GamePhase.PLACEMENT:
        return False
    current = state.current_player()
    return current is not None and current.player_id == conn.player_id


def _draw_from_quest_deck(state) -> ContractCard | None:
    """Draw a card from the quest deck, reshuffling discard if needed."""
    if not state.board.quest_deck and state.board.quest_discard:
        state.board.quest_deck = list(state.board.quest_discard)
        state.board.quest_discard.clear()
        random.shuffle(state.board.quest_deck)
    if state.board.quest_deck:
        return state.board.quest_deck.pop(0)
    return None


def _draw_intrigue_cards(state, player, count: int) -> list[dict]:
    drawn: list[dict] = []
    for _ in range(count):
        if state.board.intrigue_deck:
            c = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(c)
            drawn.append(c.model_dump())
    return drawn


def _grant_random_building(state, player) -> dict | None:
    if not state.board.building_deck:
        return None
    tile = state.board.building_deck.pop(0)
    return _assign_building_to_player(state, player, tile)


def _assign_building_to_player(
    state, player, tile,
) -> dict:
    """Assign a building tile to a player, creating an action space."""
    lot_idx = len(state.board.constructed_buildings)
    space_id = f"building_{tile.id}"
    space = ActionSpace(
        space_id=space_id,
        name=tile.name,
        space_type="building",
        owner_id=player.player_id,
        building_tile=tile,
        reward=tile.visitor_reward,
        reward_special=tile.visitor_reward_special,
    )
    state.board.action_spaces[space_id] = space
    state.board.constructed_buildings.append(space_id)
    if tile in state.board.face_up_buildings:
        state.board.face_up_buildings.remove(tile)
        if state.board.building_deck:
            new_b = state.board.building_deck.pop(0)
            new_b.accumulated_vp = 1
            state.board.face_up_buildings.append(new_b)
    player.victory_points += tile.accumulated_vp
    return {
        "building_id": tile.id,
        "building_name": tile.name,
        "lot_index": lot_idx,
        "space_id": space_id,
        "visitor_reward": tile.visitor_reward.model_dump(),
        "owner_bonus": tile.owner_bonus.model_dump(),
        "accumulated_vp": tile.accumulated_vp,
    }


async def _send_quest_reward_prompt(
    server, state, player, contract,
) -> None:
    """Send interactive reward prompt to the player."""
    if (
        contract.reward_draw_quests > 0
        and contract.reward_quest_draw_mode == "choose"
    ):
        choices = [
            q.model_dump()
            for q in state.board.face_up_quests
        ]
        if choices:
            state.pending_quest_reward = {
                "player_id": player.player_id,
                "reward_type": "choose_quest",
                "available_choices": choices,
                "quest_name": contract.name,
                "contract": contract.model_dump(),
            }
            await server.send_to_player(
                player.player_id,
                QuestRewardChoicePromptResponse(
                    reward_type="choose_quest",
                    available_choices=choices,
                    quest_name=contract.name,
                ),
            )
            return

    if contract.reward_building == "market_choice":
        choices = [
            b.model_dump()
            for b in state.board.face_up_buildings
        ]
        if choices:
            state.pending_quest_reward = {
                "player_id": player.player_id,
                "reward_type": "choose_building",
                "available_choices": choices,
                "quest_name": contract.name,
                "contract": contract.model_dump(),
            }
            await server.send_to_player(
                player.player_id,
                QuestRewardChoicePromptResponse(
                    reward_type="choose_building",
                    available_choices=choices,
                    quest_name=contract.name,
                ),
            )
            return


async def _check_quest_completion(
    server: GameServer, state,
) -> None:
    """Check if current player can complete quests."""
    player = state.current_player()
    if player is None or player.completed_quest_this_turn:
        await _advance_turn(server, state)
        await _notify_turn_if_needed(
            server, state, player,
        )
        return

    completable = [
        c for c in player.contract_hand
        if player.resources.can_afford(c.cost)
    ]
    if not completable:
        await _advance_turn(server, state)
        await _notify_turn_if_needed(
            server, state, player,
        )
        return

    state.waiting_for_quest_completion = True
    await server.send_to_player(
        player.player_id,
        QuestCompletionPromptResponse(
            completable_quests=[
                c.model_dump() for c in completable
            ],
        ),
    )


async def _notify_turn_if_needed(
    server: GameServer, state, prev_player,
) -> None:
    """After auto-advance, tell clients whose turn."""
    if state.phase != GamePhase.PLACEMENT:
        return
    nxt = state.current_player()
    if not nxt:
        return
    pid = (
        prev_player.player_id if prev_player else ""
    )
    await server.broadcast_to_game(
        state.game_code,
        QuestSkippedResponse(
            player_id=pid,
            next_player_id=nxt.player_id,
        ),
    )


async def _advance_turn(server: GameServer, state) -> None:
    """Advance to the next player, or trigger end-of-round if all placed."""
    state.last_activity = time.time()

    if state.all_workers_placed():
        await _end_placement_phase(server, state)
        return

    # Find next player with available workers
    count = len(state.turn_order)
    for _ in range(count):
        state.current_player_index = (state.current_player_index + 1) % count
        player = state.current_player()
        if player and player.available_workers > 0:
            return

    # All workers placed (shouldn't reach here but safety net)
    await _end_placement_phase(server, state)


async def _end_placement_phase(server: GameServer, state) -> None:
    """Handle transition after all workers are placed."""
    # Check for Backstage reassignment
    occupied_slots = [
        s for s in state.board.backstage_slots if s.occupied_by is not None
    ]
    if occupied_slots:
        state.phase = GamePhase.REASSIGNMENT
        state.reassignment_queue = [s.slot_number for s in occupied_slots]
        await server.broadcast_to_game(
            state.game_code,
            ReassignmentPhaseStartResponse(
                backstage_slots=[
                    {"slot_number": s.slot_number, "player_id": s.occupied_by}
                    for s in occupied_slots
                ]
            ),
        )
    else:
        await _end_round(server, state)


async def _end_round(server: GameServer, state) -> None:
    """End the current round: return workers, advance round."""
    round_number = state.current_round

    state.waiting_for_quest_completion = False

    # Return all workers
    for player in state.players:
        player.available_workers = player.total_workers
        player.completed_quest_this_turn = False

    # Clear board occupants
    for space in state.board.action_spaces.values():
        space.occupied_by = None
    for slot in state.board.backstage_slots:
        slot.occupied_by = None
        slot.intrigue_card_played = None

    state.game_log.append(
        GameLog(
            round_number=round_number,
            action="round_end",
            details=f"Round {round_number} ended",
            timestamp=time.time(),
        )
    )

    if state.current_round >= state.total_rounds:
        await _end_game(server, state)
        return

    # Advance to next round
    state.current_round += 1
    state.phase = GamePhase.PLACEMENT

    # Bonus worker at round 5
    bonus_granted = False
    if state.current_round == BONUS_WORKER_ROUND:
        for player in state.players:
            player.total_workers += 1
            player.available_workers = player.total_workers
        bonus_granted = True
        await server.broadcast_to_game(
            state.game_code,
            BonusWorkersGrantedResponse(
                round=BONUS_WORKER_ROUND,
                new_worker_count=state.players[0].total_workers,
            ),
        )

    # Increment VP on face-up buildings
    for building in state.board.face_up_buildings:
        building.accumulated_vp += 1

    # Set turn order based on first-player marker
    first_pid = state.board.first_player_id
    if first_pid:
        pids = [p.player_id for p in state.players]
        if first_pid in pids:
            idx = pids.index(first_pid)
            state.turn_order = pids[idx:] + pids[:idx]
    state.current_player_index = 0

    await server.broadcast_to_game(
        state.game_code,
        RoundEndResponse(
            round_number=round_number,
            next_round=state.current_round,
            first_player_id=state.board.first_player_id,
            turn_order=state.turn_order,
            bonus_worker_granted=bonus_granted,
        ),
    )

    # Broadcast updated building market with incremented VP
    await _broadcast_building_market(server, state)


async def _end_game(server: GameServer, state) -> None:
    """Calculate final scores and broadcast game over."""
    state.phase = GamePhase.GAME_OVER

    scores: list[FinalPlayerScore] = []
    for player in state.players:
        base_vp = player.victory_points
        producer_bonus = 0
        if player.producer_card:
            for contract in player.completed_contracts:
                if contract.genre in player.producer_card.bonus_genres:
                    producer_bonus += player.producer_card.bonus_vp_per_contract
        total = base_vp + producer_bonus
        scores.append(
            FinalPlayerScore(
                player_id=player.player_id,
                player_name=player.display_name,
                base_vp=base_vp,
                producer_bonus=producer_bonus,
                producer_card=player.producer_card.model_dump()
                if player.producer_card
                else {},
                total_vp=total,
                rank=0,
            )
        )

    # Sort by total VP, then tiebreakers
    tiebreaker = False
    scores.sort(
        key=lambda s: (
            s.total_vp,
            _tiebreak_coins(state, s.player_id),
            _tiebreak_resources(state, s.player_id),
            _tiebreak_quests(state, s.player_id),
        ),
        reverse=True,
    )

    # Check if tiebreaker was needed
    if len(scores) >= 2 and scores[0].total_vp == scores[1].total_vp:
        tiebreaker = True

    for i, s in enumerate(scores):
        s.rank = i + 1

    await server.broadcast_to_game(
        state.game_code,
        GameOverResponse(final_scores=scores, tiebreaker_applied=tiebreaker),
    )

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            action="game_over",
            details=f"Game over. Winner: {scores[0].player_name}",
            timestamp=time.time(),
        )
    )


def _tiebreak_coins(state, player_id: str) -> int:
    p = state.get_player(player_id)
    return p.resources.coins if p else 0


def _tiebreak_resources(state, player_id: str) -> int:
    p = state.get_player(player_id)
    return p.resources.total() if p else 0


def _tiebreak_quests(state, player_id: str) -> int:
    p = state.get_player(player_id)
    return len(p.completed_contracts) if p else 0


# ------------------------------------------------------------------
# Resource choice helpers
# ------------------------------------------------------------------


def validate_resource_choice(
    pending: dict, chosen: dict,
) -> str | None:
    """Validate a resource choice. Returns error string or None."""
    choice_type = pending.get("choice_type", "pick")
    allowed = pending.get("allowed_types", [])

    if choice_type == "pick":
        pick_count = pending.get("pick_count", 1)
        total = sum(
            v for v in chosen.values() if isinstance(v, int)
        )
        if total != pick_count:
            return (
                f"Must pick exactly {pick_count} resource(s),"
                f" got {total}."
            )
        for key, val in chosen.items():
            if not isinstance(val, int) or val < 0:
                return f"Invalid value for {key}."
            if val > 0 and key not in allowed:
                return f"{key} is not an allowed choice."
        return None

    if choice_type == "bundle":
        bundles = pending.get("bundles", [])
        for bundle in bundles:
            b_res = bundle.get("resources", {})
            if _resources_match(chosen, b_res):
                return None
        return "Selection does not match any available bundle."

    if choice_type == "combo":
        total_required = pending.get("total", 0)
        total = sum(
            v for v in chosen.values() if isinstance(v, int)
        )
        if total != total_required:
            return (
                f"Must allocate exactly {total_required},"
                f" got {total}."
            )
        for key, val in chosen.items():
            if not isinstance(val, int) or val < 0:
                return f"Invalid value for {key}."
            if val > 0 and key not in allowed:
                return f"{key} is not an allowed choice."
        return None

    return f"Unknown choice_type: {choice_type}"


def _resources_match(chosen: dict, expected: dict) -> bool:
    all_keys = set(chosen) | set(expected)
    for key in all_keys:
        if chosen.get(key, 0) != expected.get(key, 0):
            return False
    return True


def _player_non_coin_total(player) -> int:
    r = player.resources
    return r.guitarists + r.bass_players + r.drummers + r.singers


async def _send_resource_choice_prompt(
    server,
    state,
    player,
    choice_reward,
    source_type: str,
    source_name: str,
    is_spend: bool = False,
    pick_count_override: int | None = None,
    phase: str = "gain",
) -> None:
    """Send a resource choice prompt to a player."""
    import uuid
    prompt_id = str(uuid.uuid4())[:8]

    ct = choice_reward.choice_type
    allowed = choice_reward.allowed_types
    pc = pick_count_override or choice_reward.pick_count
    total = choice_reward.total
    bundles_data = [
        {"label": b.label, "resources": b.resources.model_dump()}
        for b in choice_reward.bundles
    ]

    if is_spend:
        title = f"Turn in {pc} resource(s)"
        desc = f"Select resources to turn in for {source_name}"
    elif ct == "bundle":
        title = "Choose a reward"
        desc = f"Select one option from {source_name}"
    elif ct == "combo":
        title = f"Allocate {total} resource(s)"
        desc = f"Distribute across allowed types from {source_name}"
    else:
        title = f"Pick {pc} resource(s)"
        desc = f"Choose from {source_name}"

    state.pending_resource_choice = {
        "prompt_id": prompt_id,
        "player_id": player.player_id,
        "source_type": source_type,
        "source_name": source_name,
        "choice_type": ct if not is_spend else "pick",
        "allowed_types": allowed,
        "pick_count": pc,
        "total": total,
        "bundles": bundles_data,
        "is_spend": is_spend,
        "phase": phase,
        "gain_count": choice_reward.gain_count,
        "others_pick_count": choice_reward.others_pick_count,
        "remaining_players": [],
        "choice_reward_dump": choice_reward.model_dump(),
    }

    await server.send_to_player(
        player.player_id,
        ResourceChoicePromptResponse(
            prompt_id=prompt_id,
            player_id=player.player_id,
            choice_type=ct if not is_spend else "pick",
            title=title,
            description=desc,
            allowed_types=allowed,
            pick_count=pc,
            total=total,
            bundles=bundles_data,
            is_spend=is_spend,
        ),
    )


async def handle_resource_choice(
    server, conn, msg,
) -> None:
    """Handle a player's resource choice selection."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND", "Not in a game.",
        )
        return

    pending = state.pending_resource_choice
    if pending is None:
        await conn.send_error(
            "INVALID_ACTION",
            "No pending resource choice.",
        )
        return
    if pending["player_id"] != conn.player_id:
        await conn.send_error(
            "INVALID_ACTION",
            "Not your resource choice.",
        )
        return
    if msg.prompt_id != pending["prompt_id"]:
        await conn.send_error(
            "INVALID_ACTION", "Prompt ID mismatch.",
        )
        return

    chosen = msg.chosen_resources
    error = validate_resource_choice(pending, chosen)
    if error:
        await conn.send_error("INVALID_CHOICE", error)
        return

    player = state.get_player(conn.player_id)
    is_spend = pending.get("is_spend", False)
    chosen_rc = ResourceCost(
        **{k: v for k, v in chosen.items()
           if k in ResourceCost.model_fields},
    )

    if is_spend:
        if not player.resources.can_afford(chosen_rc):
            await conn.send_error(
                "INVALID_CHOICE",
                "You don't have those resources.",
            )
            return
        player.resources.deduct(chosen_rc)
    else:
        player.resources.add(chosen_rc)

    source_name = pending.get("source_name", "")

    await server.broadcast_to_game(
        state.game_code,
        ResourceChoiceResolvedResponse(
            player_id=player.player_id,
            chosen_resources=chosen,
            is_spend=is_spend,
            source_description=source_name,
            next_player_id=None,
        ),
    )

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="resource_choice",
            details=(
                f"{player.display_name} "
                f"{'turned in' if is_spend else 'chose'}"
                f" resources from {source_name}"
            ),
            timestamp=time.time(),
        )
    )

    # Handle exchange phase 2 (spend → gain)
    if (
        is_spend
        and pending.get("phase") == "spend"
    ):
        from shared.card_models import ResourceChoiceReward
        rcr = ResourceChoiceReward(
            **pending["choice_reward_dump"],
        )
        await _send_resource_choice_prompt(
            server, state, player, rcr,
            pending["source_type"],
            source_name,
            is_spend=False,
            pick_count_override=rcr.gain_count,
            phase="gain",
        )
        return

    # Handle multi-player remaining
    remaining = pending.get("remaining_players", [])
    if remaining:
        next_pid = remaining.pop(0)
        next_player = state.get_player(next_pid)
        if next_player:
            from shared.card_models import ResourceChoiceReward
            rcr = ResourceChoiceReward(
                **pending["choice_reward_dump"],
            )
            state.pending_resource_choice = None
            await _send_resource_choice_prompt(
                server, state, next_player, rcr,
                pending["source_type"],
                source_name,
                pick_count_override=(
                    pending.get("others_pick_count", 1)
                ),
            )
            state.pending_resource_choice[
                "remaining_players"
            ] = remaining
            state.pending_resource_choice[
                "others_pick_count"
            ] = pending.get("others_pick_count", 1)
            state.pending_resource_choice[
                "choice_reward_dump"
            ] = pending["choice_reward_dump"]
            return

    state.pending_resource_choice = None
    await _check_quest_completion(server, state)


# ------------------------------------------------------------------
# Worker placement handler
# ------------------------------------------------------------------


async def handle_place_worker(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not _validate_turn(server, conn, state):
        await conn.send_error("NOT_YOUR_TURN", "It is not your turn.")
        return

    player = state.current_player()
    space = state.board.action_spaces.get(msg.space_id)
    if space is None:
        await conn.send_error("INVALID_ACTION", "Unknown action space.")
        return

    if space.occupied_by is not None:
        await conn.send_error("SPACE_OCCUPIED", "That space is already occupied.")
        return

    if player.available_workers <= 0:
        await conn.send_error("INVALID_ACTION", "No workers available.")
        return

    # Place worker
    space.occupied_by = player.player_id
    player.available_workers -= 1
    player.completed_quest_this_turn = False

    # Grant reward
    reward_dict = space.reward.model_dump()
    player.resources.add(space.reward)

    # Handle Garage spots (quest selection)
    if space.space_type == "garage":
        await _handle_garage_placement(
            server, state, player, space, msg.space_id
        )
        return

    # Handle Real Estate Listings (building purchase — deferred turn)
    if space.reward_special == "purchase_building":
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="place_worker",
                details=(
                    f"{player.display_name} placed worker on"
                    f" {space.name} — awaiting building purchase"
                ),
                timestamp=time.time(),
            )
        )
        await server.broadcast_to_game(
            state.game_code,
            WorkerPlacedResponse(
                player_id=player.player_id,
                space_id=msg.space_id,
                reward_granted=reward_dict,
                next_player_id=None,
            ),
        )
        return

    # Handle special spaces
    if space.space_type == "castle":
        # Castle Waterdeep: first-player marker + 1 intrigue card
        # Transfer first-player marker
        for p in state.players:
            p.has_first_player_marker = False
        player.has_first_player_marker = True
        state.board.first_player_id = player.player_id
        # Draw intrigue card
        if state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)

    # Owner bonus for buildings
    owner_bonus_info = {}
    if space.space_type == "building" and space.owner_id:
        owner = state.get_player(space.owner_id)
        if owner and owner.player_id != player.player_id and space.building_tile:
            owner.resources.add(space.building_tile.owner_bonus)
            owner_bonus_info = {
                "owner_id": owner.player_id,
                "owner_name": owner.display_name,
                "bonus": space.building_tile.owner_bonus.model_dump(),
            }
            state.game_log.append(
                GameLog(
                    round_number=state.current_round,
                    player_id=owner.player_id,
                    action="owner_bonus",
                    details=(
                        f"{owner.display_name} received owner bonus from"
                        f" {player.display_name} visiting {space.name}"
                    ),
                    timestamp=time.time(),
                )
            )

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="place_worker",
            details=f"{player.display_name} placed worker on {space.name}",
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedResponse(
            player_id=player.player_id,
            space_id=msg.space_id,
            reward_granted=reward_dict,
            owner_bonus=owner_bonus_info,
            next_player_id=None,
        ),
    )

    # Resource choice reward on buildings
    if (
        space.building_tile
        and space.building_tile.visitor_reward_choice
    ):
        choice = space.building_tile.visitor_reward_choice
        # Check cost affordability
        if choice.cost.total() > 0:
            if not player.resources.can_afford(choice.cost):
                await conn.send_error(
                    "INSUFFICIENT_RESOURCES",
                    "Cannot afford this building's cost.",
                )
                return
            player.resources.deduct(choice.cost)
        # Check exchange affordability
        if choice.choice_type == "exchange":
            if (
                _player_non_coin_total(player)
                < choice.pick_count
            ):
                await conn.send_error(
                    "INSUFFICIENT_RESOURCES",
                    "Not enough non-coin resources.",
                )
                return
            await _send_resource_choice_prompt(
                server, state, player, choice,
                "building", space.name,
                is_spend=True,
                phase="spend",
            )
            return

        await _send_resource_choice_prompt(
            server, state, player, choice,
            "building", space.name,
        )
        return

    await _check_quest_completion(server, state)


# ------------------------------------------------------------------
# Garage placement handler (quest acquisition)
# ------------------------------------------------------------------


async def _handle_garage_placement(
    server: GameServer, state, player, space, space_id: str
) -> None:
    """Handle placement on a Garage action space."""
    special = space.reward_special

    if special == "reset_quests":
        # Spot 3: discard all face-up, draw 4 new
        deck_reshuffled = False
        state.board.quest_discard.extend(
            state.board.face_up_quests
        )
        state.board.face_up_quests.clear()

        for _ in range(FACE_UP_QUEST_COUNT):
            if (
                not state.board.quest_deck
                and state.board.quest_discard
            ):
                deck_reshuffled = True
            card = _draw_from_quest_deck(state)
            if card:
                state.board.face_up_quests.append(card)

        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="place_worker",
                details=(
                    f"{player.display_name} placed worker on "
                    f"{space.name} — quests reset"
                ),
                timestamp=time.time(),
            )
        )

        await _advance_turn(server, state)
        next_player = state.current_player()

        await server.broadcast_to_game(
            state.game_code,
            QuestsResetResponse(
                player_id=player.player_id,
                deck_reshuffled=deck_reshuffled,
                next_player_id=(
                    next_player.player_id
                    if next_player
                    else None
                ),
            ),
        )
        await server.broadcast_to_game(
            state.game_code,
            FaceUpQuestsUpdatedResponse(
                face_up_quests=[
                    q.model_dump()
                    for q in state.board.face_up_quests
                ]
            ),
        )
    else:
        # Spots 1 & 2: player must select a quest card
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="place_worker",
                details=(
                    f"{player.display_name} placed worker on "
                    f"{space.name} — awaiting quest selection"
                ),
                timestamp=time.time(),
            )
        )

        # Send worker_placed with garage info so client
        # shows the quest selection dialog
        await server.broadcast_to_game(
            state.game_code,
            WorkerPlacedResponse(
                player_id=player.player_id,
                space_id=space_id,
                reward_granted={},
                next_player_id=None,
            ),
        )


async def handle_select_quest_card(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle quest card selection from face-up display."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    # Find the card in face-up quests
    card = None
    for q in state.board.face_up_quests:
        if q.id == msg.card_id:
            card = q
            break
    if card is None:
        await conn.send_error(
            "INVALID_ACTION", "Card not in face-up display."
        )
        return

    # Determine which garage spot the player is on
    spot_special = None
    for sid, sp in state.board.action_spaces.items():
        if (
            sp.space_type == "garage"
            and sp.occupied_by == player.player_id
        ):
            spot_special = sp.reward_special
            break

    if spot_special is None:
        await conn.send_error(
            "INVALID_ACTION",
            "You don't have a worker on a Garage spot.",
        )
        return

    # Move card to player's hand
    state.board.face_up_quests.remove(card)
    player.contract_hand.append(card)

    # Grant bonus based on spot
    bonus_reward = {}
    if spot_special == "quest_and_coins":
        player.resources.coins += 2
        bonus_reward = {"coins": 2}
    elif spot_special == "quest_and_intrigue":
        if state.board.intrigue_deck:
            intrigue = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(intrigue)
            bonus_reward = {
                "intrigue_card": intrigue.model_dump()
            }
        else:
            bonus_reward = {}

    # Draw replacement card
    replacement = _draw_from_quest_deck(state)
    if replacement:
        state.board.face_up_quests.append(replacement)

    spot_num = 1 if spot_special == "quest_and_coins" else 2

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="select_quest_card",
            details=(
                f"{player.display_name} selected "
                f"'{card.name}' from The Garage"
            ),
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        QuestCardSelectedResponse(
            player_id=player.player_id,
            card_id=card.id,
            spot_number=spot_num,
            bonus_reward=bonus_reward,
            next_player_id=None,
        ),
    )
    await server.broadcast_to_game(
        state.game_code,
        FaceUpQuestsUpdatedResponse(
            face_up_quests=[
                q.model_dump()
                for q in state.board.face_up_quests
            ]
        ),
    )

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)
    else:
        await _check_quest_completion(server, state)


# ------------------------------------------------------------------
# Backstage placement handler
# ------------------------------------------------------------------


async def handle_place_worker_backstage(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not _validate_turn(server, conn, state):
        await conn.send_error("NOT_YOUR_TURN", "It is not your turn.")
        return

    player = state.current_player()

    # Validate intrigue card
    card = None
    for c in player.intrigue_hand:
        if c.id == msg.intrigue_card_id:
            card = c
            break
    if card is None:
        await conn.send_error("NO_INTRIGUE_CARDS", "You don't have that intrigue card.")
        return

    # Validate sequential filling
    for s in state.board.backstage_slots:
        if (
            s.slot_number < msg.slot_number
            and s.occupied_by is None
        ):
            await conn.send_error(
                "INVALID_ACTION",
                f"Backstage {s.slot_number} must be filled first.",
            )
            return

    # Validate slot
    slot = None
    for s in state.board.backstage_slots:
        if s.slot_number == msg.slot_number:
            slot = s
            break
    if slot is None or slot.occupied_by is not None:
        await conn.send_error("SPACE_OCCUPIED", "That Backstage slot is occupied.")
        return

    if player.available_workers <= 0:
        await conn.send_error("INVALID_ACTION", "No workers available.")
        return

    # Place worker and play intrigue card
    slot.occupied_by = player.player_id
    slot.intrigue_card_played = card
    player.available_workers -= 1
    player.intrigue_hand.remove(card)
    player.completed_quest_this_turn = False

    # Resolve intrigue card effect
    effect_details = _resolve_intrigue_effect(state, player, card)

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="place_worker_backstage",
            details=f"{player.display_name} placed worker on Backstage slot {msg.slot_number}, played {card.name}",
            timestamp=time.time(),
        )
    )

    # Handle choose_opponent targeting
    if effect_details.get("pending"):
        eligible = effect_details.get("eligible_targets", [])

        if not eligible:
            # No valid targets — auto-unwind backstage placement
            slot.occupied_by = None
            slot.intrigue_card_played = None
            player.intrigue_hand.append(card)
            player.available_workers += 1

            await server.send_to_player(
                player.player_id,
                ErrorResponse(
                    code="NO_VALID_TARGETS",
                    message="No opponents have the targeted resources.",
                ),
            )
            await server.broadcast_to_game(
                state.game_code,
                PlacementCancelledResponse(
                    player_id=player.player_id,
                    space_id=f"backstage_slot_{msg.slot_number}",
                    next_player_id=None,
                ),
            )
            return

        # Save pending state for target selection
        state.pending_intrigue_target = {
            "player_id": player.player_id,
            "slot_number": msg.slot_number,
            "intrigue_card": card.model_dump(),
            "effect_type": card.effect_type,
            "effect_value": card.effect_value,
            "eligible_targets": eligible,
        }

        # Build target info with resource counts
        target_info = []
        for tid in eligible:
            tp = state.get_player(tid)
            if tp:
                target_info.append({
                    "player_id": tp.player_id,
                    "player_name": tp.display_name,
                    "resources": tp.resources.model_dump(),
                })

        await server.send_to_player(
            player.player_id,
            IntrigueTargetPromptResponse(
                effect_type=card.effect_type,
                effect_value=card.effect_value,
                eligible_targets=target_info,
            ),
        )

        # Broadcast worker placed (but no effect yet)
        await server.broadcast_to_game(
            state.game_code,
            WorkerPlacedBackstageResponse(
                player_id=player.player_id,
                slot_number=msg.slot_number,
                intrigue_card={"id": card.id, "name": card.name, "description": card.description},
                intrigue_effect={"type": card.effect_type, "details": {}, "pending": True},
                next_player_id=None,
            ),
        )
        return

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedBackstageResponse(
            player_id=player.player_id,
            slot_number=msg.slot_number,
            intrigue_card={"id": card.id, "name": card.name, "description": card.description},
            intrigue_effect=effect_details,
            next_player_id=None,
        ),
    )

    if effect_details.get("pending_resource_choice"):
        choice = card.choice_reward
        if card.effect_type == "resource_choice_multi":
            others = [
                p.player_id
                for p in state.players
                if p.player_id != player.player_id
            ]
            await _send_resource_choice_prompt(
                server, state, player, choice,
                "intrigue", card.name,
            )
            if state.pending_resource_choice:
                state.pending_resource_choice[
                    "remaining_players"
                ] = others
        else:
            await _send_resource_choice_prompt(
                server, state, player, choice,
                "intrigue", card.name,
            )
        return

    await _check_quest_completion(server, state)


def _resolve_intrigue_effect(state, player, card) -> dict:
    """Resolve an intrigue card's effect and return details dict."""
    effect = {"type": card.effect_type, "details": {}}
    ev = card.effect_value

    if card.effect_type == "gain_resources":
        reward = ResourceCost(**{k: v for k, v in ev.items() if k in ResourceCost.model_fields})
        player.resources.add(reward)
        effect["details"] = reward.model_dump()

    elif card.effect_type == "gain_coins":
        coins = ev.get("coins", 0)
        player.resources.coins += coins
        effect["details"] = {"coins": coins}

    elif card.effect_type == "vp_bonus":
        vp = ev.get("victory_points", 0)
        player.victory_points += vp
        effect["details"] = {"victory_points": vp}

    elif card.effect_type == "draw_contracts":
        count = ev.get("count", 1)
        drawn = []
        for _ in range(count):
            c = _draw_from_quest_deck(state)
            if c:
                player.contract_hand.append(c)
                drawn.append(c.model_dump())
        effect["details"] = {"drawn": drawn, "count": len(drawn)}

    elif card.effect_type == "draw_intrigue":
        count = ev.get("count", 1)
        drawn_cards = _draw_intrigue_cards(
            state, player, count,
        )
        effect["details"] = {
            "drawn": drawn_cards,
            "count": len(drawn_cards),
        }

    elif card.effect_type in ("steal_resources", "opponent_loses"):
        if card.effect_target == "all":
            reward = ResourceCost(**{k: v for k, v in ev.items() if k in ResourceCost.model_fields})
            for p in state.players:
                p.resources.add(reward)
            effect["details"] = {"all_gained": reward.model_dump()}
        elif card.effect_target == "choose_opponent":
            resource_keys = [k for k in ev if k in ResourceCost.model_fields and ev[k] > 0]
            eligible = []
            for p in state.players:
                if p.player_id == player.player_id:
                    continue
                has_resource = any(getattr(p.resources, k, 0) > 0 for k in resource_keys)
                if has_resource:
                    eligible.append(p.player_id)
            effect["pending"] = True
            effect["eligible_targets"] = eligible

    elif card.effect_type == "all_players_gain":
        reward = ResourceCost(**{k: v for k, v in ev.items() if k in ResourceCost.model_fields})
        for p in state.players:
            p.resources.add(reward)
        effect["details"] = {"all_gained": reward.model_dump()}

    elif card.effect_type in (
        "resource_choice", "resource_choice_multi",
    ):
        if card.choice_reward:
            effect["pending_resource_choice"] = True

    return effect


# ------------------------------------------------------------------
# Quest completion handler
# ------------------------------------------------------------------


async def handle_complete_quest(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    # Allow quest completion during own turn (placement or reassignment)
    current = state.current_player()
    is_own_turn = current and current.player_id == conn.player_id
    is_reassignment = state.phase == GamePhase.REASSIGNMENT

    if not is_own_turn and not is_reassignment:
        await conn.send_error("NOT_YOUR_TURN", "It is not your turn.")
        return

    if player.completed_quest_this_turn:
        await conn.send_error("INVALID_ACTION", "Already completed a quest this turn.")
        return

    # Find contract in hand
    contract = None
    for c in player.contract_hand:
        if c.id == msg.contract_id:
            contract = c
            break
    if contract is None:
        await conn.send_error("INVALID_ACTION", "Contract not in your hand.")
        return

    if not player.resources.can_afford(contract.cost):
        await conn.send_error("INSUFFICIENT_RESOURCES", "Not enough resources.")
        return

    # Complete the quest
    player.resources.deduct(contract.cost)
    player.victory_points += contract.victory_points
    player.resources.add(contract.bonus_resources)
    player.contract_hand.remove(contract)
    player.completed_contracts.append(contract)
    player.completed_quest_this_turn = True

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="complete_quest",
            details=(
                f"{player.display_name} completed"
                f" '{contract.name}'"
                f" for {contract.victory_points} VP"
            ),
            timestamp=time.time(),
        )
    )

    drawn_intrigue = _draw_intrigue_cards(
        state, player, contract.reward_draw_intrigue,
    )
    drawn_quests: list[dict] = []
    if (
        contract.reward_draw_quests > 0
        and contract.reward_quest_draw_mode == "random"
    ):
        for _ in range(contract.reward_draw_quests):
            c = _draw_from_quest_deck(state)
            if c:
                player.contract_hand.append(c)
                drawn_quests.append(c.model_dump())

    building_granted = None
    if contract.reward_building == "random_draw":
        building_granted = _grant_random_building(
            state, player,
        )

    has_interactive = False
    if (
        contract.reward_draw_quests > 0
        and contract.reward_quest_draw_mode == "choose"
    ):
        has_interactive = True
    if contract.reward_building == "market_choice":
        has_interactive = True

    if state.waiting_for_quest_completion:
        state.waiting_for_quest_completion = False

    await server.broadcast_to_game(
        state.game_code,
        QuestCompletedResponse(
            player_id=player.player_id,
            contract_id=contract.id,
            contract_name=contract.name,
            victory_points_earned=contract.victory_points,
            resources_spent=contract.cost.model_dump(),
            bonus_resources=(
                contract.bonus_resources.model_dump()
            ),
            drawn_intrigue=drawn_intrigue,
            drawn_quests=drawn_quests,
            building_granted=building_granted,
            pending_choice=has_interactive,
            next_player_id=None,
        ),
    )

    if has_interactive:
        await _send_quest_reward_prompt(
            server, state, player, contract,
        )
        return

    await _advance_turn(server, state)
    next_player = state.current_player()
    if next_player:
        await _notify_turn_if_needed(
            server, state, player,
        )


async def handle_quest_reward_choice(
    server: GameServer, conn: ClientConnection, msg,
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND", "Not in a game.",
        )
        return

    pending = state.pending_quest_reward
    if not pending:
        await conn.send_error(
            "INVALID_ACTION",
            "No pending reward choice.",
        )
        return

    if pending["player_id"] != conn.player_id:
        await conn.send_error(
            "NOT_YOUR_TURN",
            "Not your reward to choose.",
        )
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error(
            "INVALID_ACTION", "Player not found.",
        )
        return

    choice_id = msg.choice_id
    reward_type = pending["reward_type"]
    quest_name = pending["quest_name"]

    if reward_type == "choose_quest":
        chosen = None
        for q in state.board.face_up_quests:
            if q.id == choice_id:
                chosen = q
                break
        if chosen is None:
            await conn.send_error(
                "INVALID_ACTION",
                "Quest not in face-up quests.",
            )
            return
        state.board.face_up_quests.remove(chosen)
        player.contract_hand.append(chosen)
        replacement = _draw_from_quest_deck(state)
        if replacement:
            state.board.face_up_quests.append(
                replacement,
            )
        choice_dict = chosen.model_dump()

    elif reward_type == "choose_building":
        chosen_b = None
        for b in state.board.face_up_buildings:
            if b.id == choice_id:
                chosen_b = b
                break
        if chosen_b is None:
            await conn.send_error(
                "INVALID_ACTION",
                "Building not in market.",
            )
            return
        choice_dict = _assign_building_to_player(
            state, player, chosen_b,
        )
    else:
        await conn.send_error(
            "INVALID_ACTION",
            f"Unknown reward type: {reward_type}",
        )
        return

    state.pending_quest_reward = None

    await server.broadcast_to_game(
        state.game_code,
        QuestRewardChoiceResolvedResponse(
            player_id=player.player_id,
            reward_type=reward_type,
            choice=choice_dict,
            quest_name=quest_name,
        ),
    )

    await _advance_turn(server, state)
    await _notify_turn_if_needed(
        server, state, player,
    )


async def handle_skip_quest_completion(
    server: GameServer,
    conn: ClientConnection,
    msg,
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND", "Not in a game.",
        )
        return

    if not state.waiting_for_quest_completion:
        await conn.send_error(
            "INVALID_ACTION",
            "No quest completion to skip.",
        )
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error(
            "INVALID_ACTION", "Player not found.",
        )
        return

    current = state.current_player()
    if (
        current is None
        or current.player_id != conn.player_id
    ):
        await conn.send_error(
            "NOT_YOUR_TURN",
            "It is not your turn.",
        )
        return

    state.waiting_for_quest_completion = False

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="skip_quest_completion",
            details=(
                f"{player.display_name}"
                " skipped quest completion"
            ),
            timestamp=time.time(),
        )
    )

    await _advance_turn(server, state)
    next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        QuestSkippedResponse(
            player_id=player.player_id,
            next_player_id=(
                next_player.player_id
                if next_player
                else None
            ),
        ),
    )


# ------------------------------------------------------------------
# Contract/Intrigue acquisition handler
# ------------------------------------------------------------------


async def handle_acquire_contract(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    if msg.source == "face_up":
        # Take a specific face-up contract
        contract = None
        for c in state.board.face_up_contracts:
            if c.id == msg.contract_id:
                contract = c
                break
        if contract is None:
            await conn.send_error("INVALID_ACTION", "Contract not in face-up display.")
            return

        state.board.face_up_contracts.remove(contract)
        player.contract_hand.append(contract)

        # Refill face-up
        new_face_up = None
        if state.board.contract_deck:
            replacement = state.board.contract_deck.pop(0)
            state.board.face_up_contracts.append(replacement)
            new_face_up = replacement.model_dump()

        await server.broadcast_to_game(
            state.game_code,
            ContractAcquiredResponse(
                player_id=player.player_id,
                contract_id=contract.id,
                new_face_up=new_face_up,
            ),
        )
    else:
        # Draw from deck
        if not state.board.contract_deck:
            await conn.send_error("INVALID_ACTION", "Contract deck is empty.")
            return
        contract = state.board.contract_deck.pop(0)
        player.contract_hand.append(contract)
        await server.broadcast_to_game(
            state.game_code,
            ContractAcquiredResponse(
                player_id=player.player_id,
                contract_id=contract.id,
                new_face_up=None,
            ),
        )


async def handle_acquire_intrigue(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    if not state.board.intrigue_deck:
        await conn.send_error("INVALID_ACTION", "Intrigue deck is empty.")
        return

    card = state.board.intrigue_deck.pop(0)
    player.intrigue_hand.append(card)

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="acquire_intrigue",
            details=f"{player.display_name} drew an intrigue card",
            timestamp=time.time(),
        )
    )


# ------------------------------------------------------------------
# Building market helpers
# ------------------------------------------------------------------


async def _broadcast_building_market(server: GameServer, state) -> None:
    """Send current face-up building market state to all clients."""
    await server.broadcast_to_game(
        state.game_code,
        BuildingMarketUpdateResponse(
            face_up_buildings=[
                b.model_dump() for b in state.board.face_up_buildings
            ],
            deck_remaining=len(state.board.building_deck),
        ),
    )


# ------------------------------------------------------------------
# Building purchase handler
# ------------------------------------------------------------------


async def handle_purchase_building(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    from shared.messages import BuildingConstructedResponse

    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    # Find building in face-up market
    building = None
    for b in state.board.face_up_buildings:
        if b.id == msg.building_id:
            building = b
            break
    if building is None:
        await conn.send_error("INVALID_ACTION", "Building not available.")
        return

    if player.resources.coins < building.cost_coins:
        await conn.send_error("INSUFFICIENT_RESOURCES", "Not enough Coins.")
        return

    if not state.board.building_lots:
        await conn.send_error("INVALID_ACTION", "No empty building lots available.")
        return

    # Auto-assign next available lot
    lot_id = state.board.building_lots[0]
    lot_index = int(lot_id.split("_")[1])

    # Purchase: deduct coins, award VP
    player.resources.coins -= building.cost_coins
    player.victory_points += building.accumulated_vp
    state.board.face_up_buildings.remove(building)
    state.board.building_lots.remove(lot_id)

    # Draw replacement from deck
    if state.board.building_deck:
        replacement = state.board.building_deck.pop(0)
        replacement.accumulated_vp = 1
        state.board.face_up_buildings.append(replacement)

    # Create new action space
    space_id = f"building_{building.id}"
    state.board.action_spaces[space_id] = ActionSpace(
        space_id=space_id,
        name=building.name,
        space_type="building",
        owner_id=player.player_id,
        building_tile=building,
        reward=building.visitor_reward,
        reward_special=building.visitor_reward_special,
    )
    state.board.constructed_buildings.append(space_id)

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="purchase_building",
            details=(
                f"{player.display_name} built {building.name}"
                f" (+{building.accumulated_vp} VP)"
            ),
            timestamp=time.time(),
        )
    )

    # Advance turn (deferred from placement on Real Estate Listings)
    if state.phase == GamePhase.REASSIGNMENT:
        next_player = None
    else:
        await _advance_turn(server, state)
        next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        BuildingConstructedResponse(
            player_id=player.player_id,
            building_id=building.id,
            building_name=building.name,
            lot_index=lot_index,
            new_space_id=space_id,
            visitor_reward=building.visitor_reward.model_dump(),
            owner_bonus=building.owner_bonus.model_dump(),
            owner_id=player.player_id,
            accumulated_vp=building.accumulated_vp,
            next_player_id=(
                next_player.player_id if next_player else None
            ),
        ),
    )

    # Broadcast updated market
    await _broadcast_building_market(server, state)

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)


async def handle_cancel_purchase_building(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle cancel of building purchase — unwind the placement."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    if state.phase == GamePhase.REASSIGNMENT:
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="cancel_purchase_building",
                details=(
                    f"{player.display_name}"
                    " skipped building purchase"
                ),
                timestamp=time.time(),
            )
        )
        await server.broadcast_to_game(
            state.game_code,
            PlacementCancelledResponse(
                player_id=player.player_id,
                space_id="realtor",
                next_player_id=None,
            ),
        )
        await _finish_reassignment(server, state)
        return

    # Unwind: free the space and return the worker
    space = state.board.action_spaces.get("realtor")
    if space and space.occupied_by == player.player_id:
        space.occupied_by = None
        player.available_workers += 1

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_purchase_building",
            details=(
                f"{player.display_name}"
                " cancelled building purchase"
            ),
            timestamp=time.time(),
        )
    )

    next_player = state.current_player()
    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id="realtor",
            next_player_id=(
                next_player.player_id
                if next_player
                else None
            ),
        ),
    )


async def handle_cancel_quest_selection(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle cancel of quest selection — unwind the garage placement."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    freed_space_id = None
    for sid, sp in state.board.action_spaces.items():
        if (
            sp.space_type == "garage"
            and sp.occupied_by == player.player_id
        ):
            freed_space_id = sid
            break

    if freed_space_id is None:
        await conn.send_error(
            "INVALID_ACTION", "No garage spot to cancel.",
        )
        return

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_quest_selection",
            details=(
                f"{player.display_name}"
                " cancelled quest selection"
            ),
            timestamp=time.time(),
        )
    )

    if state.phase == GamePhase.REASSIGNMENT:
        # During reassignment, keep worker placed, skip quest
        await _finish_reassignment(server, state)
        return

    # Normal placement: unwind the placement
    sp = state.board.action_spaces[freed_space_id]
    sp.occupied_by = None
    player.available_workers += 1

    next_player = state.current_player()
    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id=freed_space_id,
            next_player_id=(
                next_player.player_id
                if next_player
                else None
            ),
        ),
    )


# ------------------------------------------------------------------
# Reassignment handler
# ------------------------------------------------------------------


async def handle_reassign_worker(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if state.phase != GamePhase.REASSIGNMENT:
        await conn.send_error("INVALID_ACTION", "Not in reassignment phase.")
        return

    if not state.reassignment_queue:
        await conn.send_error("INVALID_ACTION", "No slots to reassign.")
        return

    # Must reassign in order
    if msg.slot_number != state.reassignment_queue[0]:
        await conn.send_error(
            "INVALID_ACTION",
            f"Must reassign slot {state.reassignment_queue[0]} first.",
        )
        return

    # Find the slot
    slot = None
    for s in state.board.backstage_slots:
        if s.slot_number == msg.slot_number:
            slot = s
            break
    if slot is None or slot.occupied_by != conn.player_id:
        await conn.send_error("INVALID_ACTION", "Not your worker in that slot.")
        return

    # Cannot reassign to a Backstage slot
    if msg.target_space_id.startswith("backstage_slot_"):
        await conn.send_error("INVALID_ACTION", "Cannot reassign to a Backstage slot.")
        return

    # Validate target space
    target = state.board.action_spaces.get(msg.target_space_id)
    if target is None:
        await conn.send_error("INVALID_ACTION", "Unknown target space.")
        return
    if target.occupied_by is not None:
        await conn.send_error("SPACE_OCCUPIED", "Target space is occupied.")
        return

    player = state.get_player(conn.player_id)

    # Perform reassignment
    slot.occupied_by = None
    target.occupied_by = player.player_id
    reward_dict = target.reward.model_dump()
    player.resources.add(target.reward)
    player.completed_quest_this_turn = False  # Reset for reassignment action

    # Owner bonus for buildings
    owner_bonus_info = {}
    if target.space_type == "building" and target.owner_id:
        owner = state.get_player(target.owner_id)
        if owner and owner.player_id != player.player_id and target.building_tile:
            owner.resources.add(target.building_tile.owner_bonus)
            owner_bonus_info = {
                "owner_id": owner.player_id,
                "owner_name": owner.display_name,
                "bonus": target.building_tile.owner_bonus.model_dump(),
            }
            state.game_log.append(
                GameLog(
                    round_number=state.current_round,
                    player_id=owner.player_id,
                    action="owner_bonus",
                    details=(
                        f"{owner.display_name} received owner bonus from"
                        f" {player.display_name} visiting {target.name}"
                    ),
                    timestamp=time.time(),
                )
            )

    # Handle Castle Waterdeep special
    if target.space_type == "castle":
        for p in state.players:
            p.has_first_player_marker = False
        player.has_first_player_marker = True
        state.board.first_player_id = player.player_id
        if state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)

    state.reassignment_queue.pop(0)

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="reassign_worker",
            details=(
                f"{player.display_name} reassigned from"
                f" Backstage slot {msg.slot_number}"
                f" to {target.name}"
            ),
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        WorkerReassignedResponse(
            player_id=player.player_id,
            from_slot=msg.slot_number,
            to_space_id=msg.target_space_id,
            reward_granted=reward_dict,
            owner_bonus=owner_bonus_info,
        ),
    )

    # Handle Real Estate Listings during reassignment
    if target.reward_special == "purchase_building":
        return

    # Handle Garage spots: pause for quest selection
    if target.space_type == "garage":
        special = target.reward_special
        if special == "reset_quests":
            state.board.quest_discard.extend(
                state.board.face_up_quests
            )
            state.board.face_up_quests.clear()
            for _ in range(FACE_UP_QUEST_COUNT):
                card = _draw_from_quest_deck(state)
                if card:
                    state.board.face_up_quests.append(card)
            await server.broadcast_to_game(
                state.game_code,
                FaceUpQuestsUpdatedResponse(
                    face_up_quests=[
                        q.model_dump()
                        for q in state.board.face_up_quests
                    ]
                ),
            )
        elif special in (
            "quest_and_coins", "quest_and_intrigue",
        ):
            return

    # Resource choice reward on buildings
    if (
        target.building_tile
        and target.building_tile.visitor_reward_choice
    ):
        choice = target.building_tile.visitor_reward_choice
        if choice.cost.total() > 0:
            if not player.resources.can_afford(choice.cost):
                await _finish_reassignment(server, state)
                return
            player.resources.deduct(choice.cost)
        if choice.choice_type == "exchange":
            if (
                _player_non_coin_total(player)
                < choice.pick_count
            ):
                await _finish_reassignment(server, state)
                return
            await _send_resource_choice_prompt(
                server, state, player, choice,
                "building", target.name,
                is_spend=True,
                phase="spend",
            )
            return
        await _send_resource_choice_prompt(
            server, state, player, choice,
            "building", target.name,
        )
        return

    await _finish_reassignment(server, state)


async def _finish_reassignment(
    server: GameServer, state,
) -> None:
    """Continue reassignment queue or end the round."""
    if not state.reassignment_queue:
        await _end_round(server, state)


# ------------------------------------------------------------------
# Intrigue target handler
# ------------------------------------------------------------------


async def handle_choose_intrigue_target(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle targeted intrigue card effects (steal/opponent_loses)."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    pending = state.pending_intrigue_target
    if pending is None or pending["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending intrigue target.")
        return

    if msg.target_player_id not in pending["eligible_targets"]:
        await conn.send_error("INVALID_ACTION", "Invalid target player.")
        return

    player = state.get_player(conn.player_id)
    target = state.get_player(msg.target_player_id)
    if player is None or target is None:
        await conn.send_error("INVALID_ACTION", "Invalid player.")
        return

    effect_type = pending["effect_type"]
    effect_value = pending["effect_value"]
    resources_affected = {}

    resource_keys = [k for k in effect_value if k in ResourceCost.model_fields and effect_value[k] > 0]

    for k in resource_keys:
        amount = effect_value[k]
        target_has = getattr(target.resources, k, 0)
        actual = min(amount, target_has)
        if actual > 0:
            setattr(target.resources, k, target_has - actual)
            if effect_type == "steal_resources":
                current = getattr(player.resources, k, 0)
                setattr(player.resources, k, current + actual)
            resources_affected[k] = actual

    state.pending_intrigue_target = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="intrigue_effect",
            details=(
                f"{player.display_name} used {effect_type} on"
                f" {target.display_name}: {resources_affected}"
            ),
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        IntrigueEffectResolvedResponse(
            player_id=player.player_id,
            target_player_id=target.player_id,
            effect_type=effect_type,
            resources_affected=resources_affected,
        ),
    )

    await _check_quest_completion(server, state)


async def handle_cancel_intrigue_target(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle cancel of intrigue target selection — unwind backstage placement."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    pending = state.pending_intrigue_target
    if pending is None or pending["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending intrigue target.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    slot_number = pending["slot_number"]

    # Unwind: clear backstage slot
    for s in state.board.backstage_slots:
        if s.slot_number == slot_number:
            s.occupied_by = None
            s.intrigue_card_played = None
            break

    # Return intrigue card to hand
    from shared.card_models import IntrigueCard
    card = IntrigueCard(**pending["intrigue_card"])
    player.intrigue_hand.append(card)
    player.available_workers += 1

    state.pending_intrigue_target = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_intrigue_target",
            details=f"{player.display_name} cancelled intrigue target selection",
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id=f"backstage_slot_{slot_number}",
            next_player_id=None,
        ),
    )
