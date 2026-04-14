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
    FaceUpQuestsUpdatedResponse,
    FinalPlayerScore,
    GameOverResponse,
    QuestCardSelectedResponse,
    QuestCompletedResponse,
    QuestsResetResponse,
    ReassignmentPhaseStartResponse,
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
    if space.space_type == "building" and space.owner_id:
        owner = state.get_player(space.owner_id)
        if owner and owner.player_id != player.player_id and space.building_tile:
            owner.resources.add(space.building_tile.owner_bonus)

    state.game_log.append(
        GameLog(
            round_number=state.current_round,
            player_id=player.player_id,
            action="place_worker",
            details=f"{player.display_name} placed worker on {space.name}",
            timestamp=time.time(),
        )
    )

    # Determine next player
    await _advance_turn(server, state)
    next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedResponse(
            player_id=player.player_id,
            space_id=msg.space_id,
            reward_granted=reward_dict,
            next_player_id=next_player.player_id if next_player else None,
        ),
    )


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

    await _advance_turn(server, state)
    next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        QuestCardSelectedResponse(
            player_id=player.player_id,
            card_id=card.id,
            spot_number=spot_num,
            bonus_reward=bonus_reward,
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

    await _advance_turn(server, state)
    next_player = state.current_player()

    await server.broadcast_to_game(
        state.game_code,
        WorkerPlacedBackstageResponse(
            player_id=player.player_id,
            slot_number=msg.slot_number,
            intrigue_card={"id": card.id, "name": card.name, "description": card.description},
            intrigue_effect=effect_details,
            next_player_id=next_player.player_id if next_player else None,
        ),
    )


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
            if state.board.contract_deck:
                c = state.board.contract_deck.pop(0)
                player.contract_hand.append(c)
                drawn.append(c.id)
        effect["details"] = {"drawn": drawn}

    elif card.effect_type == "draw_intrigue":
        count = ev.get("count", 1)
        drawn = []
        for _ in range(count):
            if state.board.intrigue_deck:
                c = state.board.intrigue_deck.pop(0)
                player.intrigue_hand.append(c)
                drawn.append(c.id)
        effect["details"] = {"drawn": drawn}

    elif card.effect_type in ("steal_resources", "opponent_loses"):
        # For targeted effects, handled via choose_intrigue_target
        # For now, if target is "self" or "all", handle directly
        if card.effect_target == "all":
            reward = ResourceCost(**{k: v for k, v in ev.items() if k in ResourceCost.model_fields})
            for p in state.players:
                p.resources.add(reward)
            effect["details"] = {"all_gained": reward.model_dump()}
        # "choose_opponent" targeting is deferred to handle_choose_intrigue_target

    elif card.effect_type == "all_players_gain":
        reward = ResourceCost(**{k: v for k, v in ev.items() if k in ResourceCost.model_fields})
        for p in state.players:
            p.resources.add(reward)
        effect["details"] = {"all_gained": reward.model_dump()}

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
            details=f"{player.display_name} completed '{contract.name}' for {contract.victory_points} VP",
            timestamp=time.time(),
        )
    )

    await server.broadcast_to_game(
        state.game_code,
        QuestCompletedResponse(
            player_id=player.player_id,
            contract_id=contract.id,
            contract_name=contract.name,
            victory_points_earned=contract.victory_points,
            bonus_resources=contract.bonus_resources.model_dump(),
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

    await server.broadcast_to_game(
        state.game_code,
        BuildingConstructedResponse(
            player_id=player.player_id,
            building_id=building.id,
            building_name=building.name,
            lot_index=lot_index,
            new_space_id=space_id,
        ),
    )

    # Broadcast updated market
    await _broadcast_building_market(server, state)


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

    # Validate target space
    target = state.board.action_spaces.get(msg.target_space_id)
    if target is None:
        await conn.send_error("INVALID_ACTION", "Unknown target space.")
        return
    if target.occupied_by is not None:
        await conn.send_error("SPACE_OCCUPIED", "Target space is occupied.")
        return

    # Cannot reassign back to Garage
    if target.space_type == "garage":
        await conn.send_error("INVALID_ACTION", "Cannot reassign to The Garage.")
        return

    player = state.get_player(conn.player_id)

    # Perform reassignment
    slot.occupied_by = None
    target.occupied_by = player.player_id
    reward_dict = target.reward.model_dump()
    player.resources.add(target.reward)
    player.completed_quest_this_turn = False  # Reset for reassignment action

    # Owner bonus for buildings
    if target.space_type == "building" and target.owner_id:
        owner = state.get_player(target.owner_id)
        if owner and owner.player_id != player.player_id and target.building_tile:
            owner.resources.add(target.building_tile.owner_bonus)

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
            details=f"{player.display_name} reassigned from Backstage slot {msg.slot_number} to {target.name}",
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
        ),
    )

    # If no more slots to reassign, end the round
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

    player = state.get_player(conn.player_id)
    target = state.get_player(msg.target_player_id)
    if player is None or target is None:
        await conn.send_error("INVALID_ACTION", "Invalid player.")
        return

    # For now, targeted effects are resolved inline during Backstage placement
    # This handler is a placeholder for future interactive targeting flows
    await conn.send_error("INVALID_ACTION", "Targeting not implemented yet.")
