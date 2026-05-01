"""WebSocket client: runs in a background thread, communicates via queues."""

from __future__ import annotations

import asyncio
import json
import logging
import queue
import threading
from typing import Any

import websockets

logger = logging.getLogger(__name__)


class NetworkClient:
    """Manages the WebSocket connection to the game server.

    Runs the WebSocket in a daemon thread.  The Arcade main loop
    polls ``incoming`` each frame and puts outgoing messages into
    ``outgoing``.
    """

    def __init__(self, server_url: str = "ws://localhost:8765") -> None:
        self.server_url = server_url
        self.incoming: queue.Queue[dict[str, Any]] = queue.Queue()
        self.outgoing: queue.Queue[dict[str, Any]] = queue.Queue()
        self._ws: websockets.ClientConnection | None = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False

    # ------------------------------------------------------------------
    # Public API (called from Arcade main thread)
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Start the background networking thread."""
        if self._running:
            return
        # Drain stale queues from any previous session
        while not self.incoming.empty():
            try:
                self.incoming.get_nowait()
            except queue.Empty:
                break
        while not self.outgoing.empty():
            try:
                self.outgoing.get_nowait()
            except queue.Empty:
                break
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def disconnect(self) -> None:
        """Signal the background thread to stop."""
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def send(self, message: dict[str, Any]) -> None:
        """Enqueue a message to be sent to the server."""
        self.outgoing.put(message)

    def poll(self) -> list[dict[str, Any]]:
        """Drain all received messages (call once per frame)."""
        messages: list[dict[str, Any]] = []
        while True:
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                break
        return messages

    @property
    def connected(self) -> bool:
        return self._ws is not None and self._running

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connection_loop())
        except RuntimeError:
            pass
        except Exception:
            logger.exception("Network thread error")
        finally:
            self._loop.close()
            self._loop = None

    async def _connection_loop(self) -> None:
        """Connect, then send/receive until stopped."""
        while self._running:
            try:
                async with websockets.connect(self.server_url) as ws:
                    self._ws = ws
                    logger.info("Connected to %s", self.server_url)

                    recv_task = asyncio.create_task(self._recv_loop(ws))
                    send_task = asyncio.create_task(self._send_loop(ws))

                    done, pending = await asyncio.wait(
                        [recv_task, send_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for t in pending:
                        t.cancel()
                    for t in done:
                        if t.exception():
                            logger.debug("Task ended with: %s", t.exception())

            except (ConnectionRefusedError, OSError) as e:
                logger.warning("Connection failed: %s — retrying in 2s", e)
                self._ws = None
                if self._running:
                    await asyncio.sleep(2)
            except websockets.ConnectionClosed:
                logger.info("Connection lost — retrying in 2s")
                self._ws = None
                if self._running:
                    await asyncio.sleep(2)

        self._ws = None

    async def _recv_loop(self, ws) -> None:
        async for raw in ws:
            try:
                data = json.loads(raw)
                self.incoming.put(data)
            except json.JSONDecodeError:
                logger.warning("Received non-JSON message")

    async def _send_loop(self, ws) -> None:
        while self._running:
            try:
                msg = self.outgoing.get_nowait()
                await ws.send(json.dumps(msg))
            except queue.Empty:
                await asyncio.sleep(0.016)  # ~60fps polling
