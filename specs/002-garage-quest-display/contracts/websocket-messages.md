# WebSocket Message Contracts: Garage Quest Display

**Date**: 2026-04-13 | **Feature**: 002-garage-quest-display

## New Messages

### Client → Server

#### SelectQuestCardRequest

Sent after a player places a worker on Garage Spot 1 or 2, to choose one of the face-up quest cards.

```json
{
  "action": "select_quest_card",
  "card_id": "contract_jazz_003"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | `"select_quest_card"` | Yes | Discriminator |
| `card_id` | `string` | Yes | ID of the face-up quest card the player selects |

**Validation**: Card must be in the face-up display. Player must be in the "awaiting quest selection" state (placed worker on Spot 1 or 2 this turn).

#### PlaceWorkerBackstageRequest (renamed from PlaceWorkerGarageRequest)

```json
{
  "action": "place_worker_backstage",
  "slot_number": 1,
  "intrigue_card_id": "intrigue_012"
}
```

### Server → Client

#### FaceUpQuestsUpdatedResponse

Broadcast to all players whenever the face-up quest display changes (card taken, reset, or initial deal).

```json
{
  "action": "face_up_quests_updated",
  "face_up_quests": [
    {
      "id": "contract_jazz_003",
      "name": "Late Night Sessions",
      "genre": "jazz",
      "cost": {"guitarists": 2, "bass_players": 1, "drummers": 0, "singers": 0, "coins": 0},
      "victory_points": 6,
      "description": "Assemble a jazz trio for late night club performances."
    },
    ...
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `action` | `"face_up_quests_updated"` | Discriminator |
| `face_up_quests` | `list[ContractCard]` | Current face-up cards (0-4 cards). Empty slots are omitted. |

#### QuestCardSelectedResponse

Sent to all players when a player selects a quest card from the face-up display.

```json
{
  "action": "quest_card_selected",
  "player_id": "abc123",
  "card_id": "contract_jazz_003",
  "spot_number": 1,
  "bonus_reward": {"coins": 2},
  "next_player_id": "def456"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `action` | `"quest_card_selected"` | Discriminator |
| `player_id` | `string` | Player who selected the card |
| `card_id` | `string` | ID of the selected card (for log/display; card details hidden from opponents) |
| `spot_number` | `int` | 1 or 2 (which spot was used) |
| `bonus_reward` | `dict` | Additional reward granted (Spot 1: coins, Spot 2: intrigue card drawn) |
| `next_player_id` | `string | null` | Next player's turn, or null if round continues |

#### QuestsResetResponse

Broadcast when Spot 3 (reset) is used.

```json
{
  "action": "quests_reset",
  "player_id": "abc123",
  "deck_reshuffled": false,
  "next_player_id": "def456"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `action` | `"quests_reset"` | Discriminator |
| `player_id` | `string` | Player who triggered the reset |
| `deck_reshuffled` | `bool` | Whether the discard pile was reshuffled into the deck |
| `next_player_id` | `string | null` | Next player's turn |

Note: This is immediately followed by a `face_up_quests_updated` message with the new cards.

#### WorkerPlacedBackstageResponse (renamed from WorkerPlacedGarageResponse)

```json
{
  "action": "worker_placed_backstage",
  "player_id": "abc123",
  "slot_number": 1,
  "intrigue_card": { ... },
  "next_player_id": "def456"
}
```

## Modified Messages

### PlaceWorkerRequest (existing)

Now handles garage spots. When a player places a worker on `the_garage_1`, `the_garage_2`, or `the_garage_3`, the server recognizes the `"garage"` space type and triggers the appropriate flow:
- Spots 1 & 2: Server responds with `worker_placed` + puts player in "awaiting quest selection" state. Client shows the card selection dialog.
- Spot 3: Server responds with `worker_placed` + `quests_reset` + `face_up_quests_updated`.

### StateSync (existing)

The `game_state.board` object in state sync messages now includes:
- `face_up_quests`: Array of face-up quest card data
- `backstage_slots`: Renamed from `garage_slots`

## Removed Messages

| Old Message | Replacement |
|-------------|-------------|
| `PlaceWorkerGarageRequest` | `PlaceWorkerBackstageRequest` |
| `WorkerPlacedGarageResponse` | `WorkerPlacedBackstageResponse` |
