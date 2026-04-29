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
OUTPUT_ICONS = OUTPUT_BASE / "icons"

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

# Building card dimensions (2x base) and fonts
BLD_CARD_WIDTH = CARD_WIDTH * 2
BLD_CARD_HEIGHT = BUILDING_CARD_HEIGHT * 2
BLD_CORNER_RADIUS = CORNER_RADIUS * 2

B_FONT_TITLE = _load_font(30, bold=True)
B_FONT_BODY = _load_font(26)
B_FONT_BODY_SMALL = _load_font(22)
B_FONT_LABEL = _load_font(24, bold=True)

# Intrigue card dimensions (2x base) and fonts
INT_CARD_WIDTH = CARD_WIDTH * 2
INT_CARD_HEIGHT = CARD_HEIGHT * 2
INT_CORNER_RADIUS = CORNER_RADIUS * 2

I_FONT_TITLE = _load_font(34, bold=True)
I_FONT_BODY = _load_font(30)
I_FONT_BODY_SMALL = _load_font(26)
I_FONT_LABEL = _load_font(28, bold=True)


def create_card_base(
    width: int = CARD_WIDTH,
    height: int = CARD_HEIGHT,
    corner_radius: int = CORNER_RADIUS,
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        [0, 0, width - 1, height - 1],
        radius=corner_radius,
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


def _draw_color_band(
    draw: ImageDraw.ImageDraw,
    card_width: int,
    band_h: int,
    color: tuple,
    corner_radius: int,
) -> None:
    draw.rounded_rectangle(
        [0, 0, card_width - 1, band_h],
        radius=corner_radius,
        fill=color,
    )
    draw.rectangle(
        [0, band_h - corner_radius, card_width - 1, band_h],
        fill=color,
    )


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
_RESOURCE_FIELDS = ("guitarists", "bass_players", "drummers", "singers", "coins")


def _resource_groups(cost: ResourceCost) -> list[tuple[str, int]]:
    return [
        (f, getattr(cost, f, 0)) for f in _RESOURCE_FIELDS if getattr(cost, f, 0) > 0
    ]


def _resource_icon_list(cost: ResourceCost) -> list[str]:
    icons: list[str] = []
    for field in _RESOURCE_FIELDS:
        v = getattr(cost, field, 0)
        icons.extend([field] * v)
    return icons


def _draw_resource_symbols(
    draw: ImageDraw.ImageDraw,
    cost: ResourceCost,
    y: int,
    card_width: int,
) -> int:
    groups = _resource_groups(cost)
    if not groups:
        return y

    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP

    # Pack groups into rows, keeping each type together when possible
    rows: list[list[str]] = []
    current_row: list[str] = []
    for res_type, count in groups:
        if current_row and len(current_row) + count > _SYMBOLS_PER_ROW:
            rows.append(current_row)
            current_row = []
        remaining = count
        while remaining > 0:
            space = _SYMBOLS_PER_ROW - len(current_row)
            batch = min(remaining, space)
            current_row.extend([res_type] * batch)
            remaining -= batch
            if len(current_row) >= _SYMBOLS_PER_ROW:
                rows.append(current_row)
                current_row = []
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


_ALL_NON_COIN = {"guitarists", "bass_players", "drummers", "singers"}
_PICK_QUESTION_FONT = _load_font(28, bold=True)


def _draw_any_resource_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    sz = _SYMBOL_SIZE
    half = sz // 2
    color = _SYMBOL_COLORS["singers"]
    draw.rectangle(
        [cx - half, cy - half, cx + half, cy + half],
        fill=color,
        outline=_SYMBOL_OUTLINE,
        width=2,
    )
    bbox = draw.textbbox((0, 0), "?", font=_PICK_QUESTION_FONT)
    tx = cx - (bbox[0] + bbox[2]) // 2
    ty = cy - (bbox[1] + bbox[3]) // 2
    draw.text((tx, ty), "?", fill=(40, 40, 40), font=_PICK_QUESTION_FONT)


def _draw_single_symbol(
    draw: ImageDraw.ImageDraw, res_type: str, cx: int, cy: int
) -> None:
    sz = _SYMBOL_SIZE
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


def _draw_special_icon(
    draw: ImageDraw.ImageDraw,
    special: str,
    y: int,
    card_width: int,
) -> int:
    icon_h = _CARD_ICON_H
    cy = y + icon_h // 2
    if special == "draw_intrigue":
        _draw_intrigue_card_icon(draw, card_width // 2, cy)
    elif special == "draw_contract":
        _draw_quest_card_icon(draw, card_width // 2, cy)
    elif special == "draw_contract_and_complete":
        _draw_quest_card_icon(draw, card_width // 2, cy)
        y += icon_h + 2
        draw_text_centered(
            draw,
            "+4 VP if completed",
            y,
            B_FONT_BODY_SMALL,
            (20, 60, 20),
            width=card_width,
        )
        return y + 28
    elif special == "copy_occupied_space":
        label = "Use an opponent's occupied space"
        draw_text_centered(
            draw, label, y, B_FONT_BODY_SMALL, (20, 60, 20), width=card_width
        )
        return y + 28
    else:
        label = special.replace("_", " ").title()
        draw_text_centered(
            draw, label, y, B_FONT_BODY_SMALL, (20, 60, 20), width=card_width
        )
        return y + 28
    return y + icon_h + _SYMBOL_GAP


def _draw_pick_choice(
    draw: ImageDraw.ImageDraw,
    choice,
    y: int,
    card_width: int,
) -> int:
    types = choice.allowed_types
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    cy = y + sz // 2

    pick_count = getattr(choice, "pick_count", 1) or 1

    if set(types) >= _ALL_NON_COIN:
        icon_gap = sz + gap
        total_w = pick_count * sz + (pick_count - 1) * gap
        start_x = (card_width - total_w) // 2
        for i in range(pick_count):
            cx = start_x + i * icon_gap + sz // 2
            _draw_any_resource_icon(draw, cx, cy)
        return y + sz + gap

    slash_font = B_FONT_LABEL
    slash_bbox = draw.textbbox((0, 0), "/", font=slash_font)
    slash_w = slash_bbox[2] - slash_bbox[0]

    n = len(types)
    total_w = n * sz + (n - 1) * (gap + slash_w + gap)

    pick_label = f"Pick {pick_count}" if pick_count > 1 else "Pick"
    pick_bbox = draw.textbbox((0, 0), pick_label, font=slash_font)
    pick_w = pick_bbox[2] - pick_bbox[0]
    pick_gap = 10
    total_with_pick = pick_w + pick_gap + total_w
    start_x = (card_width - total_with_pick) // 2

    draw.text(
        (start_x, cy - (pick_bbox[3] - pick_bbox[1]) // 2),
        pick_label,
        fill=TEXT_COLOR,
        font=slash_font,
    )
    icon_x = start_x + pick_w + pick_gap

    for i, res_type in enumerate(types):
        cx = icon_x + sz // 2
        _draw_single_symbol(draw, res_type, cx, cy)
        icon_x += sz
        if i < n - 1:
            icon_x += gap
            draw.text(
                (icon_x, cy - (slash_bbox[3] - slash_bbox[1]) // 2),
                "/",
                fill=TEXT_COLOR,
                font=slash_font,
            )
            icon_x += slash_w + gap

    return y + sz + gap


def _draw_labeled_any_icons(
    draw: ImageDraw.ImageDraw,
    label: str,
    count: int,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = B_FONT_LABEL
    bbox = draw.textbbox((0, 0), label, font=font)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1]
    label_gap = 10
    icons_w = count * sz + (count - 1) * gap
    total_w = label_w + label_gap + icons_w
    start_x = (card_width - total_w) // 2
    cy = y + sz // 2
    draw.text(
        (start_x, cy - label_h // 2),
        label,
        fill=TEXT_COLOR,
        font=font,
    )
    icon_x = start_x + label_w + label_gap
    for i in range(count):
        cx = icon_x + sz // 2
        _draw_any_resource_icon(draw, cx, cy)
        icon_x += sz + gap
    return y + sz + gap


def _draw_stocks_line(
    draw: ImageDraw.ImageDraw,
    res_type: str,
    per_round: int,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = B_FONT_LABEL
    stocks_text = "Stocks"
    round_text = "/round"
    s_bbox = draw.textbbox((0, 0), stocks_text, font=font)
    r_bbox = draw.textbbox((0, 0), round_text, font=font)
    s_w = s_bbox[2] - s_bbox[0]
    s_h = s_bbox[3] - s_bbox[1]
    r_w = r_bbox[2] - r_bbox[0]
    text_gap = 8
    icons_w = per_round * sz + (per_round - 1) * gap
    total_w = s_w + text_gap + icons_w + text_gap + r_w
    start_x = (card_width - total_w) // 2
    cy = y + sz // 2

    draw.text(
        (start_x, cy - s_h // 2),
        stocks_text,
        fill=(20, 60, 20),
        font=font,
    )
    icon_x = start_x + s_w + text_gap
    for i in range(per_round):
        cx = icon_x + sz // 2
        _draw_single_symbol(draw, res_type, cx, cy)
        icon_x += sz + gap
    icon_x -= gap
    icon_x += text_gap
    draw.text(
        (icon_x, cy - s_h // 2),
        round_text,
        fill=(20, 60, 20),
        font=font,
    )
    return y + sz + gap


def _draw_labeled_resource_row(
    draw: ImageDraw.ImageDraw,
    label: str,
    cost: ResourceCost,
    y: int,
    card_width: int,
) -> int:
    icons = _resource_icon_list(cost)
    if not icons:
        return y

    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = B_FONT_LABEL
    bbox = draw.textbbox((0, 0), label, font=font)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1]
    label_gap = 10
    n = len(icons)
    icons_w = n * sz + (n - 1) * gap
    total_w = label_w + label_gap + icons_w
    start_x = (card_width - total_w) // 2
    cy = y + sz // 2

    draw.text(
        (start_x, cy - label_h // 2),
        label,
        fill=TEXT_COLOR,
        font=font,
    )
    icon_x = start_x + label_w + label_gap
    for res_type in icons:
        cx = icon_x + sz // 2
        _draw_single_symbol(draw, res_type, cx, cy)
        icon_x += sz + gap

    return y + sz + gap


def _draw_labeled_resource_icons(
    draw: ImageDraw.ImageDraw,
    label: str,
    res_type: str,
    count: int,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = B_FONT_LABEL
    bbox = draw.textbbox((0, 0), label, font=font)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1]
    label_gap = 10
    icons_w = count * sz + (count - 1) * gap
    total_w = label_w + label_gap + icons_w
    start_x = (card_width - total_w) // 2
    cy = y + sz // 2
    draw.text(
        (start_x, cy - label_h // 2),
        label,
        fill=TEXT_COLOR,
        font=font,
    )
    icon_x = start_x + label_w + label_gap
    for i in range(count):
        cx = icon_x + sz // 2
        _draw_single_symbol(draw, res_type, cx, cy)
        icon_x += sz + gap
    return y + sz + gap


def _draw_labeled_type_icons_with_slashes(
    draw: ImageDraw.ImageDraw,
    label: str,
    types: list[str],
    total: int,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = B_FONT_LABEL
    row_h = sz + gap
    margin = 20

    slash_bbox = draw.textbbox((0, 0), "/", font=font)
    slash_w = slash_bbox[2] - slash_bbox[0]

    n_types = len(types)
    slash_group_w = n_types * sz + (n_types - 1) * (gap + slash_w + gap)
    group_gap = gap * 2
    avail_w = card_width - margin * 2

    # Label on its own line
    draw_text_centered(draw, label, y, font, TEXT_COLOR, width=card_width)
    y += 30

    # Figure out how many groups fit per row
    per_row = total
    for candidate in range(total, 0, -1):
        row_w = candidate * slash_group_w + (candidate - 1) * group_gap
        if row_w <= avail_w:
            per_row = candidate
            break

    remaining = total
    while remaining > 0:
        count = min(per_row, remaining)
        row_w = count * slash_group_w + (count - 1) * group_gap
        start_x = (card_width - row_w) // 2
        cur_x = start_x
        cy = y + sz // 2

        for g in range(count):
            for i, res_type in enumerate(types):
                cx = cur_x + sz // 2
                _draw_single_symbol(draw, res_type, cx, cy)
                cur_x += sz
                if i < n_types - 1:
                    cur_x += gap
                    draw.text(
                        (cur_x, cy - (slash_bbox[3] - slash_bbox[1]) // 2),
                        "/",
                        fill=TEXT_COLOR,
                        font=font,
                    )
                    cur_x += slash_w + gap
            if g < count - 1:
                cur_x += group_gap

        y += row_h
        remaining -= count

    return y


def _draw_combo_choice(
    draw: ImageDraw.ImageDraw,
    choice,
    y: int,
    card_width: int,
) -> int:
    cost = choice.cost
    if cost and cost.coins > 0:
        y = _draw_labeled_resource_icons(
            draw, "Cost:", "coins", cost.coins, y, card_width
        )
    elif cost and cost.total() > 0:
        cost_str = format_resources(cost)
        draw_text_centered(
            draw, f"Cost: {cost_str}", y, B_FONT_LABEL, TEXT_COLOR, width=card_width
        )
        y += _SYMBOL_SIZE + _SYMBOL_GAP

    types = choice.allowed_types
    total = choice.total
    y = _draw_labeled_type_icons_with_slashes(
        draw, "Reward:", types, total, y, card_width
    )
    return y


def _draw_exchange_choice(
    draw: ImageDraw.ImageDraw,
    choice,
    y: int,
    card_width: int,
) -> int:
    cost_count = getattr(choice, "pick_count", 2) or 2
    gain_count = getattr(choice, "gain_count", 3) or 3
    y = _draw_labeled_any_icons(draw, "Cost:", cost_count, y, card_width)
    y = _draw_labeled_any_icons(draw, "Reward:", gain_count, y, card_width)
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
        img, draw = create_card_base(cw, ch, cr)

        genre = card.genre.value
        genre_color = GENRE_COLORS.get(genre, (80, 80, 80))

        # --- Section 1: Genre color bar ---
        band_h = 60
        _draw_color_band(draw, cw, band_h, genre_color, cr)
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


def _draw_building_title(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    center_x: int,
    max_width: int,
    card_height: int,
) -> None:
    words = text.split()
    lines: list[str] = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=B_FONT_TITLE)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    for line in lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=B_FONT_TITLE)
        tw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1] + 2
        draw.text(
            (center_x - tw // 2, y), line, fill=(255, 255, 255), font=B_FONT_TITLE
        )
        y += lh


def generate_building_cards() -> int:
    data = json.loads((CONFIG_DIR / "buildings.json").read_text(encoding="utf-8"))
    config = BuildingsConfig.model_validate(data)
    OUTPUT_BUILDINGS.mkdir(parents=True, exist_ok=True)
    cw = BLD_CARD_WIDTH
    ch = BLD_CARD_HEIGHT
    cr = BLD_CORNER_RADIUS
    count = 0
    for card in config.buildings:
        img, draw = create_card_base(cw, ch, cr)

        band_h = 80
        band_color = (30, 70, 30)
        _draw_color_band(draw, cw, band_h, band_color, cr)

        # Cost diamond in upper-left, centered vertically on the band
        diamond_sz = 36
        diamond_cx = 10 + diamond_sz
        diamond_cy = band_h // 2
        diamond_pts = [
            (diamond_cx, diamond_cy - diamond_sz),
            (diamond_cx + diamond_sz, diamond_cy),
            (diamond_cx, diamond_cy + diamond_sz),
            (diamond_cx - diamond_sz, diamond_cy),
        ]
        draw.polygon(diamond_pts, fill=(210, 180, 50), outline=(40, 40, 40), width=3)
        cost_text = str(card.cost_coins)
        bbox = draw.textbbox((0, 0), cost_text, font=B_FONT_TITLE)
        tx = diamond_cx - (bbox[0] + bbox[2]) // 2
        ty = diamond_cy - (bbox[1] + bbox[3]) // 2
        draw.text((tx, ty), cost_text, fill=TEXT_COLOR, font=B_FONT_TITLE)

        # Title — centered in the area right of the diamond
        title_left = diamond_cx + diamond_sz + 8
        title_area_w = cw - title_left - 8
        title_center_x = title_left + title_area_w // 2
        title_y = _title_start_y(
            draw, card.name, B_FONT_TITLE, 16, max_width=title_area_w
        )
        _draw_building_title(draw, card.name, title_y, title_center_x, title_area_w, ch)

        y = band_h + 10

        # "Visitor:" label (skip for cramped cards)
        if card.id != "building_014":
            draw_text_centered(draw, "Visitor:", y, B_FONT_LABEL, TEXT_COLOR, width=cw)
            y += 34

        # Visitor reward value
        if card.accumulation_type:
            if card.accumulation_type == "victory_points":
                accum_line = f"Stocks {card.accumulation_per_round}VP/round"
                draw_text_centered(
                    draw, accum_line, y, B_FONT_LABEL, (20, 60, 20), width=cw
                )
                y += 32
            else:
                y = _draw_stocks_line(
                    draw,
                    card.accumulation_type,
                    card.accumulation_per_round,
                    y,
                    cw,
                )
        else:
            # Draw base resource reward (if any)
            has_resources = card.visitor_reward.total() > 0
            if has_resources and card.visitor_reward_vp == 0:
                y = _draw_resource_symbols(draw, card.visitor_reward, y, cw)
            elif has_resources or card.visitor_reward_vp > 0:
                vis_parts = []
                vis_str = format_resources(card.visitor_reward)
                if vis_str != "None":
                    vis_parts.append(vis_str)
                if card.visitor_reward_vp > 0:
                    vis_parts.append(f"+{card.visitor_reward_vp}VP")
                vis_line = " ".join(vis_parts) if vis_parts else ""
                if vis_line:
                    draw_text_centered(
                        draw, vis_line, y, B_FONT_LABEL, (20, 60, 20), width=cw
                    )
                    y += 32

            # Draw choice reward (if any)
            if card.visitor_reward_choice:
                vc = card.visitor_reward_choice
                if vc.choice_type == "pick":
                    y = _draw_pick_choice(draw, vc, y, cw)
                elif vc.choice_type == "exchange":
                    y = _draw_exchange_choice(draw, vc, y, cw)
                elif vc.choice_type == "combo":
                    y = _draw_combo_choice(draw, vc, y, cw)
                else:
                    vis_line = _format_choice_reward(vc, card.visitor_reward)
                    draw_text_centered(
                        draw, vis_line, y, B_FONT_LABEL, (20, 60, 20), width=cw
                    )
                    y += 32
        if card.visitor_reward_special:
            y = _draw_special_icon(draw, card.visitor_reward_special, y, cw)

        # Owner bonus
        has_own_resources = card.owner_bonus.total() > 0
        simple_owner = (
            has_own_resources
            and card.owner_bonus_vp == 0
            and not card.owner_bonus_special
            and not card.owner_bonus_choice
        )
        if simple_owner:
            y = _draw_labeled_resource_row(draw, "Owner:", card.owner_bonus, y, cw)
        else:
            draw_text_centered(draw, "Owner:", y, B_FONT_LABEL, TEXT_COLOR, width=cw)
            y += 34

            if has_own_resources or card.owner_bonus_vp > 0:
                own_parts = []
                own_str = format_resources(card.owner_bonus)
                if own_str != "None":
                    own_parts.append(own_str)
                if card.owner_bonus_vp > 0:
                    own_parts.append(f"+{card.owner_bonus_vp}VP")
                own_line = " ".join(own_parts) if own_parts else ""
                if own_line:
                    draw_text_centered(
                        draw, own_line, y, B_FONT_LABEL, (80, 50, 0), width=cw
                    )
                    y += 32

            if card.owner_bonus_special:
                y = _draw_special_icon(draw, card.owner_bonus_special, y, cw)

            if card.owner_bonus_choice:
                oc = card.owner_bonus_choice
                if oc.choice_type == "pick":
                    y = _draw_pick_choice(draw, oc, y, cw)
                elif oc.choice_type == "exchange":
                    y = _draw_exchange_choice(draw, oc, y, cw)
                elif oc.choice_type == "combo":
                    y = _draw_combo_choice(draw, oc, y, cw)
                else:
                    own_line = _format_choice_reward(oc, card.owner_bonus)
                    draw_text_centered(
                        draw, own_line, y, B_FONT_LABEL, (80, 50, 0), width=cw
                    )

            if (
                not has_own_resources
                and not card.owner_bonus_choice
                and card.owner_bonus_vp == 0
                and not card.owner_bonus_special
            ):
                draw_text_centered(draw, "None", y, B_FONT_LABEL, (80, 50, 0), width=cw)

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


def _draw_intrigue_effect_icons(
    draw: ImageDraw.ImageDraw,
    effect_type: str,
    effect_value: dict,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP

    if effect_type in (
        "gain_resources",
        "all_players_gain",
        "steal_resources",
        "opponent_loses",
    ):
        prefix = ""
        if effect_type == "steal_resources":
            prefix = "Steal"
        elif effect_type == "opponent_loses":
            prefix = "Opponent loses"
        elif effect_type == "all_players_gain":
            prefix = ""

        icons: list[str] = []
        for field in _RESOURCE_FIELDS:
            v = effect_value.get(field, 0)
            icons.extend([field] * v)

        if not icons:
            return y

        font = I_FONT_LABEL
        label_w = 0
        label_gap = 10
        if prefix:
            bbox = draw.textbbox((0, 0), prefix, font=font)
            label_w = bbox[2] - bbox[0]

        n = len(icons)
        icons_w = n * sz + (n - 1) * gap
        total_w = icons_w + (label_w + label_gap if prefix else 0)
        start_x = (card_width - total_w) // 2
        cy = y + sz // 2

        if prefix:
            bbox = draw.textbbox((0, 0), prefix, font=font)
            label_h = bbox[3] - bbox[1]
            draw.text(
                (start_x, cy - label_h // 2),
                prefix,
                fill=(120, 80, 0),
                font=font,
            )
            start_x += label_w + label_gap

        for i, res_type in enumerate(icons):
            cx = start_x + i * (sz + gap) + sz // 2
            _draw_single_symbol(draw, res_type, cx, cy)

        y += sz + gap

        if effect_type == "all_players_gain":
            draw_text_centered(
                draw,
                "(all players)",
                y,
                I_FONT_BODY_SMALL,
                (150, 50, 50),
                width=card_width,
            )
            y += 32

        return y

    if effect_type == "gain_coins":
        c = effect_value.get("coins", 0)
        if c > 0:
            icons_w = c * sz + (c - 1) * gap
            start_x = (card_width - icons_w) // 2
            cy = y + sz // 2
            for i in range(c):
                cx = start_x + i * (sz + gap) + sz // 2
                _draw_single_symbol(draw, "coins", cx, cy)
            y += sz + gap
        return y

    if effect_type == "draw_contracts":
        n = effect_value.get("count", 1)
        icon_h = _CARD_ICON_H
        icons_w = n * _CARD_ICON_W + (n - 1) * gap
        start_x = (card_width - icons_w) // 2
        cy = y + icon_h // 2
        for i in range(n):
            cx = start_x + i * (_CARD_ICON_W + gap) + _CARD_ICON_W // 2
            _draw_quest_card_icon(draw, cx, cy)
        return y + icon_h + gap

    if effect_type == "draw_intrigue":
        n = effect_value.get("count", 1)
        icon_h = _CARD_ICON_H
        icons_w = n * _CARD_ICON_W + (n - 1) * gap
        start_x = (card_width - icons_w) // 2
        cy = y + icon_h // 2
        for i in range(n):
            cx = start_x + i * (_CARD_ICON_W + gap) + _CARD_ICON_W // 2
            _draw_intrigue_card_icon(draw, cx, cy)
        return y + icon_h + gap

    if effect_type == "vp_bonus":
        vp = effect_value.get("victory_points", 0)
        if vp:
            draw_text_centered(
                draw, f"+{vp} VP", y, I_FONT_LABEL, (120, 80, 0), width=card_width
            )
            y += 40
        return y

    effect = _intrigue_effect_summary(effect_type, effect_value)
    if effect:
        draw_text_centered(
            draw, effect, y, I_FONT_LABEL, (120, 80, 0), width=card_width
        )
        y += 40
    return y


def _draw_intrigue_bundle(
    draw: ImageDraw.ImageDraw,
    choice,
    y: int,
    card_width: int,
) -> int:
    sz = _SYMBOL_SIZE
    gap = _SYMBOL_GAP
    font = I_FONT_LABEL
    slash_bbox = draw.textbbox((0, 0), "/", font=font)
    slash_w = slash_bbox[2] - slash_bbox[0]

    draw_text_centered(draw, "Choose one:", y, font, TEXT_COLOR, width=card_width)
    y += 34

    bundle_icons: list[list[str]] = []
    for bundle in choice.bundles:
        bundle_icons.append(_resource_icon_list(bundle.resources))

    all_groups = bundle_icons

    # Calculate width of each group
    group_widths = []
    for icons in all_groups:
        gw = len(icons) * sz + (len(icons) - 1) * gap
        group_widths.append(gw)

    slash_space = gap + slash_w + gap
    avail_w = card_width - 40
    # Try to fit on one row; if not, split into rows
    rows: list[list[int]] = []
    current_row: list[int] = []
    current_w = 0
    for i, gw in enumerate(group_widths):
        needed = gw + (slash_space if current_row else 0)
        if current_row and current_w + needed > avail_w:
            rows.append(current_row)
            current_row = [i]
            current_w = gw
        else:
            current_row.append(i)
            current_w += needed
    if current_row:
        rows.append(current_row)

    for row_indices in rows:
        row_w = sum(group_widths[i] for i in row_indices)
        row_w += (len(row_indices) - 1) * slash_space
        start_x = (card_width - row_w) // 2
        cy = y + sz // 2
        cur_x = start_x

        for j, gi in enumerate(row_indices):
            icons = all_groups[gi]
            for k, res_type in enumerate(icons):
                cx = cur_x + sz // 2
                _draw_single_symbol(draw, res_type, cx, cy)
                cur_x += sz + gap
            cur_x -= gap
            if j < len(row_indices) - 1:
                cur_x += gap
                draw.text(
                    (cur_x, cy - (slash_bbox[3] - slash_bbox[1]) // 2),
                    "/",
                    fill=TEXT_COLOR,
                    font=font,
                )
                cur_x += slash_w + gap

        y += sz + gap

    return y


def generate_intrigue_cards() -> int:
    data = json.loads((CONFIG_DIR / "intrigue.json").read_text(encoding="utf-8"))
    config = IntrigueConfig.model_validate(data)
    OUTPUT_INTRIGUE.mkdir(parents=True, exist_ok=True)
    cw = INT_CARD_WIDTH
    ch = INT_CARD_HEIGHT
    cr = INT_CORNER_RADIUS
    count = 0
    for card in config.intrigue_cards:
        img, draw = create_card_base(cw, ch, cr)

        band_h = 80
        band_color = (60, 60, 60)
        _draw_color_band(draw, cw, band_h, band_color, cr)

        title_y = _title_start_y(draw, card.name, I_FONT_TITLE, 16, max_width=cw - 32)
        draw_text_wrapped(
            draw,
            card.name,
            title_y,
            I_FONT_TITLE,
            (255, 255, 255),
            max_lines=2,
            max_width=cw - 32,
            card_width=cw,
            card_height=ch,
        )

        y = band_h + 14

        # Effect icons / text
        if card.choice_reward:
            cr_obj = card.choice_reward
            if cr_obj.choice_type == "pick":
                y = _draw_pick_choice(draw, cr_obj, y, cw)
            elif cr_obj.choice_type == "bundle":
                y = _draw_intrigue_bundle(draw, cr_obj, y, cw)
            else:
                choice_text = _format_choice_reward(cr_obj, ResourceCost())
                y = draw_text_wrapped(
                    draw,
                    choice_text,
                    y,
                    I_FONT_LABEL,
                    (120, 80, 0),
                    max_lines=2,
                    max_width=cw - 32,
                    card_width=cw,
                    card_height=ch,
                )
            if card.effect_type == "resource_choice_multi":
                opc = cr_obj.others_pick_count
                draw_text_centered(
                    draw,
                    f"Others: Pick {opc}",
                    y,
                    I_FONT_BODY_SMALL,
                    (150, 50, 50),
                    width=cw,
                )
                y += 32
        else:
            y = _draw_intrigue_effect_icons(
                draw, card.effect_type, card.effect_value, y, cw
            )

        target_label = TARGET_LABELS.get(card.effect_target, "")
        if target_label:
            draw_text_centered(
                draw,
                target_label,
                y,
                I_FONT_BODY_SMALL,
                (150, 50, 50),
                width=cw,
            )
            y += 32

        # Description at bottom
        y += 8
        _draw_section_divider(draw, y, cw)
        y += 10
        draw_text_wrapped(
            draw,
            card.description,
            y,
            I_FONT_BODY_SMALL,
            max_lines=4,
            max_width=cw - 32,
            card_width=cw,
            card_height=ch,
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
        if len(card.bonus_genres) >= 5:
            genres = "All"
        else:
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
        img, draw = create_card_base(cw, ch, cr)
        space_id = space.get("space_id", "")
        name = space.get("name", space_id)

        band_h = 70
        band_color = (50, 70, 100)
        _draw_color_band(draw, cw, band_h, band_color, cr)

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
        img, draw = create_card_base(cw, ch, cr)
        band_h = 70
        _draw_color_band(draw, cw, band_h, backstage_band_color, cr)
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
    OUTPUT_ICONS,
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


_ICON_SIZE = 72
_ICON_OUTLINE_WIDTH = 4


def generate_resource_icons() -> int:
    OUTPUT_ICONS.mkdir(parents=True, exist_ok=True)
    icon_map = {
        "guitarist": "guitarists",
        "bass_player": "bass_players",
        "drummer": "drummers",
        "singer": "singers",
        "coin": "coins",
    }
    count = 0
    sz = _ICON_SIZE
    for filename, res_key in icon_map.items():
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = _SYMBOL_COLORS[res_key]
        if res_key == "coins":
            r = sz // 2 - 2
            cx, cy = sz // 2, sz // 2
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=color,
                outline=_SYMBOL_OUTLINE,
                width=_ICON_OUTLINE_WIDTH,
            )
        else:
            margin = 2
            draw.rectangle(
                [margin, margin, sz - 1 - margin, sz - 1 - margin],
                fill=color,
                outline=_SYMBOL_OUTLINE,
                width=_ICON_OUTLINE_WIDTH,
            )
        img.save(OUTPUT_ICONS / f"{filename}.png")
        count += 1
    return count


_CARD_ICON_PNG_W = _CARD_ICON_W * 2
_CARD_ICON_PNG_H = _CARD_ICON_H * 2
_CARD_ICON_PNG_BORDER = _CARD_ICON_BORDER * 2
_CARD_ICON_PNG_INNER = _CARD_ICON_INNER * 2
_CARD_ICON_PNG_FONT = _load_font_serif(56, bold=True)


def generate_card_icon_pngs() -> int:
    OUTPUT_ICONS.mkdir(parents=True, exist_ok=True)
    icons = [
        ("quest_icon", "Q", _QUEST_BACK_COLOR),
        ("intrigue_icon", "I", _INTRIGUE_BACK_COLOR),
    ]
    count = 0
    w, h = _CARD_ICON_PNG_W, _CARD_ICON_PNG_H
    b = _CARD_ICON_PNG_BORDER
    inn = _CARD_ICON_PNG_INNER
    cx, cy = w // 2, h // 2
    for filename, letter, back_color in icons:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, w - 1, h - 1], fill=(20, 20, 20))
        draw.rectangle([b, b, w - 1 - b, h - 1 - b], fill=(240, 240, 240))
        draw.rectangle(
            [b + inn, b + inn, w - 1 - b - inn, h - 1 - b - inn], fill=back_color
        )
        bbox = draw.textbbox((0, 0), letter, font=_CARD_ICON_PNG_FONT)
        tx = cx - (bbox[0] + bbox[2]) // 2
        ty = cy - (bbox[1] + bbox[3]) // 2
        draw.text((tx, ty), letter, fill=PARCHMENT_COLOR, font=_CARD_ICON_PNG_FONT)
        img.save(OUTPUT_ICONS / f"{filename}.png")
        count += 1
    return count


def generate_all() -> int:
    q = generate_quest_cards()
    b = generate_building_cards()
    i = generate_intrigue_cards()
    p = generate_producer_cards()
    s = generate_space_cards()
    m = generate_worker_markers()
    ri = generate_resource_icons()
    ci = generate_card_icon_pngs()
    return q + b + i + p + s + m + ri + ci


def ensure_card_images() -> None:
    if _needs_regeneration():
        print("Card images out of date, regenerating...")
        total = generate_all()
        print(f"Generated {total} card images.")


def main() -> None:
    print("Card Image Generator")
    print(f"Output: {OUTPUT_BASE}")
    print()
    if "--icons-only" in sys.argv:
        ri = generate_resource_icons()
        ci = generate_card_icon_pngs()
        total = ri + ci
        print(f"Done. {total} icon images generated.")
    elif "--spaces-only" in sys.argv:
        total = generate_space_cards()
        print(f"Done. {total} space cards generated.")
    else:
        total = generate_all()
        print(f"Done. {total} card images generated.")


if __name__ == "__main__":
    main()
