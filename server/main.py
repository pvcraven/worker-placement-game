"""Server entry point: load config, start WebSocket server."""

from __future__ import annotations

import argparse
import asyncio
import logging

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

    cleanup_task = asyncio.create_task(
        cleanup_loop(session_manager, config.rules.game_preserve_timeout_seconds)
    )

    try:
        await server.start(host=args.host, port=args.port)
    finally:
        cleanup_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
