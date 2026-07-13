# Data Model: Resource Distribution Buildings

**Date**: 2026-06-11

## Modified Entities

### BuildingTile (shared/card_models.py)

**Existing entity** — add 3 new fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `distribute_resource_type` | `str \| None` | `None` | Resource type to place on spaces (e.g., "guitarists", "coins"). None = not a distribution building. |
| `distribute_per_space` | `int` | `0` | Quantity of resources placed on each target space |
| `distribute_space_count` | `int` | `0` | Number of distinct target spaces the owner must select |

**Validation rules**:
- If `distribute_resource_type` is set, `distribute_per_space` must be > 0 and `distribute_space_count` must be > 0
- `distribute_resource_type` must be one of: "guitarists", "bass_players", "drummers", "singers", "coins"

### ActionSpace (server/models/game.py)

**Existing entity** — add 1 new field:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `placed_resources` | `dict[str, int]` | `{}` | Resources placed on this space by distribution buildings. Maps resource type to quantity. Cleared when a visitor collects them. |

**State transitions**:
- Empty → Populated: When a distribution building owner places resources here
- Populated → Accumulated: Additional resources from subsequent placements stack (values add)
- Populated → Empty: When a visitor places their worker and collects all placed resources

### GameState (server/models/game.py)

**Existing entity** — add 1 new pending field:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pending_resource_distribution` | `dict \| None` | `None` | Tracks in-progress distribution target space selection |

**pending_resource_distribution structure**:

```
{
  "player_id": str,           # Who is selecting (building owner, or visitor if unowned)
  "building_space_id": str,   # The building being visited (excluded from targets)
  "resource_type": str,       # What resource to place
  "per_space": int,           # How many per target space
  "remaining_selections": int, # How many more spaces to pick
  "selected_spaces": list[str] # Space IDs already chosen
}
```

## New Config Entries (config/buildings.json)

Five new buildings added to the `buildings` array:

| ID | distribute_resource_type | distribute_per_space | distribute_space_count | cost_coins | visitor_reward | owner_bonus |
|----|-------------------------|---------------------|----------------------|------------|----------------|-------------|
| building_024 | guitarists | 1 | 2 | 7 | 4 guitarists | 2 guitarists |
| building_025 | coins | 2 | 2 | 7 | 8 coins | 4 coins |
| building_026 | singers | 1 | 1 | 7 | 2 singers | 1 singer |
| building_027 | bass_players | 1 | 2 | 7 | 4 bass_players | 2 bass_players |
| building_028 | drummers | 1 | 1 | 7 | 2 drummers | 1 drummer |

## Message Types (shared/messages.py)

### New Messages

| Message | Direction | Fields | Purpose |
|---------|-----------|--------|---------|
| `ResourceDistributionPromptResponse` | Server → Player | `player_id`, `resource_type`, `per_space`, `remaining_selections`, `eligible_spaces` (list of space_id/name), `selected_spaces` | Prompt the selecting player to choose a target space |
| `ResourceDistributionRequest` | Player → Server | `space_id` | Player's target space selection |
| `ResourceDistributionResolvedResponse` | Server → All | `space_id`, `resource_type`, `quantity`, `all_placed_resources` (dict of space_id → placed_resources) | Broadcast that resources were placed on a space |

### Modified Messages

| Message | Change |
|---------|--------|
| `WorkerPlacedResponse` | Add `collected_placed_resources: dict[str, int] \| None` — resources collected from placed_resources pool on the visited space |

## Relationships

```
BuildingTile ──defines──→ distribution parameters
     │                     (resource_type, per_space, space_count)
     │
     └─── on visit ──→ pending_resource_distribution
                           │
                           └─── on selection ──→ ActionSpace.placed_resources
                                                     │
                                                     └─── on future visit ──→ collected by visitor
```
