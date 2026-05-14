# Data Model: Card Pick Animation

No new shared data models required. This feature is client-side only.

## Client-Side State (GameView)

| Field | Type | Purpose |
|-------|------|---------|
| `_card_animation_active` | `bool` | Blocks input during animation sequence |
| `_pending_face_up_update` | `dict \| None` | Buffers face_up_quests_updated message during animation |

## Existing Entities Used

- **AnimationManager** (`client/ui/animation_manager.py`): Manages eased sprite animations with `on_complete` callbacks
- **EaseAnimation** (`client/ui/animation_manager.py`): Dataclass for individual animation state
- **BoardRenderer** (`client/ui/board_renderer.py`): Provides quest card positions via `_quest_positions`, card scale via `card_scale()`
- **QuestCardSelectedResponse** (`shared/messages.py:257-263`): Server message with `player_id`, `card_id`, `spot_number`, `bonus_reward`
- **FaceUpQuestsUpdatedResponse** (`shared/messages.py:266-268`): Server message with updated `face_up_quests` list
