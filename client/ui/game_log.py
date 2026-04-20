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
        self._auto_scroll: bool = True
        self._max_lines: int = _VISIBLE_LINES
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
            text, x, y, color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def add_entry(self, text: str) -> None:
        self.entries.append(text)
        if len(self.entries) > _MAX_ENTRIES:
            self.entries = self.entries[-_MAX_ENTRIES:]
        if self._auto_scroll:
            self.scroll_offset = max(
                0, len(self.entries) - self._max_lines,
            )

    def scroll(self, direction: int) -> None:
        """Scroll by direction lines (negative=up, positive=down)."""
        max_offset = max(
            0, len(self.entries) - self._max_lines,
        )
        self.scroll_offset = max(
            0, min(self.scroll_offset + direction, max_offset),
        )
        self._auto_scroll = self.scroll_offset >= max_offset

    def draw(
        self, x: float, y: float, w: float, h: float,
        scale: float = 1.0,
    ) -> None:
        s = scale
        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (20, 20, 30),
        )

        font_title = max(8, int(16 * s))
        font_entry = max(8, int(12 * s))
        line_height = max(14, int(22 * s))

        # Title
        self._text(
            "title", "Game Log",
            x + w / 2, y + h - 20 * s,
            arcade.color.WHITE, font_title,
            anchor_x="center", bold=True,
        ).draw()

        # Log entries
        max_lines = min(
            _VISIBLE_LINES, int((h - 50 * s) / line_height),
        )
        self._max_lines = max_lines
        start = self.scroll_offset
        end = min(start + max_lines, len(self.entries))

        max_chars = max(20, int(60 * s))
        for i, idx in enumerate(range(start, end)):
            text = self.entries[idx]
            if len(text) > max_chars:
                text = text[: max_chars - 2] + ".."
            ty = y + h - 50 * s - i * line_height
            self._text(
                f"line_{i}", text,
                x + 8 * s, ty,
                arcade.color.LIGHT_GRAY, font_entry,
            ).draw()
