"""Client entry point: launch Arcade window and connect to server."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure card-generator is importable
_card_gen_dir = str(Path(__file__).resolve().parent.parent / "card-generator")
if _card_gen_dir not in sys.path:
    sys.path.insert(0, _card_gen_dir)

import arcade.text  # noqa: E402

# Fix DirectWrite font enumeration hang on some Windows systems by
# setting a known-good default font before any UI elements are created.
arcade.text.DEFAULT_FONT_NAMES = ("Arial",)

from client.game_window import GameWindow  # noqa: E402
from client.network_client import NetworkClient  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker Placement Game Client")
    parser.add_argument(
        "--server", default=None, help="Server WebSocket URL"
    )
    parser.add_argument("--fullscreen", action="store_true", help="Launch fullscreen")
    parser.add_argument("--name", default=None, help="Pre-fill display name")
    return parser.parse_args()


def main() -> None:
    from generate_cards import ensure_card_images
    ensure_card_images()

    args = parse_args()

    from client.user_config import load_config
    config = load_config()

    server = args.server or config["server"]
    name = args.name if args.name is not None else config["name"]

    # Create the network client (shared across all views)
    network = NetworkClient(server_url=server)

    # Create the window
    window = GameWindow(fullscreen=args.fullscreen)

    # Attach network and args to the window so views can access them
    window.network = network  # type: ignore[attr-defined]
    window.player_name = name  # type: ignore[attr-defined]
    window.player_id = None  # type: ignore[attr-defined]
    window.game_code = None  # type: ignore[attr-defined]

    # Start on the main menu
    window.show_menu()

    import arcade
    arcade.run()


if __name__ == "__main__":
    main()
