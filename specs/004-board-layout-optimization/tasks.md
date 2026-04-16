# Tasks: Board Layout Optimization

**Input**: Design documents from `/specs/004-board-layout-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (not requested in feature specification).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup tasks needed. This feature modifies existing files only; no new dependencies or project structure changes required.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational/blocking tasks. All changes are scoped to individual user stories.

**Checkpoint**: Proceed directly to user story implementation.

---

## Phase 3: User Story 1 - Remove Redundant Labels and Reclaim Vertical Space (Priority: P1) MVP

**Goal**: Remove "THE BOARD", "THE GARAGE", and "BACKSTAGE" heading labels. Shift all board elements upward. Rename backstage slot labels to "Backstage 1/2/3".

**Independent Test**: Launch a new game and verify no heading labels appear. Verify backstage slots read "Backstage 1", "Backstage 2", "Backstage 3". Verify board elements use more vertical space with no large gaps.

### Implementation for User Story 1

- [x] T001 [US1] Remove "THE BOARD", "THE GARAGE", and "BACKSTAGE" heading label draw calls in client/ui/board_renderer.py
- [x] T002 [US1] Rename backstage slot labels from "Slot 1/2/3" to "Backstage 1/2/3" in client/ui/board_renderer.py
- [x] T003 [US1] Shift all Y positions upward in `_SPACE_LAYOUT` and `_BACKSTAGE_LAYOUT` dicts to reclaim freed vertical space in client/ui/board_renderer.py

**Checkpoint**: Board renders without heading labels, backstage slots are self-describing, elements fill vertical space.

---

## Phase 4: User Story 2 - Rename Realtor and Real Estate Listings (Priority: P1)

**Goal**: Rename the permanent action space from "Real Estate Listings" / `real_estate_listings` to "Realtor" / `realtor` across config, server, and client. Update purchase dialog title to "Real Estate Listings".

**Independent Test**: Launch a game and verify the left-column action space reads "Realtor". Place a worker on it and verify the purchase dialog title reads "Real Estate Listings". Check game log entries reference "Realtor".

### Implementation for User Story 2

- [x] T004 [P] [US2] Rename space_id from "real_estate_listings" to "realtor", name from "Real Estate Listings" to "Realtor", and space_type from "real_estate_listings" to "realtor" in config/board.json
- [x] T005 [P] [US2] Rename all "real_estate_listings" string literals and comment references to "realtor" in server/game_engine.py
- [x] T006 [P] [US2] Rename "real_estate_listings" key to "realtor" in `_SPACE_LAYOUT` dict in client/ui/board_renderer.py
- [x] T007 [P] [US2] Rename "real_estate_listings" references to "realtor" in client/views/game_view.py
- [x] T008 [US2] Update purchase dialog title from "Purchase a Building" to "Real Estate Listings" in client/ui/dialogs.py

**Checkpoint**: All code, config, and display references use "realtor". Purchase dialog title reads "Real Estate Listings".

---

## Phase 5: User Story 3 - Convert Building Market to Popup Dialog (Priority: P1)

**Goal**: Remove inline building market from board surface. Add "Real Estate Listings" toggle button alongside My Quests/My Intrigue. Implement popup overlay panel showing face-up buildings with full details (name, genre, cost, VP, visitor reward, owner bonus, description) and deck count.

**Independent Test**: Launch a game and verify no building market text on the board. Click "Real Estate Listings" button to open popup with full building details. Click again to close. Open My Quests, then click Real Estate Listings to verify mutual exclusion.

**Depends on**: US2 (rename must be complete so display names are correct)

### Implementation for User Story 3

- [x] T009 [US3] Remove inline building market text rendering (face-up building names, cost, VP labels) from client/ui/board_renderer.py
- [x] T010 [US3] Add `_show_building_market` toggle boolean to GameView and implement mutual exclusion with `_show_quests_hand` and `_show_intrigue_hand` in client/views/game_view.py
- [x] T011 [US3] Add "Real Estate Listings" toggle button to bottom-left button row (alongside My Quests and My Intrigue) in client/views/game_view.py
- [x] T012 [US3] Implement `_draw_building_market_panel()` method in GameView that draws a popup overlay panel showing each face-up building's name, genre, coin cost, accumulated VP, visitor reward, owner bonus, description, and deck remaining count in client/views/game_view.py
- [x] T013 [US3] Wire building market panel drawing into the main `on_draw()` method, matching the existing hand panel draw pattern, in client/views/game_view.py

**Checkpoint**: Building market popup toggles correctly, shows full building details, mutually excludes other panels, updates when market state changes.

---

## Phase 6: User Story 4 - Batch Render Board Shapes for Performance (Priority: P2)

**Goal**: Replace individual `draw_rectangle_filled` and `draw_rectangle_outline` calls with a `ShapeElementList` that batches all static board shapes (space boxes, backstage slot boxes, background rectangles) into a single GPU draw call per frame.

**Independent Test**: Launch a game and verify the board looks visually identical. Confirm smooth 60fps rendering. Verify shape batch rebuilds when board state changes (e.g., worker placed, building constructed).

### Implementation for User Story 4

- [x] T014 [US4] Add `_shape_list: ShapeElementList` and `_shapes_dirty: bool` instance variables to BoardRenderer in client/ui/board_renderer.py
- [x] T015 [US4] Create `_rebuild_shapes()` method that clears the ShapeElementList, then builds all static rectangles (filled + outlined) for action spaces, backstage slots, and board background using `create_rectangle_filled` and `create_rectangle_outline` factory functions in client/ui/board_renderer.py
- [x] T016 [US4] Replace individual `arcade.draw_rectangle_filled` and `arcade.draw_rectangle_outline` calls in the draw path with a single `self._shape_list.draw()` call, calling `_rebuild_shapes()` only when `_shapes_dirty` is True, in client/ui/board_renderer.py
- [x] T017 [US4] Set `_shapes_dirty = True` in `update_board()` and on window resize so the shape batch rebuilds when board state or dimensions change, in client/ui/board_renderer.py

**Checkpoint**: Board renders identically using batched shapes. Shape list rebuilds on state change. 60fps maintained.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation across all user stories

- [x] T018 Run quickstart.md manual validation flow (all 11 test steps) to verify end-to-end correctness
- [x] T019 Verify Game Log section remains unchanged and unaffected by all modifications
- [x] T020 Verify edge cases: rapid toggle clicks show only last-clicked panel; popup updates on purchase; empty market shows informational message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped (no setup needed)
- **Foundational (Phase 2)**: Skipped (no blocking prerequisites)
- **US1 (Phase 3)**: Can start immediately - no dependencies on other stories
- **US2 (Phase 4)**: Can start immediately - no dependencies on other stories. Can run in parallel with US1
- **US3 (Phase 5)**: Depends on US2 completion (rename must be done before popup uses correct names)
- **US4 (Phase 6)**: Can start after US1 (layout changes must be finalized before batching shapes). Can run in parallel with US2/US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Independent - board_renderer.py label/layout changes only
- **US2 (P1)**: Independent - rename across config/server/client
- **US3 (P1)**: Depends on US2 - popup display names rely on rename being complete
- **US4 (P2)**: Depends on US1 - layout positions must be finalized before batching

### Within Each User Story

- Tasks within a story are ordered sequentially unless marked [P]
- [P] tasks touch different files and can run in parallel
- Complete each story before moving to the next priority

### Parallel Opportunities

- US1 (Phase 3) and US2 (Phase 4) can run in parallel (different primary concerns, minimal file overlap — only board_renderer.py `_SPACE_LAYOUT` key rename in US2 T006 should be coordinated)
- T004, T005, T006, T007 within US2 are all [P] — they touch different files
- US4 can start as soon as US1 layout changes are finalized (does not depend on US2/US3)

---

## Parallel Example: User Story 2

```bash
# Launch all rename tasks in parallel (each touches a different file):
Task: "T004 - Rename in config/board.json"
Task: "T005 - Rename in server/game_engine.py"
Task: "T006 - Rename in client/ui/board_renderer.py"
Task: "T007 - Rename in client/views/game_view.py"

# Then sequentially:
Task: "T008 - Update dialog title in client/ui/dialogs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete US1: Remove labels, shift layout, rename backstage slots
2. Complete US2: Rename real_estate_listings → realtor across all files
3. **STOP and VALIDATE**: Board looks cleaner, Realtor space works correctly
4. Deploy/demo if ready

### Incremental Delivery

1. US1 → Test independently → Clean board layout (MVP visual)
2. US2 → Test independently → Correct naming throughout
3. US3 → Test independently → Building market popup replaces inline display
4. US4 → Test independently → Performance optimization with batched rendering
5. Polish → Full validation → Ship

### Single Developer Strategy

Complete in priority order: US1 → US2 → US3 → US4 → Polish. Each story is a natural commit point.
