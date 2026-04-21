# Tasks: Tabbed Side Panel

**Input**: Design documents from `specs/014-tabbed-side-panel/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No test tasks — this is a client-side UI change with no server logic modifications.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the new TabbedPanel module with basic structure

- [X] T001 Create TabbedPanel class with tab definitions, active_tab state, tab bar shape list, tab text cache, and tab hit-rect dictionary in client/ui/tabbed_panel.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire TabbedPanel into GameView, replacing the old overlay system

- [X] T002 In client/views/game_view.py, replace `self.game_log_panel` with `self.tabbed_panel` (a `TabbedPanel` instance). Update `_build_ui()` to create `TabbedPanel`. Update all `self.game_log_panel.add_entry()` calls to go through the composed game log inside `TabbedPanel`.
- [X] T003 In client/views/game_view.py, remove the 4 dialog-toggle buttons ("My Quests", "My Intrigue", "Completed Quests", "Producer") from `_rebuild_buttons()`. Keep "Player Overview" button.
- [X] T004 In client/views/game_view.py, remove the toggle methods `_toggle_quests`, `_toggle_intrigue`, `_toggle_completed_quests`, `_toggle_producer` and their state flags `_show_quests_hand`, `_show_intrigue_hand`, `_show_completed_quests`, `_show_producer`.
- [X] T005 In client/views/game_view.py, remove the overlay draw methods `_draw_hand_panel`, `_draw_completed_quests_panel`, `_draw_producer_panel` and their calls in `on_draw()`. Keep `_draw_player_overview_panel`.
- [X] T006 In client/views/game_view.py, update `on_draw()` to call `self.tabbed_panel.draw()` in place of `self.game_log_panel.draw()`, passing the same position args (cw - log_w, bar_h, log_w, board_h, scale=s) plus player data dict.
- [X] T007 In client/views/game_view.py, add click handling for the tab bar: in `on_mouse_press`, call `self.tabbed_panel.on_click(x, y)` and return early if it returns True (tab was clicked).

**Checkpoint**: Panel shows with tab bar and game log content. Tabs are clickable but only game log view works. Old overlay buttons and draw methods are removed.

---

## Phase 3: User Story 1 — Tab Navigation Between Panel Views (Priority: P1)

**Goal**: All 5 tabs are clickable and switch panel content. Active tab is visually distinguished. Panel title updates.

**Independent Test**: Click each tab — title changes, content area changes, active tab highlight moves. Tabs work while dialogs are open.

### Implementation for User Story 1

- [X] T008 [US1] In client/ui/tabbed_panel.py, implement tab bar rendering: draw tab backgrounds using ShapeElementList (active tab brighter color, inactive tabs darker), draw tab labels using cached arcade.Text objects. Rebuild shapes on resize or tab change.
- [X] T009 [US1] In client/ui/tabbed_panel.py, implement `on_click(x, y) -> bool` method: hit-test against `_tab_rects`, set `active_tab` if hit, mark shapes dirty, return True/False.
- [X] T010 [US1] In client/ui/tabbed_panel.py, implement panel title rendering: draw the active tab's label as a title below the tab bar using a cached arcade.Text object.
- [X] T011 [US1] In client/ui/tabbed_panel.py, implement game log tab content: when `active_tab == "game_log"`, delegate to the composed `GameLogPanel.draw()` with adjusted y/h to account for tab bar height.
- [X] T012 [US1] In client/ui/game_log.py, make the title ("Game Log") optional or removable so TabbedPanel can draw its own title. Add a parameter to `draw()` such as `show_title=True` to allow suppressing the built-in title.
- [X] T013 [US1] In client/ui/tabbed_panel.py, implement stub content views for the remaining 4 tabs: draw placeholder text ("My Quests", "My Intrigue", etc.) centered in the content area. These will be replaced in US2/US3.
- [X] T014 [US1] In client/views/game_view.py, ensure `on_mouse_press` passes scroll events to `game_log_panel` (via `tabbed_panel`) when the game log tab is active, preserving scroll functionality.

**Checkpoint**: All 5 tabs are clickable, title updates, active tab is highlighted, game log works with scrolling. Tabs work while dialogs are open (no special handling needed — dialogs draw independently).

---

## Phase 4: User Story 2 — Card Display in Two-Column Layout (Priority: P2)

**Goal**: My Quests, My Intrigue, and Completed Quests tabs display card sprites in a 2-column grid.

**Independent Test**: Click a card tab — cards appear in 2 columns within the panel. Empty tabs show a message.

### Implementation for User Story 2

- [X] T015 [US2] In client/ui/tabbed_panel.py, implement card grid rendering method: given a list of card dicts and a card_type string, build a SpriteList with cards arranged in 2 columns. Compute card scale from panel width (panel_w / 2 - margins) / base_card_width. Stack rows vertically.
- [X] T016 [US2] In client/ui/tabbed_panel.py, implement "My Quests" tab content: when `active_tab == "my_quests"`, extract `contract_hand` from player data and render using the card grid method with card_type "quests".
- [X] T017 [P] [US2] In client/ui/tabbed_panel.py, implement "My Intrigue" tab content: when `active_tab == "my_intrigue"`, extract `intrigue_hand` from player data and render using the card grid method with card_type "intrigue".
- [X] T018 [P] [US2] In client/ui/tabbed_panel.py, implement "Completed Quests" tab content: when `active_tab == "completed_quests"`, extract `completed_contracts` from player data and render using the card grid method with card_type "quests".
- [X] T019 [US2] In client/ui/tabbed_panel.py, implement empty state rendering: when a card tab has zero cards, display a centered message (e.g., "No quests", "No intrigue cards", "No completed quests") using a cached arcade.Text object.

**Checkpoint**: All 3 card tabs display cards in 2-column grid. Empty tabs show message. Cards fit within panel width.

---

## Phase 5: User Story 3 — Producer Card Display in Panel (Priority: P3)

**Goal**: Producer tab shows the player's producer card image or a fallback message.

**Independent Test**: Click "Producer" tab — card image appears, or "No producer card" message if none assigned.

### Implementation for User Story 3

- [X] T020 [US3] In client/ui/tabbed_panel.py, implement "Producer" tab content: when `active_tab == "producer"`, extract `producer_card` from player data. If present, render the card sprite centered in the content area using card_type "producers". If absent, display "No producer card" message.

**Checkpoint**: Producer tab fully functional. All 5 tabs complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation

- [X] T021 Run black and ruff on all modified files: client/ui/tabbed_panel.py, client/ui/game_log.py, client/views/game_view.py
- [X] T022 Run pytest to verify no existing tests are broken
- [X] T023 Manual testing: run through all quickstart.md scenarios (tab switching, 2-column cards, producer, dialogs, resize, empty states)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 completion
- **US2 (Phase 4)**: Depends on Phase 3 (needs tab infrastructure from US1)
- **US3 (Phase 5)**: Depends on Phase 3 (needs tab infrastructure from US1). Can run in parallel with US2.
- **Polish (Phase 6)**: Depends on all user stories being complete

### Within Each User Story

- Tab bar rendering (T008) before click handling (T009)
- Title rendering (T010) and content stubs (T013) can run after T008
- Card grid rendering (T015) before individual card tabs (T016-T018)
- T017 and T018 can run in parallel (different tab views, same file but independent methods)

### Parallel Opportunities

- T017 and T018 can run in parallel (My Intrigue and Completed Quests tabs)
- US2 and US3 can run in parallel after US1 completes (different content renderers)

---

## Parallel Example: User Story 2

```bash
# After T015 (card grid method) and T016 (My Quests) are done:
Task T017: "Implement My Intrigue tab content"
Task T018: "Implement Completed Quests tab content"
# These can run in parallel — they add independent methods to the same file
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create TabbedPanel class (T001)
2. Complete Phase 2: Wire into GameView, remove old overlays (T002-T007)
3. Complete Phase 3: Tab switching with game log + stubs (T008-T014)
4. **STOP and VALIDATE**: All tabs clickable, game log works, old buttons gone
5. This is a usable MVP — game log works, other tabs show placeholders

### Incremental Delivery

1. Setup + Foundational → TabbedPanel wired in, old system removed
2. Add US1 → Tab switching works → Validate
3. Add US2 → Card views work → Validate
4. Add US3 → Producer view works → Validate
5. Polish → Lint, test, manual verification

---

## Notes

- No server-side changes required — purely client UI
- Constitution Principle I enforced: all rendering via arcade.Text, ShapeElementList, and sprites
- GameLogPanel is composed (not replaced) — its scroll and entry logic is preserved
- Dialogs are unaffected — they draw as overlays independently of tab state
- Player Overview remains as a separate button per spec assumptions
