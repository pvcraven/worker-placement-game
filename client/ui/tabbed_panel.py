"""Tabbed right-side panel: Game Log, Quests, Intrigue, Completed Quests, Producer."""

from __future__ import annotations

import math
from pathlib import Path

import arcade
import arcade.shape_list

from client.ui.game_log import GameLogPanel

_TAB_DEFS = [
    ("game_log", "Game Log"),
    ("my_quests", "Quests"),
    ("my_intrigue", "Intrigue"),
    ("completed_quests", "Completed"),
    ("producer", "Producer"),
]

_CARD_BASE_WIDTH = 200
_CARD_BASE_HEIGHT = 260
_CARDS_PER_PAGE = 6
_CARD_SHRINK = 0.95

_ACTIVE_COLOR = (60, 60, 80)
_INACTIVE_COLOR = (30, 30, 40)
_BG_COLOR = (20, 20, 30)
_SUB_ACTIVE_COLOR = (50, 50, 70)
_SUB_INACTIVE_COLOR = (35, 35, 50)

_STAR_PNG = Path("client/assets/card_images/icons/genre_match_star.png")


class TabbedPanel:
    """Right-side panel with selectable tab views."""

    def __init__(self) -> None:
        self.active_tab: str = "game_log"
        self.game_log = GameLogPanel()
        self._tab_rects: dict[str, tuple[float, float, float, float]] = {}
        self._tab_shape_list: arcade.shape_list.ShapeElementList | None = None
        self._tab_texts: list[arcade.Text] = []
        self._title_text: arcade.Text | None = None
        self._page_text: arcade.Text | None = None
        self._empty_text: arcade.Text | None = None
        self._content_sprite_list: arcade.SpriteList | None = None
        self._content_card_key: tuple = ()
        self._producer_sprite_list: arcade.SpriteList | None = None
        self._producer_card_id: str = ""
        self._last_rect = (0.0, 0.0, 0.0, 0.0)
        self._last_scale = 0.0
        self._last_tab = ""
        self._shapes_dirty = True
        self._card_page: int = 0
        self._card_page_count: int = 1
        # Sub-tabs (within the Quests tab)
        self._active_sub_tab: str = "my_quests"
        self._sub_tab_rects: dict[str, tuple[float, float, float, float]] = {}
        self._sub_tab_shape_list: arcade.shape_list.ShapeElementList | None = None
        self._sub_tab_texts: list[arcade.Text] = []
        self._sub_tabs_dirty: bool = True
        self._last_sub_tab: str = ""
        # Star overlay
        self._star_sprite_list: arcade.SpriteList | None = None
        self._star_card_key: tuple = ()

    def add_entry(self, text: str) -> None:
        self.game_log.add_entry(text)

    def scroll(self, direction: int) -> None:
        self.game_log.scroll(direction)

    def scroll_cards(self, direction: int) -> None:
        new_page = self._card_page + direction
        if 0 <= new_page < self._card_page_count:
            self._card_page = new_page
            self._content_sprite_list = None
            self._star_sprite_list = None
            self._shapes_dirty = True

    def _update_page_count(
        self, player_data: dict | None, game_state: dict | None
    ) -> None:
        if self.active_tab == "my_quests":
            if self._active_sub_tab == "my_quests":
                cards = player_data.get("contract_hand", []) if player_data else []
            else:
                opp = self._find_player(game_state, self._active_sub_tab)
                if opp:
                    cards = opp.get("contract_hand", []) + opp.get(
                        "completed_contracts", []
                    )
                else:
                    cards = []
        elif self.active_tab == "my_intrigue":
            cards = player_data.get("intrigue_hand", []) if player_data else []
        elif self.active_tab == "completed_quests":
            cards = player_data.get("completed_contracts", []) if player_data else []
        else:
            self._card_page_count = 1
            return
        old_count = self._card_page_count
        self._card_page_count = max(1, math.ceil(len(cards) / _CARDS_PER_PAGE))
        if self._card_page >= self._card_page_count:
            self._card_page = self._card_page_count - 1
        if self._card_page_count != old_count:
            self._shapes_dirty = True

    def on_click(self, x: float, y: float) -> bool:
        for tab_id, (rx, ry, rw, rh) in self._tab_rects.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                if self.active_tab != tab_id:
                    self.active_tab = tab_id
                    self._shapes_dirty = True
                    self._card_page = 0
                    self._active_sub_tab = "my_quests"
                    self._sub_tabs_dirty = True
                return True
        if self.active_tab == "my_quests":
            for sub_id, (rx, ry, rw, rh) in self._sub_tab_rects.items():
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    if self._active_sub_tab != sub_id:
                        self._active_sub_tab = sub_id
                        self._sub_tabs_dirty = True
                        self._content_sprite_list = None
                        self._star_sprite_list = None
                        self._card_page = 0
                    return True
        return False

    def draw(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        player_data: dict | None = None,
        scale: float = 1.0,
        game_state: dict | None = None,
    ) -> None:
        s = scale
        rect = (x, y, w, h)
        if (
            rect != self._last_rect
            or s != self._last_scale
            or self.active_tab != self._last_tab
            or self._active_sub_tab != self._last_sub_tab
        ):
            self._shapes_dirty = True
            self._content_sprite_list = None
            self._producer_sprite_list = None
            self._star_sprite_list = None
            self._sub_tabs_dirty = True

        tab_bar_h = max(28, int(36 * s))
        title_h = max(20, int(28 * s))
        sub_tab_h = 0
        if self.active_tab == "my_quests":
            sub_tab_h = max(22, int(28 * s))
        content_y = y
        content_h = h - tab_bar_h - title_h - sub_tab_h

        self._update_page_count(player_data, game_state)

        if self._shapes_dirty:
            self._rebuild_tab_bar(x, y, w, h, tab_bar_h, s)
            self._rebuild_title(x, y + h - tab_bar_h, w, title_h, s)
            if self.active_tab == "my_quests" and game_state:
                sub_tab_top = y + h - tab_bar_h - title_h
                self._rebuild_sub_tabs(
                    x, sub_tab_top, w, sub_tab_h, s, game_state, player_data
                )
            else:
                self._sub_tab_shape_list = None
                self._sub_tab_texts = []
                self._sub_tab_rects = {}
            self._last_rect = rect
            self._last_scale = s
            self._last_tab = self.active_tab
            self._last_sub_tab = self._active_sub_tab
            self._shapes_dirty = False

        # Background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            _BG_COLOR,
        )

        # Tab bar shapes and text
        if self._tab_shape_list:
            self._tab_shape_list.draw()
        for tt in self._tab_texts:
            tt.draw()

        # Title
        if self._title_text:
            self._title_text.draw()
        if self._page_text:
            self._page_text.draw()

        # Sub-tab bar (Quests tab only)
        if self._sub_tab_shape_list:
            self._sub_tab_shape_list.draw()
        for st in self._sub_tab_texts:
            st.draw()

        # Content
        if self.active_tab == "game_log":
            self.game_log.draw(x, content_y, w, content_h, scale=s, show_title=False)
        elif self.active_tab == "my_quests":
            self._draw_quests_tab(
                x, content_y, w, content_h, player_data, s, game_state
            )
        elif self.active_tab in ("my_intrigue", "completed_quests"):
            self._draw_card_tab(x, content_y, w, content_h, player_data, s)
        elif self.active_tab == "producer":
            self._draw_producer_tab(x, content_y, w, content_h, player_data, s)

    def _rebuild_tab_bar(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        tab_bar_h: float,
        scale: float,
    ) -> None:
        s = scale
        self._tab_shape_list = arcade.shape_list.ShapeElementList()
        self._tab_texts = []
        self._tab_rects = {}

        n = len(_TAB_DEFS)
        tab_w = w / n
        bar_top = y + h
        bar_bot = bar_top - tab_bar_h
        font_sz = max(9, int(13 * s))

        for i, (tab_id, label) in enumerate(_TAB_DEFS):
            tx = x + i * tab_w
            is_active = tab_id == self.active_tab
            color = _ACTIVE_COLOR if is_active else _INACTIVE_COLOR

            rect = arcade.shape_list.create_rectangle_filled(
                tx + tab_w / 2,
                bar_bot + tab_bar_h / 2,
                tab_w - 2,
                tab_bar_h - 2,
                color,
            )
            self._tab_shape_list.append(rect)
            self._tab_rects[tab_id] = (tx, bar_bot, tab_w, tab_bar_h)

            text_color = arcade.color.WHITE if is_active else arcade.color.GRAY
            tt = arcade.Text(
                label,
                tx + tab_w / 2,
                bar_bot + tab_bar_h / 2,
                text_color,
                font_size=font_sz,
                font_name="Tahoma",
                anchor_x="center",
                anchor_y="center",
                bold=is_active,
            )
            self._tab_texts.append(tt)

    def _rebuild_title(
        self,
        x: float,
        title_y: float,
        w: float,
        title_h: float,
        scale: float,
    ) -> None:
        label = ""
        for tab_id, tab_label in _TAB_DEFS:
            if tab_id == self.active_tab:
                label = tab_label
                break
        font_sz = max(8, int(16 * scale))
        self._title_text = arcade.Text(
            label,
            x + w / 2,
            title_y - title_h / 2,
            arcade.color.WHITE,
            font_size=font_sz,
            font_name="Tahoma",
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        # Page indicator (shown for card tabs with multiple pages)
        if self._card_page_count > 1 and self.active_tab in (
            "my_quests",
            "my_intrigue",
            "completed_quests",
        ):
            page_label = f"{self._card_page + 1}/{self._card_page_count}"
            page_font_sz = max(7, int(12 * scale))
            self._page_text = arcade.Text(
                page_label,
                x + 8 * scale,
                title_y - title_h / 2,
                (180, 180, 200),
                font_size=page_font_sz,
                font_name="Tahoma",
                anchor_x="left",
                anchor_y="center",
            )
        else:
            self._page_text = None

    def _rebuild_sub_tabs(
        self,
        x: float,
        top_y: float,
        w: float,
        sub_h: float,
        scale: float,
        game_state: dict,
        player_data: dict | None,
    ) -> None:
        self._sub_tab_shape_list = arcade.shape_list.ShapeElementList()
        self._sub_tab_texts = []
        self._sub_tab_rects = {}

        my_id = player_data.get("player_id", "") if player_data else ""
        entries: list[tuple[str, str]] = [("my_quests", "My Quests")]
        for p in game_state.get("players", []):
            pid = p.get("player_id", "")
            if pid and pid != my_id:
                name = p.get("display_name", pid)
                if len(name) > 10:
                    name = name[:9] + "…"
                entries.append((pid, name))

        n = len(entries)
        if n < 2:
            return
        tab_w = w / n
        bar_bot = top_y - sub_h
        font_sz = max(7, int(11 * scale))

        for i, (sub_id, label) in enumerate(entries):
            tx = x + i * tab_w
            is_active = sub_id == self._active_sub_tab
            color = _SUB_ACTIVE_COLOR if is_active else _SUB_INACTIVE_COLOR

            rect = arcade.shape_list.create_rectangle_filled(
                tx + tab_w / 2,
                bar_bot + sub_h / 2,
                tab_w - 2,
                sub_h - 2,
                color,
            )
            self._sub_tab_shape_list.append(rect)
            self._sub_tab_rects[sub_id] = (tx, bar_bot, tab_w, sub_h)

            text_color = arcade.color.WHITE if is_active else (160, 160, 160)
            tt = arcade.Text(
                label,
                tx + tab_w / 2,
                bar_bot + sub_h / 2,
                text_color,
                font_size=font_sz,
                font_name="Tahoma",
                anchor_x="center",
                anchor_y="center",
                bold=is_active,
            )
            self._sub_tab_texts.append(tt)
        self._sub_tabs_dirty = False

    def _draw_quests_tab(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        player_data: dict | None,
        scale: float,
        game_state: dict | None,
    ) -> None:
        if self._active_sub_tab == "my_quests":
            self._draw_card_tab(x, y, w, h, player_data, scale)
        else:
            opponent = self._find_player(game_state, self._active_sub_tab)
            if not opponent:
                self._draw_empty(x, y, w, h, scale, "Player not found")
                return
            self._draw_opponent_quests(x, y, w, h, opponent, scale)

    def _find_player(self, game_state: dict | None, player_id: str) -> dict | None:
        if not game_state:
            return None
        for p in game_state.get("players", []):
            if p.get("player_id") == player_id:
                return p
        return None

    def _draw_opponent_quests(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        opponent: dict,
        scale: float,
    ) -> None:
        uncompleted = opponent.get("contract_hand", [])
        completed = opponent.get("completed_contracts", [])
        all_cards = uncompleted + completed
        if not all_cards:
            self._draw_empty(x, y, w, h, scale, "No quests")
            return
        self._draw_card_grid(
            x,
            y,
            w,
            h,
            all_cards,
            "quests",
            scale,
            separator_after=len(uncompleted) if completed else -1,
        )

    def _draw_card_tab(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        player_data: dict | None,
        scale: float,
    ) -> None:
        if not player_data:
            self._draw_empty(x, y, w, h, scale)
            return

        if self.active_tab in ("my_quests",):
            cards = player_data.get("contract_hand", [])
            card_type = "quests"
            empty_msg = "No quests"
        elif self.active_tab == "my_intrigue":
            cards = player_data.get("intrigue_hand", [])
            card_type = "intrigue"
            empty_msg = "No intrigue cards"
        else:
            cards = player_data.get("completed_contracts", [])
            card_type = "quests"
            empty_msg = "No completed quests"

        if not cards:
            self._draw_empty(x, y, w, h, scale, empty_msg)
            return

        bonus_genres: list[str] = []
        show_stars = (
            self.active_tab == "my_quests" and self._active_sub_tab == "my_quests"
        ) or self.active_tab == "completed_quests"
        if show_stars and player_data:
            pc = player_data.get("producer_card")
            if pc:
                bonus_genres = pc.get("bonus_genres", [])

        self._draw_card_grid(
            x, y, w, h, cards, card_type, scale, bonus_genres=bonus_genres
        )

    def _draw_card_grid(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        cards: list[dict],
        card_type: str,
        scale: float,
        bonus_genres: list[str] | None = None,
        separator_after: int = -1,
    ) -> None:
        total_cards = len(cards)
        self._card_page_count = max(1, math.ceil(total_cards / _CARDS_PER_PAGE))
        if self._card_page >= self._card_page_count:
            self._card_page = self._card_page_count - 1

        start = self._card_page * _CARDS_PER_PAGE
        end = min(start + _CARDS_PER_PAGE, total_cards)
        page_cards = cards[start:end]

        # Adjust separator_after for current page slice
        page_sep = -1
        if separator_after > 0:
            if start < separator_after <= end:
                page_sep = separator_after - start
            elif separator_after <= start:
                page_sep = 0

        card_key = (
            card_type,
            tuple(c.get("id", "") for c in page_cards),
            self._card_page,
            self._active_sub_tab,
            page_sep,
        )
        if self._content_sprite_list is None or self._content_card_key != card_key:
            self._content_card_key = card_key
            margin = 8 * scale
            col_w = (w - margin * 3) / 2 * _CARD_SHRINK
            png_scale = 2 if card_type in ("quests", "intrigue") else 1
            card_scale = col_w / (_CARD_BASE_WIDTH * png_scale)
            card_h = _CARD_BASE_HEIGHT * card_scale * png_scale
            row_gap = 8 * scale
            sep_gap = int(20 * scale) if page_sep > 0 else 0
            grid_w = col_w * 2 + margin
            pad_x = (w - grid_w) / 2

            top_y = y + h - margin - card_h / 2

            self._content_sprite_list = arcade.SpriteList()
            self._separator_y: float | None = None
            sep_row = (page_sep + 1) // 2 if page_sep > 0 else -1
            for i, card in enumerate(page_cards):
                card_id = card.get("id", "")
                png = Path(f"client/assets/card_images/{card_type}/{card_id}.png")
                if not png.exists():
                    continue
                col = i % 2
                row = i // 2
                extra = sep_gap if row >= sep_row and sep_row >= 0 else 0
                cx = x + pad_x + col * (col_w + margin) + col_w / 2
                cy = top_y - row * (card_h + row_gap) - extra
                sprite = arcade.Sprite(str(png))
                sprite.scale = card_scale
                sprite.position = (cx, cy)
                self._content_sprite_list.append(sprite)
            if sep_row >= 0:
                self._separator_y = (
                    top_y
                    - (sep_row - 1) * (card_h + row_gap)
                    - card_h / 2
                    - row_gap / 2
                )

        self._content_sprite_list.draw()

        if getattr(self, "_separator_y", None) is not None:
            sep_y = self._separator_y
            if y <= sep_y <= y + h:
                margin = 8 * scale
                font_sz = max(7, int(10 * scale))
                arcade.draw_line(
                    x + margin, sep_y, x + w - margin, sep_y, (120, 120, 140), 1
                )
                arcade.draw_text(
                    "— Completed —",
                    x + w / 2,
                    sep_y + 2,
                    (160, 160, 180),
                    font_size=font_sz,
                    font_name="Tahoma",
                    anchor_x="center",
                    anchor_y="bottom",
                )

        if bonus_genres and _STAR_PNG.exists():
            star_key = (card_key, tuple(bonus_genres))
            if self._star_sprite_list is None or self._star_card_key != star_key:
                self._star_card_key = star_key
                self._star_sprite_list = arcade.SpriteList()
                margin = 8 * scale
                col_w = (w - margin * 3) / 2 * _CARD_SHRINK
                png_scale = 2 if card_type in ("quests", "intrigue") else 1
                card_scale = col_w / (_CARD_BASE_WIDTH * png_scale)
                card_h = _CARD_BASE_HEIGHT * card_scale * png_scale
                row_gap = 8 * scale
                sep_gap_val = int(20 * scale) if page_sep > 0 else 0
                sep_row2 = (page_sep + 1) // 2 if page_sep > 0 else -1
                grid_w2 = col_w * 2 + margin
                pad_x2 = (w - grid_w2) / 2
                top_y2 = y + h - margin - card_h / 2
                star_size = col_w * 0.15
                for i, card in enumerate(page_cards):
                    genre = card.get("genre", "")
                    if genre not in bonus_genres:
                        continue
                    col = i % 2
                    row = i // 2
                    extra = sep_gap_val if row >= sep_row2 and sep_row2 >= 0 else 0
                    cx = x + pad_x2 + col * (col_w + margin) + col_w / 2
                    cy = top_y2 - row * (card_h + row_gap) - extra
                    star = arcade.Sprite(str(_STAR_PNG))
                    star.scale = star_size / star.texture.width
                    star.position = (
                        cx - col_w / 2 + star_size / 2 + 2 * scale,
                        cy + card_h / 2 - star_size / 2 + 1 * scale,
                    )
                    self._star_sprite_list.append(star)
            self._star_sprite_list.draw()
        else:
            self._star_sprite_list = None
            self._star_card_key = ()

    def _draw_producer_tab(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        player_data: dict | None,
        scale: float,
    ) -> None:
        if not player_data:
            self._draw_empty(x, y, w, h, scale, "No producer card")
            return

        producer = player_data.get("producer_card")
        if not producer:
            self._draw_empty(x, y, w, h, scale, "No producer card")
            return

        card_id = producer.get("id", "")
        png = Path(f"client/assets/card_images/producers/{card_id}.png")
        if png.exists():
            if self._producer_sprite_list is None or self._producer_card_id != card_id:
                self._producer_card_id = card_id
                sprite = arcade.Sprite(str(png))
                max_w = w - 20 * scale
                sprite.scale = min(scale, max_w / sprite.texture.width)
                sprite.position = (x + w / 2, y + h / 2)
                self._producer_sprite_list = arcade.SpriteList()
                self._producer_sprite_list.append(sprite)
            self._producer_sprite_list.draw()
        else:
            name = producer.get("name", "???")
            desc = producer.get("description", "")
            self._draw_empty(x, y, w, h, scale, f"{name}\n{desc}")

    def _draw_empty(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        scale: float,
        msg: str = "No content",
    ) -> None:
        font_sz = max(8, int(14 * scale))
        if self._empty_text is None:
            self._empty_text = arcade.Text(
                msg,
                x + w / 2,
                y + h / 2,
                arcade.color.LIGHT_GRAY,
                font_size=font_sz,
                font_name="Tahoma",
                anchor_x="center",
                anchor_y="center",
            )
        else:
            self._empty_text.text = msg
            self._empty_text.x = x + w / 2
            self._empty_text.y = y + h / 2
            self._empty_text.font_size = font_sz
        self._empty_text.draw()
