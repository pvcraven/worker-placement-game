# Tasks: Final Score Screen

**Input**: Design documents from `specs/015-final-score-screen/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No explicit test tasks requested. Server VP calculation test included as part of foundational phase (Constitution Principle IV requires tests for game logic).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new files or dependencies needed. This feature modifies existing files only.

(No setup tasks — existing project structure is sufficient.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update shared message models and server-side VP calculation that both user stories depend on.

- [X] T001 In shared/messages.py, update FinalPlayerScore model: rename `base_vp` to `game_vp`, rename `producer_bonus` to `genre_bonus_vp`, add `resource_vp: int` field. Update total_vp comment to reflect new formula: game_vp + genre_bonus_vp + resource_vp.
- [X] T002 In server/game_engine.py, update `_end_game()` function: calculate `resource_vp` for each player as `guitarists + bass_players + drummers + singers + floor(coins / 2)`. Update the FinalPlayerScore construction to use new field names (`game_vp`, `genre_bonus_vp`, `resource_vp`). Update `total_vp` calculation to include `resource_vp`.
- [X] T003 In tests/test_game_engine.py, add test for resource VP calculation: verify that resource_vp equals musician count + floor(coins/2), verify total_vp = game_vp + genre_bonus_vp + resource_vp, verify edge case with 0 resources and odd coin count.
- [X] T004 In client/views/results_view.py, update references from `base_vp` to `game_vp` and from `producer_bonus` to `genre_bonus_vp` to match renamed FinalPlayerScore fields (keeps existing results view working until fully replaced).

**Checkpoint**: Server correctly calculates resource_vp, all field renames are consistent across shared/server/client, existing tests pass.

---

## Phase 3: User Story 1 — View Final Score Breakdown (Priority: P1)

**Goal**: Player can click "Final Screen" button to toggle a dialog overlay showing VP breakdown for all players with winner highlighted.

**Independent Test**: Click "Final Screen" button during gameplay. Dialog appears with player columns showing producer card, name, game VP, genre bonus (own player only — opponents show "?"), resource VP, and total VP. Highest-scoring player shows "WINNER". Click again or click "Close" to dismiss.

### Implementation for User Story 1

- [X] T005 [US1] In client/views/game_view.py, add state flags `_show_final_screen: bool = False` and `_game_over_final: bool = False` to `__init__`. Add `_final_scores: list | None = None` to store server-provided scores.
- [X] T006 [US1] In client/views/game_view.py `_rebuild_buttons()`, add a "Final Screen" button to the right of the existing "Player Overview" button. Wire it to a new `_toggle_final_screen()` method.
- [X] T007 [US1] In client/views/game_view.py, implement `_toggle_final_screen()`: if `_game_over_final` is True, return (ignore toggle). Otherwise flip `_show_final_screen`.
- [X] T008 [US1] In client/views/game_view.py, implement `_calculate_scores_from_state() -> list[dict]` method: iterate all players in `self.game_state["players"]`, compute game_vp (sum of completed_contracts victory_points), genre_bonus_vp (match completed contract genres against producer_card bonus_genres, multiply by bonus_vp_per_contract — use 0 for opponents whose producer_card is None), resource_vp (musicians + floor(coins/2)), and total_vp. Return list of score dicts sorted by total_vp descending.
- [X] T009 [US1] In client/views/game_view.py, implement `_draw_final_screen(cw, ch, s)` method following Player Overview dialog pattern: draw semi-transparent dark background overlay, centered white-bordered panel, "Close" button at bottom center. Use arcade.Text (cached via _text helper) and ShapeElementList for all rendering per Constitution Principle I.
- [X] T010 [US1] In client/views/game_view.py `_draw_final_screen`, render player columns horizontally: for each player score, draw producer card sprite (or "No Producer" placeholder text), player name below card, then rows for "Game VP: X", "Genre Bonus: X" (or "Genre Bonus: ?" for opponents during gameplay), "Resource VP: X", and "Total: X" (bold). Use arcade.Text objects for all text.
- [X] T011 [US1] In client/views/game_view.py `_draw_final_screen`, render "WINNER" text above the producer card for the player(s) with the highest total_vp. Handle ties (all tied players get "WINNER").
- [X] T012 [US1] In client/views/game_view.py `on_draw()`, after the Player Overview draw call, add: if `_show_final_screen`, call `_draw_final_screen(cw, ch, s)`.
- [X] T013 [US1] In client/views/game_view.py `on_mouse_press`, add hit-test for the "Close" button inside the final screen dialog. If `_game_over_final` is False, set `_show_final_screen = False`. (Game-over close behavior handled in US2.)

**Checkpoint**: "Final Screen" button visible and toggles dialog. Dialog shows all players with VP breakdown. Winner highlighted. Close button dismisses dialog. Game continues normally after closing.

---

## Phase 4: User Story 2 — Game-Over Final Screen (Priority: P2)

**Goal**: When the game ends, the final score dialog appears automatically with authoritative server-calculated scores. Close navigates to lobby.

**Independent Test**: Complete a game (or simulate game-over). Final score dialog appears automatically with full VP breakdown for all players (including opponent genre bonuses). Click "Close" to navigate to lobby.

### Implementation for User Story 2

- [X] T014 [US2] In client/views/game_view.py, update the `game_over` message handler (currently calls `window.show_results()`): instead, store `msg["final_scores"]` in `self._final_scores`, set `_show_final_screen = True` and `_game_over_final = True`. Do NOT call `window.show_results()`.
- [X] T015 [US2] In client/views/game_view.py `_draw_final_screen`, when `_final_scores` is not None (game-over mode), use the server-provided scores instead of client-calculated ones. This ensures all players see authoritative VP with full genre bonus revealed.
- [X] T016 [US2] In client/views/game_view.py `on_mouse_press` Close button handler, if `_game_over_final` is True: call `self.window.network.disconnect()` then `self.window.show_lobby()`.
- [X] T017 [US2] In client/views/game_view.py `_toggle_final_screen`, verify that the toggle button is ignored when `_game_over_final` is True (already implemented in T007, verify it works in game-over context).

**Checkpoint**: Game-over triggers dialog automatically. All scores shown with full breakdown. Toggle button disabled. Close navigates to lobby.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation

- [X] T018 Run black and ruff on all modified files: shared/messages.py, server/game_engine.py, client/views/game_view.py, client/views/results_view.py
- [X] T019 Run pytest to verify no existing tests are broken and new resource_vp test passes
- [X] T020 Manual testing: run through all quickstart.md scenarios (manual toggle, game-over, edge cases, visual consistency, button placement)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — start immediately
- **US1 (Phase 3)**: Depends on Phase 2 completion (needs renamed FinalPlayerScore fields)
- **US2 (Phase 4)**: Depends on Phase 3 completion (needs the dialog rendering from US1)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Within Each Phase

- T001 before T002 (model changes before server uses them)
- T002 before T003 (implementation before tests)
- T003 and T004 can run in parallel (different files)
- T005-T007 before T008-T013 (state/buttons before dialog rendering)
- T008 before T009-T011 (score calculation before display)
- T009 before T010-T011 (dialog frame before content)
- T012-T013 after T009-T011 (wiring after rendering)
- T014 before T015-T017 (game-over handler before dialog integration)

### Parallel Opportunities

- T003 and T004 can run in parallel (test file vs results_view file)
- T010 and T011 can run in parallel within T009's dialog frame (content rows vs winner label — same method but independent sections)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Update FinalPlayerScore model and server calculation (T001-T004)
2. Complete Phase 3: Final Screen dialog with manual toggle (T005-T013)
3. **STOP and VALIDATE**: Button toggles dialog, VP breakdown displays, winner highlighted
4. This is a usable MVP — players can check scores mid-game

### Incremental Delivery

1. Foundational → Model + server VP changes → Validate
2. Add US1 → Manual toggle dialog → Validate
3. Add US2 → Game-over auto-display + lobby navigation → Validate
4. Polish → Lint, test, manual verification

---

## Notes

- Constitution Principle I enforced: all rendering via arcade.Text, ShapeElementList, and sprites — no primitive draw calls
- Constitution Principle IV enforced: server-side resource_vp calculation has test coverage
- Existing results_view.py is updated for field renames (T004) but will be functionally replaced by the in-game dialog
- During manual toggle, opponent genre bonus shows "?" because producer cards are hidden until game-over
- The "Final Screen" button serves as both a testing aid and a permanent mid-game score checker
