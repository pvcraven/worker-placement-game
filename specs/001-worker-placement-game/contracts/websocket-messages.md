# WebSocket Message Contracts

**Branch**: `001-worker-placement-game` | **Date**: 2026-04-13

## Protocol Overview

- **Transport**: WebSocket (full-duplex)
- **Format**: JSON (UTF-8)
- **Validation**: Pydantic v2 models with discriminated unions on the `action` field
- **Direction**: Client → Server (requests), Server → Client (responses + broadcasts)

All messages have a top-level `action` field used for routing and discriminated union parsing.

## Client → Server Messages

### Lobby Messages

#### `create_game`
```json
{
  "action": "create_game",
  "player_name": "string",
  "max_players": 4
}
```
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | `"create_game"` | yes | Message type |
| player_name | string | yes | Display name (1-30 chars) |
| max_players | int | yes | 2-5 |

#### `join_game`
```json
{
  "action": "join_game",
  "game_code": "string",
  "player_name": "string"
}
```

#### `player_ready`
```json
{
  "action": "player_ready",
  "ready": true
}
```

#### `start_game`
```json
{
  "action": "start_game"
}
```
Host-only. Fails if not all players are ready or fewer than `min_players` joined.

### Gameplay Messages

#### `place_worker`
```json
{
  "action": "place_worker",
  "space_id": "string"
}
```
Places the active player's worker on the specified action space. Server validates: it's the player's turn, they have available workers, and the space is unoccupied.

#### `place_worker_garage`
```json
{
  "action": "place_worker_garage",
  "slot_number": 1,
  "intrigue_card_id": "string"
}
```
Places a worker on a Garage slot and plays the specified intrigue card. Server validates: player has the card, slot is unoccupied.

#### `complete_quest`
```json
{
  "action": "complete_quest",
  "contract_id": "string"
}
```
Completes a contract from the player's hand. Server validates: it's the player's turn, player has resources, one-per-turn limit.

#### `acquire_contract`
```json
{
  "action": "acquire_contract",
  "contract_id": "string",
  "source": "face_up"
}
```
Takes a face-up contract from the Talent Agency (Cliffwatch Inn action). `source` may be `"face_up"` (specific card) or `"deck"` (draw from deck).

#### `acquire_intrigue`
```json
{
  "action": "acquire_intrigue"
}
```
Draws an intrigue card from the deck (Cliffwatch Inn action).

#### `purchase_building`
```json
{
  "action": "purchase_building",
  "building_id": "string",
  "lot_index": 0
}
```
Purchases a building tile and places it on the specified lot. Server validates: Builder's Hall action, sufficient Coins, lot is empty.

#### `reassign_worker`
```json
{
  "action": "reassign_worker",
  "slot_number": 1,
  "target_space_id": "string"
}
```
During Reassignment Phase: moves a Garage worker to the specified action space. Server validates: correct slot order, space unoccupied, not The Garage.

#### `choose_intrigue_target`
```json
{
  "action": "choose_intrigue_target",
  "target_player_id": "string"
}
```
For intrigue cards with `"choose_opponent"` targeting — selects the target player.

### System Messages

#### `reconnect`
```json
{
  "action": "reconnect",
  "game_code": "string",
  "player_name": "string",
  "slot_index": 0
}
```

#### `ping`
```json
{
  "action": "ping"
}
```

## Server → Client Messages

### Lobby Responses

#### `game_created`
```json
{
  "action": "game_created",
  "game_code": "ABC123",
  "player_id": "string",
  "slot_index": 0
}
```

#### `player_joined`
```json
{
  "action": "player_joined",
  "player_name": "string",
  "slot_index": 1,
  "players": [
    {"player_id": "string", "name": "string", "slot_index": 0, "ready": false}
  ]
}
```
Broadcast to all players in the lobby.

#### `player_ready_update`
```json
{
  "action": "player_ready_update",
  "player_id": "string",
  "ready": true
}
```

#### `game_started`
```json
{
  "action": "game_started",
  "game_state": { "...": "full initial game state" }
}
```
Contains the full visible game state for each player (opponent hands hidden).

### Gameplay Broadcasts

#### `worker_placed`
```json
{
  "action": "worker_placed",
  "player_id": "string",
  "space_id": "string",
  "reward_granted": {"guitarists": 2, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "next_player_id": "string"
}
```

#### `worker_placed_garage`
```json
{
  "action": "worker_placed_garage",
  "player_id": "string",
  "slot_number": 1,
  "intrigue_card": {"id": "string", "name": "string", "description": "string"},
  "intrigue_effect": {"type": "string", "details": {}},
  "next_player_id": "string"
}
```

#### `quest_completed`
```json
{
  "action": "quest_completed",
  "player_id": "string",
  "contract_id": "string",
  "contract_name": "string",
  "victory_points_earned": 8,
  "bonus_resources": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 2}
}
```

#### `contract_acquired`
```json
{
  "action": "contract_acquired",
  "player_id": "string",
  "contract_id": "string",
  "new_face_up": {"id": "string", "name": "string", "...": "replacement card, if any"}
}
```

#### `building_constructed`
```json
{
  "action": "building_constructed",
  "player_id": "string",
  "building_id": "string",
  "building_name": "string",
  "lot_index": 0,
  "new_space_id": "string"
}
```

#### `reassignment_phase_start`
```json
{
  "action": "reassignment_phase_start",
  "garage_slots": [
    {"slot_number": 1, "player_id": "string"},
    {"slot_number": 2, "player_id": "string"}
  ]
}
```

#### `worker_reassigned`
```json
{
  "action": "worker_reassigned",
  "player_id": "string",
  "from_slot": 1,
  "to_space_id": "string",
  "reward_granted": {"guitarists": 2, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0}
}
```

#### `round_end`
```json
{
  "action": "round_end",
  "round_number": 3,
  "next_round": 4,
  "first_player_id": "string",
  "bonus_worker_granted": false
}
```

#### `bonus_workers_granted`
```json
{
  "action": "bonus_workers_granted",
  "round": 5,
  "new_worker_count": 4
}
```
Sent at the start of round 5 to all players.

#### `game_over`
```json
{
  "action": "game_over",
  "final_scores": [
    {
      "player_id": "string",
      "player_name": "string",
      "base_vp": 30,
      "producer_bonus": 12,
      "producer_card": {"id": "string", "name": "string"},
      "total_vp": 42,
      "rank": 1
    }
  ],
  "tiebreaker_applied": false
}
```

### State Sync

#### `state_sync`
```json
{
  "action": "state_sync",
  "game_state": { "...": "full visible game state for this player" }
}
```
Sent on reconnection. Contains the complete current game state filtered to what this player is allowed to see.

### Error & System

#### `error`
```json
{
  "action": "error",
  "code": "INVALID_ACTION",
  "message": "It is not your turn."
}
```

**Error codes**:
| Code | Description |
|------|-------------|
| `INVALID_ACTION` | Action not permitted in current state |
| `NOT_YOUR_TURN` | Player acted out of turn |
| `SPACE_OCCUPIED` | Action space already has a worker |
| `INSUFFICIENT_RESOURCES` | Not enough resources for the action |
| `NO_INTRIGUE_CARDS` | Tried to use Garage without intrigue cards |
| `LOBBY_FULL` | Game has maximum players |
| `GAME_NOT_FOUND` | Invalid game code |
| `INVALID_MESSAGE` | Malformed or unrecognized message |

#### `pong`
```json
{
  "action": "pong"
}
```

#### `player_disconnected`
```json
{
  "action": "player_disconnected",
  "player_id": "string",
  "player_name": "string"
}
```

#### `player_reconnected`
```json
{
  "action": "player_reconnected",
  "player_id": "string",
  "player_name": "string"
}
```

#### `turn_timeout`
```json
{
  "action": "turn_timeout",
  "player_id": "string",
  "player_name": "string",
  "skipped": true
}
```

## Pydantic Implementation Notes

### Discriminated Union Pattern

```python
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union

class PlaceWorkerRequest(BaseModel):
    action: Literal["place_worker"] = "place_worker"
    space_id: str

class CompleteQuestRequest(BaseModel):
    action: Literal["complete_quest"] = "complete_quest"
    contract_id: str

# ... other request types

ClientMessage = Annotated[
    Union[PlaceWorkerRequest, CompleteQuestRequest, ...],
    Field(discriminator="action")
]
```

### Message Parsing

```python
import json
from pydantic import TypeAdapter

adapter = TypeAdapter(ClientMessage)

def parse_client_message(raw: str) -> ClientMessage:
    return adapter.validate_json(raw)
```

### Visibility Filtering

The server maintains the full `GameState`. When sending state to a client, it filters:
- Other players' `contract_hand` → send count only
- Other players' `intrigue_hand` → send count only
- Other players' `producer_card` → hidden until game over
- `contract_deck` / `intrigue_deck` → send count only
- All public info (board, resources, completed contracts, VP) sent in full
