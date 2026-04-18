"""Contract and intrigue card display rendering."""

from __future__ import annotations

import arcade

_GENRE_COLORS = {
    "jazz": (25, 55, 85),       # Dark blue
    "pop": (85, 25, 55),        # Dark magenta
    "soul": (60, 40, 90),       # Dark purple
    "funk": (85, 50, 0),        # Dark amber
    "rock": (70, 8, 18),        # Dark crimson
}

_CARD_WIDTH = 190
_CARD_HEIGHT = 230


class CardRenderer:
    """Draws contract and intrigue cards with cached Text objects."""

    _cache: dict[str, arcade.Text] = {}

    @classmethod
    def _text(
        cls,
        key: str,
        text: str,
        x: float,
        y: float,
        color,
        font_size: int,
        **kwargs,
    ) -> arcade.Text:
        """Get or create a cached Text object."""
        if key in cls._cache:
            t = cls._cache[key]
            t.text = text
            t.x = x
            t.y = y
            t.color = color
            t.font_size = font_size
            return t
        t = arcade.Text(
            text, x, y, color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        cls._cache[key] = t
        return t

    @classmethod
    def draw_contract(
        cls, cx: float, cy: float, card: dict,
        highlight: bool = False, cache_key: str = "",
    ) -> None:
        """Draw a contract card centered at (cx, cy)."""
        if not cache_key:
            cache_key = f"c_{cx:.0f}_{cy:.0f}"

        genre = card.get("genre", "")
        bg_color = _GENRE_COLORS.get(genre, (80, 80, 80))
        border_color = (
            arcade.color.YELLOW if highlight else arcade.color.WHITE
        )

        # Card background — dark brown body (matches building cards)
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                cx, cy, _CARD_WIDTH, _CARD_HEIGHT,
            ),
            (50, 40, 30),
        )
        # Genre color band at top
        band_h = 36
        band_cy = cy + _CARD_HEIGHT / 2 - band_h / 2
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                cx, band_cy, _CARD_WIDTH, band_h,
            ),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                cx, cy, _CARD_WIDTH, _CARD_HEIGHT,
            ),
            border_color,
            border_width=2 if highlight else 1,
        )

        # Genre tag (top, bold, in color band)
        cls._text(
            f"{cache_key}_genre", genre.upper(),
            cx, band_cy,
            arcade.color.WHITE, 14,
            anchor_x="center", anchor_y="center",
            bold=True,
        ).draw()

        # Name (below genre band)
        name = card.get("name", "???")
        if len(name) > 20:
            name = name[:18] + ".."
        cls._text(
            f"{cache_key}_name", name,
            cx, cy + 74,
            arcade.color.WHITE, 13,
            anchor_x="center", anchor_y="center",
        ).draw()

        # Cost
        cost = card.get("cost", {})
        cost_parts = []
        mapping = {
            "guitarists": "G",
            "bass_players": "B",
            "drummers": "D",
            "singers": "S",
            "coins": "$",
        }
        for key, label in mapping.items():
            val = cost.get(key, 0)
            if val > 0:
                cost_parts.append(f"{val}{label}")
        cost_str = " ".join(cost_parts) if cost_parts else "Free"
        cls._text(
            f"{cache_key}_cost", f"Cost: {cost_str}",
            cx, cy + 50,
            arcade.color.WHITE, 12,
            anchor_x="center", anchor_y="center",
        ).draw()

        # VP
        vp = card.get("victory_points", 0)
        cls._text(
            f"{cache_key}_vp", f"{vp} VP",
            cx, cy + 22,
            arcade.color.YELLOW, 18,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        # Bonus rewards line
        bonus_parts = []
        bonus_res = card.get("bonus_resources", {})
        for rk, rs in mapping.items():
            rv = bonus_res.get(rk, 0)
            if rv > 0:
                bonus_parts.append(f"+{rv}{rs}")
        di = card.get("reward_draw_intrigue", 0)
        if di:
            bonus_parts.append(f"+{di} Intrigue")
        dq = card.get("reward_draw_quests", 0)
        if dq:
            mode = card.get(
                "reward_quest_draw_mode", "random",
            )
            tag = "Choose" if mode == "choose" else "Draw"
            bonus_parts.append(f"{tag} {dq} Quest")
        rb = card.get("reward_building")
        if rb == "market_choice":
            bonus_parts.append("Choose Free Building")
        elif rb == "random_draw":
            bonus_parts.append("Draw Free Building")
        desc_top = cy - 6
        if bonus_parts:
            bonus_str = " ".join(bonus_parts)
            cls._text(
                f"{cache_key}_bonus", bonus_str,
                cx, cy - 6,
                arcade.color.WHITE, 13,
                anchor_x="center",
                anchor_y="center",
            ).draw()
            desc_top = cy - 22

        # Description
        desc = card.get("description", "")
        if len(desc) > 120:
            desc = desc[:118] + ".."
        cls._text(
            f"{cache_key}_desc", desc,
            cx, desc_top,
            arcade.color.WHITE, 10,
            anchor_x="center", anchor_y="top",
            multiline=True, width=_CARD_WIDTH - 16,
            align="center",
        ).draw()

    @classmethod
    def draw_building(
        cls, cx: float, cy: float, card: dict,
        highlight: bool = False, cache_key: str = "",
    ) -> None:
        """Draw a building card centered at (cx, cy)."""
        if not cache_key:
            cache_key = f"b_{cx:.0f}_{cy:.0f}"

        bg_color = (50, 40, 30)
        border_color = (
            arcade.color.YELLOW if highlight
            else arcade.color.GOLD
        )

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            border_color,
            border_width=2 if highlight else 1,
        )

        name = card.get("name", "???")
        if len(name) > 20:
            name = name[:18] + ".."
        cls._text(
            f"{cache_key}_name", name,
            cx, cy + 96,
            arcade.color.GOLD, 13,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        cost = card.get("cost_coins", 0)
        cls._text(
            f"{cache_key}_cost", f"Cost: {cost} coins",
            cx, cy + 72,
            arcade.color.WHITE, 11,
            anchor_x="center", anchor_y="center",
        ).draw()

        mapping = {
            "guitarists": "G", "bass_players": "B",
            "drummers": "D", "singers": "S", "coins": "$",
        }
        visitor = card.get("visitor_reward", {})
        vis_parts = []
        for key, sym in mapping.items():
            val = visitor.get(key, 0)
            if val > 0:
                vis_parts.append(f"{val}{sym}")
        vis_str = " ".join(vis_parts) if vis_parts else "None"
        cls._text(
            f"{cache_key}_vis_lbl", "Visitor:",
            cx, cy + 48,
            arcade.color.LIGHT_GREEN, 11,
            anchor_x="center", anchor_y="center",
        ).draw()
        cls._text(
            f"{cache_key}_vis_val", vis_str,
            cx, cy + 30,
            arcade.color.LIGHT_GREEN, 12,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        owner = card.get("owner_bonus", {})
        own_parts = []
        for key, sym in mapping.items():
            val = owner.get(key, 0)
            if val > 0:
                own_parts.append(f"{val}{sym}")
        own_str = " ".join(own_parts) if own_parts else "None"
        cls._text(
            f"{cache_key}_own_lbl", "Owner Bonus:",
            cx, cy + 6,
            arcade.color.YELLOW, 11,
            anchor_x="center", anchor_y="center",
        ).draw()
        cls._text(
            f"{cache_key}_own_val", own_str,
            cx, cy - 12,
            arcade.color.YELLOW, 12,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        desc = card.get("description", "")
        if len(desc) > 100:
            desc = desc[:98] + ".."
        cls._text(
            f"{cache_key}_desc", desc,
            cx, cy - 34,
            arcade.color.WHITE, 10,
            anchor_x="center", anchor_y="top",
            multiline=True, width=_CARD_WIDTH - 16,
            align="center",
        ).draw()

    @classmethod
    def draw_intrigue(
        cls, cx: float, cy: float, card: dict,
        highlight: bool = False, cache_key: str = "",
    ) -> None:
        """Draw an intrigue card centered at (cx, cy)."""
        if not cache_key:
            cache_key = f"i_{cx:.0f}_{cy:.0f}"

        bg_color = (40, 60, 40)
        border_color = (
            arcade.color.YELLOW if highlight else arcade.color.GREEN
        )

        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            border_color,
            border_width=2 if highlight else 1,
        )

        name = card.get("name", "???")
        if len(name) > 20:
            name = name[:18] + ".."
        cls._text(
            f"{cache_key}_name", name,
            cx, cy + 96,
            arcade.color.GREEN, 12,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        cls._text(
            f"{cache_key}_lbl", "INTRIGUE",
            cx, cy + 78,
            arcade.color.LIGHT_GREEN, 11,
            anchor_x="center", anchor_y="center",
        ).draw()

        desc = card.get("description", "")
        if len(desc) > 80:
            desc = desc[:78] + ".."
        cls._text(
            f"{cache_key}_desc", desc,
            cx, cy + 20,
            arcade.color.WHITE, 11,
            anchor_x="center", anchor_y="center",
            multiline=True, width=_CARD_WIDTH - 16,
            align="center",
        ).draw()

        effect_str = cls._intrigue_effect_summary(card)
        if effect_str:
            cls._text(
                f"{cache_key}_eff", effect_str,
                cx, cy - 40,
                arcade.color.YELLOW, 11,
                anchor_x="center", anchor_y="center",
                multiline=True, width=_CARD_WIDTH - 16,
                align="center", bold=True,
            ).draw()

    @staticmethod
    def _intrigue_effect_summary(card: dict) -> str:
        etype = card.get("effect_type", "")
        val = card.get("effect_value", {})
        mapping = [
            ("guitarists", "G"), ("bass_players", "B"),
            ("drummers", "D"), ("singers", "S"),
            ("coins", "$"),
        ]
        if etype in ("gain_resources", "all_players_gain"):
            parts = []
            for k, sym in mapping:
                v = val.get(k, 0)
                if v:
                    parts.append(f"+{v}{sym}")
            label = " ".join(parts)
            if etype == "all_players_gain":
                return f"{label} (all)"
            return label
        if etype == "gain_coins":
            c = val.get("coins", 0)
            return f"+{c}$" if c else ""
        if etype == "vp_bonus":
            vp = val.get("victory_points", 0)
            return f"+{vp} VP" if vp else ""
        if etype == "draw_contracts":
            n = val.get("count", 1)
            return f"Draw {n} quest(s)"
        if etype == "draw_intrigue":
            n = val.get("count", 1)
            return f"Draw {n} intrigue"
        if etype == "steal_resources":
            parts = []
            for k, sym in mapping:
                v = val.get(k, 0)
                if v:
                    parts.append(f"{v}{sym}")
            return f"Steal {' '.join(parts)}"
        if etype == "opponent_loses":
            parts = []
            for k, sym in mapping:
                v = val.get(k, 0)
                if v:
                    parts.append(f"{v}{sym}")
            return f"Opponent loses {' '.join(parts)}"
        return ""

    @staticmethod
    def get_card_rect(
        cx: float, cy: float
    ) -> tuple[float, float, float, float]:
        """Return (left, bottom, width, height) for hit testing."""
        return (
            cx - _CARD_WIDTH / 2,
            cy - _CARD_HEIGHT / 2,
            _CARD_WIDTH,
            _CARD_HEIGHT,
        )
