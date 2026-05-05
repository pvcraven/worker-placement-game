# Tasks: Informational Dialog System

**Input**: Design documents from `specs/023-info-dialog/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not explicitly requested in feature specification — test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed — existing project with established structure.

*(No tasks — project already initialized)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the reusable InfoDialog component that all user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T001 Create `InfoDialog` class in `client/ui/info_dialog.py` — implements show/dismiss/update/draw methods with queue support, `ShapeElementList` background overlay, cached `arcade.Text`, and delta-time auto-dismiss timer per plan.md design
- [X] T002 Add `InfoDialog` instance to `GameView.__init__` in `client/views/game_view.py` — create `self._info_dialog = InfoDialog()` and load `self._round_sound = arcade.load_sound("client/assets/sounds/sound2.mp3")`
- [X] T003 Wire `InfoDialog.update()` into `GameView.on_update()` in `client/views/game_view.py` — add `self._info_dialog.update(delta_time)` call
- [X] T004 Wire `InfoDialog.draw()` into `GameView.on_draw()` in `client/views/game_view.py` — add draw call after status bar rendering, before `self.ui.draw()` (between line ~2276 and line ~2280)

**Checkpoint**: InfoDialog component exists and is wired into the game loop. No dialogs are triggered yet, but the infrastructure is ready.

---

## Phase 3: User Story 1 — Round Transition Dialog (Priority: P1) MVP

**Goal**: When a round ends and the next round begins, a centered "ROUND [N]" dialog appears and auto-dismisses after 1.5 seconds, with `sound2.mp3` playing.

**Independent Test**: Start a game, complete all placements in round 1, verify "ROUND 2" dialog appears centered and auto-dismisses after 1.5 seconds with sound effect.

### Implementation for User Story 1

- [X] T005 [US1] Add round transition dialog trigger in `_on_round_end()` in `client/views/game_view.py` — after game state updates (line ~1748), call `self._info_dialog.show(f"ROUND {next_round}", duration=1.5)` and `arcade.play_sound(self._round_sound)`

**Checkpoint**: Round transition dialog is fully functional — "ROUND N" appears centered, plays sound, and auto-dismisses after 1.5 seconds.

---

## Phase 4: User Story 2 — Waiting on Another Player Dialog (Priority: P1)

**Goal**: When a player waits for another player to make a choice (owner bonus, intrigue target, round-start resource choice), a persistent "Waiting on [Player]" dialog appears and stays until the other player finishes.

**Independent Test**: Have Player A place a worker on a building owned by Player B that triggers an owner bonus choice. Verify Player A sees "Waiting on Player B" dialog that persists until Player B makes their choice.

### Implementation for User Story 2

- [X] T006 [US2] Add waiting dialog trigger in `_on_resource_choice_prompt()` in `client/views/game_view.py` — in the `pid != my_id` branch (line ~1052), call `self._info_dialog.show(f"Waiting on {name}", duration=None)`
- [X] T007 [US2] Add waiting dialog trigger in `_on_round_start_resource_choice_prompt()` in `client/views/game_view.py` — in the `player_id != my_id` branch (line ~1232), call `self._info_dialog.show(f"Waiting on {name}", duration=None)`
- [X] T008 [US2] Add waiting dialog trigger in `_on_worker_placed_backstage()` handler or the backstage handler in `client/views/game_view.py` — when intrigue target prompt is for another player, show "Waiting on [name]" persistent dialog
- [X] T009 [US2] Add waiting dialog dismiss in `_update_current_player()` in `client/views/game_view.py` — call `self._info_dialog.dismiss()` at the start of the method as a catch-all for all waiting state resolutions
- [X] T010 [US2] Add waiting dialog dismiss in `_on_round_end()` in `client/views/game_view.py` — call `self._info_dialog.dismiss()` at the start of the handler before showing the round transition dialog

**Checkpoint**: Waiting dialogs appear for all deferred player choices and dismiss when the waited-on player completes their action or the turn advances.

---

## Phase 5: User Story 3 — Intrigue Steal Notification Dialog (Priority: P2)

**Goal**: When a steal intrigue card resolves, all players see "[Player] stole [resources] from [Target]" auto-dismissing after 1.5 seconds.

**Independent Test**: Have Player A play a steal intrigue card on Player B. Verify all players see "Alice stole 2 drummers from Bob" dialog that auto-dismisses after 1.5 seconds.

### Implementation for User Story 3

- [X] T011 [US3] Add steal notification dialog trigger in `_on_intrigue_effect_resolved()` in `client/views/game_view.py` — for `steal_resources` effect type, after updating resources (line ~694), call `self._info_dialog.show(f"{name} stole {res_str} from {tname}", duration=1.5)`

**Checkpoint**: Steal notifications appear as centered dialogs with auto-dismiss.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation across all flows.

- [X] T012 Run linter (`ruff check .`) and fix any issues
- [X] T013 Verify round transition dialog — confirm "ROUND N" appears centered, plays sound, and auto-dismisses after 1.5 seconds
- [X] T014 Verify waiting dialog — confirm persistent dialogs appear for owner bonus, intrigue target, and round-start resource choices, and dismiss when action resolves
- [X] T015 Verify dialog queue — confirm that if a round ends and a steal notification is queued simultaneously, both display sequentially without lost messages

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped — existing project
- **Foundational (Phase 2)**: No dependencies — can start immediately. BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 (InfoDialog component must exist)
- **User Story 2 (Phase 4)**: Depends on Phase 2. Can run in parallel with US1 (different code locations in game_view.py)
- **User Story 3 (Phase 5)**: Depends on Phase 2. Can run in parallel with US1 and US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### Within Phase 2 (Foundational)

- T001 must complete first (creates the InfoDialog class)
- T002, T003, T004 depend on T001 (reference InfoDialog)
- T002, T003, T004 are sequential within game_view.py (same file)

### Within Phase 4 (User Story 2)

- T006, T007, T008 are all in game_view.py (sequential)
- T009, T010 depend on T006-T008 (dismiss must work after show is wired)

### Parallel Opportunities

```bash
# Phase 2 — T001 is in a different file from T002-T004:
Task T001: "Create InfoDialog class in client/ui/info_dialog.py"
# Then T002-T004 wire it into game_view.py (sequential)

# User Stories can overlap since they touch different handlers in game_view.py:
# But since they're all in the same file, sequential is safer
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (InfoDialog component + game loop wiring)
2. Complete Phase 3: User Story 1 (round transition dialog)
3. **STOP and VALIDATE**: Test round transition dialog works
4. Run linter

### Incremental Delivery

1. Create InfoDialog component → reusable infrastructure ready
2. Wire into game loop → component renders and updates
3. Add round transition trigger → "ROUND N" dialog visible
4. Add waiting triggers → persistent dialogs for deferred choices
5. Add steal notification → intrigue effects get visual feedback
6. Each step adds value without breaking existing functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All user stories share the same InfoDialog component (Phase 2)
- No server changes needed — entirely client-side
- Sound effect (`sound2.mp3`) already exists in `client/assets/sounds/`
- Total: 15 tasks across 6 phases
