# Tasks: Building Acquisition Animation

**Input**: Design documents from `/specs/035-building-acquisition-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No automated tests requested. Animation is verified through manual testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Board Renderer Position Methods)

**Purpose**: Add public position-lookup methods to BoardRenderer that all animation stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T001 [P] Add `get_building_card_info(building_id)` method to `client/ui/board_renderer.py` — returns `(center_x, center_y, scale)` for a face-up building card by its building_id, matching the pattern of existing `get_quest_card_info()`. Look up the building's index in `_face_up_buildings`, then return position from `_bld_positions[index]` and the building card scale. Return `None` if building not found.
- [x] T002 [P] Add `get_building_lot_position(lot_index)` method to `client/ui/board_renderer.py` — computes screen position `(center_x, center_y, scale)` for a constructed building lot. Use the grid math: `col = 1 + (lot_index % 2)`, `row = (lot_index // 2) * 2`, then call `self._grid.cell_rect(col, row, 1, 2)` to get pixel coordinates. Return the center position and building card scale.

**Checkpoint**: Both position methods available — animation stories can now begin.

---

## Phase 2: User Story 1 — Face-Up Building Purchase Animation (Priority: P1) 🎯 MVP

**Goal**: When a player purchases a face-up building from the market, the building card animates from its market position (right side) to its assigned lot position (left side).

**Independent Test**: Purchase any face-up building via the Realtor action space. Observe the building card fly from the market to the constructed buildings area, landing in the correct lot position. The building should not appear in the constructed area until the animation completes.

### Implementation for User Story 1

- [x] T003 [US1] Add `_start_building_purchase_animation(building_id, lot_index, msg, event)` method to `client/views/game_view.py` — Creates a sprite from the building image (`client/assets/card_images/buildings/{building_id}.png`). Looks up origin via `board_renderer.get_building_card_info(building_id)`. Looks up destination via `board_renderer.get_building_lot_position(lot_index)`. Calls `animation_manager.animate()` with ~0.75s duration, `Easing.SINE`, and card sound. The `on_complete` callback applies the building state update (add to `constructed_buildings`, create action space entry, update coins/VP, call `_refresh_board()`, update turn status) and sets `event.done = True`. If the building is not found in the market (e.g., already removed), fall back to the lower-right corner origin so the animation still plays.
- [x] T004 [US1] Modify `_on_building_constructed()` in `client/views/game_view.py` — Currently applies state changes and calls `_refresh_board()` immediately. Refactor to: (1) extract `building_id`, `lot_index`, and full message data, (2) create an `AnimationEvent` whose setup function calls `_start_building_purchase_animation()`, (3) move all state mutation and `_refresh_board()` into the animation's `on_complete` callback, (4) enqueue the event via `self.event_queue.enqueue()`. Keep the coin deduction, VP update, resource bar update, game panel log, and turn status update logic — just move them into the callback.
- [x] T005 [US1] Modify `_on_quest_reward_choice_resolved()` in `client/views/game_view.py` — When `reward_type == "choose_building"`: extract building data from `choice` dict (`building_id`, `lot_index`, `space_id`, etc.), create an `AnimationEvent` whose setup calls `_start_building_purchase_animation()` (same market-origin animation as regular purchase), move state mutation into `on_complete` callback, and enqueue the event. The animation origin is the market since the player chose from face-up buildings.

**Checkpoint**: Face-up building purchases and market-choice quest rewards animate from market to lot. Verify by purchasing a building via Realtor.

---

## Phase 3: User Story 2 — Drawn Building Animation (Priority: P2)

**Goal**: When a player receives a building drawn from the deck (e.g., quest reward), the building card flies up from the lower-right corner of the screen to its assigned lot position.

**Independent Test**: Complete a quest that grants a random building draw. Observe the building card appear at the lower-right corner and animate upward to the constructed buildings area.

### Implementation for User Story 2

- [x] T006 [US2] Add `_start_building_draw_animation(building_id, lot_index, msg, event)` method to `client/views/game_view.py` — Similar to `_start_building_purchase_animation()` but origin is the lower-right corner of the board/screen (e.g., `(self.window.width - 100, 100)` or compute from grid cell (6, 7)). Uses a slightly smaller `start_scale` growing to normal `end_scale` for a "flying in from deck" effect. Same ~0.75s duration, `Easing.SINE`, and card sound. The `on_complete` callback applies building state update, calls `_refresh_board()`, and sets `event.done = True`.
- [x] T007 [US2] Modify `_on_quest_completed()` in `client/views/game_view.py` — When `building_granted` is present in the response: extract building data (`building_id`, `building_name`, `lot_index`, `space_id`, `visitor_reward`, `owner_bonus`, `accumulated_vp`), create an `AnimationEvent` whose setup calls `_start_building_draw_animation()`, move the building state mutation (append to `constructed_buildings`, create action space entry, call `_refresh_board()`) into the `on_complete` callback, and enqueue the event. This animation event should be enqueued after the quest completion animation event so both play sequentially (the building flies in after the quest card animation finishes).

**Checkpoint**: Drawn buildings animate from lower-right corner to lot. Verify by completing a quest with a random building reward.

---

## Phase 4: User Story 3 — Multiplayer Visibility (Priority: P3)

**Goal**: All connected clients see the same building acquisition animation, not just the acquiring player.

**Independent Test**: Connect two clients. On client A, purchase a building. On client B, observe the same market-to-lot animation. Repeat with a quest that grants a building draw.

### Implementation for User Story 3

- [ ] T008 [US3] Verify multiplayer animation visibility — No new code expected. The existing broadcast mechanism sends `BuildingConstructedResponse` and `QuestCompletedResponse` to all clients. Since the animation is triggered from response handlers (not from user action), all clients should already play the animation. Manually test with two clients: (1) purchase a face-up building on client A and verify client B plays the same animation, (2) complete a quest with building reward on client A and verify client B plays the draw animation. If animations don't play on the remote client, debug the response handler to ensure the `AnimationEvent` is created for all players (not just `player_id == my_id`).

**Checkpoint**: All three acquisition paths animate correctly on both local and remote clients.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and code quality.

- [x] T009 Run `cd src && ruff check .` and fix any linting issues in modified files
- [ ] T010 Run full manual test sweep per quickstart.md: (1) market purchase via Realtor, (2) random draw from quest reward, (3) market choice from quest reward, (4) multiplayer with two clients, (5) rapid sequential purchases to verify animation queuing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — can start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 completion (needs position methods)
- **User Story 2 (Phase 3)**: Depends on Phase 1 completion (needs position methods). Independent of US1, but can reuse patterns from it.
- **User Story 3 (Phase 4)**: Depends on US1 and US2 being implemented (needs animations to exist for testing)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 1) — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 1) — independent of US1 but benefits from implementing US1 first (shared pattern)
- **User Story 3 (P3)**: Depends on US1 and US2 — verification only, no new code expected

### Within Each User Story

- Animation setup method before handler modification
- Handler modification includes moving state update into callback

### Parallel Opportunities

- T001 and T002 can run in parallel (different methods, same file but independent)
- US1 and US2 can start in parallel after Phase 1 (different animation methods and handlers)
- T003 and T006 could be developed in parallel (different animation methods)

---

## Parallel Example: Foundational Phase

```bash
# Launch both position methods together:
Task: "Add get_building_card_info() to client/ui/board_renderer.py"
Task: "Add get_building_lot_position() to client/ui/board_renderer.py"
```

## Parallel Example: User Stories 1 & 2

```bash
# After Foundational, both stories can start in parallel:
# US1 thread:
Task: "Add _start_building_purchase_animation() to client/views/game_view.py"
Task: "Modify _on_building_constructed() in client/views/game_view.py"
Task: "Modify _on_quest_reward_choice_resolved() in client/views/game_view.py"

# US2 thread (parallel):
Task: "Add _start_building_draw_animation() to client/views/game_view.py"
Task: "Modify _on_quest_completed() in client/views/game_view.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (position methods)
2. Complete Phase 2: User Story 1 (face-up purchase animation)
3. **STOP and VALIDATE**: Test market purchase animation independently
4. This alone delivers the most common building acquisition animation

### Incremental Delivery

1. Add Foundational → Position methods ready
2. Add User Story 1 → Market purchase animates → Validate (MVP!)
3. Add User Story 2 → Deck draw animates → Validate
4. Add User Story 3 → Verify multiplayer → Validate
5. Each story adds animation coverage without breaking previous stories

---

## Notes

- [P] tasks = different files or independent methods, no dependencies
- [Story] label maps task to specific user story for traceability
- No automated tests — animation verified through manual testing per quickstart.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
