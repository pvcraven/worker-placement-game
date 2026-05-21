"""Server entry point: load config, start WebSocket server."""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys

from server.config_loader import load_config
from server.game_state import SessionManager
from server.network import GameServer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker Placement Game Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--config", default="config", help="Config directory path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser.parse_args()


async def cleanup_loop(session_manager: SessionManager, timeout: int) -> None:
    """Periodically remove expired game sessions."""
    while True:
        await asyncio.sleep(60)
        expired = session_manager.cleanup_expired(timeout)
        if expired:
            logging.info("Cleaned up %d expired session(s)", len(expired))


async def stdin_listener(shutdown_event: asyncio.Event) -> None:
    """Watch stdin for 'q' to trigger shutdown."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _wait_for_quit, shutdown_event)


def _wait_for_quit(shutdown_event: asyncio.Event) -> None:
    try:
        for line in sys.stdin:
            if line.strip().lower() == "q":
                shutdown_event.set()
                return
    except (EOFError, OSError):
        pass


async def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = load_config(args.config)
    logging.info("Configuration loaded successfully")

    session_manager = SessionManager()
    session_manager.config = config  # type: ignore[attr-defined]

    server = GameServer(session_manager)

    shutdown_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_event.set)
        except NotImplementedError:
            pass

    cleanup_task = asyncio.create_task(
        cleanup_loop(session_manager, config.rules.game_preserve_timeout_seconds)
    )
    stdin_task = asyncio.create_task(stdin_listener(shutdown_event))

    try:
        await server.start(
            host=args.host,
            port=args.port,
            shutdown_event=shutdown_event,
        )
    finally:
        cleanup_task.cancel()
        stdin_task.cancel()
        logging.info("Server shut down.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
