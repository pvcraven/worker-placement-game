"""Tabbed right-side panel: Game Log, Quests, Intrigue, Completed Quests, Producer."""

from __future__ import annotations

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

_CARD_BASE_WIDTH = 190
_CARD_BASE_HEIGHT = 230

_ACTIVE_COLOR = (60, 60, 80)
_INACTIVE_COLOR = (30, 30, 40)
_BG_COLOR = (20, 20, 30)


class TabbedPanel:
    """Right-side panel with selectable tab views."""

    def __init__(self) -> None:
        self.active_tab: str = "game_log"
        self.game_log = GameLogPanel()
        self._tab_rects: dict[str, tuple[float, float, float, float]] = {}
        self._tab_shape_list: arcade.shape_list.ShapeElementList | None = None
        self._tab_texts: list[arcade.Text] = []
        self._title_text: arcade.Text | None = None
        self._empty_text: arcade.Text | None = None
        self._content_sprite_list: arcade.SpriteList | None = None
        self._content_card_key: tuple = ()
        self._producer_sprite_list: arcade.SpriteList | None = None
        self._producer_card_id: str = ""
        self._last_rect = (0.0, 0.0, 0.0, 0.0)
        self._last_scale = 0.0
        self._last_tab = ""
        self._shapes_dirty = True

    def add_entry(self, text: str) -> None:
        self.game_log.add_entry(text)

    def scroll(self, direction: int) -> None:
        self.game_log.scroll(direction)

    def on_click(self, x: float, y: float) -> bool:
        for tab_id, (rx, ry, rw, rh) in self._tab_rects.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                if self.active_tab != tab_id:
                    self.active_tab = tab_id
                    self._shapes_dirty = True
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
    ) -> None:
        s = scale
        rect = (x, y, w, h)
        if (
            rect != self._last_rect
            or s != self._last_scale
            or self.active_tab != self._last_tab
        ):
            self._shapes_dirty = True
            self._content_sprite_list = None
            self._producer_sprite_list = None

        tab_bar_h = max(28, int(36 * s))
        title_h = max(20, int(28 * s))
        content_y = y
        content_h = h - tab_bar_h - title_h

        if self._shapes_dirty:
            self._rebuild_tab_bar(x, y, w, h, tab_bar_h, s)
            self._rebuild_title(x, y + h - tab_bar_h, w, title_h, s)
            self._last_rect = rect
            self._last_scale = s
            self._last_tab = self.active_tab
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

        # Content
        if self.active_tab == "game_log":
            self.game_log.draw(x, content_y, w, content_h, scale=s, show_title=False)
        elif self.active_tab in ("my_quests", "my_intrigue", "completed_quests"):
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

        if self.active_tab == "my_quests":
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

        self._draw_card_grid(x, y, w, h, cards, card_type, scale)

    def _draw_card_grid(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        cards: list[dict],
        card_type: str,
        scale: float,
    ) -> None:
        card_key = (card_type, tuple(c.get("id", "") for c in cards))
        if self._content_sprite_list is None or self._content_card_key != card_key:
            self._content_card_key = card_key
            margin = 8 * scale
            col_w = (w - margin * 3) / 2
            png_scale = 2 if card_type == "quests" else 1
            card_scale = col_w / (_CARD_BASE_WIDTH * png_scale)
            card_h = _CARD_BASE_HEIGHT * card_scale * png_scale
            row_gap = 8 * scale
            top_y = y + h - margin - card_h / 2

            self._content_sprite_list = arcade.SpriteList()
            for i, card in enumerate(cards):
                card_id = card.get("id", "")
                png = Path(f"client/assets/card_images/{card_type}/{card_id}.png")
                if not png.exists():
                    continue
                col = i % 2
                row = i // 2
                cx = x + margin + col * (col_w + margin) + col_w / 2
                cy = top_y - row * (card_h + row_gap)
                if cy - card_h / 2 < y:
                    break
                sprite = arcade.Sprite(str(png))
                sprite.scale = card_scale
                sprite.position = (cx, cy)
                self._content_sprite_list.append(sprite)

        self._content_sprite_list.draw()

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
