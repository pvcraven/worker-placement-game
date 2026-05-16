"""Marker color selection dialog shown at game start."""

from __future__ import annotations

import arcade
import arcade.shape_list

MARKER_COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "green": (0, 128, 0),
    "red": (255, 0, 0),
    "purple": (128, 0, 128),
    "blue": (0, 0, 255),
    "pink": (255, 105, 180),
    "lilac": (186, 147, 216),
    "orange": (255, 165, 0),
}

_COLOR_ORDER = [
    "green",
    "red",
    "purple",
    "blue",
    "pink",
    "lilac",
    "orange",
]


class MarkerSelectionDialog:
    """Full-screen dialog for choosing a marker color."""

    def __init__(self) -> None:
        self._visible = False
        self._colors: list[str] = list(_COLOR_ORDER)
        self._claims: dict[str, str] = {}
        self._my_player_id: str | None = None
        self._my_color: str | None = None

        self._bg_shapes: arcade.shape_list.ShapeElementList | None = None
        self._marker_shapes: arcade.shape_list.ShapeElementList | None = None
        self._title_text: arcade.Text | None = None
        self._label_texts: dict[str, arcade.Text] = {}
        self._last_dims: tuple[float, float] = (0.0, 0.0)

        self._marker_positions: dict[str, tuple[float, float]] = {}
        self._marker_radius: float = 0.0

    @property
    def is_visible(self) -> bool:
        return self._visible

    def show(
        self,
        available_colors: list[str],
        players: list[dict],
        my_player_id: str,
    ) -> None:
        self._visible = True
        self._colors = list(_COLOR_ORDER)
        self._my_player_id = my_player_id
        self._my_color = None
        self._claims.clear()
        for p in players:
            color = p.get("marker_color")
            if color:
                pid = p.get("player_id", "")
                name = p.get("display_name", "")
                self._claims[color] = name
                if pid == my_player_id:
                    self._my_color = color
        self._last_dims = (0.0, 0.0)

    def hide(self) -> None:
        self._visible = False

    def mark_selected(
        self,
        color: str,
        player_name: str,
        player_id: str,
    ) -> None:
        self._claims[color] = player_name
        if player_id == self._my_player_id:
            self._my_color = color
        self._last_dims = (0.0, 0.0)

    def draw(self, width: float, height: float) -> None:
        if not self._visible:
            return

        dims = (width, height)
        if dims != self._last_dims:
            self._rebuild(width, height)
            self._last_dims = dims

        if self._bg_shapes:
            self._bg_shapes.draw()
        if self._marker_shapes:
            self._marker_shapes.draw()
        if self._title_text:
            self._title_text.draw()
        for txt in self._label_texts.values():
            txt.draw()

    def handle_click(
        self,
        x: float,
        y: float,
    ) -> str | None:
        if not self._visible:
            return None
        if self._my_color is not None:
            return None

        for color, (cx, cy) in self._marker_positions.items():
            if color in self._claims:
                continue
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= self._marker_radius**2:
                return color
        return None

    def _rebuild(self, width: float, height: float) -> None:
        bg = arcade.shape_list.ShapeElementList()
        bg.append(
            arcade.shape_list.create_rectangle_filled(
                width / 2,
                height / 2,
                width,
                height,
                (0, 0, 0, 180),
            )
        )

        panel_w = min(width * 0.8, 900)
        panel_h = min(height * 0.55, 400)
        cx = width / 2
        cy = height / 2

        bg.append(
            arcade.shape_list.create_rectangle_filled(
                cx,
                cy,
                panel_w + 4,
                panel_h + 4,
                (100, 100, 120, 200),
            )
        )
        bg.append(
            arcade.shape_list.create_rectangle_filled(
                cx,
                cy,
                panel_w,
                panel_h,
                (20, 20, 30, 245),
            )
        )
        self._bg_shapes = bg

        markers = arcade.shape_list.ShapeElementList()
        self._marker_positions.clear()
        self._label_texts.clear()

        n = len(self._colors)
        spacing = panel_w / (n + 1)
        radius = min(spacing * 0.35, panel_h * 0.18)
        self._marker_radius = radius
        marker_y = cy + radius * 0.5

        for i, color in enumerate(self._colors):
            mx = cx - panel_w / 2 + spacing * (i + 1)
            self._marker_positions[color] = (mx, marker_y)

            rgb = MARKER_COLOR_MAP.get(color, (200, 200, 200))
            claimed = color in self._claims

            if claimed:
                alpha = 120
            else:
                alpha = 255

            markers.append(
                arcade.shape_list.create_ellipse_filled(
                    mx,
                    marker_y,
                    radius,
                    radius,
                    (*rgb, alpha),
                )
            )

            if not claimed:
                markers.append(
                    arcade.shape_list.create_ellipse_outline(
                        mx,
                        marker_y,
                        radius,
                        radius,
                        arcade.color.WHITE,
                        2,
                    )
                )

            font_size = max(10, int(radius * 0.45))

            color_label = arcade.Text(
                color.capitalize(),
                mx,
                marker_y - radius - font_size * 1.2,
                arcade.color.LIGHT_GRAY,
                font_size=font_size,
                font_name="Tahoma",
                anchor_x="center",
                anchor_y="center",
            )
            self._label_texts[f"{color}_name"] = color_label

            if claimed:
                player_name = self._claims[color]
                name_label = arcade.Text(
                    player_name,
                    mx,
                    marker_y - radius - font_size * 2.6,
                    arcade.color.WHITE,
                    font_size=font_size,
                    font_name="Tahoma",
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                )
                self._label_texts[f"{color}_player"] = name_label

        self._marker_shapes = markers

        title_size = max(14, int(radius * 0.7))
        self._title_text = arcade.Text(
            "Choose Your Marker Color",
            cx,
            cy + panel_h / 2 - title_size * 1.5,
            arcade.color.WHITE,
            font_size=title_size,
            font_name="Tahoma",
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
