# Tasks: Backstage & Intrigue Mechanics

**Input**: Design documents from `/specs/006-backstage-intrigue-mechanics/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/websocket-messages.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. Existing codebase has all directories and models.

*(No setup tasks — project structure, models, and message types are already in place.)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add starting resource constants shared by User Story 1

- [ ] T001 Add `STARTING_INTRIGUE_CARDS = 2`, `STARTING_COINS_BASE = 4`, and `STARTING_COINS_INCREMENT = 2` constants in shared/constants.py

**Checkpoint**: Constants defined — user story implementation can begin

---

## Phase 3: User Story 1 - Starting Resources (Priority: P1)

**Goal**: Players receive 2 intrigue cards and turn-order-based coins (4/6/8/etc.) when the game starts

**Independent Test**: Create a 3-player game. After start, verify Player 1 has 4 coins and 2 intrigue cards, Player 2 has 6 coins and 2 intrigue cards, Player 3 has 8 coins and 2 intrigue cards.

### Implementation for User Story 1

- [ ] T002 [US1] In server/lobby.py, after player creation during game initialization, shuffle the intrigue deck and deal `STARTING_INTRIGUE_CARDS` cards to each player's `intrigue_hand` (draw from `board.intrigue_deck`)
- [ ] T003 [US1] In server/lobby.py, during game initialization, grant each player starting coins using formula `STARTING_COINS_BASE + (slot_index * STARTING_COINS_INCREMENT)` where slot_index is 0-based position in turn order
- [ ] T004 [US1] Verify the `GameStartedResponse` broadcast includes the updated player state (intrigue cards in hand and coins) so clients display correct starting resources in client/views/game_view.py

**Checkpoint**: Starting resources work end-to-end. Players see correct coins and intrigue cards at game start.

---

## Phase 4: User Story 2 - Backstage Placement with Intrigue Card (Priority: P1)

**Goal**: Players can place workers on Backstage spots (left-to-right order) by selecting an intrigue card from hand. Cancel unwinds placement.

**Independent Test**: Start a game, click Backstage 1, see intrigue card selection dialog, select a card, verify placement succeeds and effect resolves. Click cancel and verify no placement.

### Implementation for User Story 2

- [ ] T005 [US2] Add `_handle_place_worker_backstage` route in server/network.py that dispatches `PlaceWorkerBackstageRequest` messages to `handle_place_worker_backstage` in server/game_engine.py
- [ ] T006 [US2] Implement `handle_place_worker_backstage()` in server/game_engine.py: validate it's the player's turn, validate `available_workers > 0`, validate sequential slot filling (all lower-numbered slots occupied), validate player has the specified intrigue card in `intrigue_hand`, place worker on slot (`occupied_by = player_id`), attach intrigue card to slot, remove card from hand, call `_resolve_intrigue_effect()`, decrement `available_workers`, broadcast `WorkerPlacedBackstageResponse`, then call `_check_quest_completion()`
- [ ] T007 [US2] In client/views/game_view.py `on_mouse_press()`, detect backstage clicks (space_id starts with `"backstage_slot_"`). Before sending a message: validate the player has intrigue cards, validate sequential filling on the client side, then show a `CardSelectionDialog` with the player's intrigue cards. On select, send `{"action": "place_worker_backstage", "slot_number": N, "intrigue_card_id": card_id}`. On cancel, close dialog (no message sent).
- [ ] T008 [US2] In client/views/game_view.py, add/update `_on_worker_placed_backstage` handler to update local game state: mark backstage slot as occupied, decrement available workers, remove played intrigue card from local hand, log intrigue effect
- [ ] T009 [US2] Add client-side validation feedback: if player clicks backstage with no intrigue cards, show error message "You need an intrigue card to place here". If sequential order violated, show "Backstage [N] must be filled first".

**Checkpoint**: Backstage placement flow works end-to-end. Player sees intrigue dialog, can select or cancel, effects resolve.

---

## Phase 5: User Story 3 - Worker Reassignment Phase & Round Advancement (Priority: P2)

**Goal**: After all workers placed, process backstage slots 1→2→3 for reassignment. Fix round advancement when no backstage slots occupied (FR-014) and after reassignment completes (FR-015).

**Independent Test**: Place workers including backstage spots, verify reassignment phase starts, verify freed workers can be placed on open action spaces. Also verify round advances when no backstage spots are used.

### Implementation for User Story 3

- [ ] T010 [US3] Diagnose and fix the round advancement bug in server/game_engine.py: trace the call chain from `_advance_turn()` → `all_workers_placed()` → `_end_placement_phase()` → `_end_round()`. Ensure that when all workers are placed and no backstage slots are occupied, `_end_round()` is called and the next round starts (FR-014)
- [ ] T011 [US3] In server/game_engine.py `_end_placement_phase()`, verify the backstage-occupied check correctly enters REASSIGNMENT phase when slots are occupied and calls `_end_round()` when they're not. Ensure `_end_round()` returns workers to players, clears board, increments round, and broadcasts round state
- [ ] T012 [US3] In server/game_engine.py `handle_reassign_worker()`, add explicit validation that the target space_id does not start with `"backstage_slot_"` and return a clear error message if attempted
- [ ] T013 [US3] Verify that after the last backstage slot is processed during reassignment, `_end_round()` is called to advance to the next round (FR-015). If not, add the call at the end of the reassignment queue processing
- [ ] T014 [US3] In client/views/game_view.py, ensure the `reassignment_phase_start` message handler updates the UI to indicate reassignment is active (e.g., update status text) and that `worker_reassigned` responses update the board state, available workers, and rewards correctly
- [ ] T015 [US3] In client/views/game_view.py, handle the round transition after reassignment: when a `round_started` or equivalent message arrives, reset the board display, update worker counts, and refresh the UI for the new round

**Checkpoint**: Reassignment phase works end-to-end. Round advances correctly both with and without backstage workers.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T016 Verify backstage slot visual state updates correctly on the board (occupied/unoccupied) in client/ui/board_renderer.py
- [ ] T017 Run quickstart.md scenarios 1-8 end-to-end and verify all test scenarios pass
- [ ] T018 Verify intrigue card effects display correctly in game log/chat after backstage placement

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Phase 2 (T001 for constants)
- **User Story 2 (Phase 4)**: Depends on Phase 2 (T001) and Phase 3 (US1 provides intrigue cards to players)
- **User Story 3 (Phase 5)**: Depends on Phase 4 (US2 provides backstage placement for reassignment to process)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Depends on US1 — players need starting intrigue cards to test backstage placement
- **User Story 3 (P2)**: Depends on US2 — backstage placement must work before reassignment can be tested

### Within Each User Story

- US1: T002 → T003 → T004
- US2: T005 (network route) → T006 (server handler) → T007 (client dialog) → T008 (client state update) → T009 (validation feedback)
- US3: T010/T011 (round advancement fix, can be parallel) → T012 (reassignment validation) → T013 (post-reassignment round advance) → T014/T015 (client UI, can be parallel)

### Parallel Opportunities

- T002 and T003 can run in parallel (both modify lobby.py but different sections — coins vs intrigue cards)
- T010 and T011 can be worked together (same investigation, related code paths)
- T014 and T015 can run in parallel (different message handlers in game_view.py)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001)
2. Complete Phase 3: User Story 1 (T002-T004)
3. **STOP and VALIDATE**: Start a game, verify coins and intrigue cards
4. Starting resources alone delivers immediate value — players have coins and intrigue cards

### Incremental Delivery

1. Foundational → Constants ready
2. Add User Story 1 → Starting resources work → Validate
3. Add User Story 2 → Backstage placement works → Validate
4. Add User Story 3 → Reassignment + round advancement work → Validate
5. Polish → Quickstart validation, visual polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Most infrastructure already exists (models, message types, intrigue effects) — tasks focus on wiring and handlers
- The round advancement bug (T010) is a critical fix — game currently stalls when all workers placed with no backstage occupants
- Commit after each task or logical group
