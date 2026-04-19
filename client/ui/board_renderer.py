"""Board layout and action space rendering."""

from __future__ import annotations

import logging
from pathlib import Path

import arcade
import arcade.shape_list

_log = logging.getLogger(__name__)

_CARD_WIDTH = 190
_CARD_HEIGHT = 230
_BUILDING_CARD_HEIGHT = 150
_SPACE_CARD_HEIGHT = 100


# Board layout positions (proportional, relative to board area)
# Permanent spaces in left column; second column for buildings
_SPACE_LAYOUT: dict[str, tuple[float, float]] = {
    "merch_store": (0.08, 0.91),
    "motown": (0.08, 0.78),
    "guitar_center": (0.08, 0.65),
    "talent_show": (0.08, 0.52),
    "rhythm_pit": (0.08, 0.39),
    "castle_waterdeep": (0.08, 0.26),
    "the_garage_1": (0.40, 0.92),
    "the_garage_2": (0.54, 0.92),
    "the_garage_3": (0.68, 0.92),
}

_BACKSTAGE_Y = [0.46, 0.33, 0.20]

# Colors for player tokens
_PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.PURPLE,
]


def _build_card_sprite_list(
    cards: list[dict],
    card_type: str,
    positions: list[tuple[float, float]],
) -> arcade.SpriteList:
    sprite_list = arcade.SpriteList()
    for card, (cx, cy) in zip(cards, positions):
        card_id = card.get("id", "")
        png_path = Path(
            f"client/assets/card_images/{card_type}/{card_id}.png"
        )
        if not png_path.exists():
            _log.warning("Card image not found: %s", png_path)
            continue
        sprite = arcade.Sprite(str(png_path))
        sprite.position = (cx, cy)
        sprite_list.append(sprite)
    return sprite_list


class BoardRenderer:
    """Draws the game board with action spaces and worker tokens."""

    def __init__(self) -> None:
        self.board_data: dict = {}
        self.players: list[dict] = []
        self._space_rects: dict[
            str, tuple[float, float, float, float]
        ] = {}
        self._building_spaces: list[dict] = []
        self._face_up_buildings: list[dict] = []
        self._deck_remaining: int = 0
        self._shape_list = arcade.shape_list.ShapeElementList()
        self._shapes_dirty = True
        self._last_draw_rect = (0.0, 0.0, 0.0, 0.0)
        self._quest_sprite_list: arcade.SpriteList | None = None
        self._building_sprite_list: arcade.SpriteList | None = None
        self._constructed_sprite_list: arcade.SpriteList | None = None
        self._space_sprite_list: arcade.SpriteList | None = None
        self._backstage_sprite_list: arcade.SpriteList | None = None
        self._realtor_sprite_list: arcade.SpriteList | None = None
        self._building_vp_texts: list[arcade.Text] = []
        self._building_vp_dirty = True

    def update_board(
        self, board: dict, players: list[dict]
    ) -> None:
        self.board_data = board
        self.players = players
        self._shapes_dirty = True

    def update_building_market(
        self, face_up_buildings: list[dict], deck_remaining: int,
    ) -> None:
        self._face_up_buildings = face_up_buildings
        self._deck_remaining = deck_remaining
        self._building_vp_dirty = True

    def draw(
        self, x: float, y: float, w: float, h: float,
        highlighted_ids: list[str] | None = None,
    ) -> None:
        """Draw the board in the given rectangle."""
        draw_rect = (x, y, w, h)
        if (
            self._shapes_dirty
            or draw_rect != self._last_draw_rect
        ):
            self._rebuild_shapes(x, y, w, h)
            self._last_draw_rect = draw_rect
            self._shapes_dirty = False

        self._shape_list.draw()

        if self._space_sprite_list:
            self._space_sprite_list.draw()

        spaces = self.board_data.get("action_spaces", {})
        backstage_slots = self.board_data.get(
            "backstage_slots", []
        )

        for space_id, (px, py) in _SPACE_LAYOUT.items():
            cx = x + px * w
            cy = y + py * h
            space_data = spaces.get(space_id, {})
            occupied = space_data.get("occupied_by")
            if occupied:
                color = self._player_color(occupied)
                arcade.draw_circle_filled(
                    cx + _CARD_WIDTH / 2 - 10, cy, 9, color,
                )

        if self._backstage_sprite_list:
            self._backstage_sprite_list.draw()

        garage_center_x = x + 0.54 * w
        n_q = max(
            len(self.board_data.get("face_up_quests", [])),
            4,
        )
        q_spacing = _CARD_WIDTH + 15
        bs_cx = (
            garage_center_x
            - n_q * q_spacing / 2
            + _CARD_WIDTH / 2
        )
        for i, py in enumerate(_BACKSTAGE_Y):
            cy = y + py * h
            slot_num = i + 1
            slot_data = {}
            for gs in backstage_slots:
                if gs.get("slot_number") == slot_num:
                    slot_data = gs
                    break
            occupied = slot_data.get("occupied_by")
            if occupied:
                color = self._player_color(occupied)
                arcade.draw_circle_filled(
                    bs_cx + _CARD_WIDTH / 2 - 10, cy, 9,
                    color,
                )
        face_up_quests = self.board_data.get(
            "face_up_quests", []
        )
        if face_up_quests:
            card_w = _CARD_WIDTH
            spacing = card_w + 15
            total_w = len(face_up_quests) * spacing
            start_x = (
                garage_center_x - total_w / 2 + card_w / 2
            )
            card_y = y + 0.68 * h
            hl = highlighted_ids or []
            positions = [
                (start_x + i * spacing, card_y)
                for i in range(len(face_up_quests))
            ]
            self._quest_sprite_list = _build_card_sprite_list(
                face_up_quests, "quests", positions,
            )
            self._quest_sprite_list.draw()
            for i, quest in enumerate(face_up_quests):
                cx = positions[i][0]
                qid = quest.get("id", f"quest_{i}")
                if qid in hl:
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            cx, card_y,
                            _CARD_WIDTH, _CARD_HEIGHT,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )
                self._space_rects[
                    f"quest_card_{qid}"
                ] = (
                    cx - card_w / 2,
                    card_y - _CARD_HEIGHT / 2,
                    card_w,
                    _CARD_HEIGHT,
                )

        # Realtor space
        if self._realtor_sprite_list:
            self._realtor_sprite_list.draw()
        realtor_data = spaces.get("realtor", {})
        if realtor_data.get("occupied_by"):
            r_rect = self._space_rects.get("realtor")
            if r_rect:
                r_cx = r_rect[0] + r_rect[2] / 2
                r_cy = r_rect[1] + r_rect[3] / 2
                color = self._player_color(
                    realtor_data["occupied_by"],
                )
                arcade.draw_circle_filled(
                    r_cx + _CARD_WIDTH / 2 - 10,
                    r_cy, 9, color,
                )

        # Face-up building cards — right-align with quest row
        quest_right = garage_center_x + n_q * q_spacing / 2
        if self._face_up_buildings:
            bld_w = _CARD_WIDTH
            bld_spacing = bld_w + 15
            n_bld = len(self._face_up_buildings)
            rightmost_cx = quest_right - bld_w / 2
            bld_start_x = (
                rightmost_cx - (n_bld - 1) * bld_spacing
            )
            bld_y = y + 0.20 * h
            bhl = highlighted_ids or []
            bld_positions = [
                (bld_start_x + i * bld_spacing, bld_y)
                for i in range(n_bld)
            ]
            self._building_sprite_list = _build_card_sprite_list(
                self._face_up_buildings, "buildings",
                bld_positions,
            )
            self._building_sprite_list.draw()
            if self._building_vp_dirty:
                self._building_vp_texts = []
                for j, b in enumerate(
                    self._face_up_buildings
                ):
                    vp = b.get("accumulated_vp", 0)
                    if vp > 0:
                        tx = (
                            bld_positions[j][0]
                            - _CARD_WIDTH / 2 + 8
                        )
                        ty = (
                            bld_y
                            - _BUILDING_CARD_HEIGHT / 2
                            + 6
                        )
                        self._building_vp_texts.append(
                            arcade.Text(
                                f"{vp} VP",
                                tx, ty,
                                color=(180, 50, 50),
                                font_size=12,
                                bold=True,
                            ),
                        )
                self._building_vp_dirty = False
            for vt in self._building_vp_texts:
                vt.draw()
            for i, bld in enumerate(self._face_up_buildings):
                bcx = bld_positions[i][0]
                bid = bld.get("id", f"building_{i}")
                if bid in bhl:
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            bcx, bld_y,
                            _CARD_WIDTH,
                            _BUILDING_CARD_HEIGHT,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )
                self._space_rects[
                    f"building_card_{bid}"
                ] = (
                    bcx - bld_w / 2,
                    bld_y - _BUILDING_CARD_HEIGHT / 2,
                    bld_w,
                    _BUILDING_CARD_HEIGHT,
                )

        if self._constructed_sprite_list:
            self._constructed_sprite_list.draw()
            merch_top_y = (
                y + 0.91 * h + _SPACE_CARD_HEIGHT / 2
            )
            first_bld_cy = (
                merch_top_y - _BUILDING_CARD_HEIGHT / 2
            )
            bld_row_step = (_BUILDING_CARD_HEIGHT + 10) / h
            building_start_x = 0.22
            for i, space_id in enumerate(
                self.board_data.get(
                    "constructed_buildings", []
                )
            ):
                space_data = spaces.get(space_id, {})
                row = i % 5
                col = i // 5
                cx = x + (building_start_x + col * 0.14) * w
                cy = first_bld_cy - row * bld_row_step * h
                occupied = space_data.get("occupied_by")
                if occupied:
                    color = self._player_color(occupied)
                    arcade.draw_circle_filled(
                        cx + _CARD_WIDTH / 2 - 14, cy, 9,
                        color,
                    )

    def _rebuild_shapes(
        self, x: float, y: float, w: float, h: float,
    ) -> None:
        """Rebuild the batched shape list for all static rects."""
        self._shape_list.clear()
        self._space_rects.clear()

        spaces = self.board_data.get("action_spaces", {})

        # Background
        self._shape_list.append(
            arcade.shape_list.create_rectangle_filled(
                x + w / 2, y + h / 2, w, h,
                (30, 40, 50),
            )
        )

        # Permanent action spaces — build sprite list
        space_cards = []
        space_positions = []
        for space_id, (px, py) in _SPACE_LAYOUT.items():
            cx = x + px * w
            cy = y + py * h
            self._space_rects[space_id] = (
                cx - _CARD_WIDTH / 2,
                cy - _SPACE_CARD_HEIGHT / 2,
                _CARD_WIDTH,
                _SPACE_CARD_HEIGHT,
            )
            space_cards.append({"id": space_id})
            space_positions.append((cx, cy))
        self._space_sprite_list = _build_card_sprite_list(
            space_cards, "spaces", space_positions,
        )

        # Backstage slots — build sprite list
        # Align left edge with leftmost face-up quest card
        garage_cx = x + 0.54 * w
        n_q = max(
            len(self.board_data.get("face_up_quests", [])),
            4,
        )
        q_spacing = _CARD_WIDTH + 15
        bs_cx = (
            garage_cx
            - n_q * q_spacing / 2
            + _CARD_WIDTH / 2
        )
        backstage_cards = []
        backstage_positions = []
        for i, py in enumerate(_BACKSTAGE_Y):
            cy = y + py * h
            slot_num = i + 1
            sid = f"backstage_slot_{slot_num}"
            self._space_rects[sid] = (
                bs_cx - _CARD_WIDTH / 2,
                cy - _SPACE_CARD_HEIGHT / 2,
                _CARD_WIDTH,
                _SPACE_CARD_HEIGHT,
            )
            backstage_cards.append({"id": sid})
            backstage_positions.append((bs_cx, cy))
        self._backstage_sprite_list = _build_card_sprite_list(
            backstage_cards, "spaces", backstage_positions,
        )

        # Realtor — centered above face-up building cards
        quest_right = garage_cx + n_q * q_spacing / 2
        n_bld = max(len(self._face_up_buildings), 3)
        bld_spacing = _CARD_WIDTH + 15
        rightmost_bld_cx = quest_right - _CARD_WIDTH / 2
        bld_start_cx = rightmost_bld_cx - (n_bld - 1) * bld_spacing
        realtor_cx = (bld_start_cx + rightmost_bld_cx) / 2
        realtor_cy = y + 0.40 * h
        self._space_rects["realtor"] = (
            realtor_cx - _CARD_WIDTH / 2,
            realtor_cy - _SPACE_CARD_HEIGHT / 2,
            _CARD_WIDTH,
            _SPACE_CARD_HEIGHT,
        )
        self._realtor_sprite_list = _build_card_sprite_list(
            [{"id": "realtor"}], "spaces",
            [(realtor_cx, realtor_cy)],
        )

        # Constructed buildings — build sprite list
        # Align top of first building with top of The Merch Store
        merch_top_y = (
            y + 0.91 * h + _SPACE_CARD_HEIGHT / 2
        )
        first_building_cy = merch_top_y - _BUILDING_CARD_HEIGHT / 2
        building_start_x = 0.22
        building_row_step = (_BUILDING_CARD_HEIGHT + 10) / h
        constructed_cards = []
        constructed_positions = []
        for i, space_id in enumerate(
            self.board_data.get(
                "constructed_buildings", []
            )
        ):
            data = spaces.get(space_id, {})
            row = i % 5
            col = i // 5
            cx = x + (building_start_x + col * 0.14) * w
            cy = first_building_cy - row * building_row_step * h
            self._space_rects[space_id] = (
                cx - _CARD_WIDTH / 2,
                cy - _BUILDING_CARD_HEIGHT / 2,
                _CARD_WIDTH,
                _BUILDING_CARD_HEIGHT,
            )
            tile = data.get("building_tile", {})
            tile_id = tile.get("id", "") if tile else ""
            if tile_id:
                constructed_cards.append({"id": tile_id})
                constructed_positions.append((cx, cy))
        self._constructed_sprite_list = _build_card_sprite_list(
            constructed_cards, "buildings", constructed_positions,
        )

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
