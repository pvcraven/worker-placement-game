# WebSocket Message Contracts: Quest Reward Expansion

## Modified Messages

### QuestCompletedResponse (server → all clients)

```json
{
  "action": "quest_completed",
  "player_id": "player_abc",
  "contract_id": "contract_rock_010",
  "contract_name": "Indie Label Showcase",
  "victory_points_earned": 5,
  "resources_spent": {"guitarists": 2, "bass_players": 1, "drummers": 0, "singers": 1, "coins": 0},
  "bonus_resources": {"guitarists": 1, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "drawn_intrigue": [
    {"id": "intrigue_007", "name": "Backstage Pass", "description": "...", "effect_type": "gain_resources", "effect_target": "self", "effect_value": {"guitarists": 1}}
  ],
  "drawn_quests": [
    {"id": "contract_jazz_005", "name": "Soul Revival", "description": "...", "genre": "jazz", "cost": {}, "victory_points": 6, "bonus_resources": {}}
  ],
  "building_granted": null,
  "pending_choice": false,
  "next_player_id": "player_def"
}
```

**Field notes**:
- `drawn_intrigue`: Full card data for each intrigue card drawn. Empty list if no intrigue draw reward. Only includes cards for the completing player.
- `drawn_quests`: Full card data for each quest card drawn randomly. Empty list if none. Only populated for "random" mode draws.
- `building_granted`: Full building tile data if a "random_draw" building was auto-assigned. null otherwise.
- `pending_choice`: True if the player must still make an interactive choice (choose from face-up quests or choose from market buildings). When true, `next_player_id` is null (turn does not advance yet).

## New Messages

### QuestRewardChoicePrompt (server → completing player only)

Sent when a quest has an interactive reward (choose quest from face-up, or choose building from market).

```json
{
  "action": "quest_reward_choice_prompt",
  "reward_type": "choose_quest",
  "available_choices": [
    {"id": "contract_pop_003", "name": "Pop Sensation", "description": "...", "genre": "pop", "cost": {}, "victory_points": 4, "bonus_resources": {}},
    {"id": "contract_rock_002", "name": "Garage Band", "description": "...", "genre": "rock", "cost": {}, "victory_points": 3, "bonus_resources": {}}
  ],
  "quest_name": "Indie Label Showcase"
}
```

For building choice:
```json
{
  "action": "quest_reward_choice_prompt",
  "reward_type": "choose_building",
  "available_choices": [
    {"id": "building_001", "name": "Sun Studio", "description": "...", "cost_coins": 4, "visitor_reward": {}, "owner_bonus": {}},
    {"id": "building_002", "name": "Abbey Road", "description": "...", "cost_coins": 6, "visitor_reward": {}, "owner_bonus": {}}
  ],
  "quest_name": "Legendary Producer"
}
```

### QuestRewardChoiceRequest (client → server)

Player's selection in response to a choice prompt.

```json
{
  "action": "quest_reward_choice",
  "choice_id": "contract_pop_003"
}
```

### QuestRewardChoiceResolved (server → all clients)

Broadcast after the player makes their choice.

```json
{
  "action": "quest_reward_choice_resolved",
  "player_id": "player_abc",
  "reward_type": "choose_quest",
  "choice": {"id": "contract_pop_003", "name": "Pop Sensation", "description": "...", "genre": "pop", "cost": {}, "victory_points": 4},
  "quest_name": "Indie Label Showcase"
}
```

For building choice:
```json
{
  "action": "quest_reward_choice_resolved",
  "player_id": "player_abc",
  "reward_type": "choose_building",
  "choice": {"id": "building_001", "name": "Sun Studio", "description": "...", "cost_coins": 4, "visitor_reward": {}, "owner_bonus": {}},
  "quest_name": "Legendary Producer"
}
```

## Message Flow Diagrams

### Non-Interactive Rewards (VP + resources + random draws)

```
Client                    Server
  |                         |
  |-- complete_quest ------>|
  |                         |-- deduct cost
  |                         |-- award VP + resources
  |                         |-- draw cards from decks
  |                         |-- advance turn
  |<-- quest_completed -----|  (includes drawn_intrigue, drawn_quests, building_granted)
  |                         |
```

### Interactive Rewards (choose quest or choose building)

```
Client                    Server
  |                         |
  |-- complete_quest ------>|
  |                         |-- deduct cost
  |                         |-- award VP + resources + non-interactive rewards
  |                         |-- set pending_quest_reward
  |<-- quest_completed -----|  (pending_choice=true, next_player_id=null)
  |<-- quest_reward_choice_prompt --|  (to completing player only)
  |                         |
  |-- quest_reward_choice ->|
  |                         |-- resolve choice (add card/building)
  |                         |-- clear pending_quest_reward
  |                         |-- advance turn
  |<-- quest_reward_choice_resolved --|  (broadcast to all)
  |                         |
```
