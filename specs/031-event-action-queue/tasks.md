# Tasks: Event Action Queue

**Input**: Design documents from `specs/031-event-action-queue/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted. Unit tests for the queue are included in Polish phase as good practice since the queue is testable without Arcade.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the core EventQueue module with all event types

- [X] T001 Create EventQueue class with QueuedEvent base, AnimationEvent, DialogEvent, and SoundEvent in client/ui/event_queue.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire the EventQueue into GameView's frame loop so all user stories can use it

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add `self.event_queue = EventQueue()` to GameView.__init__ and call `self.event_queue.update(dt)` in GameView.on_update() in client/views/game_view.py
- [X] T003 Add `self.event_queue.is_busy()` guard to on_mouse_press board click handler (replacing `_card_animation_active` check) in client/views/game_view.py

**Checkpoint**: EventQueue is initialized and updating each frame. Board clicks are gated by queue busy state. No behavior change yet — events are not enqueued.

---

## Phase 3: User Story 1 - Animations Complete Before Dialogs Appear (Priority: P1) 🎯 MVP

**Goal**: Card pick animation plays fully before quest completion dialog appears. The reported bug is fixed.

**Independent Test**: Select a quest from The Garage that triggers both a card pick animation and a quest completion prompt. The card animation should play to completion before the quest completion dialog appears. The dialog should be immediately interactive.

### Implementation for User Story 1

- [X] T004 [US1] Convert _on_quest_card_selected to enqueue an AnimationEvent wrapping _start_card_pick_animation instead of calling it directly in client/views/game_view.py
- [X] T005 [US1] Update _start_card_pick_animation so the final stage on_complete callback signals the AnimationEvent as done (instead of setting _card_animation_active = False) in client/views/game_view.py
- [X] T006 [US1] Convert _on_quest_completion_prompt to enqueue a DialogEvent wrapping the QuestCompletionDialog creation instead of showing it immediately in client/views/game_view.py
- [X] T007 [US1] Update QuestCompletionDialog on_select/on_skip callbacks to signal the DialogEvent as done in client/views/game_view.py
- [X] T008 [US1] Convert _on_face_up_quests_updated to use event_queue.is_busy() instead of _card_animation_active flag, and enqueue the face-up update as a deferred action in client/views/game_view.py
- [X] T009 [US1] Remove _card_animation_active flag, _pending_face_up_update field, and associated ad-hoc deferral logic from client/views/game_view.py

**Checkpoint**: Quest card selection → quest completion dialog flow is fully sequential. Animation plays, then dialog appears. This is the MVP.

---

## Phase 4: User Story 2 - Sounds Play at the Right Time (Priority: P2)

**Goal**: Sounds play in sync with their corresponding visual events, not before or overlapping.

**Independent Test**: Trigger a card pick animation — card sound should play when the animation starts (when the AnimationEvent starts), not before the queue reaches it. Trigger two sequential events with sounds — second sound should not overlap the first.

### Implementation for User Story 2

- [X] T010 [US2] Verify that sounds passed via AnimationManager.animate(sound=...) play correctly when AnimationEvent starts (no change expected — sounds already play at animation start) in client/ui/animation_manager.py
- [X] T011 [US2] Add optional sound parameter to DialogEvent that plays when the dialog event starts in client/ui/event_queue.py
- [X] T012 [US2] Evaluate direct arcade.play_sound() calls in _on_round_end and _update_current_player — wrap in SoundEvent if they overlap with queued events, otherwise leave as direct calls in client/views/game_view.py

**Checkpoint**: Sounds play at the correct time relative to their events. No sound overlap between sequential events.

---

## Phase 5: User Story 3 - Queue Handles Varying Event Types (Priority: P3)

**Goal**: All dialog types use the event queue, proving the architecture handles mixed event types without modification to the queue itself.

**Independent Test**: Queue a mixed sequence (e.g., animation → dialog → sound) and verify each plays in order, with the next starting only after the previous completes.

### Implementation for User Story 3

- [X] T013 [US3] Convert _on_resource_choice_prompt to enqueue a DialogEvent in client/views/game_view.py
- [X] T014 [US3] Convert _on_quest_reward_choice_prompt to enqueue a DialogEvent in client/views/game_view.py
- [X] T015 [US3] Convert _on_intrigue_play_prompt to enqueue a DialogEvent in client/views/game_view.py
- [X] T016 [US3] Convert _on_opponent_choice_prompt to enqueue a DialogEvent in client/views/game_view.py
- [X] T017 [US3] Convert _on_intrigue_target_prompt to enqueue a DialogEvent in client/views/game_view.py
- [X] T018 [US3] Convert _on_copy_space_prompt to enqueue a DialogEvent in client/views/game_view.py

**Checkpoint**: All dialog types flow through the event queue. No dialog can overlap an animation or another dialog.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testing, validation, and cleanup

- [X] T019 [P] Write unit tests for EventQueue sequential processing, immediate start, and is_busy() in tests/test_event_queue.py
- [X] T020 [P] Write unit tests for AnimationEvent, DialogEvent, and SoundEvent completion detection in tests/test_event_queue.py
- [X] T021 Run ruff check and pytest to verify all checks pass
- [ ] T022 Manual play-testing: verify quest card selection → completion dialog flow, resource choice after placement, intrigue card play sequences

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — this is the MVP
- **US2 (Phase 4)**: Depends on Phase 2 — can run in parallel with US1
- **US3 (Phase 5)**: Depends on Phase 2 — can run in parallel with US1 and US2
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — independent of US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — independent of US1/US2, but benefits from US1 being done first as a pattern reference

### Within Each User Story

- State update changes before removal of old mechanisms (T004-T008 before T009)
- Each dialog conversion in US3 is independent of others but all touch the same file

### Parallel Opportunities

- T019 and T020 can run in parallel (different test focus, same file)
- US1, US2, and US3 could theoretically run in parallel after Foundational, but US1 establishes the pattern so doing it first is recommended
- Within US3, each dialog conversion (T013-T018) is logically independent but they all modify game_view.py

---

## Parallel Example: User Story 3

```bash
# These are logically independent dialog conversions but share game_view.py:
Task T013: "Convert _on_resource_choice_prompt to enqueue a DialogEvent"
Task T014: "Convert _on_quest_reward_choice_prompt to enqueue a DialogEvent"
Task T015: "Convert _on_intrigue_play_prompt to enqueue a DialogEvent"
Task T016: "Convert _on_opponent_choice_prompt to enqueue a DialogEvent"
Task T017: "Convert _on_intrigue_target_prompt to enqueue a DialogEvent"
Task T018: "Convert _on_copy_space_prompt to enqueue a DialogEvent"
# Each follows the same pattern: wrap dialog creation in a DialogEvent, update callbacks
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T003)
3. Complete Phase 3: User Story 1 (T004-T009)
4. **STOP and VALIDATE**: Play a game, select a quest from The Garage, verify animation completes before dialog appears
5. This fixes the reported bug — ship if ready

### Incremental Delivery

1. Complete Setup + Foundational → Queue infrastructure ready
2. Add User Story 1 → Test quest flow → **Bug is fixed (MVP!)**
3. Add User Story 2 → Test sound timing → Sounds sync with events
4. Add User Story 3 → Test all dialogs → Full queue coverage
5. Each story adds value without breaking previous stories

---

## Notes

- All dialog conversions follow the same pattern: wrap `show()` call in a `DialogEvent`, update completion callbacks to signal `event.done = True`
- The EventQueue is purely client-side — no server changes needed
- Game state updates from the server continue to be applied immediately regardless of queue state (FR-010)
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
