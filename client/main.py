"""Client entry point: launch Arcade window and connect to server."""

from __future__ import annotations

import argparse

from client.game_window import GameWindow
from client.network_client import NetworkClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker Placement Game Client")
    parser.add_argument(
        "--server", default="ws://localhost:8765", help="Server WebSocket URL"
    )
    parser.add_argument("--fullscreen", action="store_true", help="Launch fullscreen")
    parser.add_argument("--name", default="", help="Pre-fill display name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Create the network client (shared across all views)
    network = NetworkClient(server_url=args.server)

    # Create the window
    window = GameWindow(fullscreen=args.fullscreen)

    # Attach network and args to the window so views can access them
    window.network = network  # type: ignore[attr-defined]
    window.player_name = args.name  # type: ignore[attr-defined]
    window.player_id = None  # type: ignore[attr-defined]
    window.game_code = None  # type: ignore[attr-defined]

    # Start on the main menu
    window.show_menu()

    import arcade
    arcade.run()


if __name__ == "__main__":
    main()
