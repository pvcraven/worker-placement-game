"""Regression tests for cancelling a quest selection triggered by visiting
an accumulating draw_contract building (e.g. Red Rocks Amphitheatre) — the
whole visit must unwind, not just skip the quest draw."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from server.game_engine import handle_cancel_quest_selection, handle_place_worker
from server.models.game import ActionSpace, GameState, Player, PlayerResources
from shared.card_models import BuildingTile
from shared.constants import GamePhase


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
    conn.send_model = AsyncMock()
    return conn


def _make_state() -> GameState:
    state = GameState(game_code="test", game_id="test-id")
    state.phase = GamePhase.PLACEMENT
    visitor = Player(
        player_id="p1",
        display_name="Visitor",
        slot_index=0,
        resources=PlayerResources(),
        available_workers=2,
        victory_points=0,
    )
    owner = Player(
        player_id="p2",
        display_name="Owner",
        slot_index=1,
        resources=PlayerResources(),
        victory_points=0,
    )
    state.players = [visitor, owner]
    state.turn_order = ["p1", "p2"]
    state.current_player_index = 0

    tile = BuildingTile(
        id="building_006",
        name="Red Rocks Amphitheatre",
        description="test",
        cost_coins=4,
        visitor_reward_special="draw_contract",
        owner_bonus_vp=2,
        accumulation_type="victory_points",
        accumulation_per_round=3,
        accumulation_initial=3,
        accumulated_stock=3,
    )
    state.board.action_spaces["building_006"] = ActionSpace(
        space_id="building_006",
        name="Red Rocks Amphitheatre",
        space_type="building",
        owner_id="p2",
        building_tile=tile,
        reward_special="draw_contract",
    )
    state.board.face_up_quests = []

    return state


def test_cancel_after_landing_on_accumulating_building_unwinds_everything():
    state = _make_state()
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.space_id = "building_006"

    asyncio.run(handle_place_worker(server, conn, msg))

    visitor = state.get_player("p1")
    owner = state.get_player("p2")
    space = state.board.action_spaces["building_006"]

    # Sanity check the visit actually granted the accumulated VP + owner bonus.
    assert visitor.victory_points == 3
    assert owner.victory_points == 2
    assert space.building_tile.accumulated_stock == 0
    assert visitor.available_workers == 1
    assert space.occupied_by == "p1"
    assert state.pending_placement is not None

    cancel_conn = _make_conn("p1")
    cancel_msg = MagicMock()
    asyncio.run(handle_cancel_quest_selection(server, cancel_conn, cancel_msg))

    assert visitor.victory_points == 0, "visitor's granted VP must be reversed"
    assert owner.victory_points == 0, "owner bonus VP must be reversed"
    assert (
        space.building_tile.accumulated_stock == 3
    ), "accumulated stock must be restored"
    assert visitor.available_workers == 2, "worker must be returned"
    assert space.occupied_by is None, "space must be freed"
    assert state.pending_placement is None
    assert state.pending_building_quest is None
