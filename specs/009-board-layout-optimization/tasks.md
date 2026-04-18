# Tasks: Board Layout Optimization

**Input**: Design documents from `/specs/009-board-layout-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested. No test tasks generated.

**Organization**: Tasks grouped by user story. All changes are client-side only (no server changes).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the cancel button asset and prepare for layout changes

- [ ] T001 Create or add cancel.png graphic (red cancel button icon, ~48x48px) in client/assets/cancel.png

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update board layout coordinates and add building card rendering — required by all user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Update `_SPACE_LAYOUT` dict in client/ui/board_renderer.py: shift all permanent spaces up (merch_store to 0.92, motown to 0.82, guitar_center to 0.72, talent_show to 0.62, rhythm_pit to 0.52, castle_waterdeep to 0.42, garages to y=0.92, move realtor to (0.38, 0.18) near building area)
- [ ] T003 Update `_BACKSTAGE_LAYOUT` list in client/ui/board_renderer.py: move backstage slots to left column at (0.08, 0.32), (0.08, 0.22), (0.08, 0.12)
- [ ] T004 Update face-up quest card positioning in client/ui/board_renderer.py `draw()` method: change card_y from `y + 0.60 * h` to `y + 0.68 * h` to shift quest cards up
- [ ] T005 Add `draw_building` classmethod to client/ui/card_renderer.py that renders a building card showing name, cost in coins, VP, visitor reward, owner bonus, and description (similar layout to draw_contract but with building-specific fields)
- [ ] T006 Add face-up building card rendering in client/ui/board_renderer.py `draw()` method: render face-up buildings as cards centered at ~y=0.30, using CardRenderer.draw_building, with click rects stored as `building_card_{id}`
- [ ] T007 Update `_rebuild_shapes()` in client/ui/board_renderer.py to account for new positions (spaces shifted up, backstage in left column, building card area)
- [ ] T008 Add `_face_up_buildings` and `_building_deck_remaining` state to BoardRenderer in client/ui/board_renderer.py, fed via existing `update_building_market()` method
- [ ] T009 Remove the "Real Estate Listings" button from the button bar in client/views/game_view.py (remove the UIFlatButton creation, the `_toggle_building_market` method, and `_show_building_market` state)
- [ ] T010 Remove `_draw_building_market_panel()` method and all references from client/views/game_view.py

**Checkpoint**: Board renders with new layout — quest cards up, backstage in left column, buildings visible on board, realtor near buildings. No popups.

---

## Phase 3: User Story 1 - Inline Quest Selection (Priority: P1)

**Goal**: Replace quest selection popup with inline highlight-and-click on face-up quest cards

**Independent Test**: Place a worker on a Garage space, verify quest cards highlight, click one to select or click cancel to abort

### Implementation for User Story 1

- [ ] T011 [US1] Add highlight state fields to game_view.py: `_highlight_mode: str | None = None`, `_highlighted_ids: list[str] = []`, `_cancel_sprite: arcade.Sprite | None = None`
- [ ] T012 [US1] Load cancel.png sprite in game_view.py `on_show_view()` and position it in lower-left corner (x=50, y=130), initially hidden
- [ ] T013 [US1] Add `_enter_highlight_mode(mode: str, ids: list[str])` method in game_view.py that sets highlight state and shows cancel sprite
- [ ] T014 [US1] Add `_exit_highlight_mode()` method in game_view.py that clears highlight state and hides cancel sprite
- [ ] T015 [US1] Modify the garage space click handler in game_view.py: instead of opening CardSelectionDialog, call `_enter_highlight_mode("quest_selection", [list of face-up quest IDs])`
- [ ] T016 [US1] Pass highlight info to board_renderer when drawing: add `highlighted_ids` parameter to BoardRenderer.draw() or store as state, so quest cards render with `highlight=True` when their ID is in the list
- [ ] T017 [US1] Draw the cancel sprite in game_view.py `on_draw()` when `_highlight_mode` is not None
- [ ] T018 [US1] Handle quest card click during highlight mode in game_view.py `on_mouse_press()`: if `_highlight_mode == "quest_selection"` and clicked card ID is in `_highlighted_ids`, send select_quest_card message and call `_exit_highlight_mode()`
- [ ] T019 [US1] Handle cancel button click in game_view.py `on_mouse_press()`: if cancel sprite rect is clicked during highlight mode, send cancel message and call `_exit_highlight_mode()`
- [ ] T020 [US1] Remove the CardSelectionDialog usage for garage quest selection from game_view.py (the `_quest_dialog` creation path for garage spaces)

**Checkpoint**: Placing a worker on a Garage space highlights quest cards with yellow borders, clicking a card selects it, clicking cancel aborts. No popup dialog.

---

## Phase 4: User Story 2 - Always-Visible Building Market (Priority: P2)

**Goal**: Buildings are always visible on the board — already achieved in Phase 2 foundational tasks

**Independent Test**: Start a game, verify buildings are visible on the board without clicking any button

### Implementation for User Story 2

- [ ] T021 [US2] Ensure BoardRenderer receives building market updates via game_view.py message handlers: wire `_on_building_market_update()` to call `board_renderer.update_building_market()` and trigger a redraw
- [ ] T022 [US2] Ensure initial game state populates board_renderer building market data in game_view.py `_on_game_started()` / `_on_state_sync()`
- [ ] T023 [US2] Verify building card display updates when a building is purchased (remove from display, show replacement) — wire `_on_building_constructed()` to refresh building market on board_renderer

**Checkpoint**: Buildings visible on board at all times. No Real Estate Listings button. Building display updates on purchase.

---

## Phase 5: User Story 3 - Inline Building Purchase (Priority: P3)

**Goal**: Replace building purchase popup with inline highlight-and-click on face-up building cards

**Independent Test**: Place a worker on Realtor, verify affordable buildings highlight, click one to purchase or click cancel to abort

### Implementation for User Story 3

- [ ] T024 [US3] Modify the Realtor space click handler in game_view.py: instead of opening BuildingPurchaseDialog, determine affordable buildings (compare player coins to building cost), call `_enter_highlight_mode("building_purchase", [affordable building IDs])`, or show error if none affordable
- [ ] T025 [US3] Handle building card click during highlight mode in game_view.py `on_mouse_press()`: if `_highlight_mode == "building_purchase"` and clicked card ID is in `_highlighted_ids`, send purchase_building message and call `_exit_highlight_mode()`
- [ ] T026 [US3] Handle click on non-highlighted (unaffordable) building during building_purchase mode: show error message "You can't afford that building" in status bar
- [ ] T027 [US3] Remove the BuildingPurchaseDialog usage from game_view.py (the `_building_dialog` creation path)
- [ ] T028 [US3] Handle quest reward "Choose Free Building": when the reward choice prompt arrives for choose_building, call `_enter_highlight_mode("building_purchase", [all building IDs])` instead of opening RewardChoiceDialog for buildings

**Checkpoint**: Placing a worker on Realtor highlights affordable buildings, clicking one purchases it, clicking cancel aborts. Error message for unaffordable clicks.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup and validation

- [ ] T029 Remove unused dialog imports and dead code from client/views/game_view.py and client/ui/dialogs.py (BuildingPurchaseDialog, unused CardSelectionDialog paths)
- [ ] T030 Run ruff check on all modified files: client/ui/board_renderer.py, client/ui/card_renderer.py, client/ui/dialogs.py, client/views/game_view.py
- [ ] T031 Run quickstart.md scenarios 1-11 end-to-end (manual testing)
- [ ] T032 Verify all existing features still work: worker placement, quest completion, intrigue, backstage reassignment, player overview

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — create cancel.png asset
- **Foundational (Phase 2)**: Depends on Phase 1 — layout changes and building rendering
- **US1 (Phase 3)**: Depends on Phase 2 — needs new layout and highlight infrastructure
- **US2 (Phase 4)**: Depends on Phase 2 — needs buildings rendered on board
- **US3 (Phase 5)**: Depends on Phase 2 and Phase 3 (reuses highlight mode from US1)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **US1 (P1)**: Establishes highlight mode infrastructure. Must complete before US3.
- **US2 (P2)**: Independent of US1. Can run in parallel after Phase 2.
- **US3 (P3)**: Depends on US1 (reuses `_enter_highlight_mode` / `_exit_highlight_mode`). Also depends on US2 (buildings must be on board).

### Parallel Opportunities

- T002, T003, T004 can run in parallel (different layout constants)
- T005 can run in parallel with T002-T004 (different file)
- T009, T010 can run in parallel (independent removals)
- US2 tasks (T021-T023) can run in parallel with US1 tasks (T011-T020) after Phase 2

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create cancel.png
2. Complete Phase 2: New layout + building rendering on board
3. Complete Phase 3: Inline quest selection with highlights
4. **STOP and VALIDATE**: Test quest highlight selection independently

### Incremental Delivery

1. Setup + Foundational → Board renders with new layout, buildings visible
2. Add US1 → Inline quest selection works → Validate
3. Add US2 → Building market wired up on board → Validate
4. Add US3 → Inline building purchase works → Validate
5. Polish → Cleanup, full regression test

---

## Notes

- All changes are client-side only — no server protocol changes
- Existing server messages (select_quest_card, cancel_quest_selection, purchase_building, cancel_purchase_building) are reused as-is
- The highlight state is transient UI state, not persisted or synced
