# Data Model: Intrigue Draw Building

## Entities

### BuildingTile (existing — no schema changes)

The new building uses the existing `BuildingTile` Pydantic model in `shared/card_models.py`. No new fields are needed.

| Field | Type | Value for Whisper Room |
|-------|------|----------------------|
| id | str | `"building_024"` |
| name | str | `"Whisper Room"` |
| description | str | `"A hidden back room where label insiders trade secrets and confidential intel — two pieces of valuable information for every visitor."` |
| cost_coins | int | `4` |
| visitor_reward | ResourceCost | all zeros |
| visitor_reward_special | str \| None | `"draw_intrigue_2"` |
| visitor_reward_choice | ResourceChoiceReward \| None | `null` |
| owner_bonus | ResourceCost | all zeros |
| owner_bonus_vp | int | `2` |
| owner_bonus_choice | ResourceChoiceReward \| None | `null` |

### WorkerPlacedResponse reward_granted dict (existing — new keys)

The `reward_granted` dict in `WorkerPlacedResponse` gains these keys when the building is visited:

| Key | Type | Description |
|-----|------|-------------|
| `intrigue_cards_drawn` | int | Number of intrigue cards drawn (2, or fewer if deck depleted) |
| `drawn_intrigue_cards` | list[dict] | List of drawn intrigue card dicts (model_dump), sent only to the visiting player |

These keys coexist with the existing `drawn_intrigue_card` (singular) used by castle draws.

## Relationships

- **Building → Intrigue Deck**: On visit, pops up to 2 cards from `state.board.intrigue_deck`
- **Building → Player**: Drawn cards appended to `player.intrigue_hand`
- **Building → Owner**: Owner receives 2 VP via `owner_bonus_vp` field (existing mechanism)

## State Transitions

No new state transitions. The building uses the standard immediate-reward flow:
1. Worker placed on building space
2. Base visitor_reward granted (all zeros for this building)
3. visitor_reward_special `draw_intrigue_2` triggers: pop up to 2 cards from deck
4. Owner bonus granted if visitor is not owner
5. Turn advances via standard post-action flow
