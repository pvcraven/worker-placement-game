# Tasks: Intrigue Targeting & Player Overview

**Input**: Design documents from `/specs/007-intrigue-targeting-player-overview/`
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

**Purpose**: Add shared message types and state model used by both user stories

- [ ] T001 [P] Add `IntrigueTargetPromptResponse` (action: "intrigue_target_prompt", fields: effect_type, effect_value, eligible_targets list) and `IntrigueEffectResolvedResponse` (action: "intrigue_effect_resolved", fields: player_id, target_player_id, effect_type, resources_affected) to shared/messages.py. Add both to the ServerMessage union. Also add `CancelIntrigueTargetRequest` (action: "cancel_intrigue_target") to ClientMessage union.
- [ ] T002 [P] Add `pending_intrigue_target: dict | None = None` field to GameState model in server/models/game.py. This dict stores: player_id, slot_number, intrigue_card (as dict), effect_type, effect_value, eligible_targets (list of player_ids).
- [ ] T003 Add route for `cancel_intrigue_target` action in server/network.py dispatch, calling `handle_cancel_intrigue_target` from server/game_engine.py.

**Checkpoint**: Message types and state model ready — user story implementation can begin

---

## Phase 3: User Story 1 - Targeted Intrigue Card Resolution (Priority: P1)

**Goal**: Players can target opponents with steal_resources and opponent_loses intrigue cards via a selection dialog. Cancel unwinds the backstage placement.

**Independent Test**: Start a 2-player game. Play a steal_resources intrigue card on a backstage slot. Verify target dialog appears, select opponent, confirm resource transfer. Also test cancel and no-valid-targets flows.

### Implementation for User Story 1

- [ ] T004 [US1] In server/game_engine.py `_resolve_intrigue_effect()`, when effect_target is "choose_opponent": compute eligible targets (opponents with at least 1 of the targeted resources), save pending state to `state.pending_intrigue_target`, and return a special effect dict with `{"type": effect_type, "pending": True, "eligible_targets": [...]}` instead of resolving immediately.
- [ ] T005 [US1] In server/game_engine.py `handle_place_worker_backstage()`, after `_resolve_intrigue_effect()` returns, check if `state.pending_intrigue_target` is set. If so, send `IntrigueTargetPromptResponse` to the active player with eligible targets (include player_id, player_name, and resource counts for each) and return early (do not call `_check_quest_completion`).
- [ ] T006 [US1] In server/game_engine.py `handle_place_worker_backstage()`, handle the no-valid-targets case: if effect_target is "choose_opponent" but no opponents have the targeted resources, auto-unwind the backstage placement (clear slot.occupied_by, return card to hand, restore available_workers, clear pending state), send an ErrorResponse with code "NO_VALID_TARGETS", and broadcast `PlacementCancelledResponse` with the backstage slot space_id.
- [ ] T007 [US1] In server/game_engine.py, replace the stub `handle_choose_intrigue_target()` with full implementation: validate pending_intrigue_target exists for this player, validate target_player_id is in eligible_targets, resolve steal_resources (transfer each resource capped at target's amount) or opponent_loses (reduce target's resources, min 0), clear pending_intrigue_target, broadcast `IntrigueEffectResolvedResponse`, then call `_check_quest_completion`.
- [ ] T008 [US1] In server/game_engine.py, implement `handle_cancel_intrigue_target()`: validate pending_intrigue_target exists, unwind the backstage placement (clear slot, return intrigue card to hand, restore available_workers), clear pending_intrigue_target, broadcast `PlacementCancelledResponse` with backstage_slot_N space_id.
- [ ] T009 [US1] In client/ui/dialogs.py, add `PlayerTargetDialog` class: takes a title, effect description string, list of eligible targets (player_id, player_name, resources dict), on_select(player_id) callback, and on_cancel callback. Shows each eligible opponent as a button with their name and relevant resource counts. Includes a Cancel button.
- [ ] T010 [US1] In client/views/game_view.py `_handle_message()`, add handler for "intrigue_target_prompt" action that calls `_on_intrigue_target_prompt(msg)`.
- [ ] T011 [US1] In client/views/game_view.py, implement `_on_intrigue_target_prompt()`: extract eligible_targets and effect info from the message, show `PlayerTargetDialog`. On select, send `{"action": "choose_intrigue_target", "target_player_id": player_id}`. On cancel, send `{"action": "cancel_intrigue_target"}`.
- [ ] T012 [US1] In client/views/game_view.py `_handle_message()`, add handler for "intrigue_effect_resolved" action that calls `_on_intrigue_effect_resolved(msg)`.
- [ ] T013 [US1] In client/views/game_view.py, implement `_on_intrigue_effect_resolved()`: update both the acting player's and target player's local resource state using the resources_affected dict (add for steal attacker, subtract for steal target; subtract only for opponent_loses target). Update resource bar if either is the local player. Log the effect to game_log_panel.

**Checkpoint**: Targeted intrigue cards work end-to-end. Steal and opponent_loses effects resolve correctly with dialog, cancel, and no-valid-targets flows.

---

## Phase 4: User Story 2 - Player Overview Panel (Priority: P2)

**Goal**: A toggle panel showing all players' resources, worker counts, and progress in a table.

**Independent Test**: Start a game, click "Player Overview", verify table shows all players with correct stats. Toggle closes it.

### Implementation for User Story 2

- [ ] T014 [P] [US2] In client/views/game_view.py `_build_ui()`, add a "Player Overview" button to the existing button row (after "Real Estate Listings"). Wire its on_click to `_toggle_player_overview()`.
- [ ] T015 [P] [US2] In client/views/game_view.py, add `_show_player_overview = False` to `__init__` and implement `_toggle_player_overview()` following the same pattern as `_toggle_quests()` — sets `_show_player_overview = True`, sets all other panel flags to False.
- [ ] T016 [US2] In client/views/game_view.py, implement `_draw_player_overview_panel(w, h)`: draw a panel overlay showing a table. Header row: Name, W, G, B, D, S, $, Intr, Quests, Done, VP. One data row per player from `self.game_state["players"]`. For opponent card counts, use `intrigue_hand_count` and `contract_hand_count` fields. For self, use `len(intrigue_hand)` and `len(contract_hand)`. Highlight the current player's row with a distinct background color.
- [ ] T017 [US2] In client/views/game_view.py `on_draw()`, add rendering call: `if self._show_player_overview: self._draw_player_overview_panel(w, h)`. Also update `_toggle_quests`, `_toggle_intrigue`, `_toggle_building_market` to set `_show_player_overview = False` for mutual exclusivity.

**Checkpoint**: Player overview panel works. Shows all player stats, toggles correctly, mutually exclusive with other panels.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T018 Verify backstage cancel during targeting correctly restores the board in client/ui/board_renderer.py (backstage slot returns to unoccupied visual state)
- [ ] T019 Run quickstart.md scenarios 1-8 end-to-end and verify all test scenarios pass
- [ ] T020 Verify intrigue target resolution displays correctly in game log after steal/opponent_loses effects

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Phase 2 (T001-T003 for messages and state model)
- **User Story 2 (Phase 4)**: No dependency on Phase 2 or US1 — can start after Phase 2 or in parallel
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) for message types and state model
- **User Story 2 (P2)**: Independent — only modifies client/views/game_view.py (different sections than US1)

### Within Each User Story

- US1: T004 (server effect detection) → T005/T006 (server backstage handling) → T007/T008 (server target/cancel handlers) → T009 (client dialog) → T010/T011 (client prompt handler) → T012/T013 (client resolution handler)
- US2: T014/T015 (button + toggle, parallel) → T016 (panel drawing) → T017 (render integration)

### Parallel Opportunities

- T001 and T002 can run in parallel (different files: messages.py vs game.py)
- T014 and T015 can run in parallel (same file but different sections)
- US2 can run in parallel with US1 (different code sections)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T003)
2. Complete Phase 3: User Story 1 (T004-T013)
3. **STOP and VALIDATE**: Start a 2-player game, play a steal card, verify targeting works
4. Targeted intrigue cards alone deliver immediate value — core mechanic is fixed

### Incremental Delivery

1. Foundational → Messages and state ready
2. Add User Story 1 → Targeting works → Validate
3. Add User Story 2 → Player overview panel → Validate
4. Polish → Quickstart validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Server route for `choose_intrigue_target` already exists in network.py — only `cancel_intrigue_target` needs a new route
- `ChooseIntrigueTargetRequest` message already exists in shared/messages.py — only new messages needed are responses and cancel request
- The existing stub handler in game_engine.py will be replaced, not extended
- Commit after each task or logical group
