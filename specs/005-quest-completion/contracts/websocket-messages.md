# WebSocket Message Contracts: Quest Completion

## New Messages

### QuestCompletionPromptResponse (server → active player only)

Sent after a worker placement resolves when the active player has one or more completable quests.

```json
{
  "action": "quest_completion_prompt",
  "completable_quests": [
    {
      "id": "contract_001",
      "name": "Jazz Festival",
      "genre": "jazz",
      "cost": {"guitarists": 2, "singers": 1, "bass_players": 0, "drummers": 0, "coins": 0},
      "victory_points": 8,
      "bonus_resources": {"guitarists": 0, "singers": 0, "bass_players": 0, "drummers": 0, "coins": 2},
      "description": "Host a legendary jazz festival"
    }
  ]
}
```

**Delivery**: Sent via `send_to_player()` (not broadcast) — only the active player sees the prompt.

### SkipQuestCompletionRequest (client → server)

Sent when the player clicks "Skip" on the quest completion dialog.

```json
{
  "action": "skip_quest_completion"
}
```

## Existing Messages (reused, no changes)

### CompleteQuestRequest (client → server)

Already exists. Sent when player selects a quest card from the completion dialog.

```json
{
  "action": "complete_quest",
  "contract_id": "contract_001"
}
```

### QuestCompletedResponse (server → all players)

Already exists. Broadcast after a quest is successfully completed.

```json
{
  "action": "quest_completed",
  "player_id": "player_123",
  "contract_id": "contract_001",
  "contract_name": "Jazz Festival",
  "victory_points_earned": 8,
  "bonus_resources": {"guitarists": 0, "singers": 0, "bass_players": 0, "drummers": 0, "coins": 2}
}
```

## Flow Sequence

```
1. Client sends: place_worker (or place_worker_backstage)
2. Server processes placement, applies reward
3. Server checks player's contract_hand against resources
4. IF eligible quests exist:
   a. Server sends quest_completion_prompt to active player
   b. Server sets waiting_for_quest_completion = True
   c. Player sends either:
      - complete_quest (with contract_id) → Server processes, broadcasts quest_completed, advances turn
      - skip_quest_completion → Server advances turn
5. IF no eligible quests:
   a. Server calls _advance_turn() immediately
```
