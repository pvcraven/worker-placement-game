# Data Model: Quest Reward Expansion

## Modified Entities

### ContractCard (shared/card_models.py)

Existing fields (unchanged):
- `id: str` — unique identifier
- `name: str` — display name
- `description: str` — flavor text
- `genre: Genre` — jazz, rock, pop, etc.
- `cost: ResourceCost` — resources required to complete
- `victory_points: int` — VP awarded on completion
- `bonus_resources: ResourceCost` — resources awarded on completion
- `is_plot_quest: bool` — whether this is a plot quest
- `ongoing_benefit_description: str | None` — ongoing benefit text

New fields:
- `reward_draw_intrigue: int = 0` — number of intrigue cards drawn on completion
- `reward_draw_quests: int = 0` — number of quest cards drawn on completion
- `reward_quest_draw_mode: str = "random"` — "random" (from deck) or "choose" (from face-up)
- `reward_building: str | None = None` — building acquisition mode: "market_choice", "random_draw", or None (no building reward)

### GameState (server/models/game.py)

New field:
- `pending_quest_reward: dict | None = None` — tracks interactive reward state when quest completion requires player choice. Contains: player_id, reward_type ("choose_quest" or "choose_building"), available_choices (list of card/building dicts).

## New Message Types (shared/messages.py)

### QuestRewardChoicePrompt (server → client)
- `action: "quest_reward_choice_prompt"`
- `reward_type: str` — "choose_quest" or "choose_building"
- `available_choices: list[dict]` — list of quest cards or buildings the player can choose from
- `quest_name: str` — name of the completed quest (for display context)

### QuestRewardChoiceRequest (client → server)
- `action: "quest_reward_choice"`
- `choice_id: str` — ID of the selected quest card or building

### QuestRewardChoiceResolved (server → all clients)
- `action: "quest_reward_choice_resolved"`
- `player_id: str`
- `reward_type: str` — "choose_quest" or "choose_building"
- `choice: dict` — the selected item details
- `quest_name: str` — name of the completed quest

## Modified Message Types

### QuestCompletedResponse (shared/messages.py)

Existing fields (unchanged):
- `action: "quest_completed"`
- `player_id: str`
- `contract_id: str`
- `contract_name: str`
- `victory_points_earned: int`
- `resources_spent: dict`
- `bonus_resources: dict`
- `next_player_id: str | None`

New fields:
- `drawn_intrigue: list[dict] = []` — full card data for intrigue cards drawn as reward
- `drawn_quests: list[dict] = []` — full card data for quest cards drawn randomly as reward
- `building_granted: dict | None = None` — building tile data if random-draw building was granted
- `pending_choice: bool = False` — True if the player still needs to make an interactive choice (choose quest or choose building)

## Config Data Changes

### contracts.json

Existing quest entries: unchanged (new fields default to 0/None).

New quest entries include new reward fields. Example:

```json
{
  "id": "contract_rock_010",
  "name": "Indie Label Showcase",
  "description": "Put on a showcase that draws the attention of indie scouts.",
  "genre": "rock",
  "cost": {"guitarists": 2, "bass_players": 1, "drummers": 0, "singers": 1, "coins": 0},
  "victory_points": 5,
  "bonus_resources": {"guitarists": 1, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "reward_draw_intrigue": 1,
  "reward_draw_quests": 0,
  "reward_quest_draw_mode": "random",
  "reward_building": null,
  "is_plot_quest": false,
  "ongoing_benefit_description": null
}
```

## Relationships

- ContractCard → ResourceCost (cost, bonus_resources): existing
- ContractCard → reward fields: new, all optional with backward-compatible defaults
- GameState → pending_quest_reward: new, nullable dict for interactive reward flow
- QuestCompletedResponse → drawn card data: new, lists of full card dicts
- QuestRewardChoicePrompt → available choices: references face-up quests or face-up buildings from board state
