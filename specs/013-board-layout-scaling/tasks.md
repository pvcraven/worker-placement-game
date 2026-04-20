# Tasks: Board Layout Scaling

**Input**: Design documents from `/specs/013-board-layout-scaling/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No test tasks generated — not requested in specification. This is a visual/rendering feature best validated by manual resize testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project setup needed. All files exist. This phase establishes the core scaling infrastructure that all user stories depend on.

- [x] T001 Add `content_width` and `content_height` properties to `GameWindow` class in `client/game_window.py` — computed as `DESIGN_WIDTH * ui_scale` and `DESIGN_HEIGHT * ui_scale` respectively

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core scaling plumbing that MUST be complete before any user story can be implemented. This wires the scale factor through the layout orchestration in `game_view.py`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Update `on_draw()` in `client/views/game_view.py` to compute a content rect using `self.window.content_width` and `self.window.content_height` instead of raw `self.window.width`/`self.window.height` for all panel layout (board area, resource bar, game log, status bar). Scale panel dimensions: resource bar height `int(100 * ui_scale)`, status bar height `int(50 * ui_scale)`, game log width `int(450 * ui_scale)`. Board area fills remaining content rect. All content anchors to bottom-left (Arcade y=0 at bottom).
- [x] T003 Update `BoardRenderer.draw()` and `BoardRenderer._rebuild_shapes()` in `client/ui/board_renderer.py` to accept a `scale: float` parameter. Store it as `self._card_scale`. Clamp to [0.3, 2.0]. Compute scaled card dimensions: `card_w = _CARD_WIDTH * scale`, `card_h = _CARD_HEIGHT * scale`, `bld_h = _BUILDING_CARD_HEIGHT * scale`, `space_h = _SPACE_CARD_HEIGHT * scale`. Use scaled dimensions for all position calculations and hit-detection rects (`_space_rects`).
- [x] T004 Apply `sprite.scale = scale` to all sprites created in `_build_card_sprite_list()` in `client/ui/board_renderer.py` — this scales space sprites, quest sprites, building sprites, backstage sprites, realtor sprite, and constructed building sprites.

**Checkpoint**: Foundation ready — scaling infrastructure is in place, `game_view.py` passes `ui_scale` to the board renderer, all sprites scale with window.

---

## Phase 3: User Story 1 — Cards Scale With Window (Priority: P1) 🎯 MVP

**Goal**: All card images on the board scale proportionally when the window is resized.

**Independent Test**: Resize the window from default to double size. All cards (permanent spaces, quests, buildings, backstage, realtor) should grow proportionally. Shrink to half — cards shrink with no overlap or clipping.

### Implementation for User Story 1

- [x] T005 [US1] Scale permanent action space positions and hit rects in `_rebuild_shapes()` in `client/ui/board_renderer.py` — use scaled card dimensions for `_space_rects` entries and sprite positions
- [x] T006 [US1] Scale face-up quest card layout in `draw()` in `client/ui/board_renderer.py` — use scaled `card_w`, `card_h`, and scaled spacing (`(_CARD_WIDTH + 15) * scale`) for quest row positioning and highlight outlines
- [x] T007 [US1] Scale backstage slot positions and hit rects in `_rebuild_shapes()` in `client/ui/board_renderer.py` — use scaled card dimensions for backstage sprite positions and `_space_rects`
- [x] T008 [US1] Scale face-up building card layout in `draw()` in `client/ui/board_renderer.py` — use scaled `card_w`, `bld_h`, and scaled spacing for building market row positioning and highlight outlines
- [x] T009 [US1] Scale realtor space position and hit rect in `_rebuild_shapes()` in `client/ui/board_renderer.py` — use scaled card dimensions
- [x] T010 [US1] Scale worker token circles in `draw()` in `client/ui/board_renderer.py` — scale radius to `max(5, int(9 * scale))` and scale position offsets (e.g., `_CARD_WIDTH/2 - 10` becomes `card_w/2 - 10*scale`)
- [x] T011 [US1] Pass `scale=self.window.ui_scale` from `on_draw()` in `client/views/game_view.py` when calling `self.board_renderer.draw()`

**Checkpoint**: All cards on the board scale with the window. The game is visually correct at all tested sizes.

---

## Phase 4: User Story 5 — All Text Scales With Window (Priority: P1)

**Goal**: All text elements across the UI scale proportionally with the window, matching card scaling.

**Independent Test**: Resize window from default to double. All text (board labels, game log, resource bar, status bar) grows proportionally. Shrink — text shrinks but stays legible (min 8pt).

### Implementation for User Story 5

- [x] T012 [P] [US5] Scale building VP text font size in `draw()` in `client/ui/board_renderer.py` — use `font_size=max(8, int(12 * scale))` for VP labels on face-up buildings
- [x] T013 [P] [US5] Scale building owner text font size in `draw()` in `client/ui/board_renderer.py` — use `font_size=max(8, int(12 * scale))` for owner labels on constructed buildings
- [x] T014 [P] [US5] Scale game log text in `draw()` in `client/ui/game_log.py` — accept `scale: float = 1.0` parameter, scale title font to `max(8, int(16 * scale))`, entry font to `max(8, int(12 * scale))`, line height to `max(14, int(22 * scale))`
- [x] T015 [P] [US5] Scale resource bar text in `draw()` in `client/ui/resource_bar.py` — accept `scale: float = 1.0` parameter, scale font sizes to `max(8, int(16 * scale))`, scale swatch dimensions to `int(20 * scale)`, scale position offsets
- [x] T016 [US5] Scale status bar text in `on_draw()` in `client/views/game_view.py` — use `font_size=max(8, int(16 * self.window.ui_scale))` for the status text
- [x] T017 [US5] Pass `scale=self.window.ui_scale` to `game_log_panel.draw()` and `resource_bar.draw()` calls in `on_draw()` in `client/views/game_view.py`

**Checkpoint**: All text across the entire UI scales proportionally with the window.

---

## Phase 5: User Story 2 — Two-Column Building Layout (Priority: P2)

**Goal**: Constructed buildings display in two columns. Permanent action spaces shift left with reduced margins.

**Independent Test**: Start a game, purchase several buildings. Verify they appear in two columns to the right of permanent spaces. Permanent spaces remain fully visible.

### Implementation for User Story 2

- [x] T018 [US2] Reduce permanent space left margin in `_SPACE_LAYOUT` in `client/ui/board_renderer.py` — change x-coordinate from `0.08` to `0.05` for the six left-column spaces (merch_store through castle_waterdeep)
- [x] T019 [US2] Change constructed building grid formula in `_rebuild_shapes()` and `draw()` in `client/ui/board_renderer.py` — change from `row = i % 5, col = i // 5` to `col = i % 2, row = i // 2`. Adjust `building_start_x` and column spacing to position two columns between permanent spaces and the quest/backstage area.

**Checkpoint**: Buildings appear in two columns. Permanent spaces are visible with reduced margins.

---

## Phase 6: User Story 3 — Building VP and Owner Text Positioning (Priority: P2)

**Goal**: VP and Owner text labels stay anchored below their building card at all window sizes.

**Independent Test**: Construct a building, resize the window. VP and Owner text remains correctly positioned below the building card.

### Implementation for User Story 3

- [x] T020 [US3] Fix VP text positioning on face-up buildings in `draw()` in `client/ui/board_renderer.py` — compute VP text position using scaled card dimensions (`card_w`, `bld_h`) relative to the building sprite's current position, not hardcoded pixel offsets
- [x] T021 [US3] Fix Owner text positioning on constructed buildings in `draw()` in `client/ui/board_renderer.py` — recompute owner text positions every frame using current building sprite positions and scaled dimensions. Force `_building_owner_dirty = True` when draw rect changes (window resize).

**Checkpoint**: VP and Owner text stays correctly anchored below buildings at all window sizes.

---

## Phase 7: User Story 4 — Game Log Panel Scales With Window (Priority: P3)

**Goal**: Game log panel scales its dimensions proportionally with the window.

**Independent Test**: Resize the window. Game log panel grows/shrinks proportionally, text remains readable.

### Implementation for User Story 4

- [x] T022 [US4] Scale game log panel dimensions in `on_draw()` in `client/views/game_view.py` — log width `int(450 * ui_scale)`, log height fills content area between resource bar and status bar. Already partially done in T002; verify and adjust as needed.
- [x] T023 [US4] Scale game log visible line count in `draw()` in `client/ui/game_log.py` — recalculate `max_lines` using scaled line height and available panel height. Scale text truncation length proportionally.

**Checkpoint**: Game log panel maintains proportional sizing at all window sizes.

---

## Phase 8: User Story 6 — Dialog Boxes Scale With Window (Priority: P2)

**Goal**: All modal dialogs scale dimensions, card images, buttons, and text proportionally with the window.

**Independent Test**: Open a card selection dialog at default size, close, resize larger, reopen. Dialog, cards, buttons, and text should be proportionally larger.

### Implementation for User Story 6

- [x] T024 [P] [US6] Scale `CardSpriteSelectionDialog` in `client/ui/dialogs.py` — accept `scale: float = 1.0` in `draw()`, scale `_CARD_SPACING` by scale, scale panel dimensions, set `sprite.scale = scale` on card sprites, scale font sizes and button dimensions
- [x] T025 [P] [US6] Scale `QuestCompletionDialog` in `client/ui/dialogs.py` — pass scale through to inner `CardSpriteSelectionDialog.draw()` call
- [x] T026 [P] [US6] Scale UIManager-based dialogs in `client/ui/dialogs.py` — for `CardSelectionDialog`, `BuildingPurchaseDialog`, `PlayerTargetDialog`, `RewardChoiceDialog`, `ResourceChoiceDialog`, and `ConfirmDialog`: accept `scale: float = 1.0` in `show()`, multiply button `width`/`height`, `font_size`, `space_between`, and `padding` by scale
- [x] T027 [US6] Pass `scale=self.window.ui_scale` when calling dialog `show()` and `draw()` methods in `client/views/game_view.py`

**Checkpoint**: All dialogs scale proportionally with the window.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final adjustments affecting multiple user stories

- [x] T028 Scale hand panel overlay dimensions and card spacing in `_draw_hand_panel()` in `client/views/game_view.py` — use `ui_scale` for panel dimensions, card spacing, and font sizes
- [x] T029 Scale player overview panel dimensions and text in `_draw_player_overview_panel()` in `client/views/game_view.py` — use `ui_scale` for panel dimensions, column widths, and font sizes
- [x] T030 Scale button row positioning in `_build_ui()` in `client/views/game_view.py` — scale button dimensions and `align_y` offset by `ui_scale`
- [x] T031 Scale cancel button sprite and position in `on_show_view()` in `client/views/game_view.py` — set `self._cancel_sprite.scale = ui_scale * 0.5` and adjust position
- [x] T032 Manual visual testing — run the game at multiple window sizes (1024×768, 1920×1080, 3840×2160, ultra-wide 2560×1080, tall 1080×1920) and verify: cards scale, text scales, two-column buildings, VP/Owner text positioned correctly, game log proportional, dialogs scale, aspect ratio maintained with top-left anchoring
- [x] T033 Run `cd src && pytest && ruff check .` to verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — T001 adds content rect properties
- **Foundational (Phase 2)**: Depends on Phase 1 — T002-T004 wire scaling through the layout
- **US1 Cards Scale (Phase 3)**: Depends on Phase 2 — applies scaling to all board card positions
- **US5 Text Scales (Phase 4)**: Depends on Phase 2 — can run in parallel with US1
- **US2 Two-Column Buildings (Phase 5)**: Depends on Phase 3 (needs scaled card dimensions)
- **US3 VP/Owner Text Fix (Phase 6)**: Depends on Phase 5 (needs two-column positions)
- **US4 Game Log Scales (Phase 7)**: Depends on Phase 2 — can run in parallel with US1/US5
- **US6 Dialog Scaling (Phase 8)**: Depends on Phase 2 — can run in parallel with other stories
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational only — no dependencies on other stories
- **US5 (P1)**: Depends on Foundational only — independent of US1
- **US2 (P2)**: Depends on US1 (needs scaled card dimensions in place)
- **US3 (P2)**: Depends on US2 (needs two-column layout positions)
- **US4 (P3)**: Depends on Foundational only — independent of other stories
- **US6 (P2)**: Depends on Foundational only — independent of other stories

### Parallel Opportunities

After Foundational phase completes, these can run in parallel:
- US1 (Cards Scale) ‖ US5 (Text Scales) ‖ US4 (Game Log) ‖ US6 (Dialogs)

Then sequentially:
- US2 (Two-Column Buildings) → US3 (VP/Owner Text Fix)

---

## Parallel Example: After Foundational Phase

```text
# These four stories can start simultaneously:
US1: T005-T011 (card scaling in board_renderer.py + game_view.py)
US5: T012-T017 (text scaling across game_log.py, resource_bar.py, board_renderer.py, game_view.py)
US4: T022-T023 (game log panel scaling in game_view.py + game_log.py)
US6: T024-T027 (dialog scaling in dialogs.py + game_view.py)

# Note: US1 and US5 both touch board_renderer.py and game_view.py,
# so if working in parallel, coordinate on those files.
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 5 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T004)
3. Complete Phase 3: US1 — Cards Scale (T005-T011)
4. Complete Phase 4: US5 — Text Scales (T012-T017)
5. **STOP and VALIDATE**: Resize window at multiple sizes — cards and text should scale proportionally
6. This MVP delivers the core scaling experience

### Incremental Delivery

1. Setup + Foundational → Scaling infrastructure ready
2. US1 + US5 → Cards and text scale (MVP!)
3. US2 + US3 → Two-column buildings with fixed labels
4. US4 → Game log scales
5. US6 → Dialogs scale
6. Polish → Hand panels, player overview, buttons scale

---

## Notes

- This is a client-only feature — no server changes needed
- All 33 tasks modify 6 existing files — no new files created
- Constitution compliance: all new text uses `arcade.Text`, no new primitive draw calls
- Scale factor is `ui_scale = min(window_w/1920, window_h/1080)`, clamped [0.3, 2.0]
- Minimum font size is 8pt at all scales
- Aspect ratio preserved: content anchors to bottom-left (top-left visually), extra space unused
