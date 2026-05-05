"""Centered informational dialog overlay with auto-dismiss and queue support."""

from __future__ import annotations

import arcade
import arcade.shape_list


class InfoDialog:
    """Reusable centered dialog that displays text messages over the game view.

    Supports auto-dismiss (timed) and persistent (until explicitly dismissed) modes.
    Multiple dialogs queue and display sequentially.
    """

    def __init__(self) -> None:
        self._queue: list[tuple[str, float | None]] = []
        self._active_message: str | None = None
        self._active_duration: float | None = None
        self._elapsed: float = 0.0

        self._bg_shapes: arcade.shape_list.ShapeElementList | None = None
        self._text_obj: arcade.Text | None = None
        self._last_dims: tuple[float, float, float] = (0.0, 0.0, 0.0)

    @property
    def is_active(self) -> bool:
        return self._active_message is not None

    def show(self, message: str, duration: float | None = 1.5) -> None:
        if self._active_message is not None:
            self._queue.append((message, duration))
            return
        self._activate(message, duration)

    def dismiss(self) -> None:
        self._active_message = None
        self._active_duration = None
        self._elapsed = 0.0
        if self._queue:
            msg, dur = self._queue.pop(0)
            self._activate(msg, dur)

    def update(self, delta_time: float) -> None:
        if self._active_message is None:
            return
        if self._active_duration is None:
            return
        self._elapsed += delta_time
        if self._elapsed >= self._active_duration:
            self.dismiss()

    def draw(self, width: float, height: float, scale: float) -> None:
        if self._active_message is None:
            return

        dims = (width, height, scale)
        if self._bg_shapes is None or dims != self._last_dims:
            self._rebuild_shapes(width, height, scale)
            self._last_dims = dims

        self._bg_shapes.draw()  # type: ignore[union-attr]

        if self._text_obj is not None:
            self._text_obj.text = self._active_message
            self._text_obj.x = width / 2
            self._text_obj.y = height / 2
            self._text_obj.font_size = max(12, int(28 * scale))
            self._text_obj.draw()

    def _activate(self, message: str, duration: float | None) -> None:
        self._active_message = message
        self._active_duration = duration
        self._elapsed = 0.0
        if self._text_obj is not None:
            self._text_obj.text = message

    def _rebuild_shapes(self, width: float, height: float, scale: float) -> None:
        shapes = arcade.shape_list.ShapeElementList()

        # Full-screen semi-transparent overlay
        shapes.append(
            arcade.shape_list.create_rectangle_filled(
                width / 2, height / 2, width, height, (0, 0, 0, 140)
            )
        )

        panel_w = width * 0.6
        panel_h = height * 0.2

        # Panel border
        shapes.append(
            arcade.shape_list.create_rectangle_filled(
                width / 2, height / 2, panel_w + 4, panel_h + 4, (100, 100, 120, 180)
            )
        )

        # Panel background
        shapes.append(
            arcade.shape_list.create_rectangle_filled(
                width / 2, height / 2, panel_w, panel_h, (20, 20, 30, 240)
            )
        )

        self._bg_shapes = shapes

        self._text_obj = arcade.Text(
            self._active_message or "",
            width / 2,
            height / 2,
            arcade.color.WHITE,
            font_size=max(12, int(28 * scale)),
            font_name="Tahoma",
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
