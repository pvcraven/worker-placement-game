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
        self._text_cache: dict[str, arcade.Text] = {}

    def _text(
        self,
        key: str,
        text: str,
        x: float,
        y: float,
        color,
        font_size: int,
        **kwargs,
    ) -> arcade.Text:
        """Get or create a cached Text object."""
        if key in self._text_cache:
            t = self._text_cache[key]
            t.text = text
            t.x = x
            t.y = y
            t.color = color
            return t
        t = arcade.Text(
            text, x, y, color, font_size=font_size, **kwargs,
        )
        self._text_cache[key] = t
        return t

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
            self._text(
                f"res_{key}", f"{label}: {val}",
                cx - 15, cy,
                arcade.color.WHITE, 16,
                anchor_x="left", anchor_y="center", bold=True,
            ).draw()

        # VP display at the end
        vp_cx = x + section_w * (count + 0.5)
        self._text(
            "vp",
            f"VP: {self.resources.get('victory_points', 0)}",
            vp_cx - 30, y + h / 2,
            arcade.color.YELLOW, 20,
            anchor_x="left", anchor_y="center", bold=True,
        ).draw()
