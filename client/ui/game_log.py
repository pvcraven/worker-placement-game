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
        arcade.draw_text(
            "Game Log",
            x + w / 2, y + h - 15,
            arcade.color.WHITE,
            font_size=12,
            anchor_x="center",
            bold=True,
        )

        # Log entries
        line_height = 16
        max_lines = min(_VISIBLE_LINES, int((h - 40) / line_height))
        start = self.scroll_offset
        end = min(start + max_lines, len(self.entries))

        for i, idx in enumerate(range(start, end)):
            text = self.entries[idx]
            if len(text) > 38:
                text = text[:36] + ".."
            ty = y + h - 40 - i * line_height
            arcade.draw_text(
                text,
                x + 8, ty,
                arcade.color.LIGHT_GRAY,
                font_size=9,
            )
