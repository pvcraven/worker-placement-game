# Data Model: Resource Choice Rewards

**Feature**: 012-resource-choice-rewards
**Date**: 2026-04-19

## New Entities

### ResourceBundle

A predefined set of resources offered as a single selectable option (used by bundle-type choices).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| label | str | yes | Display label (e.g., "2 Guitarists") |
| resources | ResourceCost | yes | The resource amounts in this bundle |

**Validation**: `label` must be non-empty. `resources` must have at least one non-zero field.

### ResourceChoiceReward

Configuration model defining a choice-based reward on a building or intrigue card.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| choice_type | str | yes | — | One of: "pick", "bundle", "combo", "exchange" |
| allowed_types | list[str] | no | [] | Resource type field names available for selection (e.g., ["guitarists", "bass_players"]) |
| pick_count | int | no | 1 | Number of individual picks (for "pick" mode) |
| total | int | no | 0 | Total to allocate across allowed types (for "combo" mode) |
| bundles | list[ResourceBundle] | no | [] | Predefined options (for "bundle" mode) |
| cost | ResourceCost | no | zeros | Resources that must be spent before choosing (e.g., 2 coins for combo building) |
| gain_count | int | no | 0 | Number of resources to gain in phase 2 (for "exchange" mode) |
| others_pick_count | int | no | 0 | How many resources each other player picks (for multi-player intrigue) |

**Validation rules by choice_type**:
- `"pick"`: `allowed_types` non-empty, `pick_count >= 1`
- `"bundle"`: `bundles` non-empty, each bundle has valid resources
- `"combo"`: `allowed_types` non-empty, `total >= 1`
- `"exchange"`: `allowed_types` non-empty, `pick_count >= 1` (spend count), `gain_count >= 1` (gain count)

## Modified Entities

### BuildingTile (shared/card_models.py)

Added field:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| visitor_reward_choice | ResourceChoiceReward \| None | no | None | If present, visitor must make a resource choice. Fixed `visitor_reward` is still granted alongside. |

When `visitor_reward_choice` is set:
1. Server grants `visitor_reward` immediately (if any non-zero values)
2. Server sends `resource_choice_prompt` to the visiting player
3. Game pauses until player responds with selection
4. Server grants chosen resources

### IntrigueCard (shared/card_models.py)

Added field:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| choice_reward | ResourceChoiceReward \| None | no | None | If present, card triggers a resource choice instead of/alongside the standard effect. |

When `choice_reward` is set:
- `effect_type` should be `"resource_choice"` (for simple choice) or `"resource_choice_multi"` (for multi-player)
- `effect_value` is ignored; the choice_reward config drives resolution
- For multi-player: main player prompted first, then others in turn order

### GameState (server/models/game.py)

Added field:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| pending_resource_choice | dict \| None | no | None | Tracks an active resource choice prompt |

**pending_resource_choice structure**:
```python
{
    "prompt_id": str,          # Unique identifier
    "player_id": str,          # Player currently choosing
    "source_type": str,        # "building" or "intrigue"
    "source_id": str,          # Building or intrigue card ID
    "choice_type": str,        # "pick", "bundle", "combo"
    "allowed_types": list,     # Available resource types
    "pick_count": int,         # For pick mode
    "total": int,              # For combo mode
    "bundles": list,           # For bundle mode
    "is_spend": bool,          # True during exchange spend phase
    "phase": str,              # "spend" or "gain" (for exchange)
    "gain_count": int,         # Resources to gain in phase 2
    "remaining_players": list, # For multi-player: players still to choose
    "others_pick_count": int,  # For multi-player: picks per other player
}
```

## New Messages

### ResourceChoicePromptResponse (Server → Client)

Sent when a player needs to make a resource choice.

| Field | Type | Description |
|-------|------|-------------|
| action | "resource_choice_prompt" | Message discriminator |
| prompt_id | str | Unique prompt identifier |
| player_id | str | Player who must choose |
| choice_type | str | "pick", "bundle", or "combo" |
| title | str | Dialog title |
| description | str | Explanation of the choice |
| allowed_types | list[str] | Resource types available |
| pick_count | int | Number of picks (pick mode) |
| total | int | Total to allocate (combo mode) |
| bundles | list[dict] | Bundle options (bundle mode) |
| is_spend | bool | True if spending/turning in |

### ResourceChoiceRequest (Client → Server)

Player's resource choice selection.

| Field | Type | Description |
|-------|------|-------------|
| action | "resource_choice" | Message discriminator |
| prompt_id | str | Matching prompt identifier |
| chosen_resources | dict | ResourceCost dict of selected resources |

### ResourceChoiceResolvedResponse (Server → Client)

Broadcast to all players when a choice is resolved.

| Field | Type | Description |
|-------|------|-------------|
| action | "resource_choice_resolved" | Message discriminator |
| player_id | str | Player who made the choice |
| chosen_resources | dict | What was selected |
| is_spend | bool | Whether resources were spent or gained |
| source_description | str | Human-readable source (building/card name) |
| next_player_id | str \| None | Next player's turn (None if more prompts pending) |

## Config Examples

### New Building: Pick 1 musician + 2 coins (US1)
```json
{
    "id": "building_025",
    "name": "Musician's Union Hall",
    "cost_coins": 4,
    "visitor_reward": {"coins": 2},
    "visitor_reward_choice": {
        "choice_type": "pick",
        "allowed_types": ["guitarists", "bass_players", "drummers", "singers"],
        "pick_count": 1
    },
    "owner_bonus": {"coins": 1}
}
```

### New Building: Pick 2 non-coin resources (US1)
```json
{
    "id": "building_026",
    "name": "Open Audition Stage",
    "cost_coins": 5,
    "visitor_reward_choice": {
        "choice_type": "pick",
        "allowed_types": ["guitarists", "bass_players", "drummers", "singers"],
        "pick_count": 2
    },
    "owner_bonus": {"coins": 1}
}
```

### New Building: Spend 2 coins, combo 4 G/B (US3)
```json
{
    "id": "building_027",
    "name": "Guitar & Bass Workshop",
    "cost_coins": 6,
    "visitor_reward_choice": {
        "choice_type": "combo",
        "allowed_types": ["guitarists", "bass_players"],
        "total": 4,
        "cost": {"coins": 2}
    },
    "owner_bonus": {"coins": 2}
}
```

### New Building: Exchange 2 for 3 (US4)
```json
{
    "id": "building_028",
    "name": "Talent Agency",
    "cost_coins": 7,
    "visitor_reward_choice": {
        "choice_type": "exchange",
        "allowed_types": ["guitarists", "bass_players", "drummers", "singers"],
        "pick_count": 2,
        "gain_count": 3
    },
    "owner_bonus": {"coins": 2}
}
```

### New Intrigue Card: Bundle choice (US2)
```json
{
    "id": "intrigue_051",
    "name": "Talent Scout's Find",
    "effect_type": "resource_choice",
    "choice_reward": {
        "choice_type": "bundle",
        "bundles": [
            {"label": "1 Singer", "resources": {"singers": 1}},
            {"label": "1 Drummer", "resources": {"drummers": 1}},
            {"label": "2 Guitarists", "resources": {"guitarists": 2}},
            {"label": "2 Bass Players", "resources": {"bass_players": 2}},
            {"label": "4 Coins", "resources": {"coins": 4}}
        ]
    }
}
```

### New Intrigue Card: Multi-player pick (US5)
```json
{
    "id": "intrigue_052",
    "name": "Industry Showcase",
    "effect_type": "resource_choice_multi",
    "choice_reward": {
        "choice_type": "pick",
        "allowed_types": ["guitarists", "bass_players", "drummers", "singers"],
        "pick_count": 2,
        "others_pick_count": 1
    }
}
```

## Relationships

```
BuildingTile --has-optional--> ResourceChoiceReward --contains--> ResourceBundle[]
IntrigueCard --has-optional--> ResourceChoiceReward --contains--> ResourceBundle[]
GameState --has-optional--> pending_resource_choice (dict)
ResourceChoiceReward --> ResourceCost (for cost, bundle resources)
```
