# Data Model: Building Purchase System

**Date**: 2026-04-14 | **Branch**: `003-building-purchase`

## Entity Changes

### BuildingTile (shared/card_models.py) — Modified

Existing model with one new field:

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| id | str | JSON config | Unique identifier (e.g., "building_001") |
| name | str | JSON config | Music-themed venue name |
| description | str | JSON config | Flavor text |
| cost_coins | int (3-8) | JSON config | Purchase cost in coins only |
| visitor_reward | ResourceCost | JSON config | Resources granted to any player landing on building |
| visitor_reward_special | str \| None | JSON config | Special effect for visitor (e.g., "draw_contract") |
| owner_bonus | ResourceCost | JSON config | Resources granted to owner when non-owner visits |
| owner_bonus_special | str \| None | JSON config | Special effect for owner |
| **accumulated_vp** | **int** (default 0) | **Runtime** | **NEW — VP accumulated while face-up in market. Set to 1 on entering market, +1 per round.** |

### BoardState (server/models/game.py) — Modified

Changes to building-related fields:

| Field | Change | Notes |
|-------|--------|-------|
| building_supply | **REMOVE** | Replaced by building_deck + face_up_buildings |
| **building_deck** | **ADD**: list[BuildingTile] | Hidden shuffled deck of remaining buildings |
| **face_up_buildings** | **ADD**: list[BuildingTile] | Up to 3 visible buildings in market, each with accumulated_vp |
| building_lots | No change | list[str], e.g., ["lot_0", "lot_1", ...] |
| constructed_buildings | No change | list[str], space_ids of purchased buildings |
| action_spaces | No change | dict[str, ActionSpace] — includes purchased buildings |

### ActionSpace (server/models/game.py) — No Change

Existing model is sufficient. Purchased buildings are already created as ActionSpace entries with `space_type="building"`, `owner_id`, and `building_tile` fields.

### Player (server/models/game.py) — No Change

The `victory_points` field already exists and will receive accumulated VP on building purchase.

### ActionSpaceConfig (server/models/config.py) — Rename Only

The `builders_hall` entry in board.json changes to `real_estate_listings`:
- `space_id`: "builders_hall" → "real_estate_listings"
- `name`: "Builder's Hall" → "Real Estate Listings"
- `space_type`: "builders_hall" → "real_estate_listings"

## State Transitions

### Building Lifecycle

```
[In Deck] → (drawn at game start or after purchase) → [Face-Up in Market, VP=1]
    → (each round end) → [Face-Up, VP += 1]
    → (purchased by player) → [Constructed on Board as ActionSpace]
```

### Face-Up Market State

```
Game Start:
  - Shuffle all 24 buildings into building_deck
  - Draw 3 → face_up_buildings (each gets accumulated_vp = 1)

On Purchase:
  - Remove selected building from face_up_buildings
  - Award accumulated_vp to buyer (player.victory_points += building.accumulated_vp)
  - Deduct cost_coins from buyer
  - Create ActionSpace on board
  - If building_deck is not empty: draw 1, set accumulated_vp = 1, add to face_up_buildings

On Round End:
  - For each building in face_up_buildings: accumulated_vp += 1
```

## Relationships

```
BoardState
  ├── building_deck: list[BuildingTile]        # hidden, 0-21 buildings
  ├── face_up_buildings: list[BuildingTile]     # visible, 0-3 buildings (with VP)
  ├── building_lots: list[str]                  # available lot slots
  ├── constructed_buildings: list[str]          # space_ids of placed buildings
  └── action_spaces: dict[str, ActionSpace]     # includes placed buildings
        └── ActionSpace (type="building")
              ├── owner_id → Player.player_id
              └── building_tile → BuildingTile (snapshot at purchase time)

Player
  ├── victory_points: int                       # receives accumulated_vp on purchase
  └── resources.coins: int                      # deducted on purchase
```

## Validation Rules

- `cost_coins` must be in range 3-8 (enforced by JSON config validation)
- `accumulated_vp` must be >= 1 when in face_up_buildings (initialized on draw)
- `face_up_buildings` length must be <= 3
- A player must have `coins >= building.cost_coins` to purchase
- A building can only be purchased once (removed from face_up_buildings on purchase)
- Owner bonus is only granted when `visitor.player_id != building.owner_id`
