# Tasks: Shadow Studio Building + Bootleg Recording Intrigue Card

**Input**: Design documents from `specs/021-zoarstar-building/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included — Constitution Principle IV requires automated test coverage for new game rules.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add config entries, message types, and model fields needed by all user stories

- [X] T001 [P] Add Shadow Studio building entry (building_023) to config/buildings.json with cost_coins: 8, visitor_reward_special: "copy_occupied_space", owner_bonus_vp: 2, zero base resources
- [X] T002 [P] Add two Bootleg Recording intrigue card entries (intrigue_053, intrigue_054) to config/intrigue.json with effect_type: "copy_occupied_space", effect_value: {"cost_coins": 2}
- [X] T003 [P] Add SelectCopySpaceRequest (action: "select_copy_space", field: space_id: str), CancelCopySpaceRequest (action: "cancel_copy_space"), and CopySpacePromptResponse (action: "copy_space_prompt", fields: eligible_spaces: list[dict], source_type: str) to shared/messages.py; add both request types to the ClientMessage union
- [X] T004 [P] Add pending_copy_source: dict | None = None field to GameState in server/models/game.py (after pending_placement)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared helpers and routing that MUST be complete before any user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement _get_copy_eligible_spaces(state, player) -> list[dict] helper in server/game_engine.py that filters state.board.action_spaces to spaces where occupied_by is not None, occupied_by != player.player_id, and space_type != "backstage"; returns list of dicts with space_id, name, space_type, and reward_preview (reward.model_dump())
- [X] T006 [P] Add _handle_select_copy_space and _handle_cancel_copy_space handler methods in server/network.py that import and delegate to handle_select_copy_space and handle_cancel_copy_space from server.game_engine
- [X] T007 [P] Register "copy_space_prompt" message handler in client/views/game_view.py _register_message_handlers() method, mapping to a new _on_copy_space_prompt stub method

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Copy an Opponent's Occupied Space (Priority: P1) 🎯 MVP

**Goal**: Player places on Shadow Studio, sees opponent-occupied spaces, selects one, receives that space's basic rewards (resources, VP)

**Independent Test**: Purchase Shadow Studio, have opponent occupy a permanent space, visit Shadow Studio, select opponent's space, verify resources granted

### Implementation for User Story 1

- [X] T008 [US1] Implement _resolve_copied_space_rewards() in server/game_engine.py — initial version handling basic resource grants: accept (server, state, player, target_space, source_space_id, pending) parameters; grant target_space.reward via player.resources.add(); build reward_dict; grant visitor_reward_vp if building with visitor_reward_vp > 0; call _evaluate_resource_triggers() on the copied reward; update pending_placement with copied_from_space_id and granted_resources; broadcast WorkerPlacedResponse with reward details; clear pending_copy_source; call _check_quest_completion()
- [X] T009 [US1] Add copy_occupied_space handling in handle_place_worker() building visitor_reward_special block (~line 1244) in server/game_engine.py: call _get_copy_eligible_spaces(); if no eligible spaces, fall through to _check_quest_completion (FR-010); otherwise set state.pending_placement = _pending, set state.pending_copy_source with player_id/source_space_id/source_type="building"/eligible_spaces, send CopySpacePromptResponse to player, return early
- [X] T010 [US1] Implement handle_select_copy_space(server, conn, msg) in server/game_engine.py: validate pending_copy_source exists and player_id matches; validate msg.space_id is in eligible_spaces list; look up target_space from state.board.action_spaces; call _resolve_copied_space_rewards() with the target space
- [X] T011 [US1] Implement handle_cancel_copy_space(server, conn, msg) in server/game_engine.py: validate pending_copy_source exists; if source_type == "intrigue" and cost_deducted > 0, return coins to player; call _unwind_placement(state, player, state.pending_placement) to free source space and reverse any already-granted rewards; clear pending_copy_source and pending_placement; broadcast PlacementCancelledResponse
- [X] T012 [US1] Implement _on_copy_space_prompt(msg) handler in client/views/game_view.py: display a selection dialog listing eligible spaces with names and reward previews (reuse existing dialog patterns from _on_intrigue_target_prompt); on_select sends {"action": "select_copy_space", "space_id": selected_id}; on_cancel sends {"action": "cancel_copy_space"}
- [X] T013 [US1] Write tests for basic copy mechanic in tests/test_copy_occupied_space.py: test_copy_basic_permanent_space (opponent on Motown, copy grants 2 bass players); test_copy_no_valid_targets (no opponents placed, no prompt shown); test_copy_excludes_own_spaces (player's own occupied spaces not in eligible list); test_copy_excludes_empty_spaces; test_cancel_copy_selection_unwinds (worker returns, Shadow Studio freed)

**Checkpoint**: At this point, User Story 1 should be fully functional — basic copy mechanic works for simple resource spaces

---

## Phase 4: User Story 2 - Owner Bonus (Priority: P2)

**Goal**: Shadow Studio owner receives 2 VP when another player visits

**Independent Test**: Have non-owner visit Shadow Studio, verify owner gains 2 VP; owner visits own building, verify no bonus

### Implementation for User Story 2

- [X] T014 [US2] Verify Shadow Studio owner bonus works by confirming building_023 config has owner_bonus_vp: 2 and the existing owner bonus block in handle_place_worker() (lines 1252-1286) handles it — no new code needed, this is config-driven per Constitution Principle VII
- [X] T015 [US2] Write tests for owner bonus in tests/test_copy_occupied_space.py: test_shadow_studio_owner_bonus (non-owner visits, owner gains 2 VP); test_shadow_studio_owner_no_self_bonus (owner visits own building, no VP bonus)

**Checkpoint**: Owner bonus verified working

---

## Phase 5: User Story 3 - Copying Special Spaces (Priority: P2)

**Goal**: Copy mechanic handles all action space types — resource choices, accumulated stock, garage, castle, realtor, and owner bonus cascading from copied buildings

**Independent Test**: Have opponent on a resource choice building, copy it via Shadow Studio, verify choice prompt appears

### Implementation for User Story 3

- [X] T016 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle accumulated stock: if target_space has building_tile with accumulation_type, drain accumulated_stock and add to reward; track in pending for cancel/unwind
- [X] T017 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle building visitor_reward_special values: "draw_intrigue" (draw card to hand), "coins_per_building" (grant coins equal to len(state.board.constructed_buildings)), "draw_contract" (set pending_building_quest and return early for quest selection), "draw_contract_and_complete" (set pending_showcase_bonus + pending_building_quest and return early)
- [X] T018 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle resource choice buildings: if target_space has building_tile.visitor_reward_choice, set pending_resource_choice and send ResourceChoicePromptResponse to player, return early (deferred)
- [X] T019 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle garage spaces: if target_space.space_type == "garage", enter quest selection flow (draw coins + optionally intrigue per garage reward, send quest highlight, set pending state), return early
- [X] T020 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle castle space: if target_space.space_type == "castle", grant first player marker and draw intrigue card
- [X] T021 [US3] Extend _resolve_copied_space_rewards() in server/game_engine.py to handle realtor space: if target_space.space_type == "realtor", enter building purchase flow (send building market data, set pending state), return early
- [X] T022 [US3] Implement owner bonus cascading for copied buildings in _resolve_copied_space_rewards() in server/game_engine.py: if target_space.space_type == "building" and target_space.owner_id exists and != player.player_id, grant the copied building's owner their owner_bonus resources, owner_bonus_vp, and owner_bonus_special; track in pending for unwind; add game_log entry
- [X] T023 [US3] Write tests for special space copying in tests/test_copy_occupied_space.py: test_copy_accumulated_stock_building (stock drained); test_copy_resource_choice_building (choice prompt appears); test_copy_garage_space (quest selection flow); test_copy_castle_space (first player + intrigue); test_copy_owner_bonus_cascading (copied building owner gets bonus); test_copy_owner_bonus_no_self (copying own building, no owner bonus)

**Checkpoint**: All action space types can be copied without errors

---

## Phase 6: User Story 5 - Copy Occupied Space via Intrigue Card (Priority: P2)

**Goal**: Player plays Bootleg Recording from backstage, pays 2 coins, selects opponent-occupied space to copy; full unwind on insufficient coins, no targets, or cancel

**Independent Test**: Give player Bootleg Recording + 2 coins, have opponent occupy a space, play card from backstage, verify coins deducted and space copied

### Implementation for User Story 5

- [X] T024 [US5] Add copy_occupied_space handling in _resolve_intrigue_effect() in server/game_engine.py (~line 1991): check player.resources.coins >= cost_coins from effect_value; if insufficient, set effect["insufficient_coins"] = True and return; call _get_copy_eligible_spaces(); if empty, set effect["no_valid_targets"] = True and return; deduct coins, set effect["pending"] = True, effect["cost_deducted"] = cost_coins, effect["eligible_spaces"] = eligible list
- [X] T025 [US5] Add copy_occupied_space flow handling in handle_place_worker_backstage() in server/game_engine.py: after _resolve_intrigue_effect() call, check for insufficient_coins flag → return card to hand, free backstage slot, return worker, send error "You need 2 coins to play this card"; check for no_valid_targets flag → same unwind, send error "No valid target spaces available"; check for pending flag → set state.pending_placement (backstage source), set state.pending_copy_source with source_type="intrigue" and cost_deducted, send CopySpacePromptResponse, return early
- [X] T026 [US5] Update handle_cancel_copy_space() in server/game_engine.py to handle intrigue source: when source_type == "intrigue", return 2 coins to player, return intrigue card to player.intrigue_hand, unwind backstage slot (clear occupied_by, return worker)
- [X] T027 [US5] Write tests for intrigue card copy in tests/test_copy_occupied_space.py: test_bootleg_basic_copy (pay 2 coins, copy space, get rewards); test_bootleg_insufficient_coins (1 coin, error, unwind backstage); test_bootleg_no_valid_targets (has coins but no opponents placed, error, unwind); test_bootleg_cancel_returns_coins (cancel selection, 2 coins returned, card returned to hand, backstage slot freed); test_bootleg_owner_bonus_cascade (copied building owner gets bonus)

**Checkpoint**: Intrigue card path works independently with full cancel/unwind support

---

## Phase 7: User Story 4 - Quest Completion After Copy (Priority: P3)

**Goal**: After copy resolves, standard post-action flow triggers quest completion check

**Independent Test**: Copy a space granting resources sufficient to complete a quest, verify quest completion prompt appears

### Implementation for User Story 4

- [X] T028 [US4] Verify _resolve_copied_space_rewards() calls _check_quest_completion(server, state) after immediate resolution (non-deferred paths) in server/game_engine.py — this should already be implemented in T008; for deferred paths (resource choice, quest selection), verify the existing deferred handlers call _check_quest_completion on completion
- [X] T029 [US4] Write test for quest completion after copy in tests/test_copy_occupied_space.py: test_quest_completion_prompt_after_copy (copy space that grants enough resources to complete a quest, verify QuestCompletionPromptResponse is sent)

**Checkpoint**: All user stories functional and independently testable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates, validation, and final checks

- [X] T030 Update specs/waterdeep-card-mapping.md to mark The Zoarstar as DONE with music-themed equivalents (Shadow Studio building + Bootleg Recording intrigue card)
- [X] T031 Run full test suite: cd src && pytest && ruff check . — fix any failures or lint issues
- [X] T032 Validate quickstart.md scenarios by reviewing test coverage against all 11 scenarios; add any missing test cases to tests/test_copy_occupied_space.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — all 4 tasks run in parallel
- **Foundational (Phase 2)**: Depends on Phase 1 completion (T003 for messages, T004 for model)
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3): No dependencies on other stories — this is the MVP
  - US2 (Phase 4): Config-driven, no code dependencies on other stories
  - US3 (Phase 5): Extends _resolve_copied_space_rewards() from US1 — depends on T008
  - US5 (Phase 6): Depends on US1 core mechanic (T008-T011) for shared copy logic
  - US4 (Phase 7): Verification only — depends on US1 (T008)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no story dependencies
- **US2 (P2)**: Independent — config-only, can run in parallel with US1
- **US3 (P2)**: Extends US1's _resolve_copied_space_rewards() — must start after T008
- **US5 (P2)**: Uses US1's shared copy logic — must start after T008-T011
- **US4 (P3)**: Verification of US1's post-action flow — must start after T008

### Within Each User Story

- Models/config before server logic
- Server logic before client UI
- Core implementation before tests
- Story complete before moving to next priority

### Parallel Opportunities

- T001, T002, T003, T004 all run in parallel (different files)
- T006, T007 run in parallel (different files)
- T014, T015 run in parallel (config verification + test writing)
- US2 (Phase 4) can run in parallel with US3 (Phase 5) since they modify different code areas

---

## Parallel Example: User Story 1

```bash
# Phase 1 — all setup tasks in parallel:
T001: Add building_023 to config/buildings.json
T002: Add intrigue cards to config/intrigue.json
T003: Add message types to shared/messages.py
T004: Add pending_copy_source to server/models/game.py

# Phase 2 — routing tasks in parallel:
T006: Add handler routes to server/network.py
T007: Register message handler in client/views/game_view.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (config + messages + model)
2. Complete Phase 2: Foundational (helpers + routing)
3. Complete Phase 3: User Story 1 (basic copy mechanic)
4. **STOP and VALIDATE**: Test basic copy on permanent spaces
5. Playtest: purchase Shadow Studio, copy opponent's space

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Basic copy works → Playtest (MVP!)
3. Add User Story 2 → Owner bonus verified
4. Add User Story 3 → All space types copyable → Playtest
5. Add User Story 5 → Intrigue card path works → Playtest
6. Add User Story 4 → Quest completion verified
7. Polish → Full test suite passes, docs updated

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- _resolve_copied_space_rewards() is built incrementally: basic in US1, extended in US3
- handle_cancel_copy_space() is built in US1, extended for intrigue coin return in US5
- Owner bonus (US2) is entirely config-driven — no new code, just verification
- Commit after each logical unit of work
