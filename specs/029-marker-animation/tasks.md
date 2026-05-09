# Tasks: Marker Placement Animation

**Input**: Design documents from `specs/029-marker-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Load tick sound and prepare animation infrastructure

- [X] T001 Load `tick_001.ogg` sound in GameView.__init__() as `self._tick_sound` in client/views/game_view.py

---

## Phase 2: Foundational — Animation Infrastructure (US4)

**Purpose**: Build the reusable AnimationManager that ALL animation user stories depend on. MUST complete before any animation work.

**Goal**: A reusable animation system that supports animating any sprite from one position to another with configurable easing, duration, and optional sound.

**Independent Test**: Create a test animation manually (e.g., a colored circle sprite animating across the screen) to verify the manager works before integrating with game logic.

- [X] T002 [US4] Create EaseAnimation dataclass and AnimationManager class in client/ui/animation_manager.py — support animate(), update(delta_time), draw(), and clear() methods using arcade.anim.ease with configurable Easing function, duration, optional sound, and optional on_complete callback
- [X] T003 [US4] Add `get_space_position(space_id) -> tuple[float, float] | None` method to BoardRenderer in client/ui/board_renderer.py — returns pixel coordinates for any action space, backstage slot, or constructed building using existing _GRID_PLACEMENT and grid calculations
- [X] T004 [US4] Instantiate AnimationManager in GameView._build_ui() and wire update(delta_time) into on_update() and draw() into on_draw() (after board rendering, before UI overlays) in client/views/game_view.py

**Checkpoint**: AnimationManager is initialized, updating each frame, and rendering. No animations queued yet but the infrastructure is ready.

---

## Phase 3: User Story 1 — Player List Marker Sprites (Priority: P1) 🎯 MVP

**Goal**: Replace colored circles in the player list with worker marker sprites. Store player marker positions for animation origin lookup.

**Independent Test**: Start a game and verify each player's name in the top-left shows a worker marker sprite (matching their color) instead of a colored circle. Resize the window and confirm sprites scale correctly.

### Implementation for User Story 1

- [X] T005 [US1] Add `_player_marker_positions: dict[str, tuple[float, float]]` and `_player_marker_sprites: dict[str, arcade.Sprite]` to GameView.__init__() in client/views/game_view.py
- [X] T006 [US1] Replace `arcade.draw_circle_filled()` call in `_draw_player_list()` with worker marker sprites — load textures via board_renderer._get_worker_texture(color_name), scale to circle size, position at (list_x + circle_r, row_top), add to a SpriteList, and store positions in `_player_marker_positions[player_id]` each frame in client/views/game_view.py

**Checkpoint**: Player list shows marker sprites. `_player_marker_positions` is populated each frame for animation origin lookup.

---

## Phase 4: User Story 2 — Animated Worker Placement for Current Player (Priority: P1)

**Goal**: When the current player places a worker, animate the marker from their name area to the board spot with sine easing and tick sound.

**Independent Test**: Place a worker on any board spot. Verify a marker sprite animates from your name in the top-left to the target spot, accompanied by a tick sound.

### Implementation for User Story 2

- [X] T007 [US2] In `_on_worker_placed()`, before `_refresh_board()`, queue a placement animation: look up origin from `_player_marker_positions[player_id]`, look up target from `board_renderer.get_space_position(space_id)`, create worker marker sprite, call `animation_manager.animate()` with Easing.SINE, ~1s duration, and tick sound in client/views/game_view.py

**Checkpoint**: Current player's placements animate from name to board spot with sound.

---

## Phase 5: User Story 3 — Animated Worker Placement for Other Players (Priority: P1)

**Goal**: In multiplayer, other players' placements also animate from their name area.

**Independent Test**: In a multiplayer game, have another player place a worker. Verify animation flies from that player's name area to the board spot.

### Implementation for User Story 3

- [X] T008 [US3] Verify that T007's implementation already handles all players (not just current player) — `_on_worker_placed()` fires for all players' placements. The origin lookup uses `_player_marker_positions[player_id]` which contains all players. If any current-player-only guard exists, remove it for the animation queueing code in client/views/game_view.py

**Checkpoint**: All players' placements animate correctly in multiplayer. Animation originates from the correct player's name area.

---

## Phase 6: User Story 5 — Animated Worker Recall (Priority: P2)

**Goal**: When the round ends, workers animate back from board spots to their owning player's name area.

**Independent Test**: Complete a round. Verify all placed workers animate from their board positions back to their respective players' name areas, each accompanied by a tick sound.

### Implementation for User Story 5

- [X] T009 [US5] In `_on_round_end()`, before clearing `occupied_by` fields: snapshot all current worker positions and their owning player IDs from board state. For each occupied space, queue a reverse animation (space position → `_player_marker_positions[owner_id]`) with Easing.SINE and tick sound. Then proceed with existing board-clearing logic in client/views/game_view.py

**Checkpoint**: Workers animate back to players' names on round end.

---

## Phase 7: User Story 6 — Animated Worker Reassignment (Priority: P2)

**Goal**: During reassignment, workers animate from backstage slot position to target action space.

**Independent Test**: Place a worker on a Backstage slot. Complete placement phase. Reassign the worker to an action space. Verify animation from backstage slot to target, with tick sound.

### Implementation for User Story 6

- [X] T010 [US6] In `_on_worker_reassigned()`, before `_refresh_board()`: look up backstage slot position via `board_renderer.get_space_position(f"backstage_slot_{from_slot}")`, look up target position via `board_renderer.get_space_position(to_space_id)`, determine player color from player_id, create marker sprite, queue animation with Easing.SINE and tick sound in client/views/game_view.py

**Checkpoint**: Reassigned workers animate from backstage to target space.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Edge case handling and cleanup

- [X] T011 [P] Add `animation_manager.clear()` call in `_on_placement_cancelled()` to interrupt any in-progress animation when a placement is cancelled in client/views/game_view.py
- [X] T012 [P] Handle backstage placement animation — in `_on_worker_placed_backstage()`, queue animation from `_player_marker_positions[player_id]` to backstage slot position with tick sound in client/views/game_view.py
- [X] T013 Run full manual test per quickstart.md: placement animation (self + other player), recall animation, reassignment animation, backstage animation, window resize during animation, rapid sequential placements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational — provides marker positions needed by all animations
- **User Stories 2, 3 (Phases 4-5)**: Depend on US1 (for player marker positions) and Foundational (for AnimationManager)
- **User Stories 5, 6 (Phases 6-7)**: Depend on US1 and Foundational; can run in parallel with US2/US3
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (AnimationManager + get_space_position)
    ↓
Phase 3: US1 - Player List Sprites (provides _player_marker_positions)
    ↓
  ┌─────────────────────────────────────────┐
  ↓                   ↓                     ↓
Phase 4: US2      Phase 6: US5         Phase 7: US6
(Placement)       (Recall)             (Reassignment)
  ↓
Phase 5: US3
(Multiplayer verification)
  ↓
Phase 8: Polish
```

### Within Each User Story

- Foundational infrastructure before story-specific integration
- Each story is one integration task (the infrastructure does the heavy lifting)

### Parallel Opportunities

- T011 and T012 in Polish phase can run in parallel
- Phases 4-5 and Phases 6-7 can potentially run in parallel (different handler methods, no file conflicts within AnimationManager calls)

---

## Parallel Example: After Phase 3 Completion

```
# These can run in parallel (different handler methods):
Task T007: Placement animation in _on_worker_placed()
Task T009: Recall animation in _on_round_end()
Task T010: Reassignment animation in _on_worker_reassigned()
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T004)
3. Complete Phase 3: Player list marker sprites (T005-T006)
4. Complete Phase 4: Placement animation (T007)
5. **STOP and VALIDATE**: Place workers and verify animation works
6. This delivers the core visual improvement

### Incremental Delivery

1. Setup + Foundational → AnimationManager ready
2. Add US1 (marker sprites) → Verify player list looks correct
3. Add US2 (placement animation) → Verify animation works → **MVP!**
4. Add US3 (multiplayer verification) → Test with 2+ players
5. Add US5 (recall animation) → Verify round-end animation
6. Add US6 (reassignment animation) → Verify backstage flow
7. Polish → Edge cases, backstage placement animation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All changes are client-side only — no server modifications needed
- US4 (Reusable Animation System) is implemented as Phase 2 Foundational since all other stories depend on it
- US3 (Multiplayer) is primarily a verification task — the placement animation code from US2 already handles all players
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
