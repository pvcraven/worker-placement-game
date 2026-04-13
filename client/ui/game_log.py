"""Scrollable game action log panel."""

from __future__ import annotations

import arcade

_MAX_ENTRIES = 200
_VISIBLE_LINES = 20


class GameLogPanel:
    """Displays a scrollable log of game actions."""

    def __init__(self) -> None:
        self.entries: list[str] = []
        self.scroll_offset: int = 0
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
        """Get or create a cached Text object, updating position and content."""
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

    def add_entry(self, text: str) -> None:
        self.entries.append(text)
        if len(self.entries) > _MAX_ENTRIES:
            self.entries = self.entries[-_MAX_ENTRIES:]
        # Auto-scroll to bottom
        self.scroll_offset = max(0, len(self.entries) - _VISIBLE_LINES)

    def draw(self, x: float, y: float, w: float, h: float) -> None:
        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (20, 20, 30),
        )

        # Title
        self._text(
            "title", "Game Log",
            x + w / 2, y + h - 20,
            arcade.color.WHITE, 16,
            anchor_x="center", bold=True,
        ).draw()

        # Log entries
        line_height = 22
        max_lines = min(_VISIBLE_LINES, int((h - 50) / line_height))
        start = self.scroll_offset
        end = min(start + max_lines, len(self.entries))

        for i, idx in enumerate(range(start, end)):
            text = self.entries[idx]
            if len(text) > 38:
                text = text[:36] + ".."
            ty = y + h - 50 - i * line_height
            self._text(
                f"line_{i}", text,
                x + 8, ty,
                arcade.color.LIGHT_GRAY, 12,
            ).draw()
