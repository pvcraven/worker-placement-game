# Tasks: Quest Completion

**Input**: Design documents from `/specs/005-quest-completion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/websocket-messages.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. Existing codebase has all directories.

*(No setup tasks — project structure is already in place.)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Message types and server model changes shared by both user stories

- [x] T001 Add `SkipQuestCompletionRequest` message model and `QuestCompletionPromptResponse` response model in shared/messages.py
- [x] T002 Register `SkipQuestCompletionRequest` in the `ClientMessage` discriminated union in shared/messages.py
- [x] T003 Add `waiting_for_quest_completion: bool = False` field to `GameState` model in server/models/game.py

**Checkpoint**: Foundation ready — message types and model field exist for both stories

---

## Phase 3: User Story 1 - End-of-Turn Quest Completion (Priority: P1)

**Goal**: After a worker placement resolves, prompt the active player with completable quests; player completes one or skips.

**Independent Test**: Place a worker, see the quest completion dialog if eligible quests exist, complete a quest or skip, verify turn advances.

### Implementation for User Story 1

- [x] T004 [US1] Add `_check_quest_completion` helper in server/game_engine.py that checks if the active player has any completable quests (using `player.resources.can_afford(c.cost)` for each card in `contract_hand`), sends `QuestCompletionPromptResponse` to the active player via `send_to_player()` if any exist, sets `state.waiting_for_quest_completion = True`, otherwise calls `_advance_turn()`
- [x] T005 [US1] Modify `handle_place_worker()` in server/game_engine.py to call `_check_quest_completion()` instead of `_advance_turn()` after the reward is applied
- [x] T006 [US1] Modify `handle_place_worker_backstage()` in server/game_engine.py to call `_check_quest_completion()` instead of `_advance_turn()` after intrigue resolution
- [x] T007 [US1] Add `handle_skip_quest_completion()` handler in server/game_engine.py that clears `waiting_for_quest_completion`, calls `_advance_turn()`, and logs the skip action
- [x] T008 [US1] Modify `handle_complete_quest()` in server/game_engine.py to clear `waiting_for_quest_completion` and call `_advance_turn()` after broadcasting `QuestCompletedResponse`
- [x] T009 [US1] Add `_handle_skip_quest_completion` route in server/network.py dispatching to `handle_skip_quest_completion`
- [x] T010 [US1] Add `QuestCompletionDialog` class in client/ui/dialogs.py — accepts a list of quest card dicts, renders them horizontally using `CardRenderer.draw_contract()`, includes a "Skip" button at the bottom, calls `on_select(contract_id)` or `on_skip()` callbacks
- [x] T011 [US1] Add `quest_completion_prompt` handler in `_handle_message()` in client/views/game_view.py that creates and shows a `QuestCompletionDialog`, wiring `on_select` to send `{"action": "complete_quest", "contract_id": id}` and `on_skip` to send `{"action": "skip_quest_completion"}`
- [x] T012 [US1] Add `quest_completed` handler update in client/views/game_view.py to update `available_workers` display and refresh board after quest completion (verify existing `_on_quest_completed` handles this, extend if needed)

**Checkpoint**: Quest completion flow works end-to-end. Player sees dialog after placement, can complete or skip.

---

## Phase 4: User Story 2 - Workers and VP Status Display (Priority: P2)

**Goal**: Add a "Workers left: N  VP: M" status line above the resource bar; relocate VP from resource bar.

**Independent Test**: Join a game, see the status line with correct workers and VP counts; verify counts update on placement and quest completion.

### Implementation for User Story 2

- [x] T013 [P] [US2] Remove VP display from `ResourceBar.draw()` in client/ui/resource_bar.py — remove the VP section at the end, adjust `section_w` calculation to use `count` instead of `count + 1`
- [x] T014 [P] [US2] Add `draw_status_line()` method to `BoardRenderer` in client/ui/board_renderer.py that draws "Workers left: [N]  VP: [M]" text using cached `arcade.Text` objects, positioned above the resource bar area
- [x] T015 [US2] Update `GameView.on_draw()` or the board renderer's main draw call in client/views/game_view.py to invoke the status line drawing, passing current player's `available_workers` and `victory_points` from game state
- [x] T016 [US2] Shift the resource bar y-position down by ~25 pixels in the layout calculation in client/views/game_view.py or client/ui/board_renderer.py (wherever the resource bar position is set)

**Checkpoint**: Status line visible with correct workers/VP; resource bar shifted down; VP no longer in resource bar.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T017 Verify quest completion dialog dismisses properly on disconnect/reconnect in client/views/game_view.py
- [ ] T018 Run quickstart.md scenarios end-to-end and verify all 5 test scenarios pass
- [x] T019 Reset `waiting_for_quest_completion = False` in `_end_round()` in server/game_engine.py as a safety net

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Phase 2 (T001-T003)
- **User Story 2 (Phase 4)**: Depends on Phase 2 (T003 for model field), but can run in parallel with US1
- **Polish (Phase 5)**: Depends on both US1 and US2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (message types + model field)
- **User Story 2 (P2)**: Independent of US1 — can run in parallel. Only depends on Foundational for the `waiting_for_quest_completion` field (minor, mostly independent)

### Within Each User Story

- US1: T004 (helper) → T005/T006 (wire into placement handlers) → T007/T008 (server response handlers) → T009 (network route) → T010 (dialog UI) → T011/T012 (client message handling)
- US2: T013 and T014 can run in parallel → T015 → T016

### Parallel Opportunities

- T013 and T014 can run in parallel (different files: resource_bar.py vs board_renderer.py)
- US1 and US2 can be worked on in parallel after Phase 2 completes
- T005 and T006 can run in parallel (different handler functions, same file but independent sections)

---

## Parallel Example: User Story 2

```
# Launch in parallel (different files):
Task T013: Remove VP from resource_bar.py
Task T014: Add status line to board_renderer.py

# Then sequentially:
Task T015: Wire status line into game_view.py draw call
Task T016: Shift resource bar position
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T003)
2. Complete Phase 3: User Story 1 (T004-T012)
3. **STOP and VALIDATE**: Test quest completion flow end-to-end
4. Quest completion is the core scoring mechanic — this alone delivers significant value

### Incremental Delivery

1. Foundational → Message types ready
2. Add User Story 1 → Quest completion works → Validate
3. Add User Story 2 → Status line visible → Validate
4. Polish → Edge cases, reconnect safety, quickstart validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- The existing `handle_complete_quest()` handler already validates resources and deducts cost — T008 only adds turn advancement
- `QuestCompletionDialog` should follow the same pattern as `BuildingPurchaseDialog` in dialogs.py (solid black background, padded)
- Commit after each task or logical group
