"""Core game logic: worker placement, resource collection, quest completion, scoring."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from server.models.game import ActionSpace, GameLog
import random

from shared.card_models import ContractCard, ResourceCost
from shared.constants import BONUS_WORKER_ROUND, GamePhase
from shared.constants import FACE_UP_QUEST_COUNT
from shared.messages import (
    BonusWorkersGrantedResponse,
    BuildingMarketUpdateResponse,
    ContractAcquiredResponse,
    CopySpacePromptResponse,
    FaceUpQuestsUpdatedResponse,
    FinalPlayerScore,
    GameOverResponse,
    IntrigueEffectResolvedResponse,
    IntriguePlayPromptResponse,
    IntrigueTargetPromptResponse,
    OpponentChoicePromptResponse,
    PlacementCancelledResponse,
    QuestCardSelectedResponse,
    QuestCompletedResponse,
    QuestCompletionPromptResponse,
    QuestRewardChoicePromptResponse,
    QuestRewardChoiceResolvedResponse,
    QuestSkippedResponse,
    ReassignmentPhaseStartResponse,
    ResourceChoicePromptResponse,
    ResourceChoiceResolvedResponse,
    RoundEndResponse,
    RoundStartBonusResponse,
    RoundStartResourceChoicePromptResponse,
    WorkerPlacedBackstageResponse,
    WorkerPlacedResponse,
    WorkerReassignedResponse,
    WorkerRecallPromptResponse,
    WorkerRecalledResponse,
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


def _evaluate_resource_triggers(state, player, reward: ResourceCost):
    """Check completed plot quests for resource triggers and apply bonuses.

    Only evaluates against the original board-action reward, not cascade.
    Returns (trigger_results, pending_swap) where pending_swap is a dict
    if a singer-swap trigger needs interactive resolution.
    """
    trigger_results: list[dict] = []
    pending_swap: dict | None = None

    resource_types = [
        "guitarists",
        "bass_players",
        "drummers",
        "singers",
        "coins",
    ]
    gained_types = [rt for rt in resource_types if getattr(reward, rt, 0) > 0]
    if not gained_types:
        return trigger_results, pending_swap

    for contract in player.completed_contracts:
        if not contract.resource_trigger_type:
            continue
        if contract.resource_trigger_type not in gained_types:
            continue

        entry: dict = {
            "contract_id": contract.id,
            "contract_name": contract.name,
            "trigger_type": contract.resource_trigger_type,
        }

        if contract.resource_trigger_bonus.total() > 0:
            player.resources.add(contract.resource_trigger_bonus)
            entry["bonus_resources"] = contract.resource_trigger_bonus.model_dump()

        if contract.resource_trigger_draw_intrigue > 0:
            drawn = _draw_intrigue_cards(
                state, player, contract.resource_trigger_draw_intrigue
            )
            entry["drawn_intrigue"] = drawn

        if contract.resource_trigger_is_swap and not player.singer_swap_used_this_round:
            non_singer_total = (
                player.resources.guitarists
                + player.resources.bass_players
                + player.resources.drummers
            )
            if non_singer_total > 0:
                pending_swap = {
                    "contract_id": contract.id,
                    "contract_name": contract.name,
                    "player_id": player.player_id,
                }
                entry["swap_pending"] = True

        trigger_results.append(entry)

    return trigger_results, pending_swap


def _extract_intrigue_reward(effect_details: dict) -> ResourceCost | None:
    """Build a ResourceCost from intrigue effect details, if resources were gained."""
    details = effect_details.get("details", {})
    etype = effect_details.get("type", "")
    if etype in ("gain_resources", "all_players_gain"):
        rc = ResourceCost(
            **{k: v for k, v in details.items() if k in ResourceCost.model_fields}
        )
        if rc.total() > 0:
            return rc
    elif etype == "gain_coins":
        coins = details.get("coins", 0)
        if coins > 0:
            return ResourceCost(coins=coins)
    elif etype == "steal_resources" and "all_gained" in details:
        rc = ResourceCost(
            **{
                k: v
                for k, v in details["all_gained"].items()
                if k in ResourceCost.model_fields
            }
        )
        if rc.total() > 0:
            return rc
    return None


def _grant_random_building(state, player) -> dict | None:
    if not state.board.building_deck:
        return None
    tile = state.board.building_deck.pop(0)
    return _assign_building_to_player(state, player, tile)


def _assign_building_to_player(
    state,
    player,
    tile,
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
    server,
    state,
    player,
    contract,
) -> None:
    """Send interactive reward prompt to the player."""
    if contract.reward_draw_quests > 0 and contract.reward_quest_draw_mode == "choose":
        choices = [q.model_dump() for q in state.board.face_up_quests]
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
        choices = [b.model_dump() for b in state.board.face_up_buildings]
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
    server: GameServer,
    state,
) -> None:
    """Check if current player can complete quests."""
    player = state.current_player()
    if player is None or player.completed_quest_this_turn:
        logger.info(
            "Quest completion skip: player=%s completed_this_turn=%s",
            player.display_name if player else None,
            player.completed_quest_this_turn if player else None,
        )
        state.pending_showcase_bonus = None
        await _advance_turn(server, state)
        await _notify_turn_if_needed(
            server,
            state,
            player,
        )
        return

    completable = [
        c for c in player.contract_hand if player.resources.can_afford(c.cost)
    ]
    logger.info(
        "Quest completion check: player=%s resources=%s hand=%s completable=%s",
        player.display_name,
        player.resources,
        [(c.name, c.cost) for c in player.contract_hand],
        [c.name for c in completable],
    )
    if not completable:
        state.pending_showcase_bonus = None
        await _advance_turn(server, state)
        await _notify_turn_if_needed(
            server,
            state,
            player,
        )
        return

    bonus_quest_id = None
    bonus_vp = 0
    if state.pending_showcase_bonus:
        showcase_cid = state.pending_showcase_bonus.get("contract_id")
        if showcase_cid and any(c.id == showcase_cid for c in completable):
            bonus_quest_id = showcase_cid
            bonus_vp = state.pending_showcase_bonus["bonus_vp"]
        else:
            state.pending_showcase_bonus = None

    state.waiting_for_quest_completion = True
    await server.send_to_player(
        player.player_id,
        QuestCompletionPromptResponse(
            completable_quests=[c.model_dump() for c in completable],
            bonus_quest_id=bonus_quest_id,
            bonus_vp=bonus_vp,
        ),
    )


async def _notify_turn_if_needed(
    server: GameServer,
    state,
    prev_player,
) -> None:
    """After auto-advance, tell clients whose turn."""
    if state.phase != GamePhase.PLACEMENT:
        return
    nxt = state.current_player()
    if not nxt:
        return
    pid = prev_player.player_id if prev_player else ""
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
    state.pending_showcase_bonus = None
    state.pending_placement = None

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
        player.use_occupied_used_this_round = False
        player.singer_swap_used_this_round = False

    # Clear board occupants
    for space in state.board.action_spaces.values():
        space.occupied_by = None
        space.also_occupied_by = None
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

    # Increment accumulated stock on constructed accumulating buildings
    for space_id in state.board.constructed_buildings:
        space = state.board.action_spaces.get(space_id)
        if space and space.building_tile and space.building_tile.accumulation_type:
            space.building_tile.accumulated_stock += (
                space.building_tile.accumulation_per_round
            )

    # Set turn order based on first-player marker
    first_pid = state.board.first_player_id
    if first_pid:
        pids = [p.player_id for p in state.players]
        if first_pid in pids:
            idx = pids.index(first_pid)
            state.turn_order = pids[idx:] + pids[:idx]
    state.current_player_index = 0

    accum_stocks = {}
    for space_id in state.board.constructed_buildings:
        space = state.board.action_spaces.get(space_id)
        if space and space.building_tile and space.building_tile.accumulation_type:
            accum_stocks[space_id] = space.building_tile.accumulated_stock

    await server.broadcast_to_game(
        state.game_code,
        RoundEndResponse(
            round_number=round_number,
            next_round=state.current_round,
            first_player_id=state.board.first_player_id,
            turn_order=state.turn_order,
            bonus_worker_granted=bonus_granted,
            accumulated_stocks=accum_stocks,
        ),
    )

    # Broadcast updated building market with incremented VP
    await _broadcast_building_market(server, state)

    # Round-start resource choice for players with reward_choose_resource_per_round
    eligible_players = []
    for pid in state.turn_order:
        p = state.get_player(pid)
        if p:
            for c in p.completed_contracts:
                if c.reward_choose_resource_per_round:
                    eligible_players.append(pid)
                    break

    if eligible_players:
        state.pending_round_start_choices = eligible_players
        first_pid = eligible_players[0]
        first_player = state.get_player(first_pid)
        contract_name = ""
        if first_player:
            for c in first_player.completed_contracts:
                if c.reward_choose_resource_per_round:
                    contract_name = c.name
                    break
            await server.send_to_player(
                first_pid,
                RoundStartResourceChoicePromptResponse(
                    player_id=first_pid,
                    contract_name=contract_name,
                ),
            )
        return


async def _end_game(server: GameServer, state) -> None:
    """Calculate final scores and broadcast game over."""
    state.phase = GamePhase.GAME_OVER

    scores: list[FinalPlayerScore] = []
    for player in state.players:
        game_vp = player.victory_points
        genre_bonus_vp = 0
        if player.producer_card:
            for contract in player.completed_contracts:
                if contract.genre in player.producer_card.bonus_genres:
                    genre_bonus_vp += player.producer_card.bonus_vp_per_contract
        r = player.resources
        resource_vp = (
            r.guitarists + r.bass_players + r.drummers + r.singers + r.coins // 2
        )
        total = game_vp + genre_bonus_vp + resource_vp
        scores.append(
            FinalPlayerScore(
                player_id=player.player_id,
                player_name=player.display_name,
                game_vp=game_vp,
                genre_bonus_vp=genre_bonus_vp,
                resource_vp=resource_vp,
                producer_card=(
                    player.producer_card.model_dump() if player.producer_card else {}
                ),
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
    pending: dict,
    chosen: dict,
) -> str | None:
    """Validate a resource choice. Returns error string or None."""
    choice_type = pending.get("choice_type", "pick")
    allowed = pending.get("allowed_types", [])

    if choice_type == "pick":
        pick_count = pending.get("pick_count", 1)
        total = sum(v for v in chosen.values() if isinstance(v, int))
        if total != pick_count:
            return f"Must pick exactly {pick_count} resource(s)," f" got {total}."
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
        total = sum(v for v in chosen.values() if isinstance(v, int))
        if total != total_required:
            return f"Must allocate exactly {total_required}," f" got {total}."
        for key, val in chosen.items():
            if not isinstance(val, int) or val < 0:
                return f"Invalid value for {key}."
            if val > 0 and key not in allowed:
                return f"{key} is not an allowed choice."
        return None

    if choice_type == "exchange":
        pick_count = pending.get("pick_count", 1)
        total = sum(v for v in chosen.values() if isinstance(v, int))
        if total != pick_count:
            return f"Must select exactly {pick_count} resource(s), got {total}."
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
    can_skip: bool = False,
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
        "can_skip": can_skip,
    }

    await server.broadcast_to_game(
        state.game_code,
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
            can_skip=can_skip,
        ),
    )


async def handle_resource_choice(
    server,
    conn,
    msg,
) -> None:
    """Handle a player's resource choice selection."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND",
            "Not in a game.",
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
            "INVALID_ACTION",
            "Prompt ID mismatch.",
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
        **{k: v for k, v in chosen.items() if k in ResourceCost.model_fields},
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

    # Handle trigger swap resolution (singer swap: spend 1 non-singer → gain 1 singer)
    if pending.get("source_type") == "trigger_swap" and is_spend:
        player.resources.singers += 1
        player.singer_swap_used_this_round = True
        swap_info = state.pending_resource_trigger_swap
        state.pending_resource_trigger_swap = None
        state.pending_resource_choice = None
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="resource_trigger_swap",
                details=(
                    f"{player.display_name} swapped a resource for"
                    f" 1 Singer ({swap_info.get('contract_name', 'plot quest')})"
                ),
                timestamp=time.time(),
            )
        )
        await server.broadcast_to_game(
            state.game_code,
            ResourceChoiceResolvedResponse(
                player_id=player.player_id,
                chosen_resources={"singers": 1},
                is_spend=False,
                source_description=f"Singer swap ({swap_info.get('contract_name', '')})",
            ),
        )
        # Resume pending owner choice if any
        pending_owner = swap_info.get("pending_owner_choice") if swap_info else None
        if pending_owner:
            from shared.card_models import ResourceChoiceReward

            owner = state.get_player(pending_owner["owner_id"])
            if owner:
                rcr = ResourceChoiceReward(**pending_owner["choice_dump"])
                await _send_resource_choice_prompt(
                    server,
                    state,
                    owner,
                    rcr,
                    "owner_bonus",
                    pending_owner["space_name"],
                )
                return
        if swap_info and swap_info.get("is_reassignment"):
            await _finish_reassignment(server, state)
        else:
            await _check_quest_completion(server, state)
        return

    # Handle exchange phase 2 (spend → gain)
    if is_spend and pending.get("phase") == "spend":
        from shared.card_models import ResourceChoiceReward

        rcr = ResourceChoiceReward(
            **pending["choice_reward_dump"],
        )
        await _send_resource_choice_prompt(
            server,
            state,
            player,
            rcr,
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
                server,
                state,
                next_player,
                rcr,
                pending["source_type"],
                source_name,
                pick_count_override=(pending.get("others_pick_count", 1)),
            )
            state.pending_resource_choice["remaining_players"] = remaining
            state.pending_resource_choice["others_pick_count"] = pending.get(
                "others_pick_count", 1
            )
            state.pending_resource_choice["choice_reward_dump"] = pending[
                "choice_reward_dump"
            ]
            return

    # Check for pending owner bonus choice after visitor choice resolves
    pending_owner = pending.get("pending_owner_choice")
    if pending_owner:
        state.pending_resource_choice = None
        owner = state.get_player(pending_owner["owner_id"])
        if owner:
            from shared.card_models import ResourceChoiceReward

            rcr = ResourceChoiceReward(**pending_owner["choice_dump"])
            await _send_resource_choice_prompt(
                server,
                state,
                owner,
                rcr,
                "owner_bonus",
                pending_owner["space_name"],
            )
            return

    state.pending_resource_choice = None
    await _check_quest_completion(server, state)


def _can_use_occupied(player, space, state) -> bool:
    """Check if player can place on an occupied space via special quest ability."""
    if player.use_occupied_used_this_round:
        return False
    if space.occupied_by == player.player_id:
        return False
    for c in player.completed_contracts:
        if c.reward_use_occupied_building:
            return True
    return False


def _get_copy_eligible_spaces(state, player) -> list[dict]:
    """Return opponent-occupied spaces eligible for copying (excludes backstage, own, empty)."""
    eligible = []
    for space in state.board.action_spaces.values():
        if space.occupied_by is None:
            continue
        if space.occupied_by == player.player_id:
            continue
        if space.space_type == "backstage":
            continue
        preview = space.reward.model_dump() if space.reward else {}
        eligible.append(
            {
                "space_id": space.space_id,
                "name": space.name,
                "space_type": space.space_type,
                "reward_preview": preview,
            }
        )
    return eligible


async def _resolve_copied_space_rewards(
    server: "GameServer",
    state,
    player,
    target_space: ActionSpace,
    source_space_id: str,
    pending: dict,
) -> None:
    """Grant rewards from a copied space, handling all space types."""
    reward = target_space.reward
    reward_dict = reward.model_dump()
    player.resources.add(reward)

    # T016: Accumulated stock
    if target_space.building_tile and target_space.building_tile.accumulation_type:
        tile = target_space.building_tile
        stock = tile.accumulated_stock
        if stock > 0:
            atype = tile.accumulation_type
            if atype == "victory_points":
                player.victory_points += stock
                reward_dict["victory_points"] = stock
            elif hasattr(player.resources, atype):
                setattr(
                    player.resources,
                    atype,
                    getattr(player.resources, atype) + stock,
                )
                reward_dict[atype] = reward_dict.get(atype, 0) + stock
            tile.accumulated_stock = 0

    # Visitor VP reward
    if target_space.building_tile and target_space.building_tile.visitor_reward_vp > 0:
        vp = target_space.building_tile.visitor_reward_vp
        player.victory_points += vp
        reward_dict["victory_points"] = reward_dict.get("victory_points", 0) + vp

    # Resource triggers
    trigger_bonuses, pending_swap = _evaluate_resource_triggers(state, player, reward)
    for tb in trigger_bonuses:
        if tb.get("bonus_resources"):
            for k, v in tb["bonus_resources"].items():
                if v:
                    reward_dict[k] = reward_dict.get(k, 0) + v
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="resource_trigger",
                details=(
                    f"{player.display_name} triggered"
                    f" {tb.get('contract_name', 'plot quest')} bonus"
                ),
                timestamp=time.time(),
            )
        )

    # T017: Building visitor_reward_special
    if (
        target_space.space_type == "building"
        and target_space.building_tile
        and target_space.building_tile.visitor_reward_special
    ):
        special = target_space.building_tile.visitor_reward_special
        if special == "draw_intrigue" and state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)
        elif special == "coins_per_building":
            coin_count = len(state.board.constructed_buildings)
            player.resources.coins += coin_count
            reward_dict["coins"] = reward_dict.get("coins", 0) + coin_count

    # T020: Castle space — first player marker + intrigue card
    if target_space.space_type == "castle":
        for p in state.players:
            p.has_first_player_marker = False
        player.has_first_player_marker = True
        state.board.first_player_id = player.player_id
        if state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)

    # Update pending before potential early returns
    pending["copied_from_space_id"] = target_space.space_id
    pending["granted_resources"] = {
        k: v for k, v in reward_dict.items() if k != "victory_points" and v
    }
    pending["granted_vp"] = reward_dict.get("victory_points", 0)
    pending["trigger_bonuses"] = trigger_bonuses

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="copy_space",
            details=(
                f"{player.display_name} copied {target_space.name}"
                f" from {source_space_id}"
            ),
            timestamp=time.time(),
        )
    )

    # T022: Owner bonus cascading for copied buildings
    owner_bonus_info = {}
    if target_space.space_type == "building" and target_space.owner_id:
        owner = state.get_player(target_space.owner_id)
        if owner and owner.player_id != player.player_id and target_space.building_tile:
            tile = target_space.building_tile
            owner.resources.add(tile.owner_bonus)
            bonus_dict = tile.owner_bonus.model_dump()
            if tile.owner_bonus_vp > 0:
                owner.victory_points += tile.owner_bonus_vp
                bonus_dict["victory_points"] = tile.owner_bonus_vp
            if tile.owner_bonus_special == "draw_intrigue":
                if state.board.intrigue_deck:
                    card = state.board.intrigue_deck.pop(0)
                    owner.intrigue_hand.append(card)
                    bonus_dict["intrigue_card"] = True
            owner_bonus_info = {
                "owner_id": owner.player_id,
                "owner_name": owner.display_name,
                "bonus": bonus_dict,
            }
            pending["owner_bonus_info"] = owner_bonus_info
            state.game_log.append(
                GameLog(
                    round_number=state.current_round,
                    player_id=owner.player_id,
                    action="owner_bonus",
                    details=(
                        f"{owner.display_name} received owner bonus from"
                        f" {player.display_name} copying {target_space.name}"
                    ),
                    timestamp=time.time(),
                )
            )

    copied_space_info = {
        "space_type": target_space.space_type,
        "reward_special": target_space.reward_special,
    }
    if target_space.building_tile:
        copied_space_info["building_tile"] = {
            "visitor_reward_special": target_space.building_tile.visitor_reward_special,
        }

    state.pending_copy_source = None

    # Garage reset_quests must happen before WorkerPlacedResponse so client
    # has updated quest IDs when entering quest selection highlight mode
    if (
        target_space.space_type == "garage"
        and target_space.reward_special == "reset_quests"
    ):
        state.board.quest_discard.extend(state.board.face_up_quests)
        state.board.face_up_quests.clear()
        for _ in range(FACE_UP_QUEST_COUNT):
            card = _draw_from_quest_deck(state)
            if card:
                state.board.face_up_quests.append(card)
        await server.broadcast_to_game(
            state.game_code,
            FaceUpQuestsUpdatedResponse(
                face_up_quests=[q.model_dump() for q in state.board.face_up_quests]
            ),
        )

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedResponse(
            player_id=player.player_id,
            space_id=source_space_id,
            reward_granted=reward_dict,
            owner_bonus=owner_bonus_info,
            trigger_bonuses=trigger_bonuses,
            next_player_id=None,
            copied_space=copied_space_info,
        ),
    )

    # T021: Realtor space — enter building purchase flow
    if target_space.reward_special == "purchase_building":
        state.pending_placement = pending
        return

    # T019: Garage spaces — enter quest selection flow
    if target_space.space_type == "garage":
        state.pending_placement = pending
        return

    # T018: Resource choice buildings
    if target_space.building_tile and target_space.building_tile.visitor_reward_choice:
        state.pending_placement = pending
        choice = target_space.building_tile.visitor_reward_choice
        if choice.cost.total() > 0:
            if not player.resources.can_afford(choice.cost):
                state.pending_placement = None
                await _check_quest_completion(server, state)
                return
            player.resources.deduct(choice.cost)
        if choice.choice_type == "exchange":
            if _player_non_coin_total(player) < choice.pick_count:
                state.pending_placement = None
                await _check_quest_completion(server, state)
                return
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                choice,
                "building",
                target_space.name,
                is_spend=True,
                phase="spend",
            )
            return
        await _send_resource_choice_prompt(
            server,
            state,
            player,
            choice,
            "building",
            target_space.name,
        )
        return

    # T017: draw_contract / draw_contract_and_complete — quest selection
    if (
        target_space.space_type == "building"
        and target_space.building_tile
        and target_space.building_tile.visitor_reward_special
        in ("draw_contract", "draw_contract_and_complete")
    ):
        state.pending_placement = pending
        state.pending_building_quest = {
            "player_id": player.player_id,
            "space_id": source_space_id,
            "granted_vp": pending["granted_vp"],
            "granted_resources": dict(pending["granted_resources"]),
            "accumulated_stock_consumed": pending.get("accumulated_stock_consumed", 0),
            "accumulation_type": pending.get("accumulation_type"),
            "owner_bonus_info": owner_bonus_info,
            "trigger_bonuses": trigger_bonuses,
        }
        if (
            target_space.building_tile.visitor_reward_special
            == "draw_contract_and_complete"
        ):
            state.pending_showcase_bonus = {
                "player_id": player.player_id,
                "contract_id": None,
                "bonus_vp": 4,
            }
        return

    await _check_quest_completion(server, state)


async def handle_skip_resource_choice(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle skipping an optional resource choice (e.g. singer swap)."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    pending = state.pending_resource_choice
    if pending is None or pending["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending resource choice.")
        return

    if not pending.get("can_skip"):
        await conn.send_error("INVALID_ACTION", "This choice cannot be skipped.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        return

    swap_info = state.pending_resource_trigger_swap
    state.pending_resource_trigger_swap = None
    state.pending_resource_choice = None

    if swap_info and swap_info.get("is_reassignment"):
        await _finish_reassignment(server, state)
    else:
        # Resume pending owner choice if any
        pending_owner = swap_info.get("pending_owner_choice") if swap_info else None
        if pending_owner:
            from shared.card_models import ResourceChoiceReward

            owner = state.get_player(pending_owner["owner_id"])
            if owner:
                rcr = ResourceChoiceReward(**pending_owner["choice_dump"])
                await _send_resource_choice_prompt(
                    server,
                    state,
                    owner,
                    rcr,
                    "owner_bonus",
                    pending_owner["space_name"],
                )
                return
        await _check_quest_completion(server, state)


# ------------------------------------------------------------------
# Worker placement handler
# ------------------------------------------------------------------


async def handle_place_worker(server: GameServer, conn: ClientConnection, msg) -> None:
    """Place a worker on a board space: validate, grant rewards, handle specials (buildings, quests, resource choices)."""
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
        if _can_use_occupied(player, space, state):
            player.use_occupied_used_this_round = True
            space.also_occupied_by = space.occupied_by
        else:
            has_ability = any(
                c.reward_use_occupied_building for c in player.completed_contracts
            )
            if has_ability and player.use_occupied_used_this_round:
                await conn.send_error(
                    "SPACE_OCCUPIED",
                    "Already used your occupied-space ability this round.",
                )
            elif has_ability and space.occupied_by == player.player_id:
                await conn.send_error(
                    "SPACE_OCCUPIED",
                    "Cannot use occupied-space ability on your own worker.",
                )
            else:
                await conn.send_error(
                    "SPACE_OCCUPIED", "That space is already occupied."
                )
            return

    if player.available_workers <= 0:
        await conn.send_error("INVALID_ACTION", "No workers available.")
        return

    # Pre-validate resource choice affordability before committing placement
    if space.building_tile and space.building_tile.visitor_reward_choice:
        choice = space.building_tile.visitor_reward_choice
        future_resources = player.resources.model_copy()
        future_resources.add(space.reward)
        if choice.cost.total() > 0 and not future_resources.can_afford(choice.cost):
            logger.warning(
                "Pre-validate fail: player %s coins=%d, cost=%s, future=%s, space=%s",
                player.display_name,
                player.resources.coins,
                choice.cost,
                future_resources,
                space.name,
            )
            await conn.send_error(
                "INSUFFICIENT_RESOURCES",
                "Cannot afford this building's cost.",
            )
            return
        if choice.choice_type == "exchange":
            future_resources.deduct(choice.cost)
            non_coin = (
                future_resources.guitarists
                + future_resources.bass_players
                + future_resources.drummers
                + future_resources.singers
            )
            if non_coin < choice.pick_count:
                await conn.send_error(
                    "INSUFFICIENT_RESOURCES",
                    "Not enough non-coin resources.",
                )
                return

    # Place worker
    space.occupied_by = player.player_id
    player.available_workers -= 1
    player.completed_quest_this_turn = False

    # Grant reward
    reward_dict = space.reward.model_dump()
    player.resources.add(space.reward)

    # Grant accumulated stock on accumulating buildings
    if space.building_tile and space.building_tile.accumulation_type:
        tile = space.building_tile
        stock = tile.accumulated_stock
        if stock > 0:
            atype = tile.accumulation_type
            if atype == "victory_points":
                player.victory_points += stock
                reward_dict["victory_points"] = stock
            elif hasattr(player.resources, atype):
                setattr(
                    player.resources,
                    atype,
                    getattr(player.resources, atype) + stock,
                )
                reward_dict[atype] = reward_dict.get(atype, 0) + stock
            tile.accumulated_stock = 0

    # Grant visitor VP reward from building
    if space.building_tile and space.building_tile.visitor_reward_vp > 0:
        player.victory_points += space.building_tile.visitor_reward_vp
        reward_dict["victory_points"] = (
            reward_dict.get("victory_points", 0) + space.building_tile.visitor_reward_vp
        )

    # Evaluate resource trigger plot quests (no cascade — uses base reward only)
    trigger_bonuses, pending_swap = _evaluate_resource_triggers(
        state, player, space.reward
    )
    trigger_bonuses_data = trigger_bonuses
    for tb in trigger_bonuses:
        if tb.get("bonus_resources"):
            for k, v in tb["bonus_resources"].items():
                if v and k in reward_dict:
                    reward_dict[k] = reward_dict.get(k, 0) + v
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="resource_trigger",
                details=(
                    f"{player.display_name} triggered"
                    f" {tb.get('contract_name', 'plot quest')} bonus"
                ),
                timestamp=time.time(),
            )
        )

    # Build pending_placement base dict for cancel/unwind support
    _acc_consumed = 0
    if space.building_tile and space.building_tile.accumulation_type:
        atype = space.building_tile.accumulation_type
        if atype == "victory_points":
            _acc_consumed = max(
                0,
                reward_dict.get("victory_points", 0)
                - space.building_tile.visitor_reward_vp,
            )
        else:
            base = (
                getattr(space.reward, atype, 0) if hasattr(space.reward, atype) else 0
            )
            _acc_consumed = max(0, reward_dict.get(atype, 0) - base)

    _pending = {
        "player_id": player.player_id,
        "space_id": msg.space_id,
        "granted_resources": {
            k: v for k, v in reward_dict.items() if k != "victory_points" and v
        },
        "granted_vp": reward_dict.get("victory_points", 0),
        "accumulated_stock_consumed": _acc_consumed,
        "accumulation_type": (
            space.building_tile.accumulation_type
            if space.building_tile and space.building_tile.accumulation_type
            else None
        ),
        "owner_bonus_info": {},
        "trigger_bonuses": trigger_bonuses_data,
    }

    # Handle Garage spots (quest selection)
    if space.space_type == "garage":
        state.pending_placement = _pending
        await _handle_garage_placement(server, state, player, space, msg.space_id)
        return

    # Handle Real Estate Listings (building purchase — deferred turn)
    if space.reward_special == "purchase_building":
        state.pending_placement = _pending
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
                trigger_bonuses=trigger_bonuses_data,
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

    # Building visitor_reward_special: draw_contract, draw_intrigue, coins_per_building
    if (
        space.space_type == "building"
        and space.building_tile
        and space.building_tile.visitor_reward_special
    ):
        special = space.building_tile.visitor_reward_special
        if special == "draw_intrigue" and state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)
        elif special == "coins_per_building":
            coin_count = len(state.board.constructed_buildings)
            player.resources.coins += coin_count
            reward_dict["coins"] = reward_dict.get("coins", 0) + coin_count
        elif special == "copy_occupied_space":
            eligible = _get_copy_eligible_spaces(state, player)
            if not eligible:
                pass
            else:
                _pending["granted_resources"] = {
                    k: v for k, v in reward_dict.items() if k != "victory_points" and v
                }
                _pending["granted_vp"] = reward_dict.get("victory_points", 0)
                state.pending_placement = _pending
                state.pending_copy_source = {
                    "player_id": player.player_id,
                    "source_space_id": msg.space_id,
                    "source_type": "building",
                    "eligible_spaces": [s["space_id"] for s in eligible],
                }
                state.game_log.append(
                    GameLog(
                        round_number=state.current_round,
                        player_id=player.player_id,
                        action="place_worker",
                        details=(
                            f"{player.display_name} placed worker on"
                            f" {space.name} — selecting space to copy"
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
                        owner_bonus={},
                        trigger_bonuses=trigger_bonuses_data,
                        next_player_id=None,
                    ),
                )
                await conn.send_model(
                    CopySpacePromptResponse(
                        eligible_spaces=eligible,
                        source_type="building",
                    )
                )
                return

    # Update _pending with any extra resources from building specials
    _pending["granted_resources"] = {
        k: v for k, v in reward_dict.items() if k != "victory_points" and v
    }
    _pending["granted_vp"] = reward_dict.get("victory_points", 0)

    # Owner bonus for buildings
    owner_bonus_info = {}
    if space.space_type == "building" and space.owner_id:
        owner = state.get_player(space.owner_id)
        if owner and owner.player_id != player.player_id and space.building_tile:
            tile = space.building_tile
            owner.resources.add(tile.owner_bonus)
            bonus_dict = tile.owner_bonus.model_dump()
            if tile.owner_bonus_vp > 0:
                owner.victory_points += tile.owner_bonus_vp
                bonus_dict["victory_points"] = tile.owner_bonus_vp
            if tile.owner_bonus_special == "draw_intrigue":
                if state.board.intrigue_deck:
                    card = state.board.intrigue_deck.pop(0)
                    owner.intrigue_hand.append(card)
                    bonus_dict["intrigue_card"] = True
            owner_bonus_info = {
                "owner_id": owner.player_id,
                "owner_name": owner.display_name,
                "bonus": bonus_dict,
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

    _pending["owner_bonus_info"] = owner_bonus_info

    # Detect pending owner bonus choice
    pending_owner_choice = None
    if (
        space.space_type == "building"
        and space.owner_id
        and space.building_tile
        and space.building_tile.owner_bonus_choice
    ):
        bonus_owner = state.get_player(space.owner_id)
        if bonus_owner and bonus_owner.player_id != player.player_id:
            pending_owner_choice = {
                "owner_id": bonus_owner.player_id,
                "choice_dump": space.building_tile.owner_bonus_choice.model_dump(),
                "space_name": space.name,
            }

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
            trigger_bonuses=trigger_bonuses_data,
            next_player_id=None,
        ),
    )

    # Singer swap trigger prompt
    if pending_swap:
        from shared.card_models import ResourceChoiceReward

        state.pending_placement = _pending
        swap_choice = ResourceChoiceReward(
            choice_type="pick",
            allowed_types=["guitarists", "bass_players", "drummers"],
            pick_count=1,
        )
        state.pending_resource_trigger_swap = {
            "player_id": player.player_id,
            "contract_id": pending_swap["contract_id"],
            "contract_name": pending_swap["contract_name"],
            "space_id": msg.space_id,
            "pending_owner_choice": pending_owner_choice,
        }
        await _send_resource_choice_prompt(
            server,
            state,
            player,
            swap_choice,
            "trigger_swap",
            f"Swap for Singer ({pending_swap['contract_name']})",
            is_spend=True,
            can_skip=True,
        )
        return

    # Resource choice reward on buildings
    if space.building_tile and space.building_tile.visitor_reward_choice:
        state.pending_placement = _pending
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
            if _player_non_coin_total(player) < choice.pick_count:
                await conn.send_error(
                    "INSUFFICIENT_RESOURCES",
                    "Not enough non-coin resources.",
                )
                return
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                choice,
                "building",
                space.name,
                is_spend=True,
                phase="spend",
            )
            if pending_owner_choice:
                state.pending_resource_choice["pending_owner_choice"] = (
                    pending_owner_choice
                )
            return

        await _send_resource_choice_prompt(
            server,
            state,
            player,
            choice,
            "building",
            space.name,
        )
        if pending_owner_choice:
            state.pending_resource_choice["pending_owner_choice"] = pending_owner_choice
        return

    # Owner bonus choice (no visitor choice to resolve first)
    if pending_owner_choice:
        from shared.card_models import ResourceChoiceReward

        state.pending_placement = _pending
        bonus_owner = state.get_player(pending_owner_choice["owner_id"])
        if bonus_owner:
            rcr = ResourceChoiceReward(**pending_owner_choice["choice_dump"])
            await _send_resource_choice_prompt(
                server,
                state,
                bonus_owner,
                rcr,
                "owner_bonus",
                pending_owner_choice["space_name"],
            )
            return

    # Building draw_contract / draw_contract_and_complete: pause for quest selection.
    if (
        space.space_type == "building"
        and space.building_tile
        and space.building_tile.visitor_reward_special
        in ("draw_contract", "draw_contract_and_complete")
    ):
        state.pending_placement = _pending
        state.pending_building_quest = {
            "player_id": player.player_id,
            "space_id": msg.space_id,
            "granted_vp": _pending["granted_vp"],
            "granted_resources": dict(_pending["granted_resources"]),
            "accumulated_stock_consumed": _pending["accumulated_stock_consumed"],
            "accumulation_type": _pending["accumulation_type"],
            "owner_bonus_info": owner_bonus_info,
            "trigger_bonuses": trigger_bonuses_data,
        }
        if space.building_tile.visitor_reward_special == "draw_contract_and_complete":
            state.pending_showcase_bonus = {
                "player_id": player.player_id,
                "contract_id": None,
                "bonus_vp": 4,
            }
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
        # Spot 3: discard all face-up, draw 4 new, then let player pick
        state.board.quest_discard.extend(state.board.face_up_quests)
        state.board.face_up_quests.clear()

        for _ in range(FACE_UP_QUEST_COUNT):
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
                    f"{space.name} — quests reset, awaiting selection"
                ),
                timestamp=time.time(),
            )
        )

        await server.broadcast_to_game(
            state.game_code,
            FaceUpQuestsUpdatedResponse(
                face_up_quests=[q.model_dump() for q in state.board.face_up_quests]
            ),
        )

        await server.broadcast_to_game(
            state.game_code,
            WorkerPlacedResponse(
                player_id=player.player_id,
                space_id=space_id,
                reward_granted={},
                next_player_id=None,
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
        await conn.send_error("INVALID_ACTION", "Card not in face-up display.")
        return

    # Determine which spot the player is on (garage or building with draw_contract)
    spot_special = None
    is_building_draw = False
    for sid, sp in state.board.action_spaces.items():
        if sp.occupied_by != player.player_id:
            continue
        if sp.space_type == "garage":
            spot_special = sp.reward_special
            break
        if (
            sp.space_type == "building"
            and sp.building_tile
            and sp.building_tile.visitor_reward_special
            in ("draw_contract", "draw_contract_and_complete")
        ):
            spot_special = sp.building_tile.visitor_reward_special
            is_building_draw = True
            break

    if spot_special is None:
        await conn.send_error(
            "INVALID_ACTION",
            "No worker on a quest selection spot.",
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
            bonus_reward = {"intrigue_card": intrigue.model_dump()}
        else:
            bonus_reward = {}

    # Draw replacement card
    replacement = _draw_from_quest_deck(state)
    if replacement:
        state.board.face_up_quests.append(replacement)

    spot_num = (
        0 if is_building_draw else (1 if spot_special == "quest_and_coins" else 2)
    )
    source = "a building" if is_building_draw else "The Garage"

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="select_quest_card",
            details=(f"{player.display_name} selected '{card.name}' from {source}"),
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
            face_up_quests=[q.model_dump() for q in state.board.face_up_quests]
        ),
    )

    state.pending_building_quest = None
    state.pending_placement = None

    # Showcase bonus: track selected contract for potential +VP bonus
    if (
        state.pending_showcase_bonus
        and state.pending_showcase_bonus.get("contract_id") is None
    ):
        state.pending_showcase_bonus["contract_id"] = card.id

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
    """Place a worker on a backstage slot with an intrigue card; resolves the card's effect immediately or defers to target selection."""
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
        if s.slot_number < msg.slot_number and s.occupied_by is None:
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

    # Check for plot quest intrigue bonus
    plot_bonus_vp = 0
    for completed in player.completed_contracts:
        if completed.bonus_vp_per_intrigue_played > 0:
            plot_bonus_vp += completed.bonus_vp_per_intrigue_played
    player.victory_points += plot_bonus_vp

    log_detail = f"{player.display_name} placed worker on Backstage slot {msg.slot_number}, played {card.name}"
    if plot_bonus_vp:
        log_detail += f" (+{plot_bonus_vp} plot quest bonus)"

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="place_worker_backstage",
            details=log_detail,
            timestamp=time.time(),
        )
    )

    # Handle copy_occupied_space intrigue card
    if effect_details.get("insufficient_coins"):
        slot.occupied_by = None
        player.available_workers += 1
        player.intrigue_hand.append(card)
        slot.intrigue_card_played = None
        player.victory_points -= plot_bonus_vp
        await conn.send_error(
            "INSUFFICIENT_COINS",
            "You need 2 coins to play this card.",
        )
        return

    if effect_details.get("no_valid_targets"):
        slot.occupied_by = None
        player.available_workers += 1
        player.intrigue_hand.append(card)
        slot.intrigue_card_played = None
        player.victory_points -= plot_bonus_vp
        await conn.send_error(
            "NO_VALID_TARGETS",
            "No valid target spaces available.",
        )
        return

    if effect_details.get("eligible_spaces"):
        state.pending_placement = {
            "player_id": player.player_id,
            "space_id": f"backstage_slot_{msg.slot_number}",
            "granted_resources": {},
            "granted_vp": plot_bonus_vp,
            "accumulated_stock_consumed": 0,
            "accumulation_type": None,
            "owner_bonus_info": {},
            "trigger_bonuses": [],
        }
        state.pending_copy_source = {
            "player_id": player.player_id,
            "source_space_id": f"backstage_slot_{msg.slot_number}",
            "source_type": "intrigue",
            "cost_deducted": effect_details.get("cost_deducted", 0),
            "intrigue_card": card.model_dump(),
            "slot_number": msg.slot_number,
            "eligible_spaces": [
                s["space_id"] for s in effect_details["eligible_spaces"]
            ],
        }

        await server.broadcast_to_game(
            state.game_code,
            WorkerPlacedBackstageResponse(
                player_id=player.player_id,
                slot_number=msg.slot_number,
                intrigue_card={
                    "id": card.id,
                    "name": card.name,
                    "description": card.description,
                },
                intrigue_effect={
                    "type": card.effect_type,
                    "details": {},
                    "pending": True,
                },
                plot_quest_bonus_vp=plot_bonus_vp,
                next_player_id=None,
            ),
        )

        await conn.send_model(
            CopySpacePromptResponse(
                eligible_spaces=effect_details["eligible_spaces"],
                source_type="intrigue",
            )
        )
        return

    # Handle choose_opponent targeting
    if effect_details.get("pending"):
        eligible = effect_details.get("eligible_targets", [])

        state.pending_placement = {
            "player_id": player.player_id,
            "space_id": f"backstage_slot_{msg.slot_number}",
            "granted_resources": {},
            "granted_vp": plot_bonus_vp,
            "accumulated_stock_consumed": 0,
            "accumulation_type": None,
            "owner_bonus_info": {},
            "trigger_bonuses": [],
        }

        state.pending_intrigue_target = {
            "player_id": player.player_id,
            "slot_number": msg.slot_number,
            "intrigue_card": card.model_dump(),
            "effect_type": card.effect_type,
            "effect_value": card.effect_value,
            "eligible_targets": eligible,
            "plot_bonus_vp": plot_bonus_vp,
        }

        # Build target info with resource counts
        target_info = []
        for tid in eligible:
            tp = state.get_player(tid)
            if tp:
                target_info.append(
                    {
                        "player_id": tp.player_id,
                        "player_name": tp.display_name,
                        "resources": tp.resources.model_dump(),
                    }
                )

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
                intrigue_card={
                    "id": card.id,
                    "name": card.name,
                    "description": card.description,
                },
                intrigue_effect={
                    "type": card.effect_type,
                    "details": {},
                    "pending": True,
                },
                plot_quest_bonus_vp=plot_bonus_vp,
                next_player_id=None,
            ),
        )
        return

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedBackstageResponse(
            player_id=player.player_id,
            slot_number=msg.slot_number,
            intrigue_card={
                "id": card.id,
                "name": card.name,
                "description": card.description,
            },
            intrigue_effect=effect_details,
            plot_quest_bonus_vp=plot_bonus_vp,
            next_player_id=None,
        ),
    )

    if effect_details.get("pending_resource_choice"):
        choice = card.choice_reward
        if card.effect_type == "resource_choice_multi":
            others = [
                p.player_id for p in state.players if p.player_id != player.player_id
            ]
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                choice,
                "intrigue",
                card.name,
            )
            if state.pending_resource_choice:
                state.pending_resource_choice["remaining_players"] = others
        else:
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                choice,
                "intrigue",
                card.name,
            )
        return

    # Check for resource triggers from intrigue-granted resources
    intrigue_reward = _extract_intrigue_reward(effect_details)
    if intrigue_reward:
        trigger_bonuses, pending_swap = _evaluate_resource_triggers(
            state, player, intrigue_reward
        )
        for tb in trigger_bonuses:
            if tb.get("bonus_resources"):
                bonus_rc = {k: v for k, v in tb["bonus_resources"].items() if v}
                if bonus_rc:
                    await server.broadcast_to_game(
                        state.game_code,
                        ResourceChoiceResolvedResponse(
                            player_id=player.player_id,
                            chosen_resources=bonus_rc,
                            is_spend=False,
                            source_description=(
                                f"{tb.get('contract_name', 'plot quest')} trigger"
                            ),
                        ),
                    )
            state.game_log.append(
                GameLog(
                    round_number=state.current_round,
                    player_id=player.player_id,
                    action="resource_trigger",
                    details=(
                        f"{player.display_name} triggered"
                        f" {tb.get('contract_name', 'plot quest')} bonus"
                        f" from intrigue card"
                    ),
                    timestamp=time.time(),
                )
            )
        if pending_swap:
            from shared.card_models import ResourceChoiceReward

            swap_choice = ResourceChoiceReward(
                choice_type="pick",
                allowed_types=["guitarists", "bass_players", "drummers"],
                pick_count=1,
            )
            state.pending_resource_trigger_swap = {
                "player_id": player.player_id,
                "contract_id": pending_swap["contract_id"],
                "contract_name": pending_swap["contract_name"],
                "space_id": f"backstage_{msg.slot_number}",
                "pending_owner_choice": None,
            }
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                swap_choice,
                "trigger_swap",
                f"Swap for Singer ({pending_swap['contract_name']})",
                is_spend=True,
                can_skip=True,
            )
            return

    await _check_quest_completion(server, state)


def _resolve_intrigue_effect(state, player, card) -> dict:
    """Resolve an intrigue card's effect and return details dict."""
    effect = {"type": card.effect_type, "details": {}}
    ev = card.effect_value

    if card.effect_type == "gain_resources":
        reward = ResourceCost(
            **{k: v for k, v in ev.items() if k in ResourceCost.model_fields}
        )
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
            state,
            player,
            count,
        )
        effect["details"] = {
            "drawn": drawn_cards,
            "count": len(drawn_cards),
        }

    elif card.effect_type in ("steal_resources", "opponent_loses"):
        if card.effect_target == "all":
            reward = ResourceCost(
                **{k: v for k, v in ev.items() if k in ResourceCost.model_fields}
            )
            for p in state.players:
                p.resources.add(reward)
            effect["details"] = {"all_gained": reward.model_dump()}
        elif card.effect_target == "choose_opponent":
            resource_keys = [
                k for k in ev if k in ResourceCost.model_fields and ev[k] > 0
            ]
            eligible = []
            for p in state.players:
                if p.player_id == player.player_id:
                    continue
                has_resource = all(
                    getattr(p.resources, k, 0) >= ev[k] for k in resource_keys
                )
                if has_resource:
                    eligible.append(p.player_id)
            effect["pending"] = True
            effect["eligible_targets"] = eligible

    elif card.effect_type == "all_players_gain":
        reward = ResourceCost(
            **{k: v for k, v in ev.items() if k in ResourceCost.model_fields}
        )
        for p in state.players:
            p.resources.add(reward)
        effect["details"] = {"all_gained": reward.model_dump()}

    elif card.effect_type in (
        "resource_choice",
        "resource_choice_multi",
    ):
        if card.choice_reward:
            effect["pending_resource_choice"] = True

    elif card.effect_type == "copy_occupied_space":
        cost_coins = ev.get("cost_coins", 2)
        if player.resources.coins < cost_coins:
            effect["insufficient_coins"] = True
        else:
            eligible = _get_copy_eligible_spaces(state, player)
            if not eligible:
                effect["no_valid_targets"] = True
            else:
                player.resources.coins -= cost_coins
                effect["pending"] = True
                effect["cost_deducted"] = cost_coins
                effect["eligible_spaces"] = eligible

    return effect


# ------------------------------------------------------------------
# Quest completion handler
# ------------------------------------------------------------------


async def handle_complete_quest(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Complete a quest: deduct resource costs, award VP and bonus rewards, trigger quest-chain draws."""
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

    # Check for plot quest genre bonuses BEFORE appending (so a plot quest
    # doesn't trigger its own bonus).
    plot_bonus_vp = 0
    for completed in player.completed_contracts:
        if (
            completed.bonus_vp_per_genre_quest > 0
            and completed.bonus_vp_genre == contract.genre
        ):
            plot_bonus_vp += completed.bonus_vp_per_genre_quest

    # One-time bonus: count buildings player currently owns
    if contract.bonus_vp_per_building_owned > 0:
        buildings_owned = sum(
            1
            for sid in state.board.constructed_buildings
            if state.board.action_spaces.get(sid)
            and state.board.action_spaces[sid].owner_id == player.player_id
        )
        plot_bonus_vp += contract.bonus_vp_per_building_owned * buildings_owned

    player.victory_points += plot_bonus_vp

    showcase_bonus_vp = 0
    if (
        state.pending_showcase_bonus
        and state.pending_showcase_bonus.get("contract_id") == contract.id
    ):
        showcase_bonus_vp = state.pending_showcase_bonus["bonus_vp"]
        player.victory_points += showcase_bonus_vp
        state.pending_showcase_bonus = None

    player.contract_hand.remove(contract)
    player.completed_contracts.append(contract)
    player.completed_quest_this_turn = True

    vp_detail = f"{contract.victory_points} VP"
    if plot_bonus_vp:
        vp_detail += f" + {plot_bonus_vp} plot quest bonus"
    if showcase_bonus_vp:
        vp_detail += f" + {showcase_bonus_vp} Audition Showcase bonus"

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="complete_quest",
            details=(
                f"{player.display_name} completed"
                f" '{contract.name}'"
                f" for {vp_detail}"
            ),
            timestamp=time.time(),
        )
    )

    drawn_intrigue = _draw_intrigue_cards(
        state,
        player,
        contract.reward_draw_intrigue,
    )
    drawn_quests: list[dict] = []
    if contract.reward_draw_quests > 0 and contract.reward_quest_draw_mode == "random":
        for _ in range(contract.reward_draw_quests):
            c = _draw_from_quest_deck(state)
            if c:
                player.contract_hand.append(c)
                drawn_quests.append(c.model_dump())

    building_granted = None
    if contract.reward_building == "random_draw":
        building_granted = _grant_random_building(
            state,
            player,
        )

    has_interactive = False
    if contract.reward_draw_quests > 0 and contract.reward_quest_draw_mode == "choose":
        has_interactive = True
    if contract.reward_building == "market_choice":
        has_interactive = True

    # --- Special reward: play intrigue from hand ---
    pending_play_intrigue = False
    if contract.reward_play_intrigue > 0 and player.intrigue_hand:
        state.pending_play_intrigue = {"player_id": player.player_id}
        has_interactive = True
        pending_play_intrigue = True

    # --- Special reward: opponent gains coins ---
    opponent_coins_granted = None
    if contract.reward_opponent_gains_coins > 0:
        opponents = [p for p in state.players if p.player_id != player.player_id]
        if len(opponents) == 1:
            opponents[0].resources.coins += contract.reward_opponent_gains_coins
            opponent_coins_granted = {
                "player_id": opponents[0].player_id,
                "player_name": opponents[0].display_name,
                "coins": contract.reward_opponent_gains_coins,
            }
            state.game_log.append(
                GameLog(
                    round_number=state.current_round,
                    player_id=player.player_id,
                    action="opponent_gains_coins",
                    details=(
                        f"{opponents[0].display_name} gained"
                        f" {contract.reward_opponent_gains_coins} coins"
                        f" from {contract.name}"
                    ),
                    timestamp=time.time(),
                )
            )
        elif len(opponents) > 1:
            state.pending_opponent_coins = {
                "player_id": player.player_id,
                "coins": contract.reward_opponent_gains_coins,
            }
            has_interactive = True

    # --- Special reward: extra permanent worker ---
    extra_workers_granted = 0
    if contract.reward_extra_worker > 0:
        player.total_workers += contract.reward_extra_worker
        extra_workers_granted = contract.reward_extra_worker
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="extra_worker",
                details=(
                    f"{player.display_name} gained"
                    f" {extra_workers_granted} extra permanent worker(s)"
                    f" from {contract.name}"
                ),
                timestamp=time.time(),
            )
        )

    # --- Special reward: recall a placed worker ---
    pending_recall = False
    if contract.reward_recall_worker:
        occupied_spaces = [
            (sid, sp)
            for sid, sp in state.board.action_spaces.items()
            if sp.occupied_by == player.player_id
        ]
        if occupied_spaces:
            state.pending_worker_recall = {"player_id": player.player_id}
            has_interactive = True
            pending_recall = True

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
            bonus_resources=(contract.bonus_resources.model_dump()),
            drawn_intrigue=drawn_intrigue,
            drawn_quests=drawn_quests,
            building_granted=building_granted,
            plot_quest_bonus_vp=plot_bonus_vp,
            pending_choice=has_interactive,
            pending_play_intrigue=pending_play_intrigue,
            opponent_coins_granted=opponent_coins_granted,
            extra_workers_granted=extra_workers_granted,
            pending_recall=pending_recall,
            showcase_bonus_vp=showcase_bonus_vp,
            next_player_id=None,
        ),
    )

    if has_interactive:
        # Existing quest reward prompts (choose quest draw, market building choice)
        if (
            contract.reward_draw_quests > 0
            and contract.reward_quest_draw_mode == "choose"
        ):
            await _send_quest_reward_prompt(server, state, player, contract)
            return
        if contract.reward_building == "market_choice":
            await _send_quest_reward_prompt(server, state, player, contract)
            return

        # Play intrigue from quest prompt
        if pending_play_intrigue:
            await server.send_to_player(
                player.player_id,
                IntriguePlayPromptResponse(
                    intrigue_hand=[c.model_dump() for c in player.intrigue_hand],
                ),
            )
            return

        # Opponent choice prompt (3+ players)
        if state.pending_opponent_coins:
            opponents = [p for p in state.players if p.player_id != player.player_id]
            await server.send_to_player(
                player.player_id,
                OpponentChoicePromptResponse(
                    opponents=[
                        {"player_id": p.player_id, "player_name": p.display_name}
                        for p in opponents
                    ],
                    coins_amount=contract.reward_opponent_gains_coins,
                ),
            )
            return

        # Worker recall prompt
        if pending_recall:
            occupied_spaces = [
                (sid, sp)
                for sid, sp in state.board.action_spaces.items()
                if sp.occupied_by == player.player_id
            ]
            await server.send_to_player(
                player.player_id,
                WorkerRecallPromptResponse(
                    occupied_spaces=[
                        {"space_id": sid, "name": sp.name}
                        for sid, sp in occupied_spaces
                    ],
                ),
            )
            return

        return

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)
        return

    await _advance_turn(server, state)
    next_player = state.current_player()
    if next_player:
        await _notify_turn_if_needed(
            server,
            state,
            player,
        )


async def handle_quest_reward_choice(
    server: GameServer,
    conn: ClientConnection,
    msg,
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND",
            "Not in a game.",
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
            "INVALID_ACTION",
            "Player not found.",
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
        await server.broadcast_to_game(
            state.game_code,
            FaceUpQuestsUpdatedResponse(
                face_up_quests=[q.model_dump() for q in state.board.face_up_quests]
            ),
        )

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
            state,
            player,
            chosen_b,
        )
        await _broadcast_building_market(server, state)
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

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)
        return

    await _advance_turn(server, state)
    await _notify_turn_if_needed(
        server,
        state,
        player,
    )


async def handle_skip_quest_completion(
    server: GameServer,
    conn: ClientConnection,
    msg,
) -> None:
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error(
            "GAME_NOT_FOUND",
            "Not in a game.",
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
            "INVALID_ACTION",
            "Player not found.",
        )
        return

    is_reassignment = state.phase == GamePhase.REASSIGNMENT
    current = state.current_player()
    is_own_turn = current is not None and current.player_id == conn.player_id
    if not is_own_turn and not is_reassignment:
        await conn.send_error(
            "NOT_YOUR_TURN",
            "It is not your turn.",
        )
        return

    state.waiting_for_quest_completion = False
    state.pending_showcase_bonus = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="skip_quest_completion",
            details=(f"{player.display_name}" " skipped quest completion"),
            timestamp=time.time(),
        )
    )

    if is_reassignment:
        await _finish_reassignment(server, state)
        return

    await _advance_turn(server, state)
    next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        QuestSkippedResponse(
            player_id=player.player_id,
            next_player_id=(next_player.player_id if next_player else None),
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
            face_up_buildings=[b.model_dump() for b in state.board.face_up_buildings],
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

    plot_bonus_vp = 0
    for completed in player.completed_contracts:
        if completed.bonus_vp_per_building_purchased > 0:
            plot_bonus_vp += completed.bonus_vp_per_building_purchased
    player.victory_points += plot_bonus_vp

    state.board.face_up_buildings.remove(building)
    state.board.building_lots.remove(lot_id)

    # Draw replacement from deck
    if state.board.building_deck:
        replacement = state.board.building_deck.pop(0)
        state.board.face_up_buildings.append(replacement)

    # Set initial accumulated stock for accumulating buildings
    if building.accumulation_type:
        building.accumulated_stock = building.accumulation_initial

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

    vp_detail = f"+{building.accumulated_vp} VP" if building.accumulated_vp else ""
    if plot_bonus_vp:
        bonus_part = f"+{plot_bonus_vp} plot quest bonus"
        vp_detail = f"{vp_detail} {bonus_part}".strip() if vp_detail else bonus_part

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="purchase_building",
            details=(
                f"{player.display_name} built {building.name}" f" ({vp_detail})"
                if vp_detail
                else f"{player.display_name} built {building.name}"
            ),
            timestamp=time.time(),
        )
    )

    state.pending_placement = None

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
            cost_coins=building.cost_coins,
            accumulated_vp=building.accumulated_vp,
            plot_quest_bonus_vp=plot_bonus_vp,
            building_tile=building.model_dump(),
            next_player_id=(next_player.player_id if next_player else None),
        ),
    )

    # Broadcast updated market
    await _broadcast_building_market(server, state)

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)


def _unwind_placement(state, player, pending: dict) -> dict:
    """Reverse all state mutations from a worker placement.

    Returns a dict with fields for PlacementCancelledResponse.
    """
    space_id = pending["space_id"]

    if space_id.startswith("backstage_slot_"):
        slot_num = int(space_id.split("_")[-1])
        for s in state.board.backstage_slots:
            if s.slot_number == slot_num:
                s.occupied_by = None
                s.intrigue_card_played = None
                break
    else:
        space = state.board.action_spaces.get(space_id)
        if space:
            space.occupied_by = None

    player.available_workers += 1

    reversed_vp = pending.get("granted_vp", 0)
    player.victory_points -= reversed_vp

    reversed_resources = dict(pending.get("granted_resources", {}))
    for res, amount in reversed_resources.items():
        if hasattr(player.resources, res) and amount:
            cur = getattr(player.resources, res)
            setattr(player.resources, res, max(0, cur - amount))

    stock_restored = 0
    stock_consumed = pending.get("accumulated_stock_consumed", 0)
    if stock_consumed and not space_id.startswith("backstage"):
        space = state.board.action_spaces.get(space_id)
        if space and space.building_tile:
            space.building_tile.accumulated_stock += stock_consumed
            stock_restored = space.building_tile.accumulated_stock

    reversed_owner_bonus = {}
    owner_info = pending.get("owner_bonus_info", {})
    if owner_info:
        owner = state.get_player(owner_info["owner_id"])
        if owner:
            bonus = owner_info.get("bonus", {})
            for res in ("guitarists", "bass_players", "drummers", "singers", "coins"):
                amt = bonus.get(res, 0)
                if amt and hasattr(owner.resources, res):
                    cur = getattr(owner.resources, res)
                    setattr(owner.resources, res, max(0, cur - amt))
            owner_vp = bonus.get("victory_points", 0)
            if owner_vp:
                owner.victory_points -= owner_vp
            reversed_owner_bonus = bonus

    for tb in pending.get("trigger_bonuses", []):
        for res, amt in tb.get("bonus_resources", {}).items():
            if amt and hasattr(player.resources, res):
                cur = getattr(player.resources, res)
                setattr(player.resources, res, max(0, cur - amt))
                reversed_resources[res] = reversed_resources.get(res, 0) + amt

    return {
        "space_id": space_id,
        "reversed_vp": reversed_vp,
        "reversed_resources": reversed_resources,
        "reversed_owner_bonus": reversed_owner_bonus,
        "stock_restored": stock_restored,
    }


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

    pending = state.pending_placement
    if pending is None or pending["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No building purchase to cancel.")
        return

    if state.phase == GamePhase.REASSIGNMENT:
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="cancel_purchase_building",
                details=f"{player.display_name} skipped building purchase",
                timestamp=time.time(),
            )
        )
        state.pending_placement = None
        await server.broadcast_to_game(
            state.game_code,
            PlacementCancelledResponse(
                player_id=player.player_id,
                space_id=pending["space_id"],
                next_player_id=None,
            ),
        )
        await _finish_reassignment(server, state)
        return

    result = _unwind_placement(state, player, pending)
    state.pending_placement = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_purchase_building",
            details=f"{player.display_name} cancelled building purchase",
            timestamp=time.time(),
        )
    )

    next_player = state.current_player()
    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id=result["space_id"],
            next_player_id=(next_player.player_id if next_player else None),
            plot_quest_bonus_vp=result["reversed_vp"],
            reversed_rewards=result["reversed_resources"],
            reversed_owner_bonus=result["reversed_owner_bonus"],
            accumulated_stock_restored=result["stock_restored"],
        ),
    )


async def handle_cancel_quest_selection(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle cancel of quest selection — unwind the placement."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    pending = state.pending_placement
    if pending is None or pending["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No quest selection to cancel.")
        return

    state.pending_showcase_bonus = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_quest_selection",
            details=f"{player.display_name} cancelled quest selection",
            timestamp=time.time(),
        )
    )

    if state.phase == GamePhase.REASSIGNMENT:
        state.pending_building_quest = None
        state.pending_placement = None
        await _finish_reassignment(server, state)
        return

    result = _unwind_placement(state, player, pending)
    state.pending_building_quest = None
    state.pending_placement = None

    next_player = state.current_player()
    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id=result["space_id"],
            next_player_id=(next_player.player_id if next_player else None),
            plot_quest_bonus_vp=result["reversed_vp"],
            reversed_rewards=result["reversed_resources"],
            reversed_owner_bonus=result["reversed_owner_bonus"],
            accumulated_stock_restored=result["stock_restored"],
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

    # Pre-validate resource choice affordability before committing reassignment
    if target.building_tile and target.building_tile.visitor_reward_choice:
        choice = target.building_tile.visitor_reward_choice
        future_resources = player.resources.model_copy()
        future_resources.add(target.reward)
        if choice.cost.total() > 0 and not future_resources.can_afford(choice.cost):
            await conn.send_error(
                "INSUFFICIENT_RESOURCES",
                "Cannot afford this building's cost.",
            )
            return
        if choice.choice_type == "exchange":
            future_resources.deduct(choice.cost)
            non_coin = (
                future_resources.guitarists
                + future_resources.bass_players
                + future_resources.drummers
                + future_resources.singers
            )
            if non_coin < choice.pick_count:
                await conn.send_error(
                    "INSUFFICIENT_RESOURCES",
                    "Not enough non-coin resources.",
                )
                return

    state.reassignment_active_player_id = player.player_id

    # Perform reassignment
    slot.occupied_by = None
    target.occupied_by = player.player_id
    reward_dict = target.reward.model_dump()
    player.resources.add(target.reward)
    player.completed_quest_this_turn = False  # Reset for reassignment action

    # Accumulating building: grant stock and reset
    if target.building_tile and target.building_tile.accumulation_type:
        tile = target.building_tile
        stock = tile.accumulated_stock
        if stock > 0:
            atype = tile.accumulation_type
            if atype == "victory_points":
                player.victory_points += stock
                reward_dict["victory_points"] = stock
            elif hasattr(player.resources, atype):
                setattr(
                    player.resources,
                    atype,
                    getattr(player.resources, atype) + stock,
                )
                reward_dict[atype] = reward_dict.get(atype, 0) + stock
            tile.accumulated_stock = 0

    # Visitor VP reward
    if target.building_tile and target.building_tile.visitor_reward_vp > 0:
        player.victory_points += target.building_tile.visitor_reward_vp
        reward_dict["victory_points"] = (
            reward_dict.get("victory_points", 0)
            + target.building_tile.visitor_reward_vp
        )

    # Building visitor_reward_special
    if (
        target.space_type == "building"
        and target.building_tile
        and target.building_tile.visitor_reward_special
    ):
        special = target.building_tile.visitor_reward_special
        if special == "draw_intrigue" and state.board.intrigue_deck:
            card = state.board.intrigue_deck.pop(0)
            player.intrigue_hand.append(card)

    # Owner bonus for buildings
    owner_bonus_info = {}
    if target.space_type == "building" and target.owner_id:
        owner = state.get_player(target.owner_id)
        if owner and owner.player_id != player.player_id and target.building_tile:
            tile = target.building_tile
            owner.resources.add(tile.owner_bonus)
            bonus_dict = tile.owner_bonus.model_dump()
            if tile.owner_bonus_vp > 0:
                owner.victory_points += tile.owner_bonus_vp
                bonus_dict["victory_points"] = tile.owner_bonus_vp
            if tile.owner_bonus_special == "draw_intrigue":
                if state.board.intrigue_deck:
                    card = state.board.intrigue_deck.pop(0)
                    owner.intrigue_hand.append(card)
                    bonus_dict["intrigue_card"] = True
            owner_bonus_info = {
                "owner_id": owner.player_id,
                "owner_name": owner.display_name,
                "bonus": bonus_dict,
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

    # Detect pending owner bonus choice
    pending_owner_choice = None
    if (
        target.space_type == "building"
        and target.owner_id
        and target.building_tile
        and target.building_tile.owner_bonus_choice
    ):
        bonus_owner = state.get_player(target.owner_id)
        if bonus_owner and bonus_owner.player_id != player.player_id:
            pending_owner_choice = {
                "owner_id": bonus_owner.player_id,
                "choice_dump": target.building_tile.owner_bonus_choice.model_dump(),
                "space_name": target.name,
            }

    # Evaluate resource trigger plot quests (no cascade — uses base reward only)
    trigger_bonuses, pending_swap = _evaluate_resource_triggers(
        state, player, target.reward
    )
    trigger_bonuses_data = trigger_bonuses
    for tb in trigger_bonuses:
        if tb.get("bonus_resources"):
            for k, v in tb["bonus_resources"].items():
                if v and k in reward_dict:
                    reward_dict[k] = reward_dict.get(k, 0) + v
        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="resource_trigger",
                details=(
                    f"{player.display_name} triggered"
                    f" {tb.get('contract_name', 'plot quest')} bonus"
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

    # Reset quests before broadcasting WorkerReassignedResponse so the
    # client enters quest_selection with the NEW quest IDs.
    if target.space_type == "garage" and target.reward_special == "reset_quests":
        state.board.quest_discard.extend(state.board.face_up_quests)
        state.board.face_up_quests.clear()
        for _ in range(FACE_UP_QUEST_COUNT):
            card = _draw_from_quest_deck(state)
            if card:
                state.board.face_up_quests.append(card)
        await server.broadcast_to_game(
            state.game_code,
            FaceUpQuestsUpdatedResponse(
                face_up_quests=[q.model_dump() for q in state.board.face_up_quests]
            ),
        )

    await server.broadcast_to_game(
        state.game_code,
        WorkerReassignedResponse(
            player_id=player.player_id,
            from_slot=msg.slot_number,
            to_space_id=msg.target_space_id,
            reward_granted=reward_dict,
            owner_bonus=owner_bonus_info,
            trigger_bonuses=trigger_bonuses_data,
        ),
    )

    # Build pending_placement for reassignment pause points
    _pending_reassign = {
        "player_id": player.player_id,
        "space_id": msg.target_space_id,
        "granted_resources": {
            k: v for k, v in reward_dict.items() if k != "victory_points" and v
        },
        "granted_vp": reward_dict.get("victory_points", 0),
        "accumulated_stock_consumed": 0,
        "accumulation_type": None,
        "owner_bonus_info": owner_bonus_info,
        "trigger_bonuses": trigger_bonuses_data,
        "is_reassignment": True,
    }

    # Singer swap trigger prompt (reassignment)
    if pending_swap:
        from shared.card_models import ResourceChoiceReward

        state.pending_placement = _pending_reassign
        swap_choice = ResourceChoiceReward(
            choice_type="pick",
            allowed_types=["guitarists", "bass_players", "drummers"],
            pick_count=1,
        )
        state.pending_resource_trigger_swap = {
            "player_id": player.player_id,
            "contract_id": pending_swap["contract_id"],
            "contract_name": pending_swap["contract_name"],
            "space_id": msg.target_space_id,
            "pending_owner_choice": pending_owner_choice,
            "is_reassignment": True,
        }
        await _send_resource_choice_prompt(
            server,
            state,
            player,
            swap_choice,
            "trigger_swap",
            f"Swap for Singer ({pending_swap['contract_name']})",
            is_spend=True,
            can_skip=True,
        )
        return

    # Handle Real Estate Listings during reassignment
    if target.reward_special == "purchase_building":
        state.pending_placement = _pending_reassign
        return

    # Handle Garage spots: pause for quest selection (reset already
    # happened above for reset_quests before WorkerReassignedResponse)
    if target.space_type == "garage":
        state.pending_placement = _pending_reassign
        return

    # Resource choice reward on buildings
    if target.building_tile and target.building_tile.visitor_reward_choice:
        state.pending_placement = _pending_reassign
        choice = target.building_tile.visitor_reward_choice
        if choice.cost.total() > 0:
            if not player.resources.can_afford(choice.cost):
                await _finish_reassignment(server, state)
                return
            player.resources.deduct(choice.cost)
        if choice.choice_type == "exchange":
            if _player_non_coin_total(player) < choice.pick_count:
                await _finish_reassignment(server, state)
                return
            await _send_resource_choice_prompt(
                server,
                state,
                player,
                choice,
                "building",
                target.name,
                is_spend=True,
                phase="spend",
            )
            if pending_owner_choice:
                state.pending_resource_choice["pending_owner_choice"] = (
                    pending_owner_choice
                )
            return
        await _send_resource_choice_prompt(
            server,
            state,
            player,
            choice,
            "building",
            target.name,
        )
        if pending_owner_choice:
            state.pending_resource_choice["pending_owner_choice"] = pending_owner_choice
        return

    # Owner bonus choice (no visitor choice to resolve first)
    if pending_owner_choice:
        from shared.card_models import ResourceChoiceReward

        state.pending_placement = _pending_reassign
        bonus_owner = state.get_player(pending_owner_choice["owner_id"])
        if bonus_owner:
            rcr = ResourceChoiceReward(**pending_owner_choice["choice_dump"])
            await _send_resource_choice_prompt(
                server,
                state,
                bonus_owner,
                rcr,
                "owner_bonus",
                pending_owner_choice["space_name"],
            )
            return

    # Building draw_contract: pause for quest selection
    if (
        target.space_type == "building"
        and target.building_tile
        and target.building_tile.visitor_reward_special == "draw_contract"
    ):
        state.pending_placement = _pending_reassign
        return

    # Building draw_contract_and_complete: quest selection + bonus VP
    if (
        target.space_type == "building"
        and target.building_tile
        and target.building_tile.visitor_reward_special == "draw_contract_and_complete"
    ):
        state.pending_placement = _pending_reassign
        state.pending_showcase_bonus = {
            "player_id": state.reassignment_active_player_id,
            "contract_id": None,
            "bonus_vp": 4,
        }
        return

    await _finish_reassignment(server, state)


async def _finish_reassignment(
    server: GameServer,
    state,
) -> None:
    """Continue reassignment queue or end the round."""
    state.pending_placement = None
    if state.reassignment_active_player_id:
        player = state.get_player(
            state.reassignment_active_player_id,
        )
        state.reassignment_active_player_id = None
        if player and not player.completed_quest_this_turn:
            completable = [
                c for c in player.contract_hand if player.resources.can_afford(c.cost)
            ]
            if completable:
                state.waiting_for_quest_completion = True
                await server.send_to_player(
                    player.player_id,
                    QuestCompletionPromptResponse(
                        completable_quests=[c.model_dump() for c in completable],
                    ),
                )
                return

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

    resource_keys = [
        k
        for k in effect_value
        if k in ResourceCost.model_fields and effect_value[k] > 0
    ]

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
    state.pending_placement = None

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

    # Check for resource triggers from stolen resources
    if effect_type == "steal_resources" and resources_affected:
        stolen_reward = ResourceCost(
            **{
                k: v
                for k, v in resources_affected.items()
                if k in ResourceCost.model_fields
            }
        )
        if stolen_reward.total() > 0:
            trigger_bonuses, pending_swap = _evaluate_resource_triggers(
                state, player, stolen_reward
            )
            for tb in trigger_bonuses:
                if tb.get("bonus_resources"):
                    bonus_rc = {k: v for k, v in tb["bonus_resources"].items() if v}
                    if bonus_rc:
                        await server.broadcast_to_game(
                            state.game_code,
                            ResourceChoiceResolvedResponse(
                                player_id=player.player_id,
                                chosen_resources=bonus_rc,
                                is_spend=False,
                                source_description=(
                                    f"{tb.get('contract_name', 'plot quest')} trigger"
                                ),
                            ),
                        )
                state.game_log.append(
                    GameLog(
                        round_number=state.current_round,
                        player_id=player.player_id,
                        action="resource_trigger",
                        details=(
                            f"{player.display_name} triggered"
                            f" {tb.get('contract_name', 'plot quest')} bonus"
                            f" from stolen resources"
                        ),
                        timestamp=time.time(),
                    )
                )
            if pending_swap:
                from shared.card_models import ResourceChoiceReward

                swap_choice = ResourceChoiceReward(
                    choice_type="pick",
                    allowed_types=[
                        "guitarists",
                        "bass_players",
                        "drummers",
                    ],
                    pick_count=1,
                )
                state.pending_resource_trigger_swap = {
                    "player_id": player.player_id,
                    "contract_id": pending_swap["contract_id"],
                    "contract_name": pending_swap["contract_name"],
                    "space_id": "backstage_intrigue",
                    "pending_owner_choice": None,
                }
                await _send_resource_choice_prompt(
                    server,
                    state,
                    player,
                    swap_choice,
                    "trigger_swap",
                    f"Swap for Singer ({pending_swap['contract_name']})",
                    is_spend=True,
                    can_skip=True,
                )
                return

    if pending.get("source") == "quest_completion":
        await _advance_after_quest_rewards(server, state, player)
    else:
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

    from shared.card_models import IntrigueCard

    reversed_bonus = pending.get("plot_bonus_vp", 0)
    card = IntrigueCard(**pending["intrigue_card"])

    if pending.get("source") == "quest_completion":
        player.intrigue_hand.append(card)
        player.victory_points -= reversed_bonus
        state.pending_intrigue_target = None

        state.game_log.append(
            GameLog(
                round_number=state.current_round,
                player_id=player.player_id,
                action="cancel_intrigue_target",
                details=f"{player.display_name} cancelled intrigue target from quest reward",
                timestamp=time.time(),
            )
        )

        await _advance_after_quest_rewards(server, state, player)
        return

    placement = state.pending_placement
    if placement is None or placement["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending placement to cancel.")
        return

    result = _unwind_placement(state, player, placement)
    player.intrigue_hand.append(card)

    state.pending_intrigue_target = None
    state.pending_placement = None

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
            space_id=result["space_id"],
            next_player_id=None,
            returned_card=pending["intrigue_card"],
            plot_quest_bonus_vp=result["reversed_vp"],
        ),
    )


# ------------------------------------------------------------------
# Copy-space handlers
# ------------------------------------------------------------------


async def handle_select_copy_space(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Player selected a target space to copy."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    pending_copy = state.pending_copy_source
    if pending_copy is None or pending_copy["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending copy selection.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    if msg.space_id not in pending_copy["eligible_spaces"]:
        await conn.send_error("INVALID_ACTION", "That space is not eligible to copy.")
        return

    target_space = state.board.action_spaces.get(msg.space_id)
    if target_space is None:
        await conn.send_error("INVALID_ACTION", "Unknown action space.")
        return

    pending = state.pending_placement
    if pending is None:
        await conn.send_error("INVALID_ACTION", "No pending placement.")
        return

    await _resolve_copied_space_rewards(
        server,
        state,
        player,
        target_space,
        pending_copy["source_space_id"],
        pending,
    )


async def handle_cancel_copy_space(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Cancel copy-space selection — unwind placement and return worker."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    pending_copy = state.pending_copy_source
    if pending_copy is None or pending_copy["player_id"] != conn.player_id:
        await conn.send_error("INVALID_ACTION", "No pending copy selection.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    pending = state.pending_placement
    if pending is None:
        await conn.send_error("INVALID_ACTION", "No pending placement.")
        return

    # Return coins for intrigue source
    returned_card = {}
    if pending_copy.get("source_type") == "intrigue":
        cost = pending_copy.get("cost_deducted", 0)
        if cost > 0:
            player.resources.coins += cost
        card_data = pending_copy.get("intrigue_card")
        if card_data:
            from shared.card_models import IntrigueCard

            card = IntrigueCard(**card_data)
            player.intrigue_hand.append(card)
            returned_card = card_data

    result = _unwind_placement(state, player, pending)
    state.pending_copy_source = None
    state.pending_placement = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="cancel_copy_space",
            details=f"{player.display_name} cancelled copy-space selection",
            timestamp=time.time(),
        )
    )

    next_player = state.current_player()
    await server.broadcast_to_game(
        state.game_code,
        PlacementCancelledResponse(
            player_id=player.player_id,
            space_id=result["space_id"],
            next_player_id=(next_player.player_id if next_player else None),
            returned_card=returned_card,
            reversed_rewards=result.get("reversed_resources", {}),
            accumulated_stock_restored=result.get("stock_restored", 0),
        ),
    )


# ------------------------------------------------------------------
# Quest-completion special reward handlers
# ------------------------------------------------------------------


async def _advance_after_quest_rewards(server: GameServer, state, player) -> None:
    """After resolving one quest-completion reward, check if more are pending."""
    # Chain: play_intrigue → opponent_coins → recall → done
    if state.pending_play_intrigue:
        await server.send_to_player(
            player.player_id,
            IntriguePlayPromptResponse(
                intrigue_hand=[c.model_dump() for c in player.intrigue_hand],
            ),
        )
        return

    if state.pending_opponent_coins:
        opponents = [p for p in state.players if p.player_id != player.player_id]
        await server.send_to_player(
            player.player_id,
            OpponentChoicePromptResponse(
                opponents=[
                    {"player_id": p.player_id, "player_name": p.display_name}
                    for p in opponents
                ],
                coins_amount=state.pending_opponent_coins["coins"],
            ),
        )
        return

    if state.pending_worker_recall:
        occupied_spaces = [
            (sid, sp)
            for sid, sp in state.board.action_spaces.items()
            if sp.occupied_by == player.player_id
        ]
        if occupied_spaces:
            await server.send_to_player(
                player.player_id,
                WorkerRecallPromptResponse(
                    occupied_spaces=[
                        {"space_id": sid, "name": sp.name}
                        for sid, sp in occupied_spaces
                    ],
                ),
            )
            return
        else:
            state.pending_worker_recall = None

    if state.phase == GamePhase.REASSIGNMENT:
        await _finish_reassignment(server, state)
        return

    await _advance_turn(server, state)
    await _notify_turn_if_needed(server, state, player)


async def handle_play_intrigue_from_quest(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle playing an intrigue card as a quest completion reward."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not state.pending_play_intrigue:
        await conn.send_error("INVALID_ACTION", "No pending intrigue play.")
        return

    if state.pending_play_intrigue["player_id"] != conn.player_id:
        await conn.send_error("NOT_YOUR_TURN", "Not your pending action.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    card = None
    for c in player.intrigue_hand:
        if c.id == msg.intrigue_card_id:
            card = c
            break
    if card is None:
        await conn.send_error("INVALID_ACTION", "Intrigue card not in hand.")
        return

    player.intrigue_hand.remove(card)
    effect_details = _resolve_intrigue_effect(state, player, card)

    plot_bonus_vp = 0
    for completed in player.completed_contracts:
        if completed.bonus_vp_per_intrigue_played > 0:
            plot_bonus_vp += completed.bonus_vp_per_intrigue_played
    player.victory_points += plot_bonus_vp

    log_detail = f"{player.display_name} played {card.name} from quest reward"
    if plot_bonus_vp:
        log_detail += f" (+{plot_bonus_vp} plot quest bonus)"

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="play_intrigue_from_quest",
            details=log_detail,
            timestamp=time.time(),
        )
    )

    state.pending_play_intrigue = None

    if effect_details.get("pending"):
        eligible = effect_details.get("eligible_targets", [])
        state.pending_intrigue_target = {
            "player_id": player.player_id,
            "intrigue_card": card.model_dump(),
            "effect_type": card.effect_type,
            "effect_value": card.effect_value,
            "eligible_targets": eligible,
            "plot_bonus_vp": plot_bonus_vp,
            "source": "quest_completion",
        }

        target_info = []
        for tid in eligible:
            tp = state.get_player(tid)
            if tp:
                target_info.append(
                    {
                        "player_id": tp.player_id,
                        "player_name": tp.display_name,
                        "resources": tp.resources.model_dump(),
                    }
                )

        await server.send_to_player(
            player.player_id,
            IntrigueTargetPromptResponse(
                effect_type=card.effect_type,
                effect_value=card.effect_value,
                eligible_targets=target_info,
            ),
        )
        return

    await _advance_after_quest_rewards(server, state, player)


async def handle_choose_opponent(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle choosing which opponent receives coins from quest reward."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not state.pending_opponent_coins:
        await conn.send_error("INVALID_ACTION", "No pending opponent choice.")
        return

    if state.pending_opponent_coins["player_id"] != conn.player_id:
        await conn.send_error("NOT_YOUR_TURN", "Not your pending action.")
        return

    player = state.get_player(conn.player_id)
    target = state.get_player(msg.target_player_id)
    if player is None or target is None:
        await conn.send_error("INVALID_ACTION", "Invalid player.")
        return

    if target.player_id == player.player_id:
        await conn.send_error("INVALID_ACTION", "Cannot choose yourself.")
        return

    coins = state.pending_opponent_coins["coins"]
    target.resources.coins += coins

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="opponent_gains_coins",
            details=(
                f"{target.display_name} gained {coins} coins"
                f" (chosen by {player.display_name})"
            ),
            timestamp=time.time(),
        )
    )

    state.pending_opponent_coins = None
    await _advance_after_quest_rewards(server, state, player)


async def handle_recall_worker(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle recalling a placed worker as a quest completion reward."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not state.pending_worker_recall:
        await conn.send_error("INVALID_ACTION", "No pending worker recall.")
        return

    if state.pending_worker_recall["player_id"] != conn.player_id:
        await conn.send_error("NOT_YOUR_TURN", "Not your pending action.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    space = state.board.action_spaces.get(msg.space_id)
    if space is None or space.occupied_by != player.player_id:
        await conn.send_error("INVALID_ACTION", "Not a valid space to recall from.")
        return

    space.occupied_by = None
    player.available_workers += 1
    state.pending_worker_recall = None

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="recall_worker",
            details=f"{player.display_name} recalled worker from {space.name}",
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        WorkerRecalledResponse(
            player_id=player.player_id,
            space_id=msg.space_id,
            space_name=space.name,
        ),
    )

    await _advance_after_quest_rewards(server, state, player)


async def handle_round_start_resource_choice(
    server: GameServer, conn: ClientConnection, msg
) -> None:
    """Handle a player's round-start resource choice."""
    state = _get_game_state(server, conn)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Not in a game.")
        return

    if not state.pending_round_start_choices:
        await conn.send_error("INVALID_ACTION", "No pending round-start choice.")
        return

    if state.pending_round_start_choices[0] != conn.player_id:
        await conn.send_error("NOT_YOUR_TURN", "Not your turn to choose.")
        return

    player = state.get_player(conn.player_id)
    if player is None:
        await conn.send_error("INVALID_ACTION", "Player not found.")
        return

    valid_types = {"guitarists", "bass_players", "drummers", "singers"}
    if msg.resource_type not in valid_types:
        await conn.send_error(
            "INVALID_ACTION",
            "Must choose a non-coin resource: guitarists, bass_players, drummers, or singers.",
        )
        return

    current = getattr(player.resources, msg.resource_type, 0)
    setattr(player.resources, msg.resource_type, current + 1)

    contract_name = ""
    for c in player.completed_contracts:
        if c.reward_choose_resource_per_round:
            contract_name = c.name
            break

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="round_start_resource",
            details=(
                f"{player.display_name} chose 1 {msg.resource_type}"
                f" from {contract_name}"
            ),
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        RoundStartBonusResponse(
            player_id=player.player_id,
            resource_type=msg.resource_type,
            contract_name=contract_name,
        ),
    )

    state.pending_round_start_choices.pop(0)

    if state.pending_round_start_choices:
        next_pid = state.pending_round_start_choices[0]
        next_player = state.get_player(next_pid)
        if next_player:
            next_contract = ""
            for c in next_player.completed_contracts:
                if c.reward_choose_resource_per_round:
                    next_contract = c.name
                    break
            await server.send_to_player(
                next_pid,
                RoundStartResourceChoicePromptResponse(
                    player_id=next_pid,
                    contract_name=next_contract,
                ),
            )
        return

    await _notify_turn_if_needed(server, state, player)
