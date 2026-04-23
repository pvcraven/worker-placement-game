"""Board layout and action space rendering."""

from __future__ import annotations

import logging
from pathlib import Path

import arcade
import arcade.shape_list

from shared.constants import (
    BUILDING_CARD_HEIGHT,
    CARD_HEIGHT,
    CARD_WIDTH,
    RESOURCE_SYMBOLS,
    SPACE_CARD_HEIGHT,
)

_RESOURCE_ABBREV = dict(RESOURCE_SYMBOLS)

_log = logging.getLogger(__name__)


_SPACE_LAYOUT: dict[str, tuple[float, float]] = {
    "merch_store": (0.08, 0.91),
    "motown": (0.08, 0.78),
    "guitar_center": (0.08, 0.65),
    "talent_show": (0.08, 0.52),
    "rhythm_pit": (0.08, 0.39),
    "fastpass": (0.08, 0.26),
    "sunset_records": (0.57, 0.92),
    "the_back_room": (0.71, 0.92),
    "the_garage": (0.85, 0.92),
}

_BACKSTAGE_Y = [0.46, 0.33, 0.20]

_PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.PURPLE,
]

_COLOR_NAMES = ["red", "blue", "green", "orange", "purple"]


def _build_card_sprite_list(
    cards: list[dict],
    card_type: str,
    positions: list[tuple[float, float]],
    scale: float = 1.0,
) -> arcade.SpriteList:
    sprite_list = arcade.SpriteList()
    for card, (cx, cy) in zip(cards, positions):
        card_id = card.get("id", "")
        png_path = Path(f"client/assets/card_images/{card_type}/{card_id}.png")
        if not png_path.exists():
            _log.warning("Card image not found: %s", png_path)
            continue
        sprite = arcade.Sprite(str(png_path))
        sprite.scale = scale
        sprite.position = (cx, cy)
        sprite_list.append(sprite)
    return sprite_list


class BoardRenderer:
    """Draws the game board with action spaces and worker tokens."""

    def __init__(self) -> None:
        self.board_data: dict = {}
        self.players: list[dict] = []
        self._space_rects: dict[str, tuple[float, float, float, float]] = {}
        self._building_spaces: list[dict] = []
        self._face_up_buildings: list[dict] = []
        self._deck_remaining: int = 0
        self._shape_list = arcade.shape_list.ShapeElementList()
        self._shapes_dirty = True
        self._last_draw_rect = (0.0, 0.0, 0.0, 0.0)
        self._last_scale = 1.0
        self._quest_sprite_list: arcade.SpriteList | None = None
        self._quest_positions: list[tuple[float, float]] = []
        self._quest_card_y: float = 0
        self._building_sprite_list: arcade.SpriteList | None = None
        self._bld_positions: list[tuple[float, float]] = []
        self._bld_card_y: float = 0
        self._constructed_sprite_list: arcade.SpriteList | None = None
        self._space_sprite_list: arcade.SpriteList | None = None
        self._backstage_sprite_list: arcade.SpriteList | None = None
        self._realtor_sprite_list: arcade.SpriteList | None = None
        self._building_vp_texts: list[arcade.Text] = []
        self._building_vp_dirty = True
        self._building_owner_texts: list[arcade.Text] = []
        self._building_owner_dirty = True
        self._building_accum_texts: list[arcade.Text] = []
        self._turn_order: list[str] = []
        self._current_player_id: str | None = None
        self._worker_sprite_list = arcade.SpriteList()
        self._worker_sprites: dict[str, arcade.Sprite] = {}
        self._worker_textures: dict[str, arcade.Texture] = {}
        self._workers_dirty = True

    def update_board(
        self,
        board: dict,
        players: list[dict],
        turn_order: list[str] | None = None,
        current_player_id: str | None = None,
    ) -> None:
        self.board_data = board
        self.players = players
        if turn_order is not None:
            self._turn_order = turn_order
        if current_player_id is not None:
            self._current_player_id = current_player_id
        self._shapes_dirty = True
        self._building_owner_dirty = True
        self._workers_dirty = True

    def update_building_market(
        self,
        face_up_buildings: list[dict],
        deck_remaining: int,
    ) -> None:
        self._face_up_buildings = face_up_buildings
        self._deck_remaining = deck_remaining
        self._building_vp_dirty = True
        self._shapes_dirty = True

    def draw(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        highlighted_ids: list[str] | None = None,
        scale: float = 1.0,
    ) -> None:
        """Draw the board in the given rectangle."""
        s = max(0.3, min(scale, 2.0))
        draw_rect = (x, y, w, h)
        if (
            self._shapes_dirty
            or draw_rect != self._last_draw_rect
            or s != self._last_scale
        ):
            self._rebuild_shapes(x, y, w, h, s)
            self._last_draw_rect = draw_rect
            self._last_scale = s
            self._shapes_dirty = False
            self._building_vp_dirty = True
            self._building_owner_dirty = True
            self._workers_dirty = True

        card_w = CARD_WIDTH * s
        card_h = CARD_HEIGHT * s
        bld_h = BUILDING_CARD_HEIGHT * s
        space_h = SPACE_CARD_HEIGHT * s
        font_sm = max(8, int(12 * s))

        self._shape_list.draw()

        if self._space_sprite_list:
            self._space_sprite_list.draw()

        if self._backstage_sprite_list:
            self._backstage_sprite_list.draw()

        face_up_quests = self.board_data.get("face_up_quests", [])
        if self._quest_sprite_list:
            self._quest_sprite_list.draw()
            hl = highlighted_ids or []
            for i, quest in enumerate(face_up_quests):
                if i >= len(self._quest_positions):
                    break
                qid = quest.get("id", f"quest_{i}")
                if qid in hl:
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            self._quest_positions[i][0],
                            self._quest_card_y,
                            card_w,
                            card_h,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )

        # Realtor space
        if self._realtor_sprite_list:
            self._realtor_sprite_list.draw()

        # Face-up building cards
        if self._building_sprite_list:
            self._building_sprite_list.draw()
            if self._building_vp_dirty:
                self._building_vp_texts = []
                for j, b in enumerate(self._face_up_buildings):
                    vp = b.get("accumulated_vp", 0)
                    if vp > 0 and j < len(self._bld_positions):
                        tx = self._bld_positions[j][0] - card_w / 2 + 8 * s
                        ty = self._bld_card_y - bld_h / 2 + 6 * s
                        self._building_vp_texts.append(
                            arcade.Text(
                                f"{vp} VP",
                                tx,
                                ty,
                                color=(180, 50, 50),
                                font_size=font_sm,
                                bold=True,
                            ),
                        )
                self._building_vp_dirty = False
            for vt in self._building_vp_texts:
                vt.draw()
            bhl = highlighted_ids or []
            for i, bld in enumerate(self._face_up_buildings):
                if i >= len(self._bld_positions):
                    break
                bid = bld.get("id", f"building_{i}")
                if bid in bhl:
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            self._bld_positions[i][0],
                            self._bld_card_y,
                            card_w,
                            bld_h,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )

        spaces = self.board_data.get("action_spaces", {})
        if self._constructed_sprite_list:
            self._constructed_sprite_list.draw()
            merch_top_y = y + 0.91 * h + space_h / 2
            first_bld_cy = merch_top_y - bld_h / 2
            bld_row_step = (bld_h + 10 * s) / h
            building_start_x = 0.22
            building_col_step = 0.14
            if self._building_owner_dirty:
                self._building_owner_texts = []
            for i, space_id in enumerate(
                self.board_data.get("constructed_buildings", [])
            ):
                space_data = spaces.get(space_id, {})
                col = i % 2
                row = i // 2
                cx = x + (building_start_x + col * building_col_step) * w
                cy = first_bld_cy - row * bld_row_step * h
                if self._building_owner_dirty:
                    owner_id = space_data.get("owner_id", "")
                    if owner_id:
                        owner_name = self._player_name(owner_id)
                        tx = cx - card_w / 2 + 8 * s
                        ty = cy - bld_h / 2 + 6 * s
                        self._building_owner_texts.append(
                            arcade.Text(
                                f"Owner: {owner_name}",
                                tx,
                                ty,
                                color=(180, 50, 50),
                                font_size=font_sm,
                                bold=True,
                            ),
                        )
            if self._building_owner_dirty:
                self._building_accum_texts = []
                for i, space_id in enumerate(
                    self.board_data.get("constructed_buildings", [])
                ):
                    space_data = spaces.get(space_id, {})
                    bt = space_data.get("building_tile", {})
                    stock = 0
                    if bt:
                        stock = bt.get("accumulated_stock", 0)
                    if stock > 0:
                        col = i % 2
                        row = i // 2
                        cx = x + (building_start_x + col * building_col_step) * w
                        cy = first_bld_cy - row * bld_row_step * h
                        tx = cx - card_w / 2 + 8 * s
                        ty = cy - bld_h / 2 + 20 * s
                        atype = bt.get("accumulation_type", "")
                        sym = _RESOURCE_ABBREV.get(atype, "")
                        if atype == "victory_points":
                            label = f"Stock: {stock} VP"
                        elif sym:
                            label = f"Stock: {stock}{sym}"
                        else:
                            label = f"Stock: {stock}"
                        self._building_accum_texts.append(
                            arcade.Text(
                                label,
                                tx,
                                ty,
                                color=(20, 60, 20),
                                font_size=font_sm,
                                bold=True,
                            ),
                        )
                self._building_owner_dirty = False
            for ot in self._building_owner_texts:
                ot.draw()
            for at in self._building_accum_texts:
                at.draw()

        if self._workers_dirty:
            self._update_workers(x, y, w, h, s)
        self._worker_sprite_list.draw()

    def _rebuild_shapes(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        scale: float = 1.0,
    ) -> None:
        """Rebuild the batched shape list for all static rects."""
        s = scale
        self._shape_list.clear()
        self._space_rects.clear()

        card_w = CARD_WIDTH * s
        card_h = CARD_HEIGHT * s
        bld_h = BUILDING_CARD_HEIGHT * s
        space_h = SPACE_CARD_HEIGHT * s

        spaces = self.board_data.get("action_spaces", {})

        # Background
        self._shape_list.append(
            arcade.shape_list.create_rectangle_filled(
                x + w / 2,
                y + h / 2,
                w,
                h,
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
                cx - card_w / 2,
                cy - space_h / 2,
                card_w,
                space_h,
            )
            space_cards.append({"id": space_id})
            space_positions.append((cx, cy))
        self._space_sprite_list = _build_card_sprite_list(
            space_cards,
            "spaces",
            space_positions,
            scale=s * 0.5,
        )

        # Backstage slots — build sprite list
        garage_cx = x + 0.71 * w
        n_q = max(
            len(self.board_data.get("face_up_quests", [])),
            4,
        )
        q_spacing = (CARD_WIDTH + 15) * s
        bs_cx = garage_cx - n_q * q_spacing / 2 + card_w / 2
        backstage_cards = []
        backstage_positions = []
        for i, py in enumerate(_BACKSTAGE_Y):
            cy = y + py * h
            slot_num = i + 1
            sid = f"backstage_slot_{slot_num}"
            self._space_rects[sid] = (
                bs_cx - card_w / 2,
                cy - space_h / 2,
                card_w,
                space_h,
            )
            backstage_cards.append({"id": sid})
            backstage_positions.append((bs_cx, cy))
        self._backstage_sprite_list = _build_card_sprite_list(
            backstage_cards,
            "spaces",
            backstage_positions,
            scale=s * 0.5,
        )

        # Realtor — centered above face-up building cards
        quest_right = garage_cx + n_q * q_spacing / 2
        n_bld = max(len(self._face_up_buildings), 3)
        bld_spacing = (CARD_WIDTH + 15) * s
        rightmost_bld_cx = quest_right - card_w / 2
        bld_start_cx = rightmost_bld_cx - (n_bld - 1) * bld_spacing
        realtor_cx = (bld_start_cx + rightmost_bld_cx) / 2
        realtor_cy = y + 0.40 * h
        self._space_rects["realtor"] = (
            realtor_cx - card_w / 2,
            realtor_cy - space_h / 2,
            card_w,
            space_h,
        )
        self._realtor_sprite_list = _build_card_sprite_list(
            [{"id": "realtor"}],
            "spaces",
            [(realtor_cx, realtor_cy)],
            scale=s * 0.5,
        )

        # Constructed buildings — two-column grid
        merch_top_y = y + 0.91 * h + space_h / 2
        first_building_cy = merch_top_y - bld_h / 2
        building_start_x = 0.22
        building_col_step = 0.14
        building_row_step = (bld_h + 10 * s) / h
        constructed_cards = []
        constructed_positions = []
        for i, space_id in enumerate(self.board_data.get("constructed_buildings", [])):
            data = spaces.get(space_id, {})
            col = i % 2
            row = i // 2
            cx = x + (building_start_x + col * building_col_step) * w
            cy = first_building_cy - row * building_row_step * h
            self._space_rects[space_id] = (
                cx - card_w / 2,
                cy - bld_h / 2,
                card_w,
                bld_h,
            )
            tile = data.get("building_tile", {})
            tile_id = tile.get("id", "") if tile else ""
            if tile_id:
                constructed_cards.append({"id": tile_id})
                constructed_positions.append((cx, cy))
        self._constructed_sprite_list = _build_card_sprite_list(
            constructed_cards,
            "buildings",
            constructed_positions,
            scale=s * 0.5,
        )

        # Face-up quests
        face_up_quests = self.board_data.get("face_up_quests", [])
        if face_up_quests:
            total_w = len(face_up_quests) * q_spacing
            q_start_x = garage_cx - total_w / 2 + card_w / 2
            self._quest_card_y = y + 0.68 * h
            self._quest_positions = [
                (q_start_x + i * q_spacing, self._quest_card_y)
                for i in range(len(face_up_quests))
            ]
            self._quest_sprite_list = _build_card_sprite_list(
                face_up_quests,
                "quests",
                self._quest_positions,
                scale=s * 0.5,
            )
            for i, quest in enumerate(face_up_quests):
                qid = quest.get("id", f"quest_{i}")
                cx = self._quest_positions[i][0]
                self._space_rects[f"quest_card_{qid}"] = (
                    cx - card_w / 2,
                    self._quest_card_y - card_h / 2,
                    card_w,
                    card_h,
                )
        else:
            self._quest_sprite_list = None
            self._quest_positions = []

        # Face-up building market
        if self._face_up_buildings:
            bld_spacing_v = (CARD_WIDTH + 15) * s
            n_bld = len(self._face_up_buildings)
            rightmost_cx = quest_right - card_w / 2
            bld_start_cx = rightmost_cx - (n_bld - 1) * bld_spacing_v
            self._bld_card_y = y + 0.20 * h
            self._bld_positions = [
                (bld_start_cx + i * bld_spacing_v, self._bld_card_y)
                for i in range(n_bld)
            ]
            self._building_sprite_list = _build_card_sprite_list(
                self._face_up_buildings,
                "buildings",
                self._bld_positions,
                scale=s * 0.5,
            )
            for i, bld in enumerate(self._face_up_buildings):
                bid = bld.get("id", f"building_{i}")
                bcx = self._bld_positions[i][0]
                self._space_rects[f"building_card_{bid}"] = (
                    bcx - card_w / 2,
                    self._bld_card_y - bld_h / 2,
                    card_w,
                    bld_h,
                )
        else:
            self._building_sprite_list = None
            self._bld_positions = []

    def _player_name(self, player_id: str) -> str:
        for p in self.players:
            if p.get("player_id") == player_id:
                return p.get("display_name", "???")
        return "???"

    def _player_color(self, player_id: str) -> tuple:
        for i, p in enumerate(self.players):
            if p.get("player_id") == player_id:
                return _PLAYER_COLORS[i % len(_PLAYER_COLORS)]
        return arcade.color.GRAY

    def _player_color_name(self, player_id: str) -> str:
        for i, p in enumerate(self.players):
            if p.get("player_id") == player_id:
                return _COLOR_NAMES[i % len(_COLOR_NAMES)]
        return "red"

    def _get_worker_texture(self, color_name: str) -> arcade.Texture:
        if color_name not in self._worker_textures:
            png = Path(f"client/assets/card_images/markers/worker_{color_name}.png")
            self._worker_textures[color_name] = arcade.load_texture(str(png))
        return self._worker_textures[color_name]

    def _update_workers(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        s: float,
    ) -> None:
        spaces = self.board_data.get("action_spaces", {})
        backstage_slots = self.board_data.get("backstage_slots", [])
        card_w = CARD_WIDTH * s
        bld_h = BUILDING_CARD_HEIGHT * s
        space_h = SPACE_CARD_HEIGHT * s
        token_offset = card_w / 2 - 10 * s
        token_size = max(10, int(18 * s))

        wanted: dict[str, tuple[str, float, float]] = {}

        for space_id, (px, py) in _SPACE_LAYOUT.items():
            cx = x + px * w
            cy = y + py * h
            occupied = spaces.get(space_id, {}).get("occupied_by")
            if occupied:
                color_name = self._player_color_name(occupied)
                wanted[space_id] = (color_name, cx + token_offset, cy)

        garage_cx = x + 0.71 * w
        n_q = max(len(self.board_data.get("face_up_quests", [])), 4)
        q_spacing = (CARD_WIDTH + 15) * s
        bs_cx = garage_cx - n_q * q_spacing / 2 + card_w / 2
        for i, py_val in enumerate(_BACKSTAGE_Y):
            cy = y + py_val * h
            slot_num = i + 1
            slot_data = {}
            for gs in backstage_slots:
                if gs.get("slot_number") == slot_num:
                    slot_data = gs
                    break
            occupied = slot_data.get("occupied_by")
            if occupied:
                key = f"backstage_{slot_num}"
                color_name = self._player_color_name(occupied)
                wanted[key] = (color_name, bs_cx + token_offset, cy)

        realtor_data = spaces.get("realtor", {})
        if realtor_data.get("occupied_by"):
            r_rect = self._space_rects.get("realtor")
            if r_rect:
                r_cx = r_rect[0] + r_rect[2] / 2
                r_cy = r_rect[1] + r_rect[3] / 2
                pid = realtor_data["occupied_by"]
                color_name = self._player_color_name(pid)
                wanted["realtor_worker"] = (
                    color_name,
                    r_cx + token_offset,
                    r_cy,
                )

        merch_top_y = y + 0.91 * h + space_h / 2
        first_bld_cy = merch_top_y - bld_h / 2
        bld_row_step = (bld_h + 10 * s) / h
        building_start_x = 0.22
        building_col_step = 0.14
        for i, space_id in enumerate(self.board_data.get("constructed_buildings", [])):
            occupied = spaces.get(space_id, {}).get("occupied_by")
            if occupied:
                col = i % 2
                row = i // 2
                cx = x + (building_start_x + col * building_col_step) * w
                cy = first_bld_cy - row * bld_row_step * h
                color_name = self._player_color_name(occupied)
                wanted[f"bld_{space_id}"] = (
                    color_name,
                    cx + card_w / 2 - 14 * s,
                    cy,
                )

        stale = set(self._worker_sprites) - set(wanted)
        for key in stale:
            sp = self._worker_sprites.pop(key)
            sp.remove_from_sprite_lists()

        for key, (color_name, wx, wy) in wanted.items():
            if key in self._worker_sprites:
                sp = self._worker_sprites[key]
                sp.position = (wx, wy)
                sp.scale = token_size / max(sp.texture.height, 1)
            else:
                tex = self._get_worker_texture(color_name)
                sp = arcade.Sprite(tex)
                sp.scale = token_size / max(tex.height, 1)
                sp.position = (wx, wy)
                self._worker_sprites[key] = sp
                self._worker_sprite_list.append(sp)

        self._workers_dirty = False

    def get_space_at(self, x: float, y: float) -> str | None:
        """Return the space_id at screen coordinates."""
        for space_id, (rx, ry, rw, rh) in self._space_rects.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return space_id
        return None
