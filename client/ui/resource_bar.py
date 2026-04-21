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
            t.font_size = font_size
            return t
        t = arcade.Text(
            text,
            x,
            y,
            color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def update_resources(self, resources: dict) -> None:
        self.resources = resources

    def draw(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        workers_left: int = 0,
        victory_points: int = 0,
        intrigue_count: int = 0,
        quests_open: int = 0,
        quests_closed: int = 0,
        scale: float = 1.0,
    ) -> None:
        s = scale
        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (25, 25, 35),
        )

        font_sz = max(8, int(16 * s))
        swatch = int(20 * s)
        count = len(_RESOURCE_CONFIG)
        section_w = w / count
        left_shift = section_w * 0.25
        row_y = y + h * 0.33
        top_y = y + h * 0.72

        for i, (key, label, color) in enumerate(_RESOURCE_CONFIG):
            cx = x + section_w * (i + 0.5) - left_shift
            val = self.resources.get(key, 0)

            arcade.draw_rect_filled(
                arcade.rect.XYWH(cx - 30 * s, row_y, swatch, swatch),
                color,
            )

            self._text(
                f"res_{key}",
                f"{label}: {val}",
                cx - 15 * s,
                row_y,
                arcade.color.WHITE,
                font_sz,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            ).draw()

        top_row = [
            ("workers_left", f"Workers left: {workers_left}"),
            ("vp", f"VP: {victory_points}"),
            ("intrigue", f"Intrigue: {intrigue_count}"),
            ("quests_open", f"Quests Open: {quests_open}"),
            ("quests_closed", f"Quests Done: {quests_closed}"),
        ]
        for i, (key, label) in enumerate(top_row):
            cx = x + section_w * (i + 0.5) - left_shift
            self._text(
                key,
                label,
                cx - 15 * s,
                top_y,
                arcade.color.WHITE,
                font_sz,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            ).draw()
