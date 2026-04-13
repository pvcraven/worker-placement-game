"""WebSocket server: accept connections, route messages, manage sessions."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import websockets
from websockets.asyncio.server import ServerConnection

from shared.messages import (
    ErrorResponse,
    PongResponse,
    parse_client_message,
)

if TYPE_CHECKING:
    from server.game_state import SessionManager

logger = logging.getLogger(__name__)


class ClientConnection:
    """Wraps a WebSocket connection with player/game metadata."""

    def __init__(self, ws: ServerConnection) -> None:
        self.ws = ws
        self.player_id: str | None = None
        self.game_code: str | None = None

    async def send_json(self, msg: dict) -> None:
        try:
            import json
            await self.ws.send(json.dumps(msg))
        except websockets.ConnectionClosed:
            logger.debug("Send failed: connection closed for player %s", self.player_id)

    async def send_model(self, model) -> None:
        try:
            await self.ws.send(model.model_dump_json())
        except websockets.ConnectionClosed:
            logger.debug("Send failed: connection closed for player %s", self.player_id)

    async def send_error(self, code: str, message: str) -> None:
        await self.send_model(ErrorResponse(code=code, message=message))


class GameServer:
    """Top-level WebSocket server managing all connections."""

    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager
        self.connections: dict[str, ClientConnection] = {}  # player_id -> connection

    async def handler(self, ws: ServerConnection) -> None:
        """Handle a single WebSocket connection lifecycle."""
        conn = ClientConnection(ws)
        logger.info("New connection from %s", ws.remote_address)
        try:
            async for raw_message in ws:
                await self._route_message(conn, raw_message)
        except websockets.ConnectionClosed:
            logger.info("Connection closed for player %s", conn.player_id)
        finally:
            await self._handle_disconnect(conn)

    async def _route_message(
        self, conn: ClientConnection, raw: str | bytes
    ) -> None:
        """Parse and route an incoming client message."""
        try:
            msg = parse_client_message(raw)
        except Exception:
            await conn.send_error("INVALID_MESSAGE", "Could not parse message.")
            return

        action = msg.action
        handler_name = f"_handle_{action}"
        handler = getattr(self, handler_name, None)
        if handler is None:
            await conn.send_error("INVALID_ACTION", f"Unknown action: {action}")
            return

        try:
            await handler(conn, msg)
        except Exception:
            logger.exception("Error handling action %s", action)
            await conn.send_error("INVALID_ACTION", "Internal server error.")

    # ------------------------------------------------------------------
    # Lobby handlers
    # ------------------------------------------------------------------

    async def _handle_create_game(self, conn, msg) -> None:
        from server.lobby import create_game
        await create_game(self, conn, msg)

    async def _handle_join_game(self, conn, msg) -> None:
        from server.lobby import join_game
        await join_game(self, conn, msg)

    async def _handle_player_ready(self, conn, msg) -> None:
        from server.lobby import player_ready
        await player_ready(self, conn, msg)

    async def _handle_start_game(self, conn, msg) -> None:
        from server.lobby import start_game
        await start_game(self, conn, msg)

    # ------------------------------------------------------------------
    # Gameplay handlers
    # ------------------------------------------------------------------

    async def _handle_place_worker(self, conn, msg) -> None:
        from server.game_engine import handle_place_worker
        await handle_place_worker(self, conn, msg)

    async def _handle_place_worker_garage(self, conn, msg) -> None:
        from server.game_engine import handle_place_worker_garage
        await handle_place_worker_garage(self, conn, msg)

    async def _handle_complete_quest(self, conn, msg) -> None:
        from server.game_engine import handle_complete_quest
        await handle_complete_quest(self, conn, msg)

    async def _handle_acquire_contract(self, conn, msg) -> None:
        from server.game_engine import handle_acquire_contract
        await handle_acquire_contract(self, conn, msg)

    async def _handle_acquire_intrigue(self, conn, msg) -> None:
        from server.game_engine import handle_acquire_intrigue
        await handle_acquire_intrigue(self, conn, msg)

    async def _handle_purchase_building(self, conn, msg) -> None:
        from server.game_engine import handle_purchase_building
        await handle_purchase_building(self, conn, msg)

    async def _handle_reassign_worker(self, conn, msg) -> None:
        from server.game_engine import handle_reassign_worker
        await handle_reassign_worker(self, conn, msg)

    async def _handle_choose_intrigue_target(self, conn, msg) -> None:
        from server.game_engine import handle_choose_intrigue_target
        await handle_choose_intrigue_target(self, conn, msg)

    # ------------------------------------------------------------------
    # System handlers
    # ------------------------------------------------------------------

    async def _handle_reconnect(self, conn, msg) -> None:
        from server.lobby import reconnect
        await reconnect(self, conn, msg)

    async def _handle_ping(self, conn, msg) -> None:
        await conn.send_model(PongResponse())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def register_connection(self, player_id: str, conn: ClientConnection) -> None:
        conn.player_id = player_id
        self.connections[player_id] = conn

    def get_connection(self, player_id: str) -> ClientConnection | None:
        return self.connections.get(player_id)

    async def broadcast_to_game(self, game_code: str, model) -> None:
        """Send a message to all connected players in a game."""
        session = self.session_manager.get_session(game_code)
        if session is None:
            return
        data = model.model_dump_json()
        for player in session.players:
            conn = self.connections.get(player.player_id)
            if conn and conn.ws.state.name == "OPEN":
                try:
                    await conn.ws.send(data)
                except websockets.ConnectionClosed:
                    pass

    async def send_to_player(self, player_id: str, model) -> None:
        """Send a message to a specific player."""
        conn = self.connections.get(player_id)
        if conn:
            await conn.send_model(model)

    async def _handle_disconnect(self, conn: ClientConnection) -> None:
        """Clean up when a connection is lost."""
        if conn.player_id:
            self.connections.pop(conn.player_id, None)
            if conn.game_code:
                session = self.session_manager.get_session(conn.game_code)
                if session:
                    player = session.get_player(conn.player_id)
                    if player:
                        player.is_connected = False
                        from shared.messages import PlayerDisconnectedResponse
                        await self.broadcast_to_game(
                            conn.game_code,
                            PlayerDisconnectedResponse(
                                player_id=conn.player_id,
                                player_name=player.display_name,
                            ),
                        )

    async def start(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        """Start the WebSocket server."""
        logger.info("Starting server on ws://%s:%d", host, port)
        async with websockets.serve(self.handler, host, port):
            await asyncio.Future()  # Run forever
