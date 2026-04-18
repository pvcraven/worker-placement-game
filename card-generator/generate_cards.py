"""Generate PNG card images from JSON config files using Pillow."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from server.models.config import (  # noqa: E402
    BuildingsConfig,
    ContractsConfig,
    IntrigueConfig,
    ProducersConfig,
)
from shared.card_models import ResourceCost  # noqa: E402

CARD_WIDTH = 190
CARD_HEIGHT = 230
PARCHMENT_COLOR = (235, 220, 185)
TEXT_COLOR = (60, 40, 20)
CORNER_RADIUS = 12

GENRE_COLORS = {
    "jazz": (40, 80, 120),
    "pop": (120, 40, 80),
    "soul": (80, 55, 120),
    "funk": (120, 70, 10),
    "rock": (100, 15, 25),
}

OUTPUT_BASE = PROJECT_ROOT / "client" / "assets" / "card_images"
OUTPUT_QUESTS = OUTPUT_BASE / "quests"
OUTPUT_BUILDINGS = OUTPUT_BASE / "buildings"
OUTPUT_INTRIGUE = OUTPUT_BASE / "intrigue"
OUTPUT_PRODUCERS = OUTPUT_BASE / "producers"

CONFIG_DIR = PROJECT_ROOT / "config"

FONT_NAME = "tahoma"
FONT_BOLD_NAME = "tahomabd"


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = FONT_BOLD_NAME if bold else FONT_NAME
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size)


FONT_TITLE = _load_font(17, bold=True)
FONT_GENRE = _load_font(18, bold=True)
FONT_BODY = _load_font(15)
FONT_BODY_SMALL = _load_font(13)
FONT_VP = _load_font(26, bold=True)
FONT_LABEL = _load_font(14, bold=True)


def create_card_base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [0, 0, CARD_WIDTH - 1, CARD_HEIGHT - 1],
        radius=CORNER_RADIUS,
        fill=PARCHMENT_COLOR,
    )
    return img, draw


def format_resources(cost: ResourceCost) -> str:
    mapping = [
        ("guitarists", "G"),
        ("bass_players", "B"),
        ("drummers", "D"),
        ("singers", "S"),
        ("coins", "$"),
    ]
    parts = []
    for field, sym in mapping:
        val = getattr(cost, field, 0)
        if val > 0:
            parts.append(f"{val}{sym}")
    return " ".join(parts) if parts else "None"


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: tuple = TEXT_COLOR,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (CARD_WIDTH - tw) // 2
    draw.text((x, y), text, fill=color, font=font)


def draw_text_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: tuple = TEXT_COLOR,
    max_width: int = CARD_WIDTH - 16,
    max_lines: int = 10,
) -> int:
    if not text:
        return y
    words = text.split()
    lines: list[str] = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    margin = 8
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1] + 2
        if y + line_h > CARD_HEIGHT - margin:
            break
        draw_text_centered(draw, line, y, font, color)
        y += line_h
    return y


def truncate_name(name: str, max_len: int = 20) -> str:
    if len(name) > max_len:
        return name[: max_len - 2] + ".."
    return name


def generate_quest_cards() -> int:
    data = json.loads((CONFIG_DIR / "contracts.json").read_text())
    config = ContractsConfig.model_validate(data)
    OUTPUT_QUESTS.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.contracts:
        img, draw = create_card_base()
        genre = card.genre.value
        genre_color = GENRE_COLORS.get(genre, (80, 80, 80))
        band_h = 38
        draw.rounded_rectangle(
            [0, 0, CARD_WIDTH - 1, band_h],
            radius=CORNER_RADIUS,
            fill=genre_color,
        )
        draw.rectangle(
            [0, band_h - CORNER_RADIUS, CARD_WIDTH - 1, band_h],
            fill=genre_color,
        )
        draw_text_centered(
            draw, genre.upper(), 8, FONT_GENRE, (255, 255, 255),
        )
        y = band_h + 4
        name = truncate_name(card.name)
        draw_text_centered(draw, name, y, FONT_TITLE)
        y += 22
        cost_str = f"Cost: {format_resources(card.cost)}"
        draw_text_centered(draw, cost_str, y, FONT_BODY)
        y += 20
        vp_str = f"{card.victory_points} VP"
        draw_text_centered(draw, vp_str, y, FONT_VP, (120, 80, 0))
        y += 30
        bonus_parts = []
        br = format_resources(card.bonus_resources)
        if br != "None":
            bonus_parts.append(f"+{br}")
        if card.reward_draw_intrigue:
            bonus_parts.append(f"+{card.reward_draw_intrigue} Intrigue")
        if card.reward_draw_quests:
            is_choose = card.reward_quest_draw_mode == "choose"
            mode = "Choose" if is_choose else "Draw"
            bonus_parts.append(f"{mode} {card.reward_draw_quests} Quest")
        if card.reward_building == "market_choice":
            bonus_parts.append("Choose Building")
        elif card.reward_building == "random_draw":
            bonus_parts.append("Draw Building")
        if bonus_parts:
            bonus_str = " ".join(bonus_parts)
            draw_text_centered(
                draw, bonus_str, y, FONT_BODY, (100, 60, 10),
            )
            y += 18
        if card.is_plot_quest:
            draw_text_centered(
                draw, "[PLOT QUEST]", y, FONT_BODY_SMALL, (150, 50, 50),
            )
            y += 16
        if card.ongoing_benefit_description:
            y = draw_text_wrapped(
                draw, card.ongoing_benefit_description, y,
                FONT_BODY_SMALL, (80, 50, 20), max_lines=2,
            )
        y = draw_text_wrapped(draw, card.description, y, FONT_BODY_SMALL)
        img.save(OUTPUT_QUESTS / f"{card.id}.png")
        count += 1
    return count


def generate_building_cards() -> int:
    data = json.loads((CONFIG_DIR / "buildings.json").read_text())
    config = BuildingsConfig.model_validate(data)
    OUTPUT_BUILDINGS.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.buildings:
        img, draw = create_card_base()
        y = 12
        name = truncate_name(card.name)
        draw_text_centered(
            draw, name, y, FONT_TITLE, (100, 60, 10),
        )
        y += 24
        cost_str = f"Cost: {card.cost_coins} coins"
        draw_text_centered(draw, cost_str, y, FONT_BODY)
        y += 22
        vis_str = format_resources(card.visitor_reward)
        vis_line = f"Visitor: {vis_str}"
        draw_text_centered(
            draw, vis_line, y, FONT_LABEL, (30, 90, 30),
        )
        y += 18
        if card.visitor_reward_special:
            special = card.visitor_reward_special.replace(
                "_", " ",
            ).title()
            draw_text_centered(
                draw, special, y, FONT_BODY_SMALL, (30, 90, 30),
            )
            y += 18
        own_str = format_resources(card.owner_bonus)
        own_line = f"Owner: {own_str}"
        draw_text_centered(
            draw, own_line, y, FONT_LABEL, (120, 80, 0),
        )
        y += 18
        if card.owner_bonus_special:
            special = card.owner_bonus_special.replace(
                "_", " ",
            ).title()
            draw_text_centered(
                draw, special, y, FONT_BODY_SMALL, (120, 80, 0),
            )
            y += 18
        y = draw_text_wrapped(draw, card.description, y, FONT_BODY_SMALL)
        img.save(OUTPUT_BUILDINGS / f"{card.id}.png")
        count += 1
    return count


def _intrigue_effect_summary(effect_type: str, effect_value: dict) -> str:
    mapping = [
        ("guitarists", "G"),
        ("bass_players", "B"),
        ("drummers", "D"),
        ("singers", "S"),
        ("coins", "$"),
    ]
    if effect_type in ("gain_resources", "all_players_gain"):
        parts = []
        for k, sym in mapping:
            v = effect_value.get(k, 0)
            if v:
                parts.append(f"+{v}{sym}")
        label = " ".join(parts)
        if effect_type == "all_players_gain":
            return f"{label} (all)"
        return label
    if effect_type == "gain_coins":
        c = effect_value.get("coins", 0)
        return f"+{c}$" if c else ""
    if effect_type == "vp_bonus":
        vp = effect_value.get("victory_points", 0)
        return f"+{vp} VP" if vp else ""
    if effect_type == "draw_contracts":
        n = effect_value.get("count", 1)
        return f"Draw {n} quest(s)"
    if effect_type == "draw_intrigue":
        n = effect_value.get("count", 1)
        return f"Draw {n} intrigue"
    if effect_type == "steal_resources":
        parts = []
        for k, sym in mapping:
            v = effect_value.get(k, 0)
            if v:
                parts.append(f"{v}{sym}")
        return f"Steal {' '.join(parts)}"
    if effect_type == "opponent_loses":
        parts = []
        for k, sym in mapping:
            v = effect_value.get(k, 0)
            if v:
                parts.append(f"{v}{sym}")
        return f"Opponent loses {' '.join(parts)}"
    return ""


TARGET_LABELS = {
    "self": "",
    "choose_opponent": "Target: Opponent",
    "all": "All Players",
}


def generate_intrigue_cards() -> int:
    data = json.loads((CONFIG_DIR / "intrigue.json").read_text())
    config = IntrigueConfig.model_validate(data)
    OUTPUT_INTRIGUE.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.intrigue_cards:
        img, draw = create_card_base()
        y = 12
        name = truncate_name(card.name)
        draw_text_centered(
            draw, name, y, FONT_TITLE, (30, 80, 30),
        )
        y += 22
        draw_text_centered(
            draw, "INTRIGUE", y, FONT_BODY, (60, 120, 60),
        )
        y += 22
        y = draw_text_wrapped(
            draw, card.description, y, FONT_BODY_SMALL, max_lines=4,
        )
        y += 6
        effect = _intrigue_effect_summary(
            card.effect_type, card.effect_value,
        )
        if effect:
            draw_text_centered(
                draw, effect, y, FONT_LABEL, (120, 80, 0),
            )
            y += 20
        target_label = TARGET_LABELS.get(card.effect_target, "")
        if target_label:
            draw_text_centered(
                draw, target_label, y, FONT_BODY_SMALL, (150, 50, 50),
            )
        img.save(OUTPUT_INTRIGUE / f"{card.id}.png")
        count += 1
    return count


def generate_producer_cards() -> int:
    data = json.loads((CONFIG_DIR / "producers.json").read_text())
    config = ProducersConfig.model_validate(data)
    OUTPUT_PRODUCERS.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.producers:
        img, draw = create_card_base()
        y = 12
        name = truncate_name(card.name)
        draw_text_centered(
            draw, name, y, FONT_TITLE, (100, 50, 100),
        )
        y += 22
        draw_text_centered(
            draw, "PRODUCER", y, FONT_BODY, (130, 80, 130),
        )
        y += 24
        genres = ", ".join(
            g.value.title() for g in card.bonus_genres
        )
        draw_text_centered(
            draw, f"Genres: {genres}", y, FONT_LABEL,
        )
        y += 22
        vp_str = f"{card.bonus_vp_per_contract}VP/contract"
        draw_text_centered(
            draw, vp_str, y, FONT_VP, (120, 80, 0),
        )
        y += 32
        y = draw_text_wrapped(
            draw, card.description, y, FONT_BODY_SMALL,
        )
        img.save(OUTPUT_PRODUCERS / f"{card.id}.png")
        count += 1
    return count


def main() -> None:
    print("Card Image Generator")
    print(f"Output: {OUTPUT_BASE}")
    print()
    q = generate_quest_cards()
    print(f"Quest cards: {q} written to {OUTPUT_QUESTS}/")
    b = generate_building_cards()
    print(f"Building cards: {b} written to {OUTPUT_BUILDINGS}/")
    i = generate_intrigue_cards()
    print(f"Intrigue cards: {i} written to {OUTPUT_INTRIGUE}/")
    p = generate_producer_cards()
    print(f"Producer cards: {p} written to {OUTPUT_PRODUCERS}/")
    total = q + b + i + p
    print(f"\nDone. {total} card images generated.")


if __name__ == "__main__":
    main()
