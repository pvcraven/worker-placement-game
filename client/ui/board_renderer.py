"""Board layout and action space rendering."""

from __future__ import annotations

import logging
import math
from pathlib import Path

import arcade
import arcade.shape_list

from client.ui.board_grid import BoardGrid
from shared.constants import (
    BUILDING_CARD_HEIGHT,
    CARD_HEIGHT,
    CARD_WIDTH,
    RESOURCE_SYMBOLS,
    SPACE_CARD_HEIGHT,
)

_RESOURCE_ABBREV = dict(RESOURCE_SYMBOLS)

_ICONS_DIR = Path("client/assets/card_images/icons")
_RESOURCE_ICON_FILES = {
    "guitarists": "guitarist.png",
    "bass_players": "bass_player.png",
    "drummers": "drummer.png",
    "singers": "singer.png",
    "coins": "coin.png",
}

_log = logging.getLogger(__name__)

_GRID_PLACEMENT: dict[str, tuple[float, float, float, float]] = {
    # 3x3 permanent space grid
    "merch_store": (0, 0, 1, 1),
    "motown": (1, 0, 1, 1),
    "guitar_center": (2, 0, 1, 1),
    "talent_show": (0, 1, 1, 1),
    "rhythm_pit": (1, 1, 1, 1),
    "jam_session": (2, 1, 1, 1),
    "whisper_room": (0, 2, 1, 1),
    "vip_entrance": (1, 2, 1, 1),
    "the_green_room": (2, 2, 1, 1),
    # Garage spaces
    "sunset_records": (3.5, 0, 1, 1),
    "the_back_room": (4.5, 0, 1, 1),
    "the_garage": (5.5, 0, 1, 1),
    # Backstage slots
    "backstage_slot_1": (3, 4, 1, 1),
    "backstage_slot_2": (3, 5, 1, 1),
    "backstage_slot_3": (3, 6, 1, 1),
    # Realtor
    "realtor": (5, 4, 1, 1),
}

_PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.PURPLE,
    (255, 105, 180),  # pink
    (186, 147, 216),  # lilac
]

_COLOR_NAMES = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "pink",
    "lilac",
]

MARKER_COLOR_MAP: dict[str, tuple[int, ...]] = {
    "green": arcade.color.GREEN,
    "red": arcade.color.RED,
    "purple": arcade.color.PURPLE,
    "blue": arcade.color.BLUE,
    "pink": (255, 105, 180),
    "lilac": (186, 147, 216),
    "orange": arcade.color.ORANGE,
}

_BUILDINGS_PER_PAGE = 9


def _build_card_sprite_list(
    cards: list[dict],
    card_type: str,
    positions: list[tuple[float, float]],
    scale: float = 1.0,
) -> arcade.SpriteList:
    sprite_list = arcade.SpriteList()
    for card, (cx, cy) in zip(cards, positions):
        if card is None:
            continue
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
        self._grid: BoardGrid | None = None
        self._quest_sprite_list: arcade.SpriteList | None = None
        self._quest_positions: list[tuple[float, float]] = []
        self._quest_scale: float = 1.0
        self._building_sprite_list: arcade.SpriteList | None = None
        self._bld_positions: list[tuple[float, float]] = []
        self._constructed_sprite_list: arcade.SpriteList | None = None
        self._space_sprite_list: arcade.SpriteList | None = None
        self._backstage_sprite_list: arcade.SpriteList | None = None
        self._backstage_closed_sprite_list: arcade.SpriteList | None = None
        self._backstage_closed = False
        self._realtor_sprite_list: arcade.SpriteList | None = None
        self._building_vp_texts: list[arcade.Text] = []
        self._building_vp_dirty = True
        self._building_owner_texts: list[arcade.Text] = []
        self._building_owner_dirty = True
        self._building_accum_texts: list[arcade.Text] = []
        self._placed_resource_sprites = arcade.SpriteList()
        self._turn_order: list[str] = []
        self._current_player_id: str | None = None
        self._worker_sprite_list = arcade.SpriteList()
        self._worker_sprites: dict[str, arcade.Sprite] = {}
        self._worker_textures: dict[str, arcade.Texture] = {}
        self._workers_dirty = True
        self._star_overlay_list: arcade.SpriteList | None = None
        self._star_overlay_key: tuple = ()
        self._building_page: int = 0
        self._building_page_count: int = 1
        self._building_page_text: arcade.Text | None = None

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
        self._star_overlay_list = None

    def update_building_market(
        self,
        face_up_buildings: list[dict],
        deck_remaining: int,
    ) -> None:
        self._face_up_buildings = face_up_buildings
        self._deck_remaining = deck_remaining
        self._building_vp_dirty = True
        self._shapes_dirty = True

    def swap_backstage_cards(self, closed: bool) -> None:
        self._backstage_closed = closed

    def scroll_buildings(self, direction: int) -> None:
        new_page = self._building_page + direction
        if 0 <= new_page < self._building_page_count:
            self._building_page = new_page
            self._shapes_dirty = True
            self._building_owner_dirty = True
            self._workers_dirty = True

    def _grid_rect(
        self, col: float, row: float, col_span: float, row_span: float
    ) -> tuple[float, float, float, float]:
        """Get (cx, cy, w, h) from grid, converting to click-rect format for _space_rects."""
        assert self._grid is not None
        return self._grid.cell_rect(col, row, col_span, row_span)

    def _click_rect(
        self, cx: float, cy: float, cw: float, ch: float
    ) -> tuple[float, float, float, float]:
        """Convert center-based rect to (left, bottom, width, height) for click detection."""
        return (cx - cw / 2, cy - ch / 2, cw, ch)

    def draw(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        highlighted_ids: list[str] | None = None,
        scale: float = 1.0,
        bonus_genres: list[str] | None = None,
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
            self._star_overlay_list = None

        g = self._grid
        assert g is not None
        img_w = CARD_WIDTH * 2
        bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
        quest_scale = g.card_scale(2.5, CARD_WIDTH, CARD_HEIGHT)
        scaled_card_w = img_w * quest_scale
        scaled_card_h = CARD_HEIGHT * 2 * quest_scale
        scaled_bld_h = BUILDING_CARD_HEIGHT * 2 * bld_scale
        font_sm = max(8, int(12 * s))

        self._shape_list.draw()

        if self._space_sprite_list:
            self._space_sprite_list.draw()

        if self._backstage_closed and self._backstage_closed_sprite_list:
            self._backstage_closed_sprite_list.draw()
        elif self._backstage_sprite_list:
            self._backstage_sprite_list.draw()

        face_up_quests = self.board_data.get("face_up_quests", [])
        if self._quest_sprite_list:
            self._quest_sprite_list.draw()
            hl = highlighted_ids or []
            for i, quest in enumerate(face_up_quests):
                if i >= len(self._quest_positions):
                    break
                if quest is None:
                    continue
                qid = quest.get("id", f"quest_{i}")
                if qid in hl:
                    qx, qy = self._quest_positions[i]
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            qx,
                            qy,
                            scaled_card_w,
                            scaled_card_h,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )

        # Star overlay for genre-matching face-up quests
        star_png = Path("client/assets/card_images/icons/genre_match_star.png")
        if (
            bonus_genres
            and face_up_quests
            and self._quest_positions
            and star_png.exists()
        ):
            star_key = (
                tuple(q.get("id", "") if q else "" for q in face_up_quests),
                tuple(bonus_genres),
            )
            if self._star_overlay_list is None or self._star_overlay_key != star_key:
                self._star_overlay_key = star_key
                self._star_overlay_list = arcade.SpriteList()
                star_size = scaled_card_w * 0.15
                for i, quest in enumerate(face_up_quests):
                    if i >= len(self._quest_positions):
                        break
                    if quest is None:
                        continue
                    genre = quest.get("genre", "")
                    if genre not in bonus_genres:
                        continue
                    star = arcade.Sprite(str(star_png))
                    star.scale = star_size / star.texture.width
                    qx, qy = self._quest_positions[i]
                    star.position = (
                        qx - scaled_card_w / 2 + star_size / 2 + 2 * s,
                        qy + scaled_card_h / 2 - star_size * 0.5,
                    )
                    self._star_overlay_list.append(star)
            if self._star_overlay_list:
                self._star_overlay_list.draw()
        else:
            self._star_overlay_list = None
            self._star_overlay_key = ()

        # Realtor space
        if self._realtor_sprite_list:
            self._realtor_sprite_list.draw()

        # Face-up building cards
        if self._building_sprite_list:
            self._building_sprite_list.draw()
            if self._building_vp_dirty:
                self._building_vp_texts = []
                scaled_bld_w = img_w * bld_scale
                for j, b in enumerate(self._face_up_buildings):
                    vp = b.get("accumulated_vp", 0)
                    if vp > 0 and j < len(self._bld_positions):
                        bx, by = self._bld_positions[j]
                        tx = bx - scaled_bld_w / 2 + 8 * s
                        ty = by - scaled_bld_h / 2 + 6 * s
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
                    bx, by = self._bld_positions[i]
                    arcade.draw_rect_outline(
                        arcade.rect.XYWH(
                            bx,
                            by,
                            img_w * bld_scale,
                            scaled_bld_h,
                        ),
                        arcade.color.YELLOW,
                        border_width=2,
                    )

        spaces = self.board_data.get("action_spaces", {})
        if self._constructed_sprite_list:
            self._constructed_sprite_list.draw()
            con_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
            con_cw = img_w * con_scale
            con_ch = BUILDING_CARD_HEIGHT * 2 * con_scale

            all_constructed = self.board_data.get("constructed_buildings", [])
            bld_start = self._building_page * _BUILDINGS_PER_PAGE
            bld_end = min(bld_start + _BUILDINGS_PER_PAGE, len(all_constructed))
            page_buildings = all_constructed[bld_start:bld_end]

            if self._building_owner_dirty:
                self._building_owner_texts = []
            for j, space_id in enumerate(page_buildings):
                space_data = spaces.get(space_id, {})
                col = j % 3
                row = 3 + (j // 3) * 2
                cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
                if self._building_owner_dirty:
                    owner_id = space_data.get("owner_id", "")
                    if owner_id:
                        owner_name = self._player_name(owner_id)
                        tx = cx - con_cw / 2 + 8 * s
                        ty = cy - con_ch / 2 + 6 * s
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
                for j, space_id in enumerate(page_buildings):
                    space_data = spaces.get(space_id, {})
                    bt = space_data.get("building_tile", {})
                    stock = 0
                    if bt:
                        stock = bt.get("accumulated_stock", 0)
                    if stock > 0:
                        col = j % 3
                        row = 3 + (j // 3) * 2
                        cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
                        tx = cx - con_cw / 2 + 8 * s
                        ty = cy - con_ch / 2 + 20 * s
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
                self._placed_resource_sprites = arcade.SpriteList()
                icon_sz = int(12 * s)
                icon_gap = int(2 * s)

                for j, space_id in enumerate(page_buildings):
                    space_data = spaces.get(space_id, {})
                    placed = space_data.get("placed_resources", {})
                    if placed:
                        col = j % 3
                        row = 3 + (j // 3) * 2
                        cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
                        bx = cx - con_cw / 2 + 8 * s + icon_sz / 2
                        by = cy - con_ch / 2 + 34 * s + icon_sz / 2
                        self._add_placed_icons(
                            placed, bx, by, icon_sz, icon_gap,
                        )
                for space_id, (col, row, cs, rs) in _GRID_PLACEMENT.items():
                    if space_id.startswith("backstage_slot_") or space_id == "realtor":
                        continue
                    placed = spaces.get(space_id, {}).get("placed_resources", {})
                    if placed:
                        cx, cy, _, _ = g.cell_rect(col, row, cs, rs)
                        space_scale = g.card_scale(1, CARD_WIDTH, SPACE_CARD_HEIGHT)
                        sp_cw = CARD_WIDTH * 2 * space_scale
                        sp_ch = SPACE_CARD_HEIGHT * 2 * space_scale
                        bx = cx - sp_cw / 2 + 4 * s + icon_sz / 2
                        by = cy - sp_ch / 2 + 4 * s + icon_sz / 2
                        self._add_placed_icons(
                            placed, bx, by, icon_sz, icon_gap,
                        )

                self._building_owner_dirty = False

                # Page indicator
                if self._building_page_count > 1:
                    pg_label = f"{self._building_page + 1}/{self._building_page_count}"
                    pg_cx, pg_cy, _, _ = g.cell_rect(1, 7.5, 1, 1)
                    self._building_page_text = arcade.Text(
                        pg_label,
                        pg_cx,
                        pg_cy,
                        color=arcade.color.LIGHT_GRAY,
                        font_size=font_sm,
                        bold=True,
                        anchor_x="center",
                        anchor_y="center",
                    )
                else:
                    self._building_page_text = None

            for ot in self._building_owner_texts:
                ot.draw()
            for at in self._building_accum_texts:
                at.draw()
            self._placed_resource_sprites.draw()
            if self._building_page_text:
                self._building_page_text.draw()

        if self._workers_dirty:
            self._update_workers(s)
        self._worker_sprite_list.draw()

    def _add_placed_icons(
        self,
        placed: dict,
        start_x: float,
        start_y: float,
        icon_sz: int,
        gap: int,
    ) -> None:
        """Add resource icon sprites for placed_resources on a space."""
        ix = start_x
        for rtype, qty in placed.items():
            png_name = _RESOURCE_ICON_FILES.get(rtype)
            if not png_name:
                continue
            png_path = _ICONS_DIR / png_name
            if not png_path.exists():
                continue
            for _ in range(qty):
                sprite = arcade.Sprite(str(png_path))
                sprite.scale = icon_sz / sprite.texture.width
                sprite.position = (ix, start_y)
                self._placed_resource_sprites.append(sprite)
                ix += icon_sz + gap

    def _rebuild_shapes(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        _scale: float = 1.0,
    ) -> None:
        """Rebuild the batched shape list for all static rects."""
        self._shape_list.clear()
        self._space_rects.clear()

        g = BoardGrid(x, y, w, h)
        self._grid = g

        space_scale = g.card_scale(1, CARD_WIDTH, SPACE_CARD_HEIGHT)
        bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
        quest_scale = g.card_scale(2.5, CARD_WIDTH, CARD_HEIGHT)
        self._quest_scale = quest_scale

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

        # Permanent action spaces + backstage + realtor — from grid placement
        space_cards = []
        space_positions = []
        backstage_cards = []
        backstage_positions = []

        img_w = CARD_WIDTH * 2
        for space_id, (col, row, cs, rs) in _GRID_PLACEMENT.items():
            cx, cy, _, _ = g.cell_rect(col, row, cs, rs)
            scaled_w = img_w * space_scale
            scaled_h = SPACE_CARD_HEIGHT * 2 * space_scale
            self._space_rects[space_id] = self._click_rect(cx, cy, scaled_w, scaled_h)

            if space_id.startswith("backstage_slot_"):
                backstage_cards.append({"id": space_id})
                backstage_positions.append((cx, cy))
            elif space_id == "realtor":
                pass  # handled separately for sprite list
            else:
                space_cards.append({"id": space_id})
                space_positions.append((cx, cy))

        self._space_sprite_list = _build_card_sprite_list(
            space_cards,
            "spaces",
            space_positions,
            scale=space_scale,
        )
        self._backstage_sprite_list = _build_card_sprite_list(
            backstage_cards,
            "spaces",
            backstage_positions,
            scale=space_scale,
        )
        closed_cards = [{"id": f"{c['id']}_closed"} for c in backstage_cards]
        self._backstage_closed_sprite_list = _build_card_sprite_list(
            closed_cards,
            "spaces",
            backstage_positions,
            scale=space_scale,
        )

        # Realtor sprite
        r_col, r_row, r_cs, r_rs = _GRID_PLACEMENT["realtor"]
        r_cx, r_cy, _, _ = g.cell_rect(r_col, r_row, r_cs, r_rs)
        self._realtor_sprite_list = _build_card_sprite_list(
            [{"id": "realtor"}],
            "spaces",
            [(r_cx, r_cy)],
            scale=space_scale,
        )

        # Constructed buildings — columns 0-2, below 3x3 grid, paginated
        all_constructed = self.board_data.get("constructed_buildings", [])
        self._building_page_count = max(
            1, math.ceil(len(all_constructed) / _BUILDINGS_PER_PAGE)
        )
        if self._building_page >= self._building_page_count:
            self._building_page = self._building_page_count - 1
        start = self._building_page * _BUILDINGS_PER_PAGE
        end = min(start + _BUILDINGS_PER_PAGE, len(all_constructed))
        page_buildings = all_constructed[start:end]

        constructed_cards = []
        constructed_positions = []
        for j, space_id in enumerate(page_buildings):
            data = spaces.get(space_id, {})
            col = j % 3
            row = 3 + (j // 3) * 2
            cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
            scaled_w = img_w * bld_scale
            scaled_h = BUILDING_CARD_HEIGHT * 2 * bld_scale
            self._space_rects[space_id] = self._click_rect(cx, cy, scaled_w, scaled_h)
            tile = data.get("building_tile", {})
            tile_id = tile.get("id", "") if tile else ""
            if tile_id:
                constructed_cards.append({"id": tile_id})
                constructed_positions.append((cx, cy))
        self._constructed_sprite_list = _build_card_sprite_list(
            constructed_cards,
            "buildings",
            constructed_positions,
            scale=bld_scale,
        )

        # Face-up quests — 2 columns (4, 5), 2 rows of 3-high cards
        face_up_quests = self.board_data.get("face_up_quests", [])
        if face_up_quests:
            quest_grid = [(3, 1), (4, 1), (5, 1), (6, 1)]
            self._quest_positions = []
            for i in range(min(len(face_up_quests), len(quest_grid))):
                qc, qr = quest_grid[i]
                cx, cy, _, _ = g.cell_rect(qc, qr, 1, 2.5)
                self._quest_positions.append((cx, cy))
            self._quest_sprite_list = _build_card_sprite_list(
                face_up_quests[: len(self._quest_positions)],
                "quests",
                self._quest_positions,
                scale=quest_scale,
            )
            scaled_q_w = img_w * quest_scale
            scaled_q_h = CARD_HEIGHT * 2 * quest_scale
            for i, quest in enumerate(face_up_quests):
                if i >= len(self._quest_positions):
                    break
                if quest is None:
                    continue
                qid = quest.get("id", f"quest_{i}")
                qx, qy = self._quest_positions[i]
                self._space_rects[f"quest_card_{qid}"] = self._click_rect(
                    qx, qy, scaled_q_w, scaled_q_h
                )
        else:
            self._quest_sprite_list = None
            self._quest_positions = []

        # Face-up building market — columns 4-6, row 5.5, 1.5 rows each
        if self._face_up_buildings:
            self._bld_positions = []
            for i in range(len(self._face_up_buildings)):
                bc = 4 + i
                cx, cy, _, _ = g.cell_rect(bc, 5.5, 1, 2)
                self._bld_positions.append((cx, cy))
            self._building_sprite_list = _build_card_sprite_list(
                self._face_up_buildings,
                "buildings",
                self._bld_positions,
                scale=bld_scale,
            )
            scaled_b_w = img_w * bld_scale
            scaled_b_h = BUILDING_CARD_HEIGHT * 2 * bld_scale
            for i, bld in enumerate(self._face_up_buildings):
                bid = bld.get("id", f"building_{i}")
                bx, by = self._bld_positions[i]
                self._space_rects[f"building_card_{bid}"] = self._click_rect(
                    bx, by, scaled_b_w, scaled_b_h
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
                mc = p.get("marker_color")
                if mc and mc in MARKER_COLOR_MAP:
                    return MARKER_COLOR_MAP[mc]
                return _PLAYER_COLORS[i % len(_PLAYER_COLORS)]
        return arcade.color.GRAY

    def _player_color_name(self, player_id: str) -> str:
        for i, p in enumerate(self.players):
            if p.get("player_id") == player_id:
                mc = p.get("marker_color")
                if mc:
                    return mc
                return _COLOR_NAMES[i % len(_COLOR_NAMES)]
        return "red"

    def _get_worker_texture(self, color_name: str) -> arcade.Texture:
        if color_name not in self._worker_textures:
            png = Path(f"client/assets/card_images/markers/worker_{color_name}.png")
            self._worker_textures[color_name] = arcade.load_texture(str(png))
        return self._worker_textures[color_name]

    def _update_workers(self, s: float) -> None:
        g = self._grid
        assert g is not None
        spaces = self.board_data.get("action_spaces", {})
        backstage_slots = self.board_data.get("backstage_slots", [])
        space_scale = g.card_scale(1, CARD_WIDTH, SPACE_CARD_HEIGHT)
        token_offset = CARD_WIDTH * 2 * space_scale / 2 - 10 * s
        token_size = max(10, int(18 * s))

        wanted: dict[str, tuple[str, float, float]] = {}

        # Permanent action spaces + top-row spaces
        for space_id, (col, row, cs, rs) in _GRID_PLACEMENT.items():
            if space_id.startswith("backstage_slot_") or space_id == "realtor":
                continue
            cx, cy, _, _ = g.cell_rect(col, row, cs, rs)
            occupied = spaces.get(space_id, {}).get("occupied_by")
            if occupied:
                color_name = self._player_color_name(occupied)
                wanted[space_id] = (color_name, cx + token_offset, cy)

        # Backstage slots
        for space_id, (col, row, cs, rs) in _GRID_PLACEMENT.items():
            if not space_id.startswith("backstage_slot_"):
                continue
            cx, cy, _, _ = g.cell_rect(col, row, cs, rs)
            slot_num = int(space_id.split("_")[-1])
            slot_data = {}
            for gs in backstage_slots:
                if gs.get("slot_number") == slot_num:
                    slot_data = gs
                    break
            occupied = slot_data.get("occupied_by")
            if occupied:
                key = f"backstage_{slot_num}"
                color_name = self._player_color_name(occupied)
                wanted[key] = (color_name, cx + token_offset, cy)

        # Realtor
        realtor_data = spaces.get("realtor", {})
        if realtor_data.get("occupied_by"):
            r_col, r_row, r_cs, r_rs = _GRID_PLACEMENT["realtor"]
            r_cx, r_cy, _, _ = g.cell_rect(r_col, r_row, r_cs, r_rs)
            pid = realtor_data["occupied_by"]
            color_name = self._player_color_name(pid)
            wanted["realtor_worker"] = (color_name, r_cx + token_offset, r_cy)

        # Constructed buildings (current page only)
        bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
        bld_cw = CARD_WIDTH * 2 * bld_scale
        all_constructed = self.board_data.get("constructed_buildings", [])
        bld_start = self._building_page * _BUILDINGS_PER_PAGE
        bld_end = min(bld_start + _BUILDINGS_PER_PAGE, len(all_constructed))
        for j, space_id in enumerate(all_constructed[bld_start:bld_end]):
            occupied = spaces.get(space_id, {}).get("occupied_by")
            if occupied:
                col = j % 3
                row = 3 + (j // 3) * 2
                cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
                color_name = self._player_color_name(occupied)
                wanted[f"bld_{space_id}"] = (
                    color_name,
                    cx + bld_cw / 2 - 14 * s,
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

    def get_space_position(self, space_id: str) -> tuple[float, float] | None:
        """Return pixel coordinates for an action space, backstage slot, or constructed building."""
        g = self._grid
        if g is None:
            return None

        s = self._last_scale
        space_scale = g.card_scale(1, CARD_WIDTH, SPACE_CARD_HEIGHT)
        token_offset = CARD_WIDTH * 2 * space_scale / 2 - 10 * s

        if space_id in _GRID_PLACEMENT:
            col, row, cs, rs = _GRID_PLACEMENT[space_id]
            cx, cy, _, _ = g.cell_rect(col, row, cs, rs)
            return (cx + token_offset, cy)

        all_constructed = self.board_data.get("constructed_buildings", [])
        if space_id in all_constructed:
            bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
            bld_cw = CARD_WIDTH * 2 * bld_scale
            j = all_constructed.index(space_id)
            col = j % 3
            row = 3 + (j // 3) * 2
            cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
            return (cx + bld_cw / 2 - 14 * s, cy)

        return None

    def get_quest_card_info(self, card_id: str) -> tuple[float, float, float] | None:
        """Return (x, y, scale) for a face-up quest card, or None."""
        face_up = self.board_data.get("face_up_quests", [])
        for i, quest in enumerate(face_up):
            if quest is None:
                continue
            if quest.get("id") == card_id and i < len(self._quest_positions):
                x, y = self._quest_positions[i]
                return (x, y, self._quest_scale)
        return None

    def get_building_card_info(
        self, building_id: str
    ) -> tuple[float, float, float] | None:
        """Return (x, y, scale) for a face-up building card, or None."""
        g = self._grid
        if g is None:
            return None
        bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
        for i, bld in enumerate(self._face_up_buildings):
            if bld is None:
                continue
            if bld.get("id") == building_id and i < len(self._bld_positions):
                x, y = self._bld_positions[i]
                return (x, y, bld_scale)
        return None

    def get_building_lot_position(
        self, lot_index: int
    ) -> tuple[float, float, float] | None:
        """Return (x, y, scale) for a constructed building lot.

        lot_index is the raw lot number from the server. We convert
        it to a sequential position based on how many buildings are
        already constructed on the current page.
        """
        g = self._grid
        if g is None:
            return None
        all_constructed = self.board_data.get("constructed_buildings", [])
        seq = len(all_constructed)
        bld_scale = g.card_scale(2, CARD_WIDTH, BUILDING_CARD_HEIGHT)
        col = seq % 3
        row = 3 + (seq // 3) * 2
        cx, cy, _, _ = g.cell_rect(col, row, 1, 1.75)
        return (cx, cy, bld_scale)
