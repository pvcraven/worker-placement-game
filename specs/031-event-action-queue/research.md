# Research: Event Action Queue

## Current State Analysis

### How Events Overlap Today

The root cause: server messages arrive in quick succession and each message handler immediately shows its visual effect. There is no coordination layer.

**Example flow (quest card selection → quest completion):**
1. Server broadcasts `quest_card_selected` → client starts card pick animation (3.25s total across 3 stages)
2. Server sends `quest_completion_prompt` milliseconds later → client immediately shows QuestCompletionDialog
3. Result: dialog appears on top of the still-playing animation; dialog may be unresponsive until animation sprite stops consuming clicks

### Existing Deferral Mechanism

A partial solution already exists for face-up quest updates:
- `_card_animation_active` flag (set in `_start_card_pick_animation`, cleared in stage 3 callback)
- `_pending_face_up_update` stores a deferred board update
- `_on_face_up_quests_updated` checks the flag and defers if animation is active
- Board clicks are also blocked while `_card_animation_active` is True

This ad-hoc approach doesn't scale — each new deferral case needs its own flag and pending variable.

### Dialog Types and Completion Patterns

All dialogs use callback-based completion: the dialog invokes `on_select`, `on_skip`, or `on_cancel`, and the callback sets the dialog reference to `None` and sends a server message.

| Dialog | Variable | Completion Mechanism |
|--------|----------|---------------------|
| QuestCompletionDialog | `_quest_completion_dialog` | `on_select` / `on_skip` callbacks |
| ResourceChoiceDialog | `_resource_choice_dialog` | `on_select` / `on_skip` callbacks |
| CardSpriteSelectionDialog | `_card_sprite_dialog` | `on_select` / `on_cancel` callbacks |
| PlayerTargetDialog | `_target_dialog` | `on_select` / `on_cancel` callbacks |
| RewardChoiceDialog | `_reward_choice_dialog` | `on_select` callback |

### Sound Playback

Sounds are played in two ways:
1. **Directly**: `arcade.play_sound(self._turn_sound)` — fires immediately when called
2. **Via animation**: Passed as `sound` parameter to `AnimationManager.animate()` — plays when animation starts

## Design Decisions

### Decision 1: Queue Architecture

**Decision**: A simple FIFO queue of event objects, each with a `start()` method and a way to signal completion. The queue processes one event at a time.

**Rationale**: The existing `AnimationManager` already handles multi-animation concurrency. The queue only needs to gate *between* event types (animation batch → dialog → next animation batch). A simple sequential queue is the minimum viable solution.

**Alternatives considered**:
- Priority queue: Rejected — events must play in arrival order, not by priority
- Parallel lanes (animations in one lane, dialogs in another): Rejected — the whole point is to prevent overlap

### Decision 2: Event Completion Signaling

**Decision**: Each event provides a callback or method for the queue to detect completion. Animations use the existing `on_complete` callback. Dialogs signal completion when their callback fires (setting reference to None). Sounds use a timer.

**Rationale**: This matches existing patterns — no new completion mechanisms needed. The queue wraps around what already exists.

**Alternatives considered**:
- Polling (check each frame if event is done): Viable but the callback approach is already built into animations and dialogs
- Promise/Future pattern: Over-engineered for this use case

### Decision 3: Where the Queue Lives

**Decision**: A new `EventQueue` class in `client/ui/event_queue.py`, owned by `GameView`. Message handlers enqueue events instead of showing them directly. The queue's `update()` is called each frame.

**Rationale**: Keeps queue logic out of game_view.py (which is already large). GameView already calls `self.animation_manager.update(dt)` each frame — same pattern for the event queue.

**Alternatives considered**:
- Inline in GameView: Would make an already large file even larger
- Inside AnimationManager: Too coupled — the queue manages more than animations

### Decision 4: Scope of Initial Integration

**Decision**: Start by integrating the quest card selection → quest completion flow (the reported bug). Then extend to other dialog/animation overlaps. Sound timing is handled by associating sounds with their parent event rather than playing them independently.

**Rationale**: Fixing the most visible bug first proves the architecture. The queue is designed to be extended incrementally.
