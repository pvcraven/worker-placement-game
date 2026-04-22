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
from shared.constants import (  # noqa: E402
    BUILDING_CARD_HEIGHT,
    CARD_HEIGHT,
    CARD_WIDTH,
    RESOURCE_SYMBOLS,
    SPACE_CARD_HEIGHT,
)

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
OUTPUT_SPACES = OUTPUT_BASE / "spaces"
OUTPUT_MARKERS = OUTPUT_BASE / "markers"

CONFIG_DIR = PROJECT_ROOT / "config"

FONT_NAME = "tahoma"
FONT_BOLD_NAME = "tahomabd"


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = FONT_BOLD_NAME if bold else FONT_NAME
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size)


def _load_font_serif(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "timesbd" if bold else "times"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return _load_font(size, bold)


FONT_TITLE = _load_font(17, bold=True)
FONT_GENRE = _load_font(18, bold=True)
FONT_BODY = _load_font(15)
FONT_BODY_SMALL = _load_font(13)
FONT_VP = _load_font(26, bold=True)
FONT_LABEL = _load_font(14, bold=True)

# Quest card dimensions (2x base) and fonts
QUEST_CARD_WIDTH = CARD_WIDTH * 2
QUEST_CARD_HEIGHT = CARD_HEIGHT * 2
QUEST_CORNER_RADIUS = CORNER_RADIUS * 2

Q_FONT_TITLE = _load_font(30, bold=True)
Q_FONT_GENRE = _load_font(34, bold=True)
Q_FONT_BODY = _load_font(26)
Q_FONT_BODY_SMALL = _load_font(22)
Q_FONT_VP = _load_font(44, bold=True)
Q_FONT_LABEL = _load_font(24, bold=True)
Q_FONT_SECTION = _load_font(20, bold=True)


def create_card_base(
    height: int = CARD_HEIGHT,
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (CARD_WIDTH, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [0, 0, CARD_WIDTH - 1, height - 1],
        radius=CORNER_RADIUS,
        fill=PARCHMENT_COLOR,
    )
    return img, draw


def format_resources(cost: ResourceCost) -> str:
    parts = []
    for field, sym in RESOURCE_SYMBOLS:
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
    width: int = CARD_WIDTH,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=color, font=font)


def draw_text_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: tuple = TEXT_COLOR,
    max_width: int = CARD_WIDTH - 16,
    max_lines: int = 10,
    card_width: int = CARD_WIDTH,
    card_height: int = CARD_HEIGHT,
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
    for line in lines[:max_lines]:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1] + 2
        if y + line_h > card_height - margin:
            break
        draw_text_centered(draw, line, y, font, color, width=card_width)
        y += line_h
    return y


def _title_start_y(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    single_line_y: int,
    max_width: int = CARD_WIDTH - 16,
) -> int:
    """Return y shifted up when title text will wrap to a second line."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    if tw <= max_width:
        return single_line_y
    line_h = bbox[3] - bbox[1] + 2
    return max(2, single_line_y - line_h // 2)


def _draw_section_divider(draw: ImageDraw.ImageDraw, y: int, w: int) -> None:
    margin = 20
    draw.line([(margin, y), (w - margin, y)], fill=(180, 160, 130), width=2)


_CARD_ICON_W = 42
_CARD_ICON_H = 57
_CARD_ICON_BORDER = 3
_CARD_ICON_INNER = 3
_QUEST_BACK_COLOR = (140, 25, 25)
_INTRIGUE_BACK_COLOR = (60, 60, 60)
_CARD_ICON_FONT = _load_font_serif(28, bold=True)


def _draw_quest_card_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    _draw_card_icon(draw, cx, cy, "Q", _QUEST_BACK_COLOR)


def _draw_intrigue_card_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
) -> None:
    _draw_card_icon(draw, cx, cy, "I", _INTRIGUE_BACK_COLOR)


def _draw_card_icon(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    letter: str,
    back_color: tuple,
) -> None:
    w2 = _CARD_ICON_W // 2
    h2 = _CARD_ICON_H // 2
    b = _CARD_ICON_BORDER
    inn = _CARD_ICON_INNER

    # Black outer border
    draw.rectangle(
        [cx - w2, cy - h2, cx + w2, cy + h2],
        fill=(20, 20, 20),
    )
    # White inner border
    draw.rectangle(
        [cx - w2 + b, cy - h2 + b, cx + w2 - b, cy + h2 - b],
        fill=(240, 240, 240),
    )
    # Card back
    draw.rectangle(
        [cx - w2 + b + inn, cy - h2 + b + inn, cx + w2 - b - inn, cy + h2 - b - inn],
        fill=back_color,
    )
    # Letter — center using full bbox offset
    bbox = draw.textbbox((0, 0), letter, font=_CARD_ICON_FONT)
    tx = cx - (bbox[0] + bbox[2]) // 2
    ty = cy - (bbox[1] + bbox[3]) // 2
    draw.text(
        (tx, ty),
        letter,
        fill=PARCHMENT_COLOR,
        font=_CARD_ICON_FONT,
    )


# Symbol colors for resource icons on quest cards
_SYMBOL_COLORS = {
    "guitarists": (220, 120, 20),  # orange
    "bass_players": (30, 30, 30),  # black
    "drummers": (140, 60, 160),  # purple
    "singers": (240, 240, 240),  # white
    "coins": (210, 180, 50),  # gold
}
_SYMBOL_OUTLINE = (40, 40, 40)
_SYMBOL_SIZE = 36
_SYMBOL_GAP = 10
_SYMBOLS_PER_ROW = 8


def _draw_resource_symbols(
    draw: ImageDraw.ImageDraw,
    cost: ResourceCost,
    y: int,
    card_width: int,
) -> int:
    groups: list[tuple[str, int]] = []
    for field in ("guitarists", "bass_players", "drummers", "singers", "coins"):
        val = getattr(cost, field, 0)
        if val > 0:
            groups.append((field, val))
    if not groups:
        return y

    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP

    # Pack groups into rows, keeping each type together
    rows: list[list[str]] = []
    current_row: list[str] = []
    for res_type, count in groups:
        if current_row and len(current_row) + count > _SYMBOLS_PER_ROW:
            rows.append(current_row)
            current_row = []
        current_row.extend([res_type] * count)
    if current_row:
        rows.append(current_row)

    for row in rows:
        total_w = len(row) * sz + (len(row) - 1) * gap
        start_x = (card_width - total_w) // 2
        for j, res_type in enumerate(row):
            cx = start_x + j * (sz + gap) + sz // 2
            cy = y + sz // 2
            color = _SYMBOL_COLORS[res_type]
            if res_type == "coins":
                r = sz // 2
                draw.ellipse(
                    [cx - r, cy - r, cx + r, cy + r],
                    fill=color,
                    outline=_SYMBOL_OUTLINE,
                    width=2,
                )
            else:
                half = sz // 2
                draw.rectangle(
                    [cx - half, cy - half, cx + half, cy + half],
                    fill=color,
                    outline=_SYMBOL_OUTLINE,
                    width=2,
                )
        y += sz + gap
    return y


def generate_quest_cards() -> int:
    data = json.loads((CONFIG_DIR / "contracts.json").read_text(encoding="utf-8"))
    config = ContractsConfig.model_validate(data)
    OUTPUT_QUESTS.mkdir(parents=True, exist_ok=True)
    cw = QUEST_CARD_WIDTH
    ch = QUEST_CARD_HEIGHT
    cr = QUEST_CORNER_RADIUS
    count = 0
    for card in config.contracts:
        img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [0, 0, cw - 1, ch - 1],
            radius=cr,
            fill=PARCHMENT_COLOR,
        )

        genre = card.genre.value
        genre_color = GENRE_COLORS.get(genre, (80, 80, 80))

        # --- Section 1: Genre color bar ---
        band_h = 60
        draw.rounded_rectangle(
            [0, 0, cw - 1, band_h],
            radius=cr,
            fill=genre_color,
        )
        draw.rectangle(
            [0, band_h - cr, cw - 1, band_h],
            fill=genre_color,
        )
        draw_text_centered(
            draw, genre.upper(), 10, Q_FONT_GENRE, (255, 255, 255), width=cw
        )

        # --- Section 2: Title ---
        y = band_h + 8
        y = draw_text_wrapped(
            draw,
            card.name,
            y,
            Q_FONT_TITLE,
            max_lines=2,
            max_width=cw - 32,
            card_width=cw,
            card_height=ch,
        )
        y += 6
        if card.is_plot_quest:
            draw_text_centered(
                draw, "[PLOT QUEST]", y, Q_FONT_BODY_SMALL, (150, 50, 50), width=cw
            )
            y += 28

        # --- Section 3: Requires ---
        y += 4
        _draw_section_divider(draw, y, cw)
        y += 8
        draw_text_centered(draw, "Requires", y, Q_FONT_SECTION, (100, 70, 30), width=cw)
        y += 28
        y = _draw_resource_symbols(draw, card.cost, y, cw)
        y += 4

        # --- Section 4: Reward ---
        _draw_section_divider(draw, y, cw)
        y += 8
        draw_text_centered(draw, "Reward", y, Q_FONT_SECTION, (100, 70, 30), width=cw)
        y += 28

        # VP
        vp_text = f"{card.victory_points} VP"
        draw_text_centered(draw, vp_text, y, Q_FONT_VP, (140, 100, 10), width=cw)
        y += 48

        # Bonus resources as symbols
        if card.bonus_resources.total() > 0:
            y += 8
            y = _draw_resource_symbols(draw, card.bonus_resources, y, cw)

        # Special rewards
        if card.reward_draw_intrigue:
            draw_text_centered(
                draw,
                f"+{card.reward_draw_intrigue} Intrigue Card",
                y,
                Q_FONT_BODY,
                (80, 50, 20),
                width=cw,
            )
            y += 32
        if card.reward_draw_quests:
            is_choose = card.reward_quest_draw_mode == "choose"
            mode = "Choose" if is_choose else "Draw"
            draw_text_centered(
                draw,
                f"{mode} {card.reward_draw_quests} Quest",
                y,
                Q_FONT_BODY,
                (80, 50, 20),
                width=cw,
            )
            y += 32
        if card.reward_building == "market_choice":
            draw_text_centered(
                draw, "Choose Building", y, Q_FONT_BODY, (80, 50, 20), width=cw
            )
            y += 32
        elif card.reward_building == "random_draw":
            draw_text_centered(
                draw, "Draw Building", y, Q_FONT_BODY, (80, 50, 20), width=cw
            )
            y += 32

        if card.ongoing_benefit_description:
            y += 4
            _draw_section_divider(draw, y, cw)
            y += 8
            y = draw_text_wrapped(
                draw,
                card.ongoing_benefit_description,
                y,
                Q_FONT_BODY_SMALL,
                (80, 50, 20),
                max_width=cw - 32,
                max_lines=3,
                card_width=cw,
                card_height=ch,
            )

        # --- Description ---
        y += 4
        _draw_section_divider(draw, y, cw)
        y += 8
        desc = card.description.replace("—", "-").replace("–", "-")
        y = draw_text_wrapped(
            draw,
            desc,
            y,
            Q_FONT_BODY_SMALL,
            (100, 80, 50),
            max_width=cw - 32,
            max_lines=4,
            card_width=cw,
            card_height=ch,
        )

        img.save(OUTPUT_QUESTS / f"{card.id}.png")
        count += 1
    return count


_TYPE_ABBREV = {
    "guitarists": "G",
    "bass_players": "B",
    "drummers": "D",
    "singers": "S",
    "coins": "$",
}


def _format_choice_reward(choice, fixed_reward) -> str:
    ct = choice.choice_type
    types_str = "/".join(_TYPE_ABBREV.get(t, t) for t in choice.allowed_types)
    fixed_str = format_resources(fixed_reward)
    extra = f" + {fixed_str}" if fixed_str != "None" else ""

    if ct == "pick":
        return f"Pick {choice.pick_count} {types_str}{extra}"
    if ct == "bundle":
        labels = [b.label for b in choice.bundles]
        return "Choose: " + " / ".join(labels[:3])
    if ct == "combo":
        cost_str = ""
        if choice.cost and choice.cost.total() > 0:
            cost_str = f"Pay {format_resources(choice.cost)}, "
        return f"{cost_str}Combo {choice.total} {types_str}"
    if ct == "exchange":
        return f"Trade {choice.pick_count} -> {choice.gain_count} {types_str}"
    return "Choice"


def generate_building_cards() -> int:
    data = json.loads((CONFIG_DIR / "buildings.json").read_text(encoding="utf-8"))
    config = BuildingsConfig.model_validate(data)
    OUTPUT_BUILDINGS.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.buildings:
        img, draw = create_card_base(height=BUILDING_CARD_HEIGHT)
        band_h = 40
        band_color = (30, 70, 30)
        draw.rounded_rectangle(
            [0, 0, CARD_WIDTH - 1, band_h],
            radius=CORNER_RADIUS,
            fill=band_color,
        )
        draw.rectangle(
            [0, band_h - CORNER_RADIUS, CARD_WIDTH - 1, band_h],
            fill=band_color,
        )
        y = _title_start_y(draw, card.name, FONT_TITLE, 8)
        y = draw_text_wrapped(
            draw,
            card.name,
            y,
            FONT_TITLE,
            (255, 255, 255),
            max_lines=2,
        )
        y = band_h + 6
        cost_str = f"Cost: {card.cost_coins} coins"
        draw_text_centered(draw, cost_str, y, FONT_BODY)
        y += 22
        if card.accumulation_type:
            atype = _TYPE_ABBREV.get(card.accumulation_type, card.accumulation_type)
            if card.accumulation_type == "victory_points":
                atype = "VP"
            accum_line = f"Stocks {card.accumulation_per_round}{atype}/round"
            draw_text_centered(draw, accum_line, y, FONT_LABEL, (20, 60, 20))
            y += 18
        elif card.visitor_reward_choice:
            vis_line = _format_choice_reward(
                card.visitor_reward_choice,
                card.visitor_reward,
            )
            draw_text_centered(draw, vis_line, y, FONT_LABEL, (20, 60, 20))
            y += 18
        else:
            vis_str = format_resources(card.visitor_reward)
            vis_parts = []
            if vis_str != "None":
                vis_parts.append(vis_str)
            if card.visitor_reward_vp > 0:
                vis_parts.append(f"+{card.visitor_reward_vp}VP")
            vis_line = f"Visitor: {' '.join(vis_parts) if vis_parts else 'None'}"
            draw_text_centered(draw, vis_line, y, FONT_LABEL, (20, 60, 20))
            y += 18
        if card.visitor_reward_special:
            special = card.visitor_reward_special.replace("_", " ").title()
            draw_text_centered(draw, special, y, FONT_BODY_SMALL, (20, 60, 20))
            y += 16
        own_parts = []
        own_str = format_resources(card.owner_bonus)
        if own_str != "None":
            own_parts.append(own_str)
        if card.owner_bonus_vp > 0:
            own_parts.append(f"+{card.owner_bonus_vp}VP")
        if card.owner_bonus_special:
            special = card.owner_bonus_special.replace("_", " ").title()
            own_parts.append(special)
        if card.owner_bonus_choice:
            types_str = "/".join(
                _TYPE_ABBREV.get(t, t) for t in card.owner_bonus_choice.allowed_types
            )
            own_parts.append(f"Pick 1 {types_str}")
        own_line = f"Owner: {' '.join(own_parts) if own_parts else 'None'}"
        draw_text_centered(draw, own_line, y, FONT_LABEL, (80, 50, 0))
        y += 18
        img.save(OUTPUT_BUILDINGS / f"{card.id}.png")
        count += 1
    return count


def _intrigue_effect_summary(effect_type: str, effect_value: dict) -> str:
    if effect_type in ("gain_resources", "all_players_gain"):
        parts = []
        for k, sym in RESOURCE_SYMBOLS:
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
        for k, sym in RESOURCE_SYMBOLS:
            v = effect_value.get(k, 0)
            if v:
                parts.append(f"{v}{sym}")
        return f"Steal {' '.join(parts)}"
    if effect_type == "opponent_loses":
        parts = []
        for k, sym in RESOURCE_SYMBOLS:
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
    data = json.loads((CONFIG_DIR / "intrigue.json").read_text(encoding="utf-8"))
    config = IntrigueConfig.model_validate(data)
    OUTPUT_INTRIGUE.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.intrigue_cards:
        img, draw = create_card_base()
        y = _title_start_y(draw, card.name, FONT_TITLE, 12)
        y = draw_text_wrapped(
            draw,
            card.name,
            y,
            FONT_TITLE,
            (30, 80, 30),
            max_lines=2,
        )
        y += 4
        draw_text_centered(
            draw,
            "INTRIGUE",
            y,
            FONT_BODY,
            (60, 120, 60),
        )
        y += 22
        y = draw_text_wrapped(
            draw,
            card.description,
            y,
            FONT_BODY_SMALL,
            max_lines=4,
        )
        y += 6
        if card.choice_reward:
            choice_text = _format_choice_reward(
                card.choice_reward,
                ResourceCost(),
            )
            y = draw_text_wrapped(
                draw,
                choice_text,
                y,
                FONT_LABEL,
                (120, 80, 0),
                max_lines=2,
            )
            if card.effect_type == "resource_choice_multi":
                opc = card.choice_reward.others_pick_count
                draw_text_centered(
                    draw,
                    f"Others: Pick {opc}",
                    y,
                    FONT_BODY_SMALL,
                    (150, 50, 50),
                )
                y += 16
        else:
            effect = _intrigue_effect_summary(
                card.effect_type,
                card.effect_value,
            )
            if effect:
                draw_text_centered(
                    draw,
                    effect,
                    y,
                    FONT_LABEL,
                    (120, 80, 0),
                )
                y += 20
        target_label = TARGET_LABELS.get(
            card.effect_target,
            "",
        )
        if target_label:
            draw_text_centered(
                draw,
                target_label,
                y,
                FONT_BODY_SMALL,
                (150, 50, 50),
            )
        img.save(OUTPUT_INTRIGUE / f"{card.id}.png")
        count += 1
    return count


def generate_producer_cards() -> int:
    data = json.loads((CONFIG_DIR / "producers.json").read_text(encoding="utf-8"))
    config = ProducersConfig.model_validate(data)
    OUTPUT_PRODUCERS.mkdir(parents=True, exist_ok=True)
    count = 0
    for card in config.producers:
        img, draw = create_card_base()
        y = _title_start_y(draw, card.name, FONT_TITLE, 12)
        y = draw_text_wrapped(
            draw,
            card.name,
            y,
            FONT_TITLE,
            (100, 50, 100),
            max_lines=2,
        )
        y += 4
        draw_text_centered(
            draw,
            "PRODUCER",
            y,
            FONT_BODY,
            (130, 80, 130),
        )
        y += 24
        genres = ", ".join(g.value.title() for g in card.bonus_genres)
        draw_text_centered(
            draw,
            f"Genres: {genres}",
            y,
            FONT_LABEL,
        )
        y += 22
        vp_str = f"{card.bonus_vp_per_contract}VP/contract"
        draw_text_centered(
            draw,
            vp_str,
            y,
            FONT_VP,
            (120, 80, 0),
        )
        y += 32
        y = draw_text_wrapped(
            draw,
            card.description,
            y,
            FONT_BODY_SMALL,
        )
        img.save(OUTPUT_PRODUCERS / f"{card.id}.png")
        count += 1
    return count


SPECIAL_REWARD_LABELS = {
    "quest_and_coins": "Quest + 2$",
    "quest_and_intrigue": "Quest + Intrigue",
    "reset_quests": "Reset Quests",
    "purchase_building": "Buy Building",
    "first_player_marker_and_intrigue": "1st Player + Intrigue",
    "acquire_contract_or_intrigue": "Contract/Intrigue",
}


def _resource_reward_str(reward: dict) -> str:
    parts = []
    for key, sym in RESOURCE_SYMBOLS:
        val = reward.get(key, 0)
        if val > 0:
            parts.append(f"{val}{sym}")
    return " ".join(parts) if parts else ""


def generate_space_cards() -> int:
    data = json.loads((CONFIG_DIR / "board.json").read_text(encoding="utf-8"))
    spaces = data.get("permanent_spaces", [])
    OUTPUT_SPACES.mkdir(parents=True, exist_ok=True)
    cw = CARD_WIDTH * 2
    ch = SPACE_CARD_HEIGHT * 2
    cr = CORNER_RADIUS * 2
    count = 0

    for space in spaces:
        img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [0, 0, cw - 1, ch - 1],
            radius=cr,
            fill=PARCHMENT_COLOR,
        )
        space_id = space.get("space_id", "")
        name = space.get("name", space_id)

        band_h = 70
        band_color = (50, 70, 100)
        draw.rounded_rectangle(
            [0, 0, cw - 1, band_h],
            radius=cr,
            fill=band_color,
        )
        draw.rectangle(
            [0, band_h - cr, cw - 1, band_h],
            fill=band_color,
        )

        title_y = 10
        bbox = draw.textbbox((0, 0), name, font=Q_FONT_TITLE)
        if bbox[2] - bbox[0] > cw - 32:
            title_y = 4
        draw_text_wrapped(
            draw,
            name,
            title_y,
            Q_FONT_TITLE,
            (255, 255, 255),
            max_lines=2,
            max_width=cw - 32,
            card_width=cw,
            card_height=ch,
        )

        reward = space.get("reward")
        reward_special = space.get("reward_special")
        light_mid = (band_h + ch) // 2

        if reward_special == "first_player_marker_and_intrigue":
            y = band_h + 10
            draw_text_centered(
                draw, "1st Player", y, Q_FONT_LABEL, TEXT_COLOR, width=cw
            )
            bbox = draw.textbbox((0, 0), "1st Player", font=Q_FONT_LABEL)
            text_h = bbox[3] - bbox[1]
            icon_cy = y + text_h + 12 + _CARD_ICON_H // 2
            _draw_intrigue_card_icon(draw, cw // 2, icon_cy)
        elif reward_special == "quest_and_coins":
            coin_sz = _SYMBOL_SIZE
            icon_gap = 12
            coin_gap = _SYMBOL_GAP
            total_w = _CARD_ICON_W + icon_gap + coin_sz * 2 + coin_gap
            left_x = cw // 2 - total_w // 2
            icon_cy = light_mid
            _draw_quest_card_icon(draw, left_x + _CARD_ICON_W // 2, icon_cy)
            coin_x = left_x + _CARD_ICON_W + icon_gap
            for i in range(2):
                ccx = coin_x + i * (coin_sz + coin_gap) + coin_sz // 2
                r = coin_sz // 2
                draw.ellipse(
                    [ccx - r, icon_cy - r, ccx + r, icon_cy + r],
                    fill=_SYMBOL_COLORS["coins"],
                    outline=_SYMBOL_OUTLINE,
                    width=2,
                )
        elif reward_special == "quest_and_intrigue":
            icon_gap = 16
            total_w = _CARD_ICON_W * 2 + icon_gap
            icon_cy = light_mid
            _draw_quest_card_icon(
                draw, cw // 2 - total_w // 2 + _CARD_ICON_W // 2, icon_cy
            )
            _draw_intrigue_card_icon(
                draw, cw // 2 + total_w // 2 - _CARD_ICON_W // 2, icon_cy
            )
        elif reward_special == "reset_quests":
            y = band_h + 10
            draw_text_centered(
                draw, "Reset Quests", y, Q_FONT_LABEL, TEXT_COLOR, width=cw
            )
            bbox = draw.textbbox((0, 0), "Reset Quests", font=Q_FONT_LABEL)
            text_h = bbox[3] - bbox[1]
            icon_cy = y + text_h + 12 + _CARD_ICON_H // 2
            _draw_quest_card_icon(draw, cw // 2, icon_cy)
        elif reward_special:
            label = SPECIAL_REWARD_LABELS.get(
                reward_special,
                reward_special.replace("_", " ").title(),
            )
            bbox = draw.textbbox((0, 0), label, font=Q_FONT_LABEL)
            text_h = bbox[3] - bbox[1]
            y = light_mid - text_h // 2
            draw_text_wrapped(
                draw,
                label,
                y,
                Q_FONT_LABEL,
                TEXT_COLOR,
                max_lines=2,
                max_width=cw - 32,
                card_width=cw,
                card_height=ch,
            )
        elif reward:
            from shared.card_models import ResourceCost

            cost = ResourceCost(**reward)
            total = sum(
                getattr(cost, f, 0)
                for f in ("guitarists", "bass_players", "drummers", "singers", "coins")
            )
            rows = 1 if total <= _SYMBOLS_PER_ROW else 2
            content_h = rows * _SYMBOL_SIZE + (rows - 1) * _SYMBOL_GAP
            y = light_mid - content_h // 2
            _draw_resource_symbols(draw, cost, y, cw)

        img.save(OUTPUT_SPACES / f"{space_id}.png")
        count += 1

    # Backstage slots
    backstage_band_color = (100, 50, 50)
    for slot_num in range(1, 4):
        img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [0, 0, cw - 1, ch - 1],
            radius=cr,
            fill=PARCHMENT_COLOR,
        )
        band_h = 70
        draw.rounded_rectangle(
            [0, 0, cw - 1, band_h],
            radius=cr,
            fill=backstage_band_color,
        )
        draw.rectangle(
            [0, band_h - cr, cw - 1, band_h],
            fill=backstage_band_color,
        )
        draw_text_centered(
            draw,
            f"Backstage {slot_num}",
            14,
            Q_FONT_TITLE,
            (255, 255, 255),
            width=cw,
        )
        bbox = draw.textbbox((0, 0), "Play Intrigue", font=Q_FONT_LABEL)
        text_h = bbox[3] - bbox[1]
        bs_y = (band_h + ch) // 2 - text_h // 2
        draw_text_centered(
            draw,
            "Play Intrigue",
            bs_y,
            Q_FONT_LABEL,
            TEXT_COLOR,
            width=cw,
        )
        img.save(OUTPUT_SPACES / f"backstage_slot_{slot_num}.png")
        count += 1

    return count


JSON_FILES = [
    CONFIG_DIR / "contracts.json",
    CONFIG_DIR / "buildings.json",
    CONFIG_DIR / "intrigue.json",
    CONFIG_DIR / "producers.json",
    CONFIG_DIR / "board.json",
]

OUTPUT_DIRS = [
    OUTPUT_QUESTS,
    OUTPUT_BUILDINGS,
    OUTPUT_INTRIGUE,
    OUTPUT_PRODUCERS,
    OUTPUT_SPACES,
    OUTPUT_MARKERS,
]


def _needs_regeneration() -> bool:
    newest_json = 0.0
    for f in JSON_FILES:
        if not f.exists():
            return False
        newest_json = max(newest_json, f.stat().st_mtime)
    oldest_png = float("inf")
    png_count = 0
    for d in OUTPUT_DIRS:
        if not d.exists():
            return True
        for p in d.glob("*.png"):
            oldest_png = min(oldest_png, p.stat().st_mtime)
            png_count += 1
    if png_count == 0:
        return True
    return newest_json > oldest_png


PLAYER_COLORS = [
    ("red", (255, 0, 0)),
    ("blue", (0, 0, 255)),
    ("green", (0, 128, 0)),
    ("orange", (255, 165, 0)),
    ("purple", (128, 0, 128)),
]

MARKER_SIZE = 36


def generate_worker_markers() -> int:
    OUTPUT_MARKERS.mkdir(parents=True, exist_ok=True)
    count = 0
    for name, color in PLAYER_COLORS:
        img = Image.new("RGBA", (MARKER_SIZE, MARKER_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        r = MARKER_SIZE // 2 - 1
        cx, cy = MARKER_SIZE // 2, MARKER_SIZE // 2
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            fill=(*color, 255),
            outline=(255, 255, 255, 200),
            width=2,
        )
        img.save(OUTPUT_MARKERS / f"worker_{name}.png")
        count += 1
    return count


def generate_all() -> int:
    q = generate_quest_cards()
    b = generate_building_cards()
    i = generate_intrigue_cards()
    p = generate_producer_cards()
    s = generate_space_cards()
    m = generate_worker_markers()
    return q + b + i + p + s + m


def ensure_card_images() -> None:
    if _needs_regeneration():
        print("Card images out of date, regenerating...")
        total = generate_all()
        print(f"Generated {total} card images.")


def main() -> None:
    print("Card Image Generator")
    print(f"Output: {OUTPUT_BASE}")
    print()
    total = generate_all()
    print(f"Done. {total} card images generated.")


if __name__ == "__main__":
    main()
