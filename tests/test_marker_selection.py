"""Tests for marker color selection during game start."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from server.lobby import select_marker
from server.models.game import GameState, Player
from shared.constants import GamePhase, MARKER_COLORS


def _make_player(
    name: str,
    slot: int,
    marker_color: str | None = None,
) -> Player:
    return Player(
        player_id=f"pid-{slot}",
        display_name=name,
        slot_index=slot,
        marker_color=marker_color,
    )


def _make_state() -> GameState:
    state = GameState(
        game_code="ABC",
        game_id="game_ABC_1",
        max_players=4,
    )
    state.phase = GamePhase.MARKER_SELECTION
    state.players = [
        _make_player("Alice", 0),
        _make_player("Bob", 1),
    ]
    state.last_activity = time.time()
    return state


def _make_server(state: GameState) -> MagicMock:
    server = MagicMock()
    server.session_manager.get_session.return_value = state
    server.broadcast_to_game = AsyncMock()
    server.send_to_player = AsyncMock()
    return server


def _make_conn(player_id: str, game_code: str = "ABC") -> MagicMock:
    conn = MagicMock()
    conn.player_id = player_id
    conn.game_code = game_code
    conn.send_model = AsyncMock()
    conn.send_error = AsyncMock()
    return conn


def _make_msg(color: str) -> MagicMock:
    msg = MagicMock()
    msg.color = color
    return msg


def test_valid_selection():
    state = _make_state()
    server = _make_server(state)
    conn = _make_conn("pid-0")
    msg = _make_msg("green")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[0].marker_color == "green"
    conn.send_error.assert_not_called()
    server.broadcast_to_game.assert_called_once()
    response = server.broadcast_to_game.call_args[0][1]
    assert response.action == "marker_selected"
    assert response.color == "green"
    assert response.player_id == "pid-0"
    assert response.all_selected is False


def test_duplicate_color_rejected():
    state = _make_state()
    state.players[0].marker_color = "red"
    server = _make_server(state)
    conn = _make_conn("pid-1")
    msg = _make_msg("red")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[1].marker_color is None
    conn.send_error.assert_called_once()
    error_args = conn.send_error.call_args[0]
    assert error_args[0] == "INVALID_ACTION"


def test_already_selected_rejected():
    state = _make_state()
    state.players[0].marker_color = "blue"
    server = _make_server(state)
    conn = _make_conn("pid-0")
    msg = _make_msg("green")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[0].marker_color == "blue"
    conn.send_error.assert_called_once()


def test_invalid_color_rejected():
    state = _make_state()
    server = _make_server(state)
    conn = _make_conn("pid-0")
    msg = _make_msg("magenta")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[0].marker_color is None
    conn.send_error.assert_called_once()


def test_wrong_phase_rejected():
    state = _make_state()
    state.phase = GamePhase.PLACEMENT
    server = _make_server(state)
    conn = _make_conn("pid-0")
    msg = _make_msg("green")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[0].marker_color is None
    conn.send_error.assert_called_once()


def test_all_selected_flag():
    state = _make_state()
    state.players[0].marker_color = "red"
    server = _make_server(state)
    conn = _make_conn("pid-1")
    msg = _make_msg("blue")

    asyncio.run(select_marker(server, conn, msg))

    assert state.players[1].marker_color == "blue"
    response = server.broadcast_to_game.call_args[0][1]
    assert response.all_selected is True


def test_all_marker_colors_are_valid():
    for color in MARKER_COLORS:
        state = _make_state()
        server = _make_server(state)
        conn = _make_conn("pid-0")
        msg = _make_msg(color)

        asyncio.run(select_marker(server, conn, msg))

        assert state.players[0].marker_color == color
        conn.send_error.assert_not_called()
