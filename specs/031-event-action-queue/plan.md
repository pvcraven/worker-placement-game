# Implementation Plan: Event Action Queue

**Branch**: `031-event-action-queue` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/031-event-action-queue/spec.md`

## Summary

Add a sequential event queue to the game client that processes animations, dialogs, and sounds one at a time in FIFO order. This fixes the bug where dialogs appear on top of playing animations (e.g., quest completion dialog overlapping card pick animation) and establishes an extensible pattern for all future presentational events.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2
**Storage**: N/A (client-side only, no persistence)
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade window)
**Project Type**: Desktop game (client-server)
**Performance Goals**: 60 fps — queue processing must be O(1) per frame
**Constraints**: Queue must not block game state updates from server; must integrate with existing AnimationManager callback pattern
**Scale/Scope**: Single new module (~100-150 lines), modifications to game_view.py message handlers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | **PASS** | No new rendering — queue is logic only |
| II. Pydantic Data Modeling | **PASS** | Queue is internal client state, not crossing boundaries. Simple dataclasses suffice per Principle V |
| III. Client-Server Separation | **PASS** | Queue is purely client-side presentation. No game state mutations. Server unchanged |
| IV. Test-Driven Game Logic | **PASS** | No server game logic changes. Queue can have unit tests without Arcade dependency |
| V. Simplicity First | **PASS** | Simple FIFO queue with callback-based completion. No frameworks, no abstractions beyond the three event types needed now |
| VI. Server-Authoritative Protocol | **PASS** | Server messages unchanged. Queue only defers when the client *presents* them |
| VII. Config-Driven Content | **N/A** | No game content changes |
| VIII. Pending State | **N/A** | Server pending state unchanged |
| IX. Cancel/Unwind | **N/A** | No cancel flows affected |
| X. Post-Action Turn Flow | **PASS** | Server turn flow unchanged. Client just defers visual presentation |

**Gate result**: All applicable principles pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/031-event-action-queue/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 quickstart guide
├── contracts/           # Phase 1 interface contracts
│   └── event-queue-interface.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
client/
  ui/
    event_queue.py         # NEW — EventQueue, QueuedEvent, AnimationEvent, DialogEvent, SoundEvent
    animation_manager.py   # MODIFIED — minor, completion callbacks work with queue
  views/
    game_view.py           # MODIFIED — message handlers enqueue events; on_update drives queue

tests/
  test_event_queue.py      # NEW — unit tests for queue processing logic
```

**Structure Decision**: Single new file `client/ui/event_queue.py` alongside existing UI components. No new directories needed. The queue is a peer to `animation_manager.py` in the UI layer.

## Implementation Details

### Phase 1: Core EventQueue (P1 — Animations before dialogs)

**1a. Create `client/ui/event_queue.py`**

Define base `QueuedEvent` class with `start()`, `is_complete()`, `update(dt)` methods. Implement three concrete types:

- `AnimationEvent`: Wraps a setup function that configures and starts animations. A callback sets `done = True` when the final animation completes.
- `DialogEvent`: Wraps a function that creates and shows a dialog. The dialog's existing completion callbacks set `done = True`. Optional sound plays on start.
- `SoundEvent`: Plays a sound and completes after a specified duration.

Implement `EventQueue` with `enqueue()`, `update(dt)`, and `is_busy()`. Processing logic: if `current` is None or complete, pop next from queue and call `start()`.

**1b. Integrate into `GameView`**

- Add `self.event_queue = EventQueue()` in `__init__`
- Add `self.event_queue.update(dt)` in `on_update()`
- Replace `_card_animation_active` flag checks with `self.event_queue.is_busy()` where appropriate
- Remove `_pending_face_up_update` mechanism — the queue handles deferral

**1c. Convert quest card selection flow**

In `_on_quest_card_selected`: instead of directly calling `_start_card_pick_animation`, enqueue an `AnimationEvent` that wraps the animation setup.

In `_on_quest_completion_prompt`: instead of immediately creating and showing `QuestCompletionDialog`, enqueue a `DialogEvent` that wraps the dialog creation. The dialog's `on_select`/`on_skip` callbacks signal event completion.

**1d. Convert other overlapping flows**

Apply the same pattern to:
- `_on_resource_choice_prompt` — enqueue as DialogEvent
- `_on_quest_reward_choice_prompt` — enqueue as DialogEvent
- `_on_intrigue_play_prompt` — enqueue as DialogEvent
- `_on_opponent_choice_prompt` — enqueue as DialogEvent
- `_on_intrigue_target_prompt` — enqueue as DialogEvent
- `_on_copy_space_prompt` — enqueue as DialogEvent

### Phase 2: Sound Timing (P2)

- Sounds currently passed to `AnimationManager.animate()` as `sound` parameter play when the animation starts — this already works correctly within the queue since AnimationEvents start when their turn comes
- Direct `arcade.play_sound()` calls (turn sound, round sound) — wrap in `SoundEvent` or leave as-is depending on whether they overlap with other events
- Turn notification sounds play independently (they don't overlap animations) so they can remain direct calls initially

### Phase 3: Testing

- Unit tests for `EventQueue`: verify sequential processing, immediate start when idle, `is_busy()` correctness
- Unit tests for each event type: verify completion detection
- Manual testing: play a game and verify card animation completes before quest completion dialog appears

## Complexity Tracking

No constitution violations. No complexity justifications needed.
