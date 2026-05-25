# Tasks: Backstage Closed Cards

**Input**: Design documents from `/specs/037-backstage-closed-cards/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks are grouped by user story. US1 and US2 are both P1 but US2 depends on US1 infrastructure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Card Image Generation)

**Purpose**: Generate the closed variant backstage card images

- [X] T001 Generate closed variant backstage card images (`backstage_slot_N_closed.png`) in `card-generator/generate_cards.py` — add a loop after the existing backstage card generation (~line 1857) that creates cards with "CLOSED" in dark red text `(180, 40, 40)` and a dark red rectangular box border around the text, saving to `client/assets/card_images/spaces/backstage_slot_{1,2,3}_closed.png`
- [X] T002 Run `python card-generator/generate_cards.py` to generate the new PNG files and verify they exist in `client/assets/card_images/spaces/`

---

## Phase 2: Foundational (Board Renderer Sprite Lists)

**Purpose**: Build the closed backstage sprite list and add the swap mechanism

**⚠️ CRITICAL**: Must complete before game view integration

- [X] T003 In `client/ui/board_renderer.py` `_build_board_layout()`, after building `self._backstage_sprite_list` (~line 499), build a second sprite list `self._backstage_closed_sprite_list` using card IDs `backstage_slot_1_closed`, `backstage_slot_2_closed`, `backstage_slot_3_closed` at the same positions and scale. Initialize `self._backstage_closed = False`.
- [X] T004 In `client/ui/board_renderer.py`, add method `swap_backstage_cards(self, closed: bool)` that sets `self._backstage_closed = closed`.
- [X] T005 In `client/ui/board_renderer.py` `draw()` method (~line 230), change the `self._backstage_sprite_list.draw()` call to draw `self._backstage_closed_sprite_list` when `self._backstage_closed` is `True`, otherwise draw `self._backstage_sprite_list`.

**Checkpoint**: Board renderer can now swap between normal and closed backstage cards when `swap_backstage_cards()` is called

---

## Phase 3: User Story 1 - Show Closed During Reassignment (Priority: P1) 🎯 MVP

**Goal**: Backstage slots display "CLOSED" during the reassignment phase

**Independent Test**: Start a game, complete placement phase, enter reassignment — verify backstage cards show "CLOSED" with dark red boxed text

### Implementation for User Story 1

- [X] T006 [US1] In `client/views/game_view.py` `_on_reassignment_phase_start()` (~line 2711), add call to `self.board_renderer.swap_backstage_cards(closed=True)` after setting `self.game_state["phase"] = "reassignment"`

**Checkpoint**: Backstage cards now show "CLOSED" when reassignment phase starts

---

## Phase 4: User Story 2 - Revert After Reassignment (Priority: P1)

**Goal**: Backstage slots revert to "Play Intrigue" when the next round begins

**Independent Test**: Complete reassignment phase, advance to next round — verify backstage cards return to showing "Play Intrigue"

### Implementation for User Story 2

- [X] T007 [US2] In `client/views/game_view.py` `_on_round_end()` (~line 2951), add call to `self.board_renderer.swap_backstage_cards(closed=False)` after setting `self.game_state["phase"] = "placement"`

**Checkpoint**: Backstage cards now revert to normal "Play Intrigue" when a new round starts

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Handle reconnect edge case and verify end-to-end

- [X] T008 In `client/views/game_view.py`, find the state sync / reconnect handler (where `game_state` is replaced on reconnect). After the state is applied, check `self.game_state.get("phase") == "reassignment"` and call `self.board_renderer.swap_backstage_cards(closed=...)` accordingly.
- [X] T009 Run quickstart.md validation — start a game, play through placement and reassignment phases, verify cards swap correctly in both directions. Test reconnect during reassignment.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — generates card images
- **Foundational (Phase 2)**: Depends on Phase 1 (needs closed PNG files to exist)
- **User Story 1 (Phase 3)**: Depends on Phase 2 (needs swap method in board renderer)
- **User Story 2 (Phase 4)**: Depends on Phase 2 (needs swap method in board renderer). Independent of US1.
- **Polish (Phase 5)**: Depends on Phases 3 and 4

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) — independent of US1

### Within Each Phase

- T001 → T002 (generate then verify)
- T003 → T004 → T005 (build list, add swap method, wire drawing)
- T006 independent of T007
- T008 → T009 (reconnect fix, then end-to-end validation)

### Parallel Opportunities

- T006 and T007 can run in parallel (different methods in game_view.py, no cross-dependency)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Generate closed card images
2. Complete Phase 2: Board renderer sprite list + swap
3. Complete Phase 3: Wire up reassignment phase start
4. **STOP and VALIDATE**: Enter reassignment — backstage cards should show "CLOSED"

### Full Delivery

1. Complete MVP (Phases 1–3)
2. Add User Story 2 (Phase 4) — revert on round end
3. Polish (Phase 5) — reconnect handling + end-to-end test

---

## Notes

- No server changes needed — purely client-side
- Total: 9 tasks across 5 phases
- 3 files modified: `generate_cards.py`, `board_renderer.py`, `game_view.py`
- No new dependencies or models
