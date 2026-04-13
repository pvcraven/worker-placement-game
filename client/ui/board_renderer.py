"""Board layout and action space rendering."""

from __future__ import annotations

import arcade


# Board layout positions (proportional, relative to board area)
_SPACE_LAYOUT: dict[str, tuple[float, float]] = {
    "three_cups": (0.08, 0.7),
    "grinning_lion_pub": (0.08, 0.5),
    "the_arena": (0.08, 0.3),
    "pool_of_tears": (0.22, 0.7),
    "the_cathedral": (0.22, 0.5),
    "castle_waterdeep": (0.22, 0.3),
    "cliffwatch_inn_1": (0.40, 0.75),
    "cliffwatch_inn_2": (0.40, 0.55),
    "cliffwatch_inn_3": (0.40, 0.35),
    "builders_hall": (0.55, 0.55),
}

_GARAGE_LAYOUT: list[tuple[float, float]] = [
    (0.55, 0.80),  # Slot 1
    (0.55, 0.65),  # Slot 2
    (0.55, 0.50),  # Slot 3 -- intentionally offset from builders_hall
]

_SPACE_WIDTH = 170
_SPACE_HEIGHT = 75

# Colors for player tokens
_PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.PURPLE,
]


class BoardRenderer:
    """Draws the game board with action spaces and worker tokens."""

    def __init__(self) -> None:
        self.board_data: dict = {}
        self.players: list[dict] = []
        self._space_rects: dict[str, tuple[float, float, float, float]] = {}
        self._building_spaces: list[dict] = []

    def update_board(self, board: dict, players: list[dict]) -> None:
        self.board_data = board
        self.players = players

    def draw(self, x: float, y: float, w: float, h: float) -> None:
        """Draw the board in the given rectangle."""
        self._space_rects.clear()

        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (30, 40, 50),
        )

        spaces = self.board_data.get("action_spaces", {})
        garage_slots = self.board_data.get("garage_slots", [])

        # Draw permanent action spaces
        for space_id, (px, py) in _SPACE_LAYOUT.items():
            cx = x + px * w
            cy = y + py * h
            space_data = spaces.get(space_id, {})
            self._draw_space(cx, cy, space_id, space_data)

        # Draw Garage slots
        for i, (px, py) in enumerate(_GARAGE_LAYOUT):
            cx = x + px * w
            cy = y + py * h
            slot_num = i + 1
            slot_data = {}
            for gs in garage_slots:
                if gs.get("slot_number") == slot_num:
                    slot_data = gs
                    break
            self._draw_garage_slot(cx, cy, slot_num, slot_data)

        # Draw constructed buildings
        building_start_x = 0.70
        for i, space_id in enumerate(self.board_data.get("constructed_buildings", [])):
            space_data = spaces.get(space_id, {})
            row = i % 5
            col = i // 5
            cx = x + (building_start_x + col * 0.15) * w
            cy = y + (0.8 - row * 0.15) * h
            self._draw_space(cx, cy, space_id, space_data, is_building=True)

        # Board title
        arcade.draw_text(
            "THE BOARD",
            x + w / 2, y + h - 20,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            bold=True,
        )

        # Garage label
        arcade.draw_text(
            "THE GARAGE",
            x + 0.55 * w, y + 0.90 * h,
            arcade.color.YELLOW,
            font_size=16,
            anchor_x="center",
            bold=True,
        )

    def _draw_space(
        self,
        cx: float,
        cy: float,
        space_id: str,
        data: dict,
        is_building: bool = False,
    ) -> None:
        sw, sh = _SPACE_WIDTH, _SPACE_HEIGHT
        self._space_rects[space_id] = (cx - sw / 2, cy - sh / 2, sw, sh)

        occupied = data.get("occupied_by")
        bg_color = (60, 80, 60) if is_building else (50, 60, 80)
        if occupied:
            bg_color = (80, 80, 40)

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, sw, sh),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, sw, sh),
            arcade.color.WHITE,
            border_width=1,
        )

        name = data.get("name", space_id)
        if len(name) > 22:
            name = name[:20] + ".."
        arcade.draw_text(
            name,
            cx, cy + 12,
            arcade.color.WHITE,
            font_size=13,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        # Show reward hint
        reward = data.get("reward", {})
        reward_str = self._reward_summary(reward, data.get("reward_special"))
        if reward_str:
            arcade.draw_text(
                reward_str,
                cx, cy - 14,
                arcade.color.LIGHT_GRAY,
                font_size=11,
                anchor_x="center",
                anchor_y="center",
            )

        # Worker token
        if occupied:
            color = self._player_color(occupied)
            arcade.draw_circle_filled(cx + sw / 2 - 14, cy, 9, color)

    def _draw_garage_slot(
        self, cx: float, cy: float, slot_num: int, data: dict
    ) -> None:
        sw, sh = _SPACE_WIDTH, 60
        space_id = f"garage_slot_{slot_num}"
        self._space_rects[space_id] = (cx - sw / 2, cy - sh / 2, sw, sh)

        occupied = data.get("occupied_by")
        bg_color = (80, 50, 50) if not occupied else (80, 80, 40)

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, sw, sh),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, sw, sh),
            arcade.color.YELLOW,
            border_width=1,
        )

        arcade.draw_text(
            f"Slot {slot_num}",
            cx, cy + 8,
            arcade.color.YELLOW,
            font_size=13,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        if occupied:
            color = self._player_color(occupied)
            arcade.draw_circle_filled(cx + sw / 2 - 14, cy, 9, color)
            card = data.get("intrigue_card_played")
            if card:
                arcade.draw_text(
                    card.get("name", "")[:16],
                    cx, cy - 12,
                    arcade.color.LIGHT_GRAY,
                    font_size=10,
                    anchor_x="center",
                )

    def _reward_summary(self, reward: dict, special: str | None) -> str:
        if special:
            labels = {
                "acquire_contract_or_intrigue": "Contract/Intrigue",
                "purchase_building": "Buy Building",
                "first_player_marker_and_intrigue": "1st Player + Intrigue",
            }
            return labels.get(special, special)
        parts = []
        mapping = {
            "guitarists": "G",
            "bass_players": "B",
            "drummers": "D",
            "singers": "S",
            "coins": "$",
        }
        for key, label in mapping.items():
            val = reward.get(key, 0)
            if val > 0:
                parts.append(f"{val}{label}")
        return " ".join(parts) if parts else ""

    def _player_color(self, player_id: str) -> tuple:
        for i, p in enumerate(self.players):
            if p.get("player_id") == player_id:
                return _PLAYER_COLORS[i % len(_PLAYER_COLORS)]
        return arcade.color.GRAY

    def get_space_at(self, x: float, y: float) -> str | None:
        """Return the space_id at the given screen coordinates, or None."""
        for space_id, (rx, ry, rw, rh) in self._space_rects.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return space_id
        return None
