"""Player resource display bar at the bottom of the screen."""

from __future__ import annotations

import arcade

_RESOURCE_CONFIG = [
    ("guitarists", "Guitarists", arcade.color.RED),
    ("bass_players", "Bass", (30, 30, 30)),
    ("drummers", "Drummers", (220, 220, 220)),
    ("singers", "Singers", arcade.color.PURPLE),
    ("coins", "Coins", arcade.color.GOLD),
]


class ResourceBar:
    """Draws the player's resources as colored blocks at the bottom."""

    def __init__(self) -> None:
        self.resources: dict = {}

    def update_resources(self, resources: dict) -> None:
        self.resources = resources

    def draw(self, x: float, y: float, w: float, h: float) -> None:
        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (25, 25, 35),
        )

        count = len(_RESOURCE_CONFIG)
        section_w = w / (count + 1)  # +1 for VP display

        for i, (key, label, color) in enumerate(_RESOURCE_CONFIG):
            cx = x + section_w * (i + 0.5)
            cy = y + h / 2
            val = self.resources.get(key, 0)

            # Color swatch
            arcade.draw_rect_filled(
                arcade.rect.XYWH(cx - 30, cy, 20, 20),
                color,
            )

            # Label and count
            arcade.draw_text(
                f"{label}: {val}",
                cx - 15, cy,
                arcade.color.WHITE,
                font_size=16,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            )

        # VP display at the end
        vp_cx = x + section_w * (count + 0.5)
        arcade.draw_text(
            f"VP: {self.resources.get('victory_points', 0)}",
            vp_cx - 30, y + h / 2,
            arcade.color.YELLOW,
            font_size=20,
            anchor_x="left",
            anchor_y="center",
            bold=True,
        )
