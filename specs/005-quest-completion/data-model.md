# Data Model: Quest Completion

## Existing Entities (no changes needed)

### ContractCard
Already has all fields needed for quest completion:
- `id: str` — unique identifier
- `name: str` — display name
- `cost: ResourceCost` — resources required to complete
- `victory_points: int` — VP awarded on completion
- `bonus_resources: ResourceCost` — extra resources granted on completion
- `genre: str` — card genre (jazz, pop, soul, funk, rock)
- `description: str` — flavor text

### Player
Already has all fields needed:
- `contract_hand: list[ContractCard]` — quests the player holds
- `completed_contracts: list[ContractCard]` — completed quest history
- `resources: PlayerResources` — current resources (checked against quest cost)
- `victory_points: int` — total VP
- `available_workers: int` — workers left to place this round
- `completed_quest_this_turn: bool` — one-per-turn limit flag

### PlayerResources
Already has utility methods:
- `can_afford(cost: ResourceCost) -> bool`
- `deduct(cost: ResourceCost)`
- `add(reward: ResourceCost)`

## New Fields

### GameState (server/models/game.py)
- `waiting_for_quest_completion: bool = False` — set to `True` when the server sends a quest completion prompt; cleared when the player completes or skips.

## State Transitions

```
Worker Placed → Reward Applied → Check Eligibility
                                      │
                                      ├── No eligible quests → _advance_turn()
                                      │
                                      └── Has eligible quests → Send prompt
                                           │                    (waiting_for_quest_completion = True)
                                           │
                                           ├── Player completes quest → Process, clear flag, _advance_turn()
                                           │
                                           └── Player skips → Clear flag, _advance_turn()
```
