# Data Model: The Green Room — Intrigue Quest Space

## Modified Entities

### BoardState (server/models/game.py)

No new fields needed. The Green Room uses existing `action_spaces` and `constructed_buildings` fields.

### GameState (server/models/game.py)

No new fields needed. Reuses existing pending state fields:
- `pending_placement: dict | None` — stores placement info for unwind (existing)
- `pending_play_intrigue: dict | None` — stores intrigue play prompt state (existing, spec 019)
- `pending_intrigue_target: dict | None` — stores target selection for targeted intrigue effects (existing)

The `pending_play_intrigue` dict gains a new `"source"` value: `"green_room"` (alongside existing `None` for quest completion source).

### ActionSpace (server/models/game.py)

No new fields. The Green Room is configured via existing fields:
- `space_type: "permanent"`
- `reward_special: "play_intrigue_and_quest"` (new value for existing field)
- `reward: {}` (no base resource reward)
- `slots: 1`

### board.json (config/board.json)

New entry added to `permanent_spaces` array:

| Field | Value |
|-------|-------|
| `space_id` | `"the_green_room"` |
| `name` | `"The Green Room"` |
| `space_type` | `"permanent"` |
| `reward` | `{}` (empty — no base resources) |
| `reward_special` | `"play_intrigue_and_quest"` |
| `slots` | `1` |

## Modified Messages (shared/messages.py)

### WorkerPlacedResponse (existing)

No changes needed. The response already includes `space_id` which the client uses to determine the UI flow.

### IntriguePlayPromptResponse (existing)

No changes needed. Already sends `intrigue_hand` to the player. Will be sent after worker placement on The Green Room.

### PlayIntrigueFromQuestRequest (existing)

Reused as-is. The client sends this with the selected `intrigue_card_id`.

### QuestCardSelectedResponse (existing)

The `spot_number` field will use a new value (3) to identify The Green Room as the source:
- 0 = building draw
- 1 = quest_and_coins (Sunset Records)
- 2 = quest_and_intrigue (The Back Room) / reset_quests (The Garage)
- 3 = play_intrigue_and_quest (The Green Room) — **new value**

## State Transitions

```
Player places worker on The Green Room
    │
    ├─ Player has no intrigue cards → Error, placement rejected (no worker consumed)
    │
    ├─ Player has intrigue cards:
    │   ├─ Set pending_placement (for unwind)
    │   ├─ Set pending_play_intrigue = {"player_id": ..., "source": "green_room"}
    │   ├─ Send IntriguePlayPromptResponse to player
    │   │
    │   ├─ Player cancels → _unwind_placement(), clear pending states
    │   │
    │   └─ Player plays intrigue card:
    │       ├─ Remove card from hand
    │       ├─ _resolve_intrigue_effect()
    │       ├─ Clear pending_play_intrigue
    │       │
    │       ├─ Effect is pending (target selection):
    │       │   ├─ Set pending_intrigue_target (source: "green_room")
    │       │   ├─ Player selects target → resolve → continue to quest selection
    │       │   └─ Player cancels target → unwind placement, return card
    │       │
    │       └─ Effect resolved immediately → continue to quest selection
    │
    └─ Quest selection phase:
        ├─ Player selects face-up quest card
        ├─ Card added to hand, replacement drawn
        ├─ Broadcast QuestCardSelectedResponse (spot_number=3)
        └─ _check_quest_completion() → _advance_turn()
```

## Board Layout (client/ui/board_renderer.py)

### New _GRID_PLACEMENT mapping

The 9 permanent spaces arranged in a 3x3 grid:

| Grid Position | Space |
|---------------|-------|
| (0, 0) | Merch Store |
| (1, 0) | Motown |
| (2, 0) | Guitar Center |
| (0, 1) | Talent Show |
| (1, 1) | Rhythm Pit |
| (2, 1) | Jam Session |
| (0, 2) | Whisper Room |
| (1, 2) | VIP Entrance |
| (2, 2) | The Green Room |

Constructed buildings: columns 0-2, starting at row 3+ (below permanent spaces), paginated.

Non-permanent spaces (garage, backstage, realtor) retain their current column positions but row offsets may shift.
