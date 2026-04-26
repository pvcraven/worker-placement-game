# Data Model: Resource Trigger Plot Quests

## Modified Entities

### ContractCard (shared/card_models.py)

New fields added to the existing `ContractCard` model:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `resource_trigger_type` | `str \| None` | `None` | Resource type that activates this trigger. Values: `"guitarists"`, `"bass_players"`, `"coins"`, `"singers"`. `None` means no trigger. |
| `resource_trigger_bonus` | `ResourceCost` | `ResourceCost()` | Bonus resources granted automatically when trigger fires. |
| `resource_trigger_draw_intrigue` | `int` | `0` | Number of intrigue cards drawn when trigger fires. |
| `resource_trigger_is_swap` | `bool` | `False` | If true, prompts player to optionally exchange 1 non-trigger resource for 1 of the trigger resource type. |

### Card Data (config/contracts.json)

Five cards receive new trigger fields:

| Card ID | Card Name | trigger_type | trigger_bonus | trigger_draw_intrigue | trigger_is_swap |
|---------|-----------|-------------|---------------|----------------------|-----------------|
| `contract_rock_001` | Rock Loyalty Program | `"guitarists"` | `{guitarists: 1}` | 0 | false |
| `contract_funk_002` | Explore the Groove Archive | `"guitarists"` | — | 1 | false |
| `contract_soul_004` | Miracle at the Microphone | `"singers"` | — | 0 | true |
| `contract_jazz_002` | Fence Bootleg Recordings | `"bass_players"` | `{coins: 2}` | 0 | false |
| `contract_pop_010` | Payola Pipeline | `"coins"` | `{bass_players: 1}` | 0 | false |

## Modified Messages (shared/messages.py)

### WorkerPlacedResponse

| New Field | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger_bonuses` | `list[dict]` | `[]` | List of trigger results. Each entry: `{"quest_name": str, "bonus_resources": dict, "intrigue_drawn": int}` |

### WorkerReassignedResponse

| New Field | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger_bonuses` | `list[dict]` | `[]` | Same structure as WorkerPlacedResponse. |

## Relationships

- A player's `completed_contracts` list is scanned for trigger matches every time that player receives resources from a board action.
- Trigger evaluation happens AFTER the main reward is granted but BEFORE any quest completion prompt.
- The Singer swap trigger reuses the existing `ResourceChoicePromptResponse` / `ResourceChoiceResolvedResponse` flow with `choice_type = "exchange"`.

## Validation Rules

- `resource_trigger_type` must be one of: `"guitarists"`, `"bass_players"`, `"drummers"`, `"singers"`, `"coins"`, or `None`.
- If `resource_trigger_is_swap` is true, `resource_trigger_bonus` and `resource_trigger_draw_intrigue` should be zero (the swap IS the bonus).
- Triggers do not cascade — only original board action rewards are evaluated.
