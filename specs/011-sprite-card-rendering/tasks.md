# Tasks: Sprite Card Rendering

**Input**: Design documents from `/specs/011-sprite-card-rendering/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested. No test tasks generated.

**Organization**: Tasks grouped by user story. All changes are in client/ — no server or shared code changes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No project setup needed — all infrastructure exists. Skip to Phase 2.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create shared sprite helper logic used by all user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Add a helper function `_build_card_sprite_list(cards, card_type, positions)` in `client/ui/board_renderer.py` that: takes a list of card dicts, a card type string (`"quests"`, `"buildings"`, `"intrigue"`), and a list of (cx, cy) positions; creates an `arcade.SpriteList`; for each card, constructs the PNG path as `client/assets/card_images/{card_type}/{card_id}.png`, creates an `arcade.Sprite` from that path positioned at (cx, cy), and appends it to the list; logs a warning and skips if the PNG file does not exist; returns the `arcade.SpriteList`

**Checkpoint**: Helper function exists and can be called by any rendering context. Script runs without errors.

---

## Phase 3: User Story 1 - Board Quest Cards as Sprites (Priority: P1)

**Goal**: Replace face-up quest card rendering on the main board with sprites in a SpriteList

**Independent Test**: Launch game, observe board. Quest cards display as parchment PNG images with genre bands instead of colored rectangles with text overlays.

### Implementation for User Story 1

- [X] T002 [US1] Add `_quest_sprite_list: arcade.SpriteList | None = None` field to `BoardRenderer.__init__()` in `client/ui/board_renderer.py`
- [X] T003 [US1] In `BoardRenderer.draw()` in `client/ui/board_renderer.py`, replace the face-up quest card rendering loop (lines ~155-170 that call `CardRenderer.draw_contract()`) with: compute the same (cx, cy) positions for each quest card, call the helper to build `_quest_sprite_list` from `face_up_quests` with type `"quests"`, draw the sprite list via `_quest_sprite_list.draw()`, and preserve the `_space_rects` click-detection entries using the sprite positions
- [X] T004 [US1] In `BoardRenderer.draw()` in `client/ui/board_renderer.py`, add highlight rendering after the quest sprite list draw: for each highlighted quest card ID, find the matching sprite by position and draw `arcade.draw_rect_outline()` around it using `arcade.color.YELLOW` with `border_width=2`
- [X] T005 [US1] Visually verify board quest cards per quickstart.md scenarios 1, 3, and 5: cards appear as PNG sprites, highlights work, clicking works

**Checkpoint**: Board quest cards render as sprites. Building cards and hand panel still use old rendering.

---

## Phase 4: User Story 2 - Board Building Cards as Sprites (Priority: P2)

**Goal**: Replace face-up building card rendering on the main board with sprites in a SpriteList

**Independent Test**: Launch game, observe building cards on the board. They display as parchment PNG images instead of colored rectangles.

### Implementation for User Story 2

- [X] T006 [US2] Add `_building_sprite_list: arcade.SpriteList | None = None` field to `BoardRenderer.__init__()` in `client/ui/board_renderer.py`
- [X] T007 [US2] In `BoardRenderer.draw()` in `client/ui/board_renderer.py`, replace the face-up building card rendering loop (lines ~183-200 that call `CardRenderer.draw_building()`) with: compute the same (cx, cy) positions for each building card, call the helper to build `_building_sprite_list` from `_face_up_buildings` with type `"buildings"`, draw the sprite list via `_building_sprite_list.draw()`, and preserve the `_space_rects` click-detection entries
- [X] T008 [US2] In `BoardRenderer.draw()` in `client/ui/board_renderer.py`, add highlight rendering for building cards: for each highlighted building card ID, draw `arcade.draw_rect_outline()` around the sprite using `arcade.color.YELLOW` with `border_width=2`
- [X] T009 [US2] Visually verify board building cards per quickstart.md scenarios 2 and 4

**Checkpoint**: Both board quest and building cards render as sprites.

---

## Phase 5: User Story 3 - Hand Panel Cards as Sprites (Priority: P3)

**Goal**: Replace quest and intrigue card rendering in the hand panel overlay with sprites

**Independent Test**: Open quest hand panel and intrigue hand panel. Cards display as PNG sprites.

### Implementation for User Story 3

- [X] T010 [US3] Add `_hand_sprite_list: arcade.SpriteList | None = None` field to `GameView.__init__()` in `client/views/game_view.py`
- [X] T011 [US3] In `GameView._draw_hand_panel()` in `client/views/game_view.py`, replace the card rendering loop (lines ~1530-1537 that call `draw_fn()`) with: determine card type (`"quests"` for quest hand, `"intrigue"` for intrigue hand), compute the same (cx, cy) positions for each card, build `_hand_sprite_list` using the helper function (import from board_renderer or duplicate the helper into game_view), draw the sprite list via `_hand_sprite_list.draw()`
- [X] T012 [US3] Visually verify hand panel cards per quickstart.md scenarios 6, 7, and 10

**Checkpoint**: Board cards and hand panel cards all render as sprites.

---

## Phase 6: User Story 4 - Quest Completion Dialog Cards as Sprites (Priority: P4)

**Goal**: Replace quest card rendering in QuestCompletionDialog with sprites

**Independent Test**: Trigger quest completion dialog. Quest cards display as PNG sprites.

### Implementation for User Story 4

- [X] T013 [US4] Add `_quest_sprite_list: arcade.SpriteList | None = None` field to `QuestCompletionDialog.__init__()` in `client/ui/dialogs.py`
- [X] T014 [US4] In `QuestCompletionDialog.draw()` in `client/ui/dialogs.py`, replace the card rendering loop (lines ~267-273 that call `CardRenderer.draw_contract()`) with: compute the same (cx, cy) positions for each quest card, build `_quest_sprite_list` from `self.quests` with type `"quests"`, draw the sprite list via `_quest_sprite_list.draw()`
- [X] T015 [US4] Visually verify quest completion dialog per quickstart.md scenario 8

**Checkpoint**: All 5 call sites now use sprite-based rendering.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Remove dead code, clean up imports, final validation

- [X] T016 Remove `CardRenderer` import from `client/ui/board_renderer.py` and verify no remaining references
- [X] T017 Remove `CardRenderer` import from `client/views/game_view.py` and verify no remaining references
- [X] T018 Remove `CardRenderer` import from `client/ui/dialogs.py` and verify no remaining references
- [X] T019 Delete `client/ui/card_renderer.py` entirely per quickstart.md scenario 11
- [X] T020 Run `ruff check client/` and fix any lint issues
- [X] T021 Verify card data change handling per quickstart.md scenario 9: during gameplay, when face-up cards change, the board updates to show the new card's sprite
- [X] T022 Full visual verification: launch game, test all quickstart.md scenarios 1-11

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A — no setup needed
- **Foundational (Phase 2)**: No dependencies — helper function creation
- **US1 (Phase 3)**: Depends on Phase 2 — board quest card sprites
- **US2 (Phase 4)**: Depends on Phase 2 — board building card sprites
- **US3 (Phase 5)**: Depends on Phase 2 — hand panel card sprites
- **US4 (Phase 6)**: Depends on Phase 2 — dialog card sprites
- **Polish (Phase 7)**: Depends on ALL user stories (US1-US4) — removes CardRenderer only after all call sites converted

### User Story Dependencies

- **US1 (P1)**: Independent after Phase 2
- **US2 (P2)**: Independent after Phase 2, can run in parallel with US1
- **US3 (P3)**: Independent after Phase 2, can run in parallel with US1/US2
- **US4 (P4)**: Independent after Phase 2, can run in parallel with US1/US2/US3

### Parallel Opportunities

- T002 and T006 can run in parallel (same file but different fields in __init__)
- US1-US4 implementation tasks can all run in parallel after Phase 2 (each modifies a different draw method)
- T016, T017, T018 can run in parallel (different files, import removal)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Helper function
2. Complete Phase 3: Board quest cards as sprites
3. **STOP and VALIDATE**: Check board quest card PNGs display correctly

### Incremental Delivery

1. Foundational → Helper function ready
2. Add US1 → Board quest cards as sprites → Validate
3. Add US2 → Board building cards as sprites → Validate
4. Add US3 → Hand panel cards as sprites → Validate
5. Add US4 → Dialog cards as sprites → Validate
6. Polish → Remove CardRenderer, lint, full verification

---

## Notes

- All 4 user stories modify rendering code in different methods/classes — no cross-story conflicts
- The helper function in Phase 2 is shared across all contexts — it can live in board_renderer.py and be imported, or be duplicated as a standalone utility
- Card images are 190x230 pixels at 1:1 scale — no scaling needed when creating sprites
- Arcade's texture cache deduplicates PNG loads, so the same card image used in multiple contexts shares one GPU texture
- The `_space_rects` click detection in board_renderer.py must be preserved using sprite positions
