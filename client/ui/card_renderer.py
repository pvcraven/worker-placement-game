"""Contract and intrigue card display rendering."""

from __future__ import annotations

import arcade

_GENRE_COLORS = {
    "jazz": (70, 130, 180),     # Steel blue
    "pop": (255, 105, 180),     # Hot pink
    "soul": (148, 103, 189),    # Purple
    "funk": (180, 110, 0),      # Dark amber
    "rock": (220, 20, 60),      # Crimson
}

_CARD_WIDTH = 190
_CARD_HEIGHT = 200


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

        # Card background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            bg_color,
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(cx, cy, _CARD_WIDTH, _CARD_HEIGHT),
            border_color,
            border_width=2 if highlight else 1,
        )

        # Name
        name = card.get("name", "???")
        if len(name) > 20:
            name = name[:18] + ".."
        cls._text(
            f"{cache_key}_name", name,
            cx, cy + 78,
            arcade.color.WHITE, 13,
            anchor_x="center", anchor_y="center",
        ).draw()

        # Genre tag
        cls._text(
            f"{cache_key}_genre", genre.upper(),
            cx, cy + 62,
            arcade.color.WHITE, 11,
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
            cx, cy + 30,
            arcade.color.WHITE, 11,
            anchor_x="center", anchor_y="center",
        ).draw()

        # VP
        vp = card.get("victory_points", 0)
        cls._text(
            f"{cache_key}_vp", f"{vp} VP",
            cx, cy + 2,
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
            bonus_parts.append("Free Building")
        elif rb == "random_draw":
            bonus_parts.append("Random Building")
        if bonus_parts:
            bonus_str = " ".join(bonus_parts)
            cls._text(
                f"{cache_key}_bonus", bonus_str,
                cx, cy - 18,
                arcade.color.LIGHT_GREEN, 10,
                anchor_x="center",
                anchor_y="center",
            ).draw()

        # Description
        desc = card.get("description", "")
        if len(desc) > 120:
            desc = desc[:118] + ".."
        cls._text(
            f"{cache_key}_desc", desc,
            cx, cy - 50,
            arcade.color.WHITE, 10,
            anchor_x="center", anchor_y="center",
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
            cx, cy + 78,
            arcade.color.GREEN, 12,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        cls._text(
            f"{cache_key}_lbl", "INTRIGUE",
            cx, cy + 62,
            arcade.color.LIGHT_GREEN, 11,
            anchor_x="center", anchor_y="center",
        ).draw()

        desc = card.get("description", "")
        if len(desc) > 80:
            desc = desc[:78] + ".."
        cls._text(
            f"{cache_key}_desc", desc,
            cx, cy,
            arcade.color.WHITE, 11,
            anchor_x="center", anchor_y="center",
            multiline=True, width=_CARD_WIDTH - 16, align="center",
        ).draw()

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
