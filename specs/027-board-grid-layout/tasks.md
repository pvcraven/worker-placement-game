# Tasks: Board Grid Layout

**Input**: Design documents from `specs/027-board-grid-layout/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted. Existing test suite validates via `pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the BoardGrid utility and update card dimension constants

- [X] T001 Create `client/ui/board_grid.py` with `BoardGrid` class. Constructor takes `(x, y, w, h, cols=7, rows=8, margin_pct=0.02)` and computes `cell_w = w / cols`, `cell_h = h / rows`, `margin = margin_pct * cell_w`. Implement `cell_rect(col, row, col_span=1.0, row_span=1.0)` returning `(center_x, center_y, content_width, content_height)` where center_x/center_y place the element at the grid position (col/row are float, supporting half-integers like 3.5), content_width/height are the cell span minus margins on each side. Row 0 = top of board: `pixel_y = y + h - (row + row_span/2) * cell_h`. Implement `card_scale(row_span, base_width, base_height)` returning a single uniform scale factor that fits a card of `base_width × base_height` pixels into the content area of `col_span=1, row_span=row_span` cells. Implement `panel_width(panel_cols=2)` returning `panel_cols * cell_w`. Add `cell_width` and `cell_height` as read-only properties.

- [X] T002 [P] Update card height constants in `shared/constants.py` (lines 51-54). Keep `CARD_WIDTH = 200`. Set `SPACE_CARD_HEIGHT` to a 1-row proportional height (keep current 100 or adjust if needed for the grid aspect ratio). Set `BUILDING_CARD_HEIGHT` to exactly 1.5× `SPACE_CARD_HEIGHT`. Set `CARD_HEIGHT` (quest cards) to exactly 3× `SPACE_CARD_HEIGHT`. All card types must share `CARD_WIDTH = 200` as base width.

**Checkpoint**: BoardGrid utility ready. Card constants updated.

---

## Phase 2: Foundational — Card Image Regeneration

**Purpose**: Regenerate all card images with uniform base width and proportional heights

- [X] T003 Update space card generation in `card-generator/generate_cards.py`. Currently space cards are generated at `cw = CARD_WIDTH * 2` (~line 1602). Change to use `CARD_WIDTH` as the base width (same as other card types). Adjust the space card canvas height to match the updated `SPACE_CARD_HEIGHT` constant. Scale internal drawing elements (text, icons, borders) proportionally for the new dimensions. All space card PNGs in `client/assets/card_images/spaces/` must be regenerated.

- [X] T004 Update building card generation in `card-generator/generate_cards.py`. Verify building cards use `CARD_WIDTH` as base width (they likely already do). Adjust canvas height to match updated `BUILDING_CARD_HEIGHT` (1.5× space height). Verify building market card PNGs and constructed building PNGs use the same dimensions.

- [X] T005 Update quest card generation in `card-generator/generate_cards.py`. Verify quest cards use `CARD_WIDTH` as base width. Adjust canvas height to match updated `CARD_HEIGHT` (3× space height). Verify all quest card PNGs are regenerated correctly.

- [X] T006 Run card image generation: `cd card-generator && python generate_cards.py`. Verify all PNG outputs in `client/assets/card_images/` have the correct uniform width and proportional heights.

**Checkpoint**: All card images regenerated with uniform base width. Visual check: cards look correct at their new aspect ratios.

---

## Phase 3: User Story 1 — Grid-Based Board Layout (Priority: P1) MVP

**Goal**: Replace ad-hoc fractional positioning in board_renderer.py with BoardGrid calls. All board elements snap to grid cells.

**Independent Test**: Start a game. All elements should be aligned to grid positions. Resize the window — elements stay aligned without overlap.

### Implementation for User Story 1

- [X] T007 [US1] Add grid placement data to `client/ui/board_renderer.py`. Replace `_SPACE_LAYOUT` dict (lines 24-36) and `_BACKSTAGE_Y` list (line 38) with a `_GRID_PLACEMENT` dict mapping element IDs to `(col, row, col_span, row_span)` tuples. Include all permanent action spaces: merch_store (0,0,1,1), motown (0,1,1,1), guitar_center (0,2,1,1), talent_show (0,3,1,1), rhythm_pit (0,4,1,1), jam_session (0,5,1,1), whisper_room (0,6,1,1), fastpass (0,7,1,1), sunset_records (3.5,0,1,1), the_back_room (4.5,0,1,1), the_garage (5.5,0,1,1). Include backstage: backstage_slot_1 (3,0,1,1), backstage_slot_2 (3,1,1,1), backstage_slot_3 (3,2,1,1). Include realtor: realtor (3,4,1,1). Import `BoardGrid` from `client.ui.board_grid`.

- [X] T008 [US1] Refactor `_rebuild_shapes()` in `client/ui/board_renderer.py` (lines 360-555). At the start of the method, create `self._grid = BoardGrid(x, y, w, h)`. Replace ALL fractional positioning math with `self._grid.cell_rect()` calls using `_GRID_PLACEMENT` coordinates:
  - Permanent action spaces (~lines 391-410): loop `_GRID_PLACEMENT` entries for space IDs, call `cell_rect(col, row, 1, 1)` for each, build sprites and click rects from returned center/dimensions.
  - Backstage slots (~lines 412-439): use `_GRID_PLACEMENT["backstage_slot_N"]` positions instead of `_BACKSTAGE_Y` list and dynamic garage-based centering.
  - Realtor space (~lines 441-460): use `_GRID_PLACEMENT["realtor"]` instead of `y + 0.40 * h` and midpoint calculation.
  - Constructed buildings (~lines 462-495): compute grid position as `col = 1 + (i % 2)`, `row = (i // 2) * 1.5`, call `cell_rect(col, row, 1, 1.5)`. Remove hardcoded `building_start_x = 0.22`, `building_col_step = 0.125`, and manual `merch_top_y` math.
  - Face-up quests (~lines 497-525): compute grid position for each quest: quests 0-1 at `(4+i, 2, 1, 3)`, quests 2-3 at `(4+(i-2), 5, 1, 3)`. Remove `garage_cx`, `q_spacing`, manual centering.
  - Face-up building market (~lines 526-554): compute grid position as `(4+i, 5.5, 1, 1.5)`. Remove manual right-alignment math.
  - Use `self._grid.card_scale()` for uniform scaling instead of per-element `s * 0.5` or `bld_scale = 0.42`.

- [X] T009 [US1] Refactor `draw()` method in `client/ui/board_renderer.py` (lines 137-358). Update the cached dimension variables (card_w, card_h, bld_h, space_h at ~lines 164-168) to use `self._grid.card_scale()` for uniform sizing. Update VP text positioning, owner text positioning, stock text positioning, and highlight rectangle positioning to use grid-derived coordinates from `self._grid.cell_rect()` instead of `self._quest_positions`, `self._bld_positions`, and manual offset calculations. Ensure all sprite list cache invalidation logic still works correctly.

- [X] T010 [US1] Refactor `_update_workers()` in `client/ui/board_renderer.py` (lines 580-677). Replace all positioning math with `self._grid.cell_rect()` calls:
  - Permanent spaces (~lines 597-603): use `_GRID_PLACEMENT[space_id]` instead of `_SPACE_LAYOUT` fractional positions.
  - Backstage slots (~lines 605-621): use `_GRID_PLACEMENT[f"backstage_slot_{slot_num}"]` instead of `_BACKSTAGE_Y` list.
  - Realtor (~lines 623-635): use `_GRID_PLACEMENT["realtor"]` instead of `self._space_rects` lookup.
  - Constructed buildings (~lines 637-657): compute grid position `col = 1 + (i % 2)`, `row = (i // 2) * 1.5`, use `cell_rect()`. Remove duplicated `building_start_x`, `building_col_step`, `bld_scale` constants.
  - Worker token offset: derive from grid cell width instead of `card_w / 2 - 10 * s`.

- [X] T011 [US1] Verify click detection still works in `get_space_at()` (lines 679-684). The method uses `self._space_rects` which is populated during `_rebuild_shapes()`. After refactoring T008, ensure all `_space_rects` entries use the same (x, y, w, h) format — the grid's `cell_rect()` returns (center_x, center_y, w, h) so convert to (left_x, bottom_y, w, h) for click rects. Test by clicking every interactive space type.

**Checkpoint**: All board elements positioned via grid. Window resize works correctly. Click detection functional for all spaces. MVP complete.

---

## Phase 4: User Story 2 — Element Placement on Grid (Priority: P2)

**Goal**: Fine-tune the placement map to match the spec's detailed grid positions. Verify all elements appear in their expected grid regions.

**Independent Test**: Start a game with multiple players. All element types appear at their documented grid positions.

### Implementation for User Story 2

- [X] T012 [US2] Fine-tune grid placement positions in `client/ui/board_renderer.py`. After visual testing from US1, adjust any `_GRID_PLACEMENT` coordinates or dynamic position calculations that don't match the spec placement map. Verify:
  - Purchased buildings fill columns 1-2 at 1.5-row intervals (rows 0, 1.5, 3, 4.5, 6, 7.5)
  - Face-up quests at (4,2), (5,2), (4,5), (5,5) — each spanning 3 rows
  - Building market at (4,5.5), (5,5.5), (6,5.5) — each spanning 1.5 rows
  - Top-row spaces at half-columns 3.5, 4.5, 5.5
  - No visual overlaps between any elements

- [X] T013 [US2] Verify half-column positioning renders correctly in `client/ui/board_grid.py`. Confirm that `cell_rect(3.5, 0, 1, 1)` places Sunset Records centered between columns 3 and 4. Confirm `cell_rect(4.5, 0, 1, 1)` and `cell_rect(5.5, 0, 1, 1)` work similarly for Back Room and Garage. If off by half a cell, fix the center_x calculation.

**Checkpoint**: All elements at documented grid positions. Half-column rendering correct. Visual layout matches spec placement map.

---

## Phase 5: User Story 3 — Side Panel Grid Integration (Priority: P3)

**Goal**: Derive side panel width from grid cell size instead of hardcoded 450px.

**Independent Test**: Resize the window. Side panel width scales proportionally with the board grid.

### Implementation for User Story 3

- [X] T014 [US3] Update side panel width calculation in `client/views/game_view.py` (~line 2272). Replace `log_w = int(450 * s)` with grid-derived width. Compute the full 9-column cell width: `full_cell_w = cw / 9`, then `log_w = int(2 * full_cell_w)`. The board area width becomes `board_w = cw - log_w` (this line already exists at ~line 2273). Ensure the board's 7-column grid and the panel's 2-column allocation are consistent.

- [X] T015 [US3] Verify `BoardGrid` in `board_renderer.py` receives the correct `w` parameter after the panel width change. The board_renderer is called with `w=board_w` (~line 2289) which is now `cw - log_w`. The grid divides this into 7 columns. Verify that `cell_w` from the grid matches `full_cell_w` from game_view (both should be `cw / 9`). If they differ, adjust the grid's column count or the width passed to it.

**Checkpoint**: Side panel width derived from grid. Panel and board scale proportionally together.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T016 Run existing test suite: `cd src && pytest` to verify no regressions
- [X] T017 Run linting: `cd src && ruff check .` to verify code quality
- [ ] T018 Manual test (requires visual verification): start a 2-player game, verify all element types render at correct grid positions per quickstart.md Scenario 1
- [ ] T019 Manual test: resize the window to various sizes (narrow, wide, square), verify elements stay aligned per quickstart.md Scenario 2
- [ ] T020 Manual test: click every interactive space type (permanent, backstage, realtor, quests, buildings), verify click detection per quickstart.md Scenario 3
- [ ] T021 Manual test: purchase buildings and place workers, verify worker tokens and building cards at correct grid positions per quickstart.md Scenarios 3-4

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately. T001 and T002 are parallel (different files).
- **Foundational (Phase 2)**: T003-T005 depend on T002 (updated constants). T006 depends on T003-T005.
- **US1 (Phase 3)**: Depends on T001 (BoardGrid class) and T006 (regenerated card images). T007-T011 are sequential (all modify board_renderer.py).
- **US2 (Phase 4)**: Depends on US1 completion. T012-T013 are sequential (visual tuning).
- **US3 (Phase 5)**: Depends on US1 completion. T014 modifies game_view.py. T015 verifies board_renderer.py integration.
- **Polish (Phase 6)**: Depends on all user stories complete.

### User Story Dependencies

- **US1 (P1)**: Depends on Setup + Foundational. Independent of US2/US3.
- **US2 (P2)**: Depends on US1 (needs grid rendering working to fine-tune positions).
- **US3 (P3)**: Depends on US1 (needs grid working). Independent of US2.

### Within board_renderer.py (sequential constraint)

All tasks modifying `client/ui/board_renderer.py` must be sequential:
T007 → T008 → T009 → T010 → T011 → T012 → T013

### Parallel Opportunities

- T001 (board_grid.py) and T002 (constants.py) can run in parallel
- T003, T004, T005 (card generator changes) are sequential (same file) but independent of T001
- US3 (game_view.py) can run in parallel with US2 (board_renderer.py fine-tuning) since they modify different files
- T014 (game_view.py) is independent of T012-T013 (board_renderer.py)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create BoardGrid utility + update constants (T001-T002)
2. Complete Phase 2: Regenerate card images (T003-T006)
3. Complete Phase 3: Grid-based positioning in board_renderer (T007-T011)
4. **STOP and VALIDATE**: Start a game, verify grid alignment, resize window, click spaces
5. Board is fully functional at this point

### Incremental Delivery

1. T001-T002 → Setup → BoardGrid utility and constants ready
2. T003-T006 → Foundational → Card images regenerated with uniform dimensions
3. T007-T011 → US1 → All elements positioned via grid (MVP!)
4. T012-T013 → US2 → Fine-tuned positions matching spec placement map
5. T014-T015 → US3 → Side panel width derived from grid
6. T016-T021 → Polish → Tests pass, all manual scenarios verified

---

## Notes

- This feature is entirely client-side — no server changes needed
- The card generator tasks (T003-T005) may need visual iteration once grid cell proportions are finalized
- The main complexity is in T008 (refactoring _rebuild_shapes) — this is the largest single task
- All 5 board_renderer.py tasks (T007-T011) must be done sequentially since they modify the same file
- US2 is primarily visual tuning — it may be trivially completed if US1 positions are already correct
- Total: 21 tasks (2 setup, 4 foundational, 5 US1, 2 US2, 2 US3, 6 polish)
