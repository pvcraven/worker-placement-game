# Tasks: Card Pick Animation

**Input**: Design documents from `specs/030-card-pick-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Not requested in spec. Manual visual testing only.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed — all changes go in existing files. This phase prepares the board renderer to expose data the animation needs.

- [X] T001 Store quest card scale as `self._quest_scale` during `_rebuild_shapes()` in client/ui/board_renderer.py
- [X] T002 Add `get_quest_card_info(card_id)` method returning `(x, y, scale)` for a face-up quest card in client/ui/board_renderer.py

**Checkpoint**: Board renderer can provide quest card position and scale by ID

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add animation state fields and input blocking to GameView — required before any animation work.

- [X] T003 Add `_card_animation_active` bool and `_pending_face_up_update` dict fields to `__init__` in client/views/game_view.py
- [X] T004 Add early return in `on_mouse_press()` when `_card_animation_active` is True in client/views/game_view.py
- [X] T005 Modify `_on_face_up_quests_updated()` to buffer message in `_pending_face_up_update` when `_card_animation_active` is True in client/views/game_view.py

**Checkpoint**: Input blocking and message buffering infrastructure in place

---

## Phase 3: User Story 1 — Card Animates to Center on Selection (Priority: P1) MVP

**Goal**: When a quest card is selected, it animates from its board position to the screen center using SINE easing over 0.75 seconds. The original slot appears empty. Plays on all connected clients.

**Independent Test**: Select a quest card during gameplay. The card should glide smoothly to screen center. The original slot should be empty during animation. Verify on a second connected client that the same animation plays.

### Implementation for User Story 1

- [X] T006 [US1] Add animation trigger in `_on_quest_card_selected()`: create a new `arcade.Sprite` from `client/assets/card_images/quests/{card_id}.png` with scale from `get_quest_card_info()`, remove the selected card from local `face_up_quests`, refresh board to show empty slot, set `_card_animation_active = True`, and start entry animation to screen center with `Easing.SINE` and 0.75s duration in client/views/game_view.py
- [ ] T007 [US1] Verify animation plays on all clients by testing with 2+ connected clients — the `quest_card_selected` message is already broadcast, so each client's `_on_quest_card_selected()` triggers the animation independently

**Checkpoint**: Card animates from board to center on all clients. Original slot is empty. Input is blocked.

---

## Phase 4: User Story 2 — Card Pauses at Center Then Exits Toward Player (Priority: P2)

**Goal**: After reaching center, the card holds for 1 second, then flies toward the selecting player's row in the player list using Quad-In easing over 0.75 seconds.

**Independent Test**: After the card reaches center, it should visibly pause for 1 second, then accelerate off toward the correct player's name in the upper-left player list. Verify the exit targets the correct player when different players select cards.

### Implementation for User Story 2

- [X] T008 [US2] Chain pause phase in the entry animation's `on_complete` callback: animate the same sprite from screen center to screen center (zero distance) with `Easing.LINEAR` and 1.0s duration in client/views/game_view.py
- [X] T009 [US2] Chain exit phase in the pause animation's `on_complete` callback: animate the sprite from screen center to `_player_marker_positions[player_id]` with `Easing.QUAD_IN` and 0.75s duration in client/views/game_view.py
- [X] T010 [US2] In the exit animation's `on_complete` callback: set `_card_animation_active = False`, apply `_pending_face_up_update` if buffered by calling `_on_face_up_quests_updated()`, then clear the buffer in client/views/game_view.py

**Checkpoint**: Full 3-phase animation plays (entry → pause → exit). Board refreshes after exit. Input unblocked.

---

## Phase 5: User Story 3 — Board Updates with Slot Stability (Priority: P3)

**Goal**: After animation completes, the board refreshes with the replacement card in the vacated slot. Non-selected cards stay in their original positions.

**Independent Test**: Note the positions of all 4 face-up cards. Select one. After animation, verify the 3 non-selected cards are in exactly the same positions. The replacement card should appear only in the slot of the selected card.

### Implementation for User Story 3

- [X] T011 [US3] Before starting the animation, save the pre-animation slot-to-card-ID mapping (e.g., `_pre_animation_slots: list[str]` with card IDs in slot order) in client/views/game_view.py
- [X] T012 [US3] When applying the deferred `_pending_face_up_update`, reorder the new `face_up_quests` list to match the original slot assignments: keep each surviving card in its original slot index and place the new card in the vacated slot, then call `_refresh_board()` in client/views/game_view.py

**Checkpoint**: All 3 user stories complete. Non-selected cards remain stationary after animation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup.

- [X] T013 Run `pytest` and `ruff check .` to verify no regressions in client/views/game_view.py or client/ui/board_renderer.py
- [ ] T014 Manual end-to-end test with 2+ clients: verify full animation sequence, slot stability, input blocking, and edge cases (empty deck, window resize)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Can start in parallel with Setup (different files for T003-T005 vs T001-T002)
- **User Story 1 (Phase 3)**: Depends on Setup (T001-T002) and Foundational (T003-T005)
- **User Story 2 (Phase 4)**: Depends on User Story 1 (T006) — extends the animation chain
- **User Story 3 (Phase 5)**: Depends on User Story 2 (T010) — adds slot reordering to the deferred update
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Independent after foundational — core animation
- **User Story 2 (P2)**: Depends on US1 — extends the animation with pause and exit phases
- **User Story 3 (P3)**: Depends on US2 — adds slot-stable refresh logic to the deferred update

### Within Each Phase

- T001 and T002 are sequential (T002 uses the field stored by T001)
- T003, T004, T005 are sequential (all in the same file, T004/T005 use fields from T003)
- T008, T009, T010 are sequential (each chains onto the previous callback)
- T011 and T012 are sequential (T012 uses the mapping saved by T011)

### Parallel Opportunities

- Setup (T001-T002) and Foundational (T003-T005) can run in parallel — different files
- Within US1, T007 is a manual verification step that runs after T006

---

## Parallel Example: Setup + Foundational

```text
# These can run in parallel (different files):
Task T001-T002: board_renderer.py changes
Task T003-T005: game_view.py foundational changes
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (board renderer exposes card data)
2. Complete Phase 2: Foundational (input blocking + message buffering)
3. Complete Phase 3: User Story 1 (card animates to center)
4. **STOP and VALIDATE**: Select a quest card — does the card animate to center? Is the original slot empty? Does it play on all clients?
5. Demo if ready — even without pause/exit, the core effect is visible

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 → Card moves to center (MVP!)
3. Add US2 → Full animation arc with pause and exit
4. Add US3 → Slot-stable refresh for visual polish
5. Each story adds visual refinement without breaking previous work

---

## Notes

- No server changes needed — all tasks are client-side
- No new files — all modifications in existing `client/views/game_view.py` and `client/ui/board_renderer.py`
- `client/ui/animation_manager.py` is used as-is with no modifications
- Manual visual testing is the primary verification method (no automated animation tests)
- Commit after each phase checkpoint
