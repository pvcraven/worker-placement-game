# WebSocket Message Contracts: Backstage & Intrigue Mechanics

## Existing Messages (already implemented)

### Client → Server

#### PlaceWorkerBackstageRequest
```json
{
  "action": "place_worker_backstage",
  "slot_number": 1,
  "intrigue_card_id": "intrigue_005"
}
```
- `slot_number`: 1-3, the backstage slot to place on
- `intrigue_card_id`: ID of the intrigue card to play from hand

### Server → Client (Broadcast)

#### WorkerPlacedBackstageResponse
```json
{
  "action": "worker_placed_backstage",
  "player_id": "player_abc",
  "slot_number": 2,
  "intrigue_card": { "id": "intrigue_005", "name": "...", ... },
  "intrigue_effect": { "type": "gain_coins", "value": {"coins": 4} },
  "next_player_id": "player_def"
}
```

#### ReassignmentPhaseStartResponse
```json
{
  "action": "reassignment_phase_start",
  "occupied_slots": [
    { "slot_number": 1, "player_id": "player_abc" },
    { "slot_number": 3, "player_id": "player_def" }
  ]
}
```

#### WorkerReassignedResponse
```json
{
  "action": "worker_reassigned",
  "player_id": "player_abc",
  "from_slot": 1,
  "space_id": "the_tavern",
  "reward": { "guitarists": 2 },
  "next_reassignment_player_id": "player_def",
  "next_reassignment_slot": 3
}
```

## New Messages (to be added)

### Server → Client (to specific player)

#### BackstagePromptResponse
Sent to a player during reassignment to indicate it's their turn to place a freed worker.
```json
{
  "action": "backstage_prompt",
  "player_id": "player_abc",
  "slot_number": 1,
  "available_spaces": ["the_tavern", "the_arena", "building_lot_3"]
}
```
- `available_spaces`: List of space_ids the player can choose from (unoccupied, non-backstage)

## Validation Rules

### PlaceWorkerBackstageRequest
- Server validates: game phase is PLACEMENT
- Server validates: it's the requesting player's turn
- Server validates: slot_number slots below this one are all occupied (sequential filling)
- Server validates: the target slot is unoccupied
- Server validates: player has the specified intrigue card in intrigue_hand
- Server validates: player has available_workers > 0

### Reassignment Placement
- Server validates: game phase is REASSIGNMENT
- Server validates: it's the prompted player's turn in the reassignment queue
- Server validates: target space is unoccupied
- Server validates: target space is not a backstage slot
