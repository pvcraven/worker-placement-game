# Data Model: Building Revamp

## Entity Changes

### BuildingTile (shared/card_models.py) — MODIFY

Current fields (unchanged):
- `id: str`
- `name: str`
- `description: str`
- `cost_coins: int`
- `visitor_reward: ResourceCost`
- `visitor_reward_special: str | None` (draw_contract, draw_intrigue)
- `visitor_reward_choice: ResourceChoiceReward | None`
- `owner_bonus: ResourceCost`
- `owner_bonus_special: str | None`
- `accumulated_vp: int` (existing: VP for unpurchased buildings in market)

New fields:
- `accumulation_type: str | None = None` — Resource key being accumulated ("guitarists", "bass_players", "drummers", "singers", "coins", "victory_points"), or None for standard buildings
- `accumulation_per_round: int = 0` — Amount added to stock at each round start
- `accumulation_initial: int = 0` — Starting stock when building is purchased
- `accumulated_stock: int = 0` — Current accumulated count (runtime state, not persisted in JSON config)
- `visitor_reward_vp: int = 0` — Victory points granted to visitor (separate from ResourceCost)
- `owner_bonus_vp: int = 0` — Victory points granted to owner when visited
- `owner_bonus_choice: ResourceChoiceReward | None = None` — Owner chooses from allowed resource types

### ResourceCost (shared/card_models.py) — NO CHANGE

VP is NOT added to ResourceCost. VP is tracked separately via `player.victory_points` and granted via explicit fields on BuildingTile (`visitor_reward_vp`, `owner_bonus_vp`).

### ActionSpace (server/models/game.py) — NO CHANGE

Already carries `building_tile: BuildingTile | None` which will contain the new fields.

### PlayerState (server/models/game.py) — NO CHANGE

VP already tracked via `victory_points: int`. Building rewards that grant VP will add to this field directly.

## State Transitions

### Accumulating Building Lifecycle

```
[In Market / Face-up]
    │
    ├── Player purchases building
    │   └── accumulated_stock = accumulation_initial (e.g., 2)
    │
    ├── Building acquired free (quest reward)
    │   └── accumulated_stock = 0
    │
    v
[Constructed / In Play]
    │
    ├── Round Start (_end_round)
    │   └── accumulated_stock += accumulation_per_round
    │
    ├── Player visits (not owner)
    │   ├── Visitor gets: accumulated_stock of accumulation_type
    │   ├── Owner gets: owner_bonus (fixed) + owner_bonus_vp + owner_bonus_choice
    │   └── accumulated_stock = 0
    │
    └── Owner visits own building
        ├── Owner gets: accumulated_stock of accumulation_type
        ├── Owner does NOT get owner_bonus
        └── accumulated_stock = 0
```

### Owner Bonus Choice Flow

```
[Visitor places worker on building with owner_bonus_choice]
    │
    ├── Visitor receives visitor_reward + visitor_reward_vp + visitor_reward_special
    │
    ├── Server sends ResourceChoicePrompt to OWNER (not visitor)
    │   └── choice_type: "pick", pick_count: 1, allowed_types: [type_a, type_b]
    │
    ├── Owner selects resource type
    │
    ├── Server validates and grants chosen resource to owner
    │
    └── Game continues (check quest completion, advance turn)
```

## JSON Config Changes

### buildings.json — Full Replacement

All 28 existing buildings removed. 20 new buildings added. Example entries:

**Accumulating building (Category A)**:
```json
{
  "id": "building_001",
  "name": "TBD from existing names",
  "description": "TBD",
  "cost_coins": 4,
  "visitor_reward": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "visitor_reward_special": null,
  "visitor_reward_choice": null,
  "owner_bonus": {"guitarists": 1, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "owner_bonus_special": null,
  "owner_bonus_vp": 0,
  "owner_bonus_choice": null,
  "accumulation_type": "guitarists",
  "accumulation_per_round": 2,
  "accumulation_initial": 2
}
```

**Standard building with owner choice (Category D)**:
```json
{
  "id": "building_015",
  "name": "TBD",
  "description": "TBD",
  "cost_coins": 8,
  "visitor_reward": {"guitarists": 2, "bass_players": 0, "drummers": 0, "singers": 1, "coins": 0},
  "visitor_reward_special": null,
  "visitor_reward_choice": null,
  "owner_bonus": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "owner_bonus_special": null,
  "owner_bonus_vp": 0,
  "owner_bonus_choice": {
    "choice_type": "pick",
    "allowed_types": ["guitarists", "singers"],
    "pick_count": 1
  }
}
```

**VP-accumulating building (A6)**:
```json
{
  "id": "building_006",
  "name": "TBD",
  "description": "TBD",
  "cost_coins": 4,
  "visitor_reward": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "visitor_reward_special": "draw_contract",
  "visitor_reward_choice": null,
  "visitor_reward_vp": 0,
  "owner_bonus": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "owner_bonus_special": null,
  "owner_bonus_vp": 2,
  "owner_bonus_choice": null,
  "accumulation_type": "victory_points",
  "accumulation_per_round": 3,
  "accumulation_initial": 3
}
```

## Validation Rules

- `cost_coins` must be 3-8 (existing rule, unchanged)
- If `accumulation_type` is set, `accumulation_per_round` must be > 0
- If `accumulation_type` is null, `accumulation_per_round` and `accumulation_initial` must be 0
- `owner_bonus_choice` and `owner_bonus` are mutually exclusive when owner_bonus_choice has non-zero resources (if owner_bonus_choice is set, owner_bonus should be zero-resource but owner_bonus_vp may still apply)
- `visitor_reward_vp` and `owner_bonus_vp` must be >= 0
- Building IDs must be unique (existing rule)
