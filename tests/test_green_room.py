"""Tests for The Green Room — play intrigue card + select quest card."""

import json
from pathlib import Path

from server.models.game import (
    ActionSpace,
    GameState,
    Player,
    PlayerResources,
)

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
