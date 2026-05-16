# Tasks: Colored Marker Selection

**Input**: Design documents from `/specs/033-colored-marker-selection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/messages.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed — this feature extends existing files. Skip to Phase 2.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared model, constant, and message type changes required by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Add `MARKER_SELECTION = "marker_selection"` to GamePhase enum and add `MARKER_COLORS` list constant in shared/constants.py
- [X] T002 Add `marker_color: str | None = None` field to Player model in server/models/game.py
- [X] T003 Add SelectMarkerRequest to client messages and MarkerSelectionStartResponse + MarkerSelectedResponse to server messages in shared/messages.py (include in ClientMessage/ServerMessage unions)
- [X] T004 Add `_handle_select_marker` method in server/network.py to route to `lobby.select_marker()`

**Checkpoint**: Foundation ready — shared types exist for all stories to use

---

## Phase 3: User Story 1 — Player Selects a Marker Color (Priority: P1) 🎯 MVP

**Goal**: Each player sees a dialog with seven colored markers, clicks to select one, their name appears under it, and the color becomes unavailable to others.

**Independent Test**: Start a game with 2+ players. Verify the marker selection dialog appears, each player can click a marker, their name appears under it, and selected markers become unavailable.

### Implementation for User Story 1

- [X] T005 [US1] Modify `start_game()` in server/lobby.py: after `_initialize_game()`, set `state.phase = GamePhase.MARKER_SELECTION` and broadcast `MarkerSelectionStartResponse` with all 7 colors and player list (instead of immediately sending `GameStartedResponse`)
- [X] T006 [US1] Implement `select_marker()` async handler in server/lobby.py: validate phase is MARKER_SELECTION, player hasn't already selected, color is unclaimed; set `player.marker_color`, broadcast `MarkerSelectedResponse` with player_id, player_name, color, and `all_selected` flag
- [X] T007 [US1] Create `MarkerSelectionDialog` class in client/ui/marker_selection_dialog.py: display 7 colored circles/markers using ShapeElementList, show player names under claimed markers using arcade.Text, handle click events to send SelectMarkerRequest, update display when MarkerSelectedResponse received
- [X] T008 [US1] Handle `marker_selection_start` message in client/views/game_view.py: store game state from the message, instantiate and show MarkerSelectionDialog with available colors and player list
- [X] T009 [US1] Handle `marker_selected` message in client/views/game_view.py: update MarkerSelectionDialog to show claiming player's name under the selected color and mark it unavailable

**Checkpoint**: Players can see the selection dialog and claim markers. Server rejects duplicate claims.

---

## Phase 4: User Story 2 — Game Starts After All Players Pick (Priority: P1)

**Goal**: After the last player selects, all players see final assignments for ~1 second, then the game starts automatically.

**Independent Test**: Have all players select markers, verify a brief pause occurs showing final assignments, then the game begins normally.

**Dependencies**: Requires US1 (selection flow must work first)

### Implementation for User Story 2

- [X] T010 [US2] Add 1-second delayed game start in server/lobby.py: when `all_selected` is True in `select_marker()`, use `asyncio.create_task` with a 1-second sleep, then send filtered `GameStartedResponse` to each player and broadcast `BuildingMarketUpdateResponse` (move existing start_game broadcast logic into a helper)
- [X] T011 [US2] Handle `all_selected: true` in client/views/game_view.py: keep MarkerSelectionDialog visible showing final assignments, then dismiss dialog when `game_started` message arrives and proceed with normal game setup

**Checkpoint**: Full selection → pause → game start flow works end-to-end.

---

## Phase 5: User Story 3 — Seven Distinct Marker Colors (Priority: P1)

**Goal**: Seven visually distinct marker colors are available and rendered correctly on the game board.

**Independent Test**: Verify all seven marker colors are distinguishable in the selection dialog and on the game board.

### Implementation for User Story 3

- [X] T012 [P] [US3] Generate worker_pink.png marker image using Pillow in client/assets/card_images/markers/ (match existing marker style from worker_red.png)
- [X] T013 [P] [US3] Generate worker_lilac.png marker image using Pillow in client/assets/card_images/markers/ (match existing marker style, use color (186, 147, 216))
- [X] T014 [US3] Update `_PLAYER_COLORS` and `_COLOR_NAMES` in client/ui/board_renderer.py: expand to 7 entries (green, red, purple, blue, pink, lilac, orange), add `MARKER_COLOR_MAP` dict mapping color name strings to arcade color tuples, change worker rendering to look up color from player's `marker_color` field in game state instead of `slot_index`

**Checkpoint**: All seven colors render on both the selection dialog and the game board.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconnection support, state sync, testing, and validation

- [X] T015 Handle reconnection during MARKER_SELECTION phase in server/lobby.py: in `_resend_pending_prompts()`, if `state.phase == GamePhase.MARKER_SELECTION` and player has no marker_color, send `MarkerSelectionStartResponse` with current selection state
- [X] T016 Update `_filter_state_for_player()` in server/lobby.py to include `marker_color` field in player data (verify Pydantic model_dump includes it by default)
- [X] T017 Add server-side tests for marker selection logic in tests/test_marker_selection.py: test valid selection, duplicate color rejection, all-selected detection, phase validation
- [X] T018 Run full test suite with `uv run pytest` and linting with `ruff check .` from project root

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **US1 (Phase 3)**: Depends on Phase 2 completion
- **US2 (Phase 4)**: Depends on US1 (Phase 3) completion
- **US3 (Phase 5)**: Depends on Phase 2 completion — can run in parallel with US1
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1** (Player Selects a Marker): Core selection flow — no story dependencies, but requires Phase 2
- **US2** (Game Starts After Pick): Depends on US1 — extends the selection handler with delayed game start
- **US3** (Seven Distinct Colors): Independent of US1/US2 — marker assets and renderer changes can be done in parallel

### Within Each User Story

- Server-side changes before client-side changes
- Message handling before UI rendering
- Core flow before edge cases

### Parallel Opportunities

- T012 and T013 (pink and lilac PNGs) can run in parallel
- US3 (Phase 5) can run in parallel with US1 (Phase 3)
- T001 and T002 touch different files and could be parallel, but are small enough to do sequentially

---

## Parallel Example: User Story 3

```bash
# Generate both marker images simultaneously:
Task T012: "Generate worker_pink.png in client/assets/card_images/markers/"
Task T013: "Generate worker_lilac.png in client/assets/card_images/markers/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (constants, model, messages, routing)
2. Complete Phase 3: User Story 1 (selection dialog, server handler)
3. **STOP and VALIDATE**: Test marker selection works for all players
4. Proceed to US2 + US3

### Incremental Delivery

1. Phase 2 → Shared types ready
2. Phase 3 (US1) → Players can select markers (game starts immediately after last pick)
3. Phase 4 (US2) → Add 1-second pause before game start
4. Phase 5 (US3) → Add pink/lilac assets, update board renderer to use chosen colors
5. Phase 6 → Reconnection, tests, polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All 3 user stories are P1 priority but have a natural dependency order (US1 → US2)
- US3 is independently parallelizable with US1/US2
- Commit after each task or logical group
- The 1-second pause (US2) uses asyncio.create_task to avoid blocking the server event loop
