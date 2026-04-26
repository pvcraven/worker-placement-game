# Data Model: New Special Buildings

## Existing Entities (Modified)

### GameState (server/models/game.py)

New field:
- `pending_showcase_bonus: dict | None = None` — Tracks the contract drawn from the showcase building that is eligible for +4 VP bonus. Format: `{"player_id": str, "contract_id": str, "bonus_vp": int}`. Set when a contract is drawn at the showcase building, cleared after quest completion resolves.

### QuestCompletionPromptResponse (shared/messages.py)

New fields:
- `bonus_quest_id: str | None = None` — ID of the contract eligible for showcase bonus VP. When present, the client renders "+4VP bonus" text under this contract in the quest completion window.
- `bonus_vp: int = 0` — The bonus VP amount (4) for display purposes.

### QuestCompletedResponse (shared/messages.py)

New field:
- `showcase_bonus_vp: int = 0` — The showcase bonus VP awarded (0 or 4). Included so the client can display the bonus in the game log.

## New Entities

### Building Configurations (config/buildings.json)

Two new building entries:

**Royalty Collection Building** (building_021):
- `cost_coins`: 4
- `visitor_reward`: all zeros
- `visitor_reward_special`: `"coins_per_building"`
- `owner_bonus`: `{"coins": 2}`
- `owner_bonus_vp`: 0

**Audition Showcase Building** (building_022):
- `cost_coins`: 4
- `visitor_reward`: all zeros
- `visitor_reward_special`: `"draw_contract_and_complete"`
- `owner_bonus`: all zeros
- `owner_bonus_vp`: 2

## Relationships

- `pending_showcase_bonus.contract_id` → references a `ContractCard.id` in the player's `contract_hand`
- `pending_showcase_bonus.player_id` → references a `Player.player_id`
- `QuestCompletionPromptResponse.bonus_quest_id` → references the same contract ID from `pending_showcase_bonus`
- `BoardState.constructed_buildings` → used by `coins_per_building` to count buildings in play

## State Transitions

### Royalty Collection Visit
```
Worker placed → count constructed_buildings → award N coins → owner bonus → quest completion check
```

### Audition Showcase Visit
```
Worker placed → enter quest selection highlight mode → player selects face-up contract
→ contract added to hand, replacement drawn → set pending_showcase_bonus
→ _check_quest_completion() → quest completion prompt (with bonus annotation)
→ player completes bonus contract (+4 VP) OR completes other/skips (no bonus)
→ clear pending_showcase_bonus → advance turn
```
