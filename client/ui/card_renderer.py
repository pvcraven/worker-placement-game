"""Contract and intrigue card display rendering."""

from __future__ import annotations

import arcade

_GENRE_COLORS = {
    "jazz": (70, 130, 180),     # Steel blue
    "pop": (255, 105, 180),     # Hot pink
    "soul": (148, 103, 189),    # Purple
    "funk": (255, 165, 0),      # Orange
    "rock": (220, 20, 60),      # Crimson
}

_CARD_WIDTH = 140
_CARD_HEIGHT = 190


class CardRenderer:
    """Draws contract and intrigue cards."""

    @staticmethod
    def draw_contract(
        cx: float, cy: float, card: dict, highlight: bool = False
    ) -> None:
        """Draw a contract card centered at (cx, cy)."""
        genre = card.get("genre", "")
        bg_color = _GENRE_COLORS.get(genre, (80, 80, 80))
        border_color = arcade.color.YELLOW if highlight else arcade.color.WHITE

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
        if len(name) > 18:
            name = name[:16] + ".."
        arcade.draw_text(
            name,
            cx, cy + 70,
            arcade.color.WHITE,
            font_size=10,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        # Genre tag
        arcade.draw_text(
            genre.upper(),
            cx, cy + 55,
            arcade.color.WHITE,
            font_size=8,
            anchor_x="center",
            anchor_y="center",
        )

        # Cost
        cost = card.get("cost", {})
        cost_parts = []
        mapping = {"guitarists": "G", "bass_players": "B", "drummers": "D", "singers": "S", "coins": "$"}
        for key, label in mapping.items():
            val = cost.get(key, 0)
            if val > 0:
                cost_parts.append(f"{val}{label}")
        cost_str = " ".join(cost_parts) if cost_parts else "Free"
        arcade.draw_text(
            f"Cost: {cost_str}",
            cx, cy + 20,
            arcade.color.WHITE,
            font_size=9,
            anchor_x="center",
            anchor_y="center",
        )

        # VP
        vp = card.get("victory_points", 0)
        arcade.draw_text(
            f"{vp} VP",
            cx, cy - 10,
            arcade.color.YELLOW,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        # Description (truncated)
        desc = card.get("description", "")
        if len(desc) > 40:
            desc = desc[:38] + ".."
        arcade.draw_text(
            desc,
            cx, cy - 50,
            arcade.color.WHITE,
            font_size=7,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=_CARD_WIDTH - 16,
            align="center",
        )

    @staticmethod
    def draw_intrigue(
        cx: float, cy: float, card: dict, highlight: bool = False
    ) -> None:
        """Draw an intrigue card centered at (cx, cy)."""
        bg_color = (40, 60, 40)
        border_color = arcade.color.YELLOW if highlight else arcade.color.GREEN

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
        if len(name) > 18:
            name = name[:16] + ".."
        arcade.draw_text(
            name,
            cx, cy + 70,
            arcade.color.GREEN,
            font_size=10,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        arcade.draw_text(
            "INTRIGUE",
            cx, cy + 55,
            arcade.color.LIGHT_GREEN,
            font_size=8,
            anchor_x="center",
            anchor_y="center",
        )

        desc = card.get("description", "")
        if len(desc) > 60:
            desc = desc[:58] + ".."
        arcade.draw_text(
            desc,
            cx, cy,
            arcade.color.WHITE,
            font_size=8,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=_CARD_WIDTH - 16,
            align="center",
        )

    @staticmethod
    def get_card_rect(cx: float, cy: float) -> tuple[float, float, float, float]:
        """Return (left, bottom, width, height) for hit testing."""
        return (cx - _CARD_WIDTH / 2, cy - _CARD_HEIGHT / 2, _CARD_WIDTH, _CARD_HEIGHT)
