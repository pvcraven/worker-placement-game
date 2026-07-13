"""Tests for The Green Room — play intrigue card + select quest card."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from server.game_engine import (
    handle_cancel_quest_selection,
    handle_choose_intrigue_target,
    handle_play_intrigue_from_quest,
    handle_reassign_worker,
)
from server.models.game import (
    ActionSpace,
    BackstageSlot,
    GameState,
    Player,
    PlayerResources,
)
from shared.card_models import IntrigueCard
from shared.constants import GamePhase

CONF = Path(__file__).resolve().parent.parent / "config"
CONFIG_BOARD = CONF / "board.json"


def board_config():
    return json.loads(CONFIG_BOARD.read_text())


BOARD = board_config()


def _make_player(player_id="p1", **kwargs):
    return Player(
        player_id=player_id,
        display_name=f"Player {player_id}",
        slot_index=0,
        resources=PlayerResources(**kwargs),
    )


def _make_green_room():
    return ActionSpace(
        space_id="the_green_room",
        name="The Green Room",
        space_type="permanent",
        reward_special="play_intrigue_and_quest",
    )


# --- Config validation ---


def test_green_room_in_board_config():
    spaces = BOARD["permanent_spaces"]
    green_room = [s for s in spaces if s["space_id"] == "the_green_room"]
    assert len(green_room) == 1
    gr = green_room[0]
    assert gr["name"] == "The Green Room"
    assert gr["space_type"] == "permanent"
    assert gr["reward_special"] == "play_intrigue_and_quest"
    assert gr["slots"] == 1


def test_green_room_has_empty_reward():
    spaces = BOARD["permanent_spaces"]
    gr = next(s for s in spaces if s["space_id"] == "the_green_room")
    reward = gr.get("reward", {})
    keys = ["guitarists", "bass_players", "drummers", "singers", "coins"]
    total = sum(reward.get(k, 0) for k in keys)
    assert total == 0


# --- Pending state tests ---


def test_pending_play_intrigue_green_room_source():
    state = GameState(game_code="test", game_id="test-id")
    state.pending_play_intrigue = {
        "player_id": "p1",
        "source": "green_room",
    }
    assert state.pending_play_intrigue["source"] == "green_room"
    assert state.pending_play_intrigue["player_id"] == "p1"


def test_pending_placement_kept_after_intrigue_for_green_room():
    """Pending_placement stays active after intrigue resolution."""
    state = GameState(game_code="test", game_id="test-id")
    player = _make_player()
    state.players.append(player)

    green_room = _make_green_room()
    state.board.action_spaces["the_green_room"] = green_room
    green_room.occupied_by = "p1"

    state.pending_placement = {
        "player_id": "p1",
        "space_id": "the_green_room",
        "granted_resources": {},
        "granted_vp": 0,
        "accumulated_stock_consumed": 0,
        "accumulation_type": None,
        "owner_bonus_info": {},
        "trigger_bonuses": [],
    }

    assert state.pending_placement is not None
    assert state.pending_placement["space_id"] == "the_green_room"


def test_quest_selection_recognizes_green_room():
    """Verify the green room space is recognized for quest selection."""
    green_room = _make_green_room()
    assert green_room.reward_special == "play_intrigue_and_quest"
    assert green_room.space_type == "permanent"


def test_cancel_clears_pending_play_intrigue():
    state = GameState(game_code="test", game_id="test-id")
    state.pending_play_intrigue = {
        "player_id": "p1",
        "source": "green_room",
    }
    state.pending_placement = {
        "player_id": "p1",
        "space_id": "the_green_room",
        "granted_resources": {},
        "granted_vp": 0,
        "accumulated_stock_consumed": 0,
        "accumulation_type": None,
        "owner_bonus_info": {},
        "trigger_bonuses": [],
    }

    state.pending_play_intrigue = None
    state.pending_placement = None

    assert state.pending_play_intrigue is None
    assert state.pending_placement is None


def test_intrigue_target_with_green_room_source():
    state = GameState(game_code="test", game_id="test-id")
    state.pending_intrigue_target = {
        "player_id": "p1",
        "intrigue_card": {"id": "test", "name": "Test"},
        "effect_type": "steal_resources",
        "effect_value": {"coins": 2},
        "eligible_targets": ["p2"],
        "plot_bonus_vp": 0,
        "source": "green_room",
    }

    assert state.pending_intrigue_target["source"] == "green_room"


# --- Total permanent space count ---


def test_nine_permanent_spaces():
    """Board has 9 permanent/castle spaces for the 3x3 grid."""
    spaces = BOARD["permanent_spaces"]
    perm = [s for s in spaces if s["space_type"] in ("permanent", "castle")]
    assert len(perm) == 9


# --- Regression: quest selection prompt after intrigue resolves ---
# Bug: playing an intrigue card at The Green Room silently ended the turn
# instead of prompting the player to select a quest card (FR-005).


def _make_server(state: GameState) -> MagicMock:
    server = MagicMock()
    server.session_manager.get_session.return_value = state
    server.broadcast_to_game = AsyncMock()
    server.send_to_player = AsyncMock()
    return server


def _make_conn(player_id: str, game_code: str = "test") -> MagicMock:
    conn = MagicMock()
    conn.player_id = player_id
    conn.game_code = game_code
    conn.send_error = AsyncMock()
    return conn


def _make_green_room_state(effect_type="gain_coins", effect_value=None):
    state = GameState(game_code="test", game_id="test-id")
    player = _make_player()
    other = _make_player(player_id="p2", coins=3)
    state.players = [player, other]

    green_room = _make_green_room()
    green_room.occupied_by = "p1"
    state.board.action_spaces["the_green_room"] = green_room

    is_targeted = effect_type == "steal_resources"
    card = IntrigueCard(
        id="charity_concert",
        name="Charity Concert",
        description="test",
        effect_type=effect_type,
        effect_target="choose_opponent" if is_targeted else "self",
        effect_value=effect_value or {"coins": 2},
    )
    player.intrigue_hand.append(card)

    state.pending_placement = {
        "player_id": "p1",
        "space_id": "the_green_room",
        "granted_resources": {},
        "granted_vp": 0,
        "accumulated_stock_consumed": 0,
        "accumulation_type": None,
        "owner_bonus_info": {},
        "trigger_bonuses": [],
    }
    state.pending_play_intrigue = {"player_id": "p1", "source": "green_room"}

    return state, card


def test_non_targeted_intrigue_prompts_quest_selection():
    """After a non-targeted intrigue card resolves at Green Room, the
    player must be prompted to select a quest card, and the placement
    stays pending until they do."""
    state, card = _make_green_room_state()
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.intrigue_card_id = card.id

    asyncio.run(handle_play_intrigue_from_quest(server, conn, msg))

    server.send_to_player.assert_called_once()
    sent_player_id, response = server.send_to_player.call_args[0]
    assert sent_player_id == "p1"
    assert response.action == "quest_selection_prompt"

    assert state.pending_placement is not None
    assert state.pending_placement["space_id"] == "the_green_room"
    assert state.pending_play_intrigue is None

    # Regression: the resolved-effect broadcast must carry the actual
    # effect payload (previously always empty for non-targeted effects).
    server.broadcast_to_game.assert_called_once()
    _, effect_response = server.broadcast_to_game.call_args[0]
    assert effect_response.action == "intrigue_effect_resolved"
    assert effect_response.effect_details == {"coins": 2}
    assert effect_response.plot_bonus_vp == 0


def test_vp_bonus_intrigue_conveys_victory_points():
    """Regression: playing a vp_bonus card (e.g. 'Hall of Fame Induction')
    at Green Room must both grant the VP (already worked) and tell the
    client about it, so the on-screen total updates."""
    state, card = _make_green_room_state(
        effect_type="vp_bonus",
        effect_value={"victory_points": 3},
    )
    player = state.get_player("p1")
    starting_vp = player.victory_points

    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.intrigue_card_id = card.id

    asyncio.run(handle_play_intrigue_from_quest(server, conn, msg))

    assert player.victory_points == starting_vp + 3

    server.broadcast_to_game.assert_called_once()
    _, effect_response = server.broadcast_to_game.call_args[0]
    assert effect_response.effect_details == {"victory_points": 3}


def test_cancel_before_intrigue_play_unwinds_placement():
    """Regression: the cancel button shown while awaiting an intrigue play
    at Green Room must actually unwind the worker placement (previously it
    was rendered but wired to nothing)."""
    state, card = _make_green_room_state()
    player = state.get_player("p1")
    player.available_workers = 2
    green_room = state.board.action_spaces["the_green_room"]

    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()

    asyncio.run(handle_cancel_quest_selection(server, conn, msg))

    assert state.pending_play_intrigue is None
    assert state.pending_placement is None
    assert green_room.occupied_by is None
    assert player.available_workers == 3
    assert card in player.intrigue_hand

    server.broadcast_to_game.assert_called_once()
    _, response = server.broadcast_to_game.call_args[0]
    assert response.action == "placement_cancelled"
    assert response.space_id == "the_green_room"


def test_targeted_intrigue_prompts_quest_selection():
    """Same as above, but for a targeted effect resolved via
    choose_intrigue_target (e.g. steal_resources)."""
    state, card = _make_green_room_state(
        effect_type="steal_resources",
        effect_value={"coins": 2},
    )
    player = state.get_player("p1")
    target = state.get_player("p2")

    # Simulate the card having already been played and moved to pending
    # target selection, as handle_play_intrigue_from_quest would do.
    player.intrigue_hand.remove(card)
    state.pending_play_intrigue = None
    state.pending_intrigue_target = {
        "player_id": "p1",
        "intrigue_card": card.model_dump(),
        "effect_type": card.effect_type,
        "effect_value": card.effect_value,
        "eligible_targets": [target.player_id],
        "plot_bonus_vp": 0,
        "source": "green_room",
    }

    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.target_player_id = "p2"

    asyncio.run(handle_choose_intrigue_target(server, conn, msg))

    server.send_to_player.assert_called_once()
    sent_player_id, response = server.send_to_player.call_args[0]
    assert sent_player_id == "p1"
    assert response.action == "quest_selection_prompt"

    assert state.pending_placement is not None
    assert state.pending_placement["space_id"] == "the_green_room"
    assert state.pending_intrigue_target is None

    server.broadcast_to_game.assert_called_once()
    _, effect_response = server.broadcast_to_game.call_args[0]
    assert effect_response.action == "intrigue_effect_resolved"
    assert effect_response.plot_bonus_vp == 0


# --- Regression: reassigning a backstage worker to Green Room did nothing ---
# Bug: during the reassignment phase, moving a worker onto The Green Room
# silently completed the reassignment without ever prompting for an
# intrigue play or a quest selection.


def _make_reassignment_state(intrigue_cards: int = 1):
    state = GameState(game_code="test", game_id="test-id")
    state.phase = GamePhase.REASSIGNMENT
    player = _make_player()
    for i in range(intrigue_cards):
        player.intrigue_hand.append(
            IntrigueCard(
                id=f"card_{i}",
                name=f"Card {i}",
                description="test",
                effect_type="gain_coins",
                effect_value={"coins": 1},
            )
        )
    state.players = [player]

    green_room = _make_green_room()
    state.board.action_spaces["the_green_room"] = green_room
    state.board.backstage_slots = [BackstageSlot(slot_number=1, occupied_by="p1")]
    state.reassignment_queue = [1]

    return state, player, green_room


def test_reassign_worker_to_green_room_prompts_intrigue_play():
    state, player, green_room = _make_reassignment_state()
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.slot_number = 1
    msg.target_space_id = "the_green_room"

    asyncio.run(handle_reassign_worker(server, conn, msg))

    server.send_to_player.assert_called_once()
    sent_player_id, response = server.send_to_player.call_args[0]
    assert sent_player_id == "p1"
    assert response.action == "intrigue_play_prompt"
    assert response.source == "green_room"

    assert green_room.occupied_by == "p1"
    assert state.board.backstage_slots[0].occupied_by is None
    assert state.reassignment_queue == []
    assert state.pending_play_intrigue == {"player_id": "p1", "source": "green_room"}
    assert state.pending_placement is not None
    assert state.pending_placement["space_id"] == "the_green_room"
    assert state.pending_placement["is_reassignment"] is True
    assert state.pending_placement["from_slot"] == 1


def test_reassign_worker_to_green_room_without_intrigue_cards_rejected():
    """Regression guard: if the pre-check is ever skipped, we'd rather see
    an explicit error than silently commit a broken reassignment."""
    state, player, green_room = _make_reassignment_state(intrigue_cards=0)
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.slot_number = 1
    msg.target_space_id = "the_green_room"

    asyncio.run(handle_reassign_worker(server, conn, msg))

    conn.send_error.assert_called_once()
    server.broadcast_to_game.assert_not_called()
    server.send_to_player.assert_not_called()

    assert green_room.occupied_by is None
    assert state.board.backstage_slots[0].occupied_by == "p1"
    assert state.reassignment_queue == [1]
    assert state.pending_placement is None
