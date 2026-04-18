# Data Model: Card Image Generator

**Feature**: Card Image Generator
**Date**: 2026-04-18

## Existing Models (reused, not created)

All card data models already exist in the codebase. The card generator imports them directly.

### ContractCard (`shared/card_models.py`)

| Field | Type | Notes |
|-------|------|-------|
| id | str | Used for output filename |
| name | str | Displayed on card, truncated at 20 chars |
| description | str | Multi-line text area |
| genre | Genre (StrEnum) | Determines header band color |
| cost | ResourceCost | Guitarists, bass, drums, singers, coins |
| victory_points | int | Prominent display |
| bonus_resources | ResourceCost | Optional bonus line |
| reward_draw_intrigue | int | Bonus: draw intrigue cards |
| reward_draw_quests | int | Bonus: draw quest cards |
| reward_quest_draw_mode | str | "random" or "choose" |
| reward_building | str or None | "market_choice" or "random_draw" |
| is_plot_quest | bool | Visual marker if true |
| ongoing_benefit_description | str or None | Displayed if present |

### BuildingTile (`shared/card_models.py`)

| Field | Type | Notes |
|-------|------|-------|
| id | str | Used for output filename |
| name | str | Displayed on card |
| description | str | Multi-line text area |
| cost_coins | int | "Cost: N coins" |
| visitor_reward | ResourceCost | Resource summary |
| visitor_reward_special | str or None | "draw_contract", "draw_intrigue" |
| owner_bonus | ResourceCost | Resource summary |
| owner_bonus_special | str or None | Special bonus text |

### IntrigueCard (`shared/card_models.py`)

| Field | Type | Notes |
|-------|------|-------|
| id | str | Used for output filename |
| name | str | Displayed on card |
| description | str | Multi-line text area |
| effect_type | str | Determines effect summary rendering |
| effect_target | str | "self", "choose_opponent", "all" |
| effect_value | dict | Resource amounts or counts |

### ProducerCard (`shared/card_models.py`)

| Field | Type | Notes |
|-------|------|-------|
| id | str | Used for output filename |
| name | str | Displayed on card |
| description | str | Multi-line text area |
| bonus_genres | list[Genre] | Genre names displayed |
| bonus_vp_per_contract | int | "+N VP per contract" |

## Config Loaders (reused)

From `server/models/config.py`:

| Config Class | Root Key | Card Model | JSON File |
|-------------|----------|------------|-----------|
| ContractsConfig | contracts | ContractCard | config/contracts.json |
| IntrigueConfig | intrigue_cards | IntrigueCard | config/intrigue.json |
| BuildingsConfig | buildings | BuildingTile | config/buildings.json |
| ProducersConfig | producers | ProducerCard | config/producers.json |

## New Data (card generator only)

No new persistent data models are introduced. The card generator defines rendering constants (colors, font sizes, layout coordinates) as module-level constants in `generate_cards.py`.

### Rendering Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| CARD_WIDTH | 190 | Output image width in pixels |
| CARD_HEIGHT | 230 | Output image height in pixels |
| PARCHMENT_COLOR | ~(235, 220, 185) | Card background fill |
| TEXT_COLOR | ~(60, 40, 20) | Dark brown text |
| CORNER_RADIUS | ~12 | Rounded rectangle corner radius |
| GENRE_COLORS | dict[Genre, tuple] | Header band colors per genre |
