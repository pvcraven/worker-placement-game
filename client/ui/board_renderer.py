"""Board layout and action space rendering."""

from __future__ import annotations

import arcade

from client.ui.card_renderer import CardRenderer


# Board layout positions (proportional, relative to board area)
_SPACE_LAYOUT: dict[str, tuple[float, float]] = {
    "merch_store": (0.08, 0.7),
    "motown": (0.08, 0.5),
    "guitar_center": (0.08, 0.3),
    "talent_show": (0.22, 0.7),
    "rhythm_pit": (0.22, 0.5),
    "castle_waterdeep": (0.22, 0.3),
    "the_garage_1": (0.38, 0.82),
    "the_garage_2": (0.52, 0.82),
    "the_garage_3": (0.66, 0.82),
    "builders_hall": (0.08, 0.12),
}

_BACKSTAGE_LAYOUT: list[tuple[float, float]] = [
    (0.38, 0.28),  # Slot 1
    (0.52, 0.28),  # Slot 2
    (0.66, 0.28),  # Slot 3
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
        self._space_rects: dict[
            str, tuple[float, float, float, float]
        ] = {}
        self._building_spaces: list[dict] = []
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
            text, x, y, color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def update_board(
        self, board: dict, players: list[dict]
    ) -> None:
        self.board_data = board
        self.players = players

    def draw(
        self, x: float, y: float, w: float, h: float
    ) -> None:
        """Draw the board in the given rectangle."""
        self._space_rects.clear()

        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            (30, 40, 50),
        )

        spaces = self.board_data.get("action_spaces", {})
        backstage_slots = self.board_data.get(
            "backstage_slots", []
        )

        # Draw permanent action spaces
        for space_id, (px, py) in _SPACE_LAYOUT.items():
            cx = x + px * w
            cy = y + py * h
            space_data = spaces.get(space_id, {})
            self._draw_space(cx, cy, space_id, space_data)

        # Draw Backstage slots
        for i, (px, py) in enumerate(_BACKSTAGE_LAYOUT):
            cx = x + px * w
            cy = y + py * h
            slot_num = i + 1
            slot_data = {}
            for gs in backstage_slots:
                if gs.get("slot_number") == slot_num:
                    slot_data = gs
                    break
            self._draw_backstage_slot(
                cx, cy, slot_num, slot_data
            )

        # Draw "THE GARAGE" label and face-up quest cards
        garage_center_x = x + 0.52 * w
        self._text(
            "garage_label", "THE GARAGE",
            garage_center_x, y + 0.93 * h,
            arcade.color.CYAN, 16,
            anchor_x="center", bold=True,
        ).draw()

        face_up_quests = self.board_data.get(
            "face_up_quests", []
        )
        if face_up_quests:
            card_w = 130
            spacing = card_w + 20
            total_w = len(face_up_quests) * spacing
            start_x = (
                garage_center_x - total_w / 2 + card_w / 2
            )
            card_y = y + 0.56 * h
            for i, quest in enumerate(face_up_quests):
                cx = start_x + i * spacing
                CardRenderer.draw_contract(
                    cx, card_y, quest,
                    cache_key=f"faceup_{i}",
                )
                qid = quest.get("id", f"quest_{i}")
                self._space_rects[f"quest_card_{qid}"] = (
                    cx - card_w / 2,
                    card_y - 100,
                    card_w,
                    200,
                )

        # Draw constructed buildings
        building_start_x = 0.70
        for i, space_id in enumerate(
            self.board_data.get("constructed_buildings", [])
        ):
            space_data = spaces.get(space_id, {})
            row = i % 5
            col = i // 5
            cx = x + (building_start_x + col * 0.15) * w
            cy = y + (0.8 - row * 0.15) * h
            self._draw_space(
                cx, cy, space_id, space_data, is_building=True
            )

        # Board title
        self._text(
            "board_title", "THE BOARD",
            x + w / 2, y + h - 20,
            arcade.color.WHITE, 20,
            anchor_x="center", bold=True,
        ).draw()

        # Backstage label
        self._text(
            "backstage_label", "BACKSTAGE",
            x + 0.52 * w, y + 0.38 * h,
            arcade.color.YELLOW, 16,
            anchor_x="center", bold=True,
        ).draw()

    def _draw_space(
        self,
        cx: float,
        cy: float,
        space_id: str,
        data: dict,
        is_building: bool = False,
    ) -> None:
        sw, sh = _SPACE_WIDTH, _SPACE_HEIGHT
        self._space_rects[space_id] = (
            cx - sw / 2, cy - sh / 2, sw, sh
        )

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
        self._text(
            f"space_{space_id}_name", name,
            cx, cy + 12,
            arcade.color.WHITE, 13,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        # Show reward hint
        reward = data.get("reward", {})
        reward_str = self._reward_summary(
            reward, data.get("reward_special")
        )
        if reward_str:
            self._text(
                f"space_{space_id}_reward", reward_str,
                cx, cy - 14,
                arcade.color.LIGHT_GRAY, 11,
                anchor_x="center", anchor_y="center",
            ).draw()

        # Worker token
        if occupied:
            color = self._player_color(occupied)
            arcade.draw_circle_filled(
                cx + sw / 2 - 14, cy, 9, color
            )

    def _draw_backstage_slot(
        self,
        cx: float,
        cy: float,
        slot_num: int,
        data: dict,
    ) -> None:
        sw, sh = _SPACE_WIDTH, 60
        space_id = f"backstage_slot_{slot_num}"
        self._space_rects[space_id] = (
            cx - sw / 2, cy - sh / 2, sw, sh
        )

        occupied = data.get("occupied_by")
        bg_color = (
            (80, 50, 50) if not occupied else (80, 80, 40)
        )

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, sw, sh),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, sw, sh),
            arcade.color.YELLOW,
            border_width=1,
        )

        self._text(
            f"backstage_{slot_num}_label",
            f"Slot {slot_num}",
            cx, cy + 8,
            arcade.color.YELLOW, 13,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        if occupied:
            color = self._player_color(occupied)
            arcade.draw_circle_filled(
                cx + sw / 2 - 14, cy, 9, color
            )
            card = data.get("intrigue_card_played")
            if card:
                self._text(
                    f"backstage_{slot_num}_card",
                    card.get("name", "")[:16],
                    cx, cy - 12,
                    arcade.color.LIGHT_GRAY, 11,
                    anchor_x="center",
                ).draw()

    def _reward_summary(
        self, reward: dict, special: str | None
    ) -> str:
        if special:
            labels = {
                "acquire_contract_or_intrigue": (
                    "Contract/Intrigue"
                ),
                "purchase_building": "Buy Building",
                "first_player_marker_and_intrigue": (
                    "1st Player + Intrigue"
                ),
                "quest_and_coins": "Quest + 2$",
                "quest_and_intrigue": "Quest + Intrigue",
                "reset_quests": "Reset Quests",
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

    def get_space_at(
        self, x: float, y: float
    ) -> str | None:
        """Return the space_id at screen coordinates."""
        for space_id, (rx, ry, rw, rh) in (
            self._space_rects.items()
        ):
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return space_id
        return None
