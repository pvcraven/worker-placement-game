"""Tests for join-as-reconnect lobby logic."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from server.lobby import join_game
from server.models.game import GameState, Player
from shared.constants import GamePhase


def _make_player(name: str, slot: int, connected: bool = True) -> Player:
    return Player(
        player_id=f"pid-{slot}",
        display_name=name,
        slot_index=slot,
        is_connected=connected,
    )


def _make_state(phase: GamePhase = GamePhase.PLACEMENT) -> GameState:
    state = GameState(
        game_code="ABC",
        game_id="game_ABC_1",
        max_players=4,
    )
    state.phase = phase
    state.players = [
        _make_player("Alice", 0, connected=True),
        _make_player("Bob", 1, connected=False),
    ]
    state.last_activity = time.time()
    return state


def _make_server(state: GameState) -> MagicMock:
    server = MagicMock()
    server.session_manager.get_session.return_value = state
    server.register_connection = MagicMock()
    server.broadcast_to_game = AsyncMock()
    server.send_to_player = AsyncMock()
    return server


def _make_conn() -> MagicMock:
    conn = MagicMock()
    conn.player_id = None
    conn.game_code = None
    conn.send_model = AsyncMock()
    conn.send_error = AsyncMock()
    return conn


def _make_join_msg(game_code: str, name: str) -> MagicMock:
    msg = MagicMock()
    msg.game_code = game_code
    msg.player_name = name
    msg.max_players = 4
    return msg


def test_join_active_game_reconnects_disconnected_player():
    """Joining an active game with matching name triggers reconnect."""
    state = _make_state(GamePhase.PLACEMENT)
    server = _make_server(state)
    conn = _make_conn()
    msg = _make_join_msg("ABC", "Bob")

    asyncio.run(join_game(server, conn, msg))

    bob = state.players[1]
    assert bob.is_connected is True
    server.register_connection.assert_called_once_with("pid-1", conn)
    conn.send_error.assert_not_called()
    conn.send_model.assert_called_once()
    sent = conn.send_model.call_args[0][0]
    assert sent.action == "state_sync"
    server.broadcast_to_game.assert_called_once()


def test_join_active_game_rejects_unknown_name():
    """Joining an active game with non-matching name returns error."""
    state = _make_state(GamePhase.PLACEMENT)
    server = _make_server(state)
    conn = _make_conn()
    msg = _make_join_msg("ABC", "Charlie")

    asyncio.run(join_game(server, conn, msg))

    conn.send_error.assert_called_once_with(
        "INVALID_ACTION", "Game already in progress."
    )
    conn.send_model.assert_not_called()


def test_join_active_game_rejects_connected_player_name():
    """Joining with a name that matches a currently-connected player fails."""
    state = _make_state(GamePhase.PLACEMENT)
    server = _make_server(state)
    conn = _make_conn()
    msg = _make_join_msg("ABC", "Alice")

    asyncio.run(join_game(server, conn, msg))

    conn.send_error.assert_called_once_with(
        "INVALID_ACTION", "Game already in progress."
    )


def test_join_lobby_game_still_works_normally():
    """Normal join for LOBBY phase game is unaffected."""
    state = _make_state(GamePhase.LOBBY)
    server = _make_server(state)
    conn = _make_conn()
    msg = _make_join_msg("ABC", "Charlie")

    asyncio.run(join_game(server, conn, msg))

    conn.send_error.assert_not_called()
    conn.send_model.assert_called_once()
    sent = conn.send_model.call_args[0][0]
    assert sent.action == "game_created"
    assert len(state.players) == 3
