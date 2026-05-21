# Tasks: Resource Gathering Animation

**Input**: Design documents from `/specs/036-resource-gathering-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested — animation is visual-only, tested manually per quickstart.md.

**Organization**: Tasks are grouped by user story. All changes are in a single file (`client/views/game_view.py`), so parallel opportunities within phases are limited.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Foundational

**Purpose**: Create the core helper method that all user stories depend on

- [x] T001 Add `_start_resource_gathering_animation` method to `GameView` in client/views/game_view.py. This method accepts `space_id: str`, `player_id: str`, `reward: dict`, `owner_bonus: dict`, `trigger_bonuses: list[dict]`, and `on_complete: callable`. It builds an icon list from `reward` via `_build_resource_icon_list`, resolves the origin from `board_renderer.get_space_position(space_id)` and destination from `_player_marker_positions[player_id]`. If the icon list is non-empty and both positions are available, it calls `_stream_resources(icons, origin, destination, on_all_done=on_complete)`. If the icon list is empty or positions are unavailable, it calls `on_complete()` immediately. Initially ignore owner_bonus and trigger_bonuses (those are added in US2 and US3).

**Checkpoint**: Helper method exists and handles base reward streaming with skip-when-empty logic

---

## Phase 2: User Story 1 — Resource Animation on Permanent Spot (Priority: P1) MVP

**Goal**: When a worker lands on a permanent resource spot, resource icons fly from the spot to the player's name area

**Independent Test**: Place a worker on any permanent spot that grants resources (e.g., Merch Store). Observe individual resource icons flying from the spot to the player's name area in the top-left. Place on a spot with no resources (e.g., The Garage for quest selection) and confirm no resource animation plays.

### Implementation for User Story 1

- [x] T002 [US1] Modify `_on_worker_placed` in client/views/game_view.py to chain resource animation after marker animation. Change the marker animation's `on_complete` lambda to call `_start_resource_gathering_animation` instead of directly calling `_refresh_board` and `_update_current_player`. Pass `space_id`, `pid`, `reward`, `msg.get("owner_bonus", {})`, `msg.get("trigger_bonuses", [])`, and a new final callback as arguments. The final callback should contain the original completion logic: `_refresh_board` and `_update_current_player`. Also update the no-animation branch (when origin/target are None) to call through the same path.

- [x] T003 [US1] Move special action handling into the final animation callback in client/views/game_view.py. Currently, special action setup (garage quest selection, building purchase highlight mode, building visitor reward special, intrigue draw) at lines ~432-503 of `_on_worker_placed` runs synchronously after queueing the marker animation. Refactor so this special action handling executes inside the final `on_complete` callback of `_start_resource_gathering_animation`, after board refresh and current player update. This ensures resource animations complete before the player is prompted for special interactions (FR-003). Keep `_apply_reward_to_player` and worker count decrement in their current positions (immediate, before animation).

**Checkpoint**: Worker placement on permanent spots shows resource flying animation. Spots with no resources behave as before. Special actions trigger after animation completes.

---

## Phase 3: User Story 2 — Resource Animation on Constructed Building (Priority: P1)

**Goal**: Owner bonus resources animate to the building owner's name area when a visitor places a worker on an owned building

**Independent Test**: Have one player build a building. Have another player place a worker on it. Observe: visitor's reward icons fly to visitor's name area, then owner's bonus icons fly to the owner's name area.

### Implementation for User Story 2

- [x] T004 [US2] Extend `_start_resource_gathering_animation` in client/views/game_view.py to handle owner bonus. After the base reward stream completes (in its `on_all_done` callback), check if `owner_bonus` has animatable resources via `_build_resource_icon_list(owner_bonus)`. If non-empty, resolve the owner's destination from `_player_marker_positions` using the owner's player_id (extract from `owner_bonus` dict or look up via `action_spaces[space_id]["building_tile"]["owner_id"]` from `self.game_state`). Call `_stream_resources` with the owner's icon list, same origin (space position), owner's destination, and chain the next stage as `on_all_done`. If owner bonus is empty, skip directly to the next stage. Also call `_apply_reward_to_player` for the owner's bonus resources so the owner's resource bar updates.

**Checkpoint**: Visitor placement on owned buildings shows two sequential animations: visitor rewards → owner bonus. Unowned buildings or buildings with no owner bonus behave like permanent spots.

---

## Phase 4: User Story 3 — Resource Trigger Bonus Animation (Priority: P2)

**Goal**: When plot quest triggers fire, bonus resources animate from the building to the player's name area, sequenced after base reward and owner bonus

**Independent Test**: Complete a plot quest that grants a resource trigger. Place a worker on a spot that activates the trigger. Observe base reward icons fly first, then trigger bonus icons fly in sequence.

### Implementation for User Story 3

- [x] T005 [US3] Extend `_start_resource_gathering_animation` in client/views/game_view.py to handle trigger bonuses. After the owner bonus stage completes, check if `trigger_bonuses` list is non-empty. For each trigger bonus entry, build an icon list from its `bonus_resources` dict via `_build_resource_icon_list`. Chain `_stream_resources` calls sequentially: each trigger's `on_all_done` starts the next trigger's stream. The final trigger's `on_all_done` calls `on_complete`. If `trigger_bonuses` is empty, skip directly to `on_complete`.

**Checkpoint**: All three animation stages chain correctly: base reward → owner bonus → trigger bonuses → completion. Multiple triggers sequence one after another.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and code quality

- [x] T006 Run `ruff check .` from src/ directory and fix any linting issues in client/views/game_view.py
- [ ] T007 Manual visual testing per quickstart.md scenarios in client/views/game_view.py: (1) permanent spot with resources, (2) constructed building, (3) owned building with owner bonus, (4) trigger bonus activation, (5) quest selection spot with no resources, (6) building purchase spot

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — can start immediately
- **US1 (Phase 2)**: Depends on T001 (foundational helper method)
- **US2 (Phase 3)**: Depends on T003 (US1 complete, callback chain established)
- **US3 (Phase 4)**: Depends on T004 (US2 complete, owner bonus stage in chain)
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Depends on foundational helper — establishes the callback chain
- **US2 (P1)**: Depends on US1 — extends the existing chain with owner bonus stage
- **US3 (P2)**: Depends on US2 — extends the chain with trigger bonus stage

Note: US2 and US3 extend the same method created in US1, so they must be sequential.

### Within Each User Story

- All tasks within a phase are sequential (same file, building on prior changes)

### Parallel Opportunities

- Limited — all tasks modify the same file (`client/views/game_view.py`)
- T006 (ruff check) can run after any implementation task to catch issues early

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (T001)
2. Complete Phase 2: User Story 1 (T002, T003)
3. **STOP and VALIDATE**: Test with permanent spots and constructed buildings
4. Base reward animation works for all space types

### Incremental Delivery

1. T001 → Foundation ready (helper method exists)
2. T002-T003 → US1 complete: base reward animation works (MVP)
3. T004 → US2 complete: owner bonus animation works
4. T005 → US3 complete: trigger bonus animation works
5. T006-T007 → Polish: linting and full manual test pass

---

## Notes

- All tasks modify `client/views/game_view.py` — no new files created
- No server changes — all data already present in `WorkerPlacedResponse`
- Animation parameters (scale 0.5, 1.0s duration, 0.25s stagger, SINE easing) are inherited from `_stream_resources` — no parameter changes needed
- `_build_resource_icon_list` naturally excludes victory points (not in `_RESOURCE_ICON_MAP`)
- Commit after each phase checkpoint for clean rollback points
