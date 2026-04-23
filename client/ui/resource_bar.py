"""Player resource display bar at the bottom of the screen."""

from __future__ import annotations

from pathlib import Path

import arcade

_PARCHMENT_COLOR = (235, 220, 185)
_TEXT_COLOR = (60, 40, 20)

_ICONS_DIR = Path("client/assets/card_images/icons")
_MARKERS_DIR = Path("client/assets/card_images/markers")

_RESOURCE_CONFIG = [
    ("guitarists", "Guitarists", "guitarist.png", arcade.color.RED),
    ("bass_players", "Bass", "bass_player.png", (30, 30, 30)),
    ("drummers", "Drummers", "drummer.png", (220, 220, 220)),
    ("singers", "Singers", "singer.png", arcade.color.PURPLE),
    ("coins", "Coins", "coin.png", arcade.color.GOLD),
]


class ResourceBar:
    """Draws the player's resources as sprites at the bottom."""

    def __init__(self) -> None:
        self.resources: dict = {}
        self._text_cache: dict[str, arcade.Text] = {}
        self._sprite_list: arcade.SpriteList | None = None
        self._last_draw_key: tuple = ()

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
        if key in self._text_cache:
            t = self._text_cache[key]
            t.text = text
            t.x = x
            t.y = y
            t.color = color
            t.font_size = font_size
            return t
        t = arcade.Text(
            text,
            x,
            y,
            color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def update_resources(self, resources: dict) -> None:
        self.resources = resources

    def draw(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        workers_left: int = 0,
        victory_points: int = 0,
        intrigue_count: int = 0,
        quests_open: int = 0,
        quests_closed: int = 0,
        scale: float = 1.0,
        player_color: str = "",
    ) -> None:
        s = scale

        arcade.draw_rect_filled(
            arcade.rect.XYWH(x + w / 2, y + h / 2, w, h),
            _PARCHMENT_COLOR,
        )

        font_sz = max(8, int(16 * s))
        icon_sz = int(20 * s)
        count = len(_RESOURCE_CONFIG)
        section_w = w / count
        left_shift = section_w * 0.25
        row_y = y + h * 0.33
        top_y = y + h * 0.72

        draw_key = (
            x,
            y,
            w,
            h,
            s,
            player_color,
            workers_left,
            victory_points,
            intrigue_count,
            quests_open,
            quests_closed,
            tuple(self.resources.get(k, 0) for k, _, _, _ in _RESOURCE_CONFIG),
        )

        if draw_key != self._last_draw_key:
            self._last_draw_key = draw_key
            self._sprite_list = arcade.SpriteList()
            for i, (key, _label, png_name, fallback_color) in enumerate(
                _RESOURCE_CONFIG
            ):
                cx = x + section_w * (i + 0.5) - left_shift - 30 * s
                png_path = _ICONS_DIR / png_name
                if png_path.exists():
                    sprite = arcade.Sprite(str(png_path))
                    sprite.scale = icon_sz / sprite.texture.width
                    sprite.position = (cx, row_y)
                    self._sprite_list.append(sprite)

            # Card icons for top row (indices: 0=workers, 1=vp, 2=intrigue, 3=open, 4=done)
            quest_icon_path = _ICONS_DIR / "quest_icon.png"
            intrigue_icon_path = _ICONS_DIR / "intrigue_icon.png"
            card_icon_h = int(28 * s)

            if intrigue_icon_path.exists():
                ic_cx = x + section_w * 2.5 - left_shift - 30 * s
                sprite = arcade.Sprite(str(intrigue_icon_path))
                sprite.scale = card_icon_h / sprite.texture.height
                sprite.position = (ic_cx, top_y)
                self._sprite_list.append(sprite)

            if quest_icon_path.exists():
                # Quest open icon
                qo_cx = x + section_w * 3.5 - left_shift - 30 * s
                sprite = arcade.Sprite(str(quest_icon_path))
                sprite.scale = card_icon_h / sprite.texture.height
                sprite.position = (qo_cx, top_y)
                self._sprite_list.append(sprite)

                # Quest done icon
                qd_cx = x + section_w * 4.5 - left_shift - 30 * s
                sprite = arcade.Sprite(str(quest_icon_path))
                sprite.scale = card_icon_h / sprite.texture.height
                sprite.position = (qd_cx, top_y)
                self._sprite_list.append(sprite)

            # Worker marker
            if player_color:
                marker_path = _MARKERS_DIR / f"worker_{player_color}.png"
                if marker_path.exists():
                    mc_cx = x + section_w * 0.5 - left_shift - 30 * s
                    sprite = arcade.Sprite(str(marker_path))
                    sprite.scale = card_icon_h / sprite.texture.height
                    sprite.position = (mc_cx, top_y)
                    self._sprite_list.append(sprite)

        if self._sprite_list:
            self._sprite_list.draw()

        # Fallback: draw colored rectangles for missing icon PNGs
        swatch = int(20 * s)
        for i, (key, _label, png_name, fallback_color) in enumerate(_RESOURCE_CONFIG):
            if not (_ICONS_DIR / png_name).exists():
                cx = x + section_w * (i + 0.5) - left_shift - 30 * s
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(cx, row_y, swatch, swatch),
                    fallback_color,
                )

        # Bottom row: resource labels
        for i, (key, label, _png, _color) in enumerate(_RESOURCE_CONFIG):
            cx = x + section_w * (i + 0.5) - left_shift
            val = self.resources.get(key, 0)
            self._text(
                f"res_{key}",
                f"{label}: {val}",
                cx - 15 * s,
                row_y,
                _TEXT_COLOR,
                font_sz,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            ).draw()

        # Top row: workers, VP, intrigue, quests
        top_items = [
            ("workers_left", f"Workers: {workers_left}"),
            ("vp", f"VP: {victory_points}"),
            ("intrigue", f"Intrigue: {intrigue_count}"),
            ("quests_open", f"Open: {quests_open}"),
            ("quests_closed", f"Done: {quests_closed}"),
        ]
        for i, (key, label) in enumerate(top_items):
            cx = x + section_w * (i + 0.5) - left_shift
            text_x = cx - 15 * s
            if key in ("intrigue", "quests_open", "quests_closed"):
                text_x = cx - 10 * s
            self._text(
                key,
                label,
                text_x,
                top_y,
                _TEXT_COLOR,
                font_sz,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            ).draw()
