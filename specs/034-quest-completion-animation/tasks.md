# Tasks: Quest Completion Animation

**Input**: Design documents from `/specs/034-quest-completion-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No test tasks included (not requested in spec; this is a client-side visual animation).

**Organization**: Tasks are grouped by user story. All tasks modify `client/views/game_view.py` — no parallel [P] opportunities since all changes are in the same file.

## Format: `[ID] [Story] Description`

- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- All implementation is in `client/views/game_view.py`

---

## Phase 1: Setup

**Purpose**: No setup needed. No new files, dependencies, or project structure changes. All assets (quest card PNGs, resource icon PNGs) already exist. All infrastructure (AnimationManager, EventQueue, AnimationEvent) already exists.

**Checkpoint**: N/A — proceed directly to Foundational phase.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the enqueue method skeleton and resource icon helper that all animation phases depend on.

- [x] T001 Add `_enqueue_quest_completion` method in `client/views/game_view.py` that creates an `AnimationEvent` wrapping `_start_quest_completion_animation` and enqueues it on `self.event_queue`. Follow the pattern from `_enqueue_intrigue_draw` (line 1051). The method should accept the quest completion message dict.
- [x] T002 Add `_start_quest_completion_animation` skeleton method in `client/views/game_view.py` that receives the message dict and `AnimationEvent`, extracts `contract_id`, `player_id`, `resources_spent`, `bonus_resources`, looks up `self._player_marker_positions[pid]`, computes screen center `(self.window.width / 2, self.window.height / 2)`, and creates the quest card sprite from `client/assets/card_images/quests/{contract_id}.png`. Set `event.done = True` as a placeholder completion.
- [x] T003 Add `_build_resource_icon_list` helper method in `client/views/game_view.py` that takes a resource dict (e.g., `{"guitarists": 3, "singers": 1}`) and returns a flat list of icon file paths by expanding each resource key by its count, using the mapping: `guitarists` → `client/assets/card_images/icons/guitarist.png`, `bass_players` → `bass_player.png`, `drummers` → `drummer.png`, `singers` → `singer.png`, `coins` → `coin.png`.
- [x] T004 Modify `_on_quest_completed` in `client/views/game_view.py` to call `_enqueue_quest_completion(msg)` at the start of the method (before existing state update logic), so the animation is enqueued on the event queue.

**Checkpoint**: Foundation ready — completing a quest should enqueue an animation event that creates a card sprite and immediately completes. Existing state updates and log entries still work. Intrigue draw animations that follow quest completion are sequenced after.

---

## Phase 3: User Story 1 — Card Entrance Animation (Priority: P1) MVP

**Goal**: The quest card appears at normal scale near the player's marker position and animates to screen center while scaling to 2x.

**Independent Test**: Complete any quest → observe the card sprite animate from upper-left to center, growing to 2x size, then disappearing (placeholder exit).

- [x] T005 [US1] Implement card entrance animation in `_start_quest_completion_animation` in `client/views/game_view.py`. Use `self.animation_manager.animate()` to move the quest card sprite from the player marker position to screen center over 0.5s with `Easing.SINE`, scaling from `scale` to `scale * 2`. Set `on_complete` to a callback that will trigger the next phase (for now, set `event.done = True` in the callback as placeholder).

**Checkpoint**: Completing a quest shows the card flying to center at 2x scale, then the event completes.

---

## Phase 4: User Story 2 — Resource Requirements Stream (Priority: P1)

**Goal**: After the card reaches center, resource cost icons stream one-at-a-time from the player position to the card center, staggered by ~0.25s.

**Independent Test**: Complete a quest requiring multiple resources (e.g., 4 guitarists) → observe 4 guitarist icons fly sequentially from the player area to the card center with visible stagger timing.

- [x] T006 [US2] Add `_stream_resources_to_card` method in `client/views/game_view.py`. It takes: icon file paths (from `_build_resource_icon_list`), origin position (player marker), destination position (screen center), and an `on_all_done` callback. For each icon, create an `arcade.Sprite`, then animate it. Stagger starts by using a short 0.25s "hold" animation at the origin whose `on_complete` launches the next icon's flight. Each flight icon animates from origin to destination over ~0.5s with `Easing.SINE`. Use a remaining-count integer to track completions; when the last icon arrives, call `on_all_done`.
- [x] T007 [US2] Wire card entrance `on_complete` in `_start_quest_completion_animation` to call `_stream_resources_to_card` with the `resources_spent` icons, player marker position as origin, screen center as destination. If `resources_spent` has all zero values (no icons), skip directly to the next phase. The `on_all_done` callback should set `event.done = True` as a placeholder for now.

**Checkpoint**: Completing a quest shows card entrance → resource icons stream to card → event completes. Quests with zero cost skip the stream.

---

## Phase 5: User Story 3 — Reward Distribution Animation (Priority: P2)

**Goal**: After all requirement icons finish, bonus resource reward icons fly from the card center back to the player position.

**Independent Test**: Complete a quest with bonus resources (check contracts.json for quests with `bonus_resources`) → observe reward icons fly from card center to the player area after the requirements stream finishes.

- [x] T008 [US3] Wire the requirements stream `on_all_done` callback in `_start_quest_completion_animation` to start the reward phase. If `bonus_resources` has any non-zero values, call `_stream_resources_to_card` with the `bonus_resources` icons, screen center as origin, player marker position as destination. If no bonus resources, skip directly to the next phase. Reuse the same `_stream_resources_to_card` method — it works in both directions since origin/destination are parameters.

**Checkpoint**: Completing a quest with bonus resources shows card entrance → cost stream → reward stream → event completes. Quests without bonus resources skip the reward stream.

---

## Phase 6: User Story 4 — Card Exit Animation (Priority: P2)

**Goal**: After all reward animations (or requirements if no rewards), the card animates from center to lower-right and disappears.

**Independent Test**: Complete any quest → observe the full sequence: card entrance → cost stream → reward stream (if applicable) → card flies to lower-right and disappears → gameplay resumes.

- [x] T009 [US4] Add `_exit_quest_card` method in `client/views/game_view.py` that animates the quest card sprite from screen center to the lower-right corner `(self.window.width + 100, -100)` over 0.75s with `Easing.QUAD_IN`, scaling from `scale * 2` back to `scale`. The `on_complete` callback sets `event.done = True`.
- [x] T010 [US4] Wire the reward stream `on_all_done` (or the requirements `on_all_done` when no rewards, or the entrance `on_complete` when no costs and no rewards) to call `_exit_quest_card`. Ensure the full callback chain works for all combinations: costs+rewards, costs-only, rewards-only, neither.

**Checkpoint**: Full animation sequence works end-to-end for all quest types. Event queue unblocks after exit.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and integration validation.

- [x] T011 Verify edge case handling in `_start_quest_completion_animation` in `client/views/game_view.py`: if the quest card image file is missing, set `event.done = True` immediately and return (graceful fallback, matching the pattern in `_start_card_pick_animation` line 992). If the player marker position is not found, use fallback `(0.0, float(self.window.height))`.
- [ ] T012 Manual integration test: run server and client, complete quests with varying resource costs and rewards to verify the full animation sequence. Check that drawn intrigue card animations play after the quest completion animation. Check that `next_player_id` turn updates are applied correctly. Verify no stale sprites remain on screen.
- [x] T013 Run `cd src && pytest && ruff check .` to verify no regressions or lint errors.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A — nothing to do
- **Foundational (Phase 2)**: T001 → T002 → T003 → T004 (sequential, same file)
- **US1 (Phase 3)**: Depends on Phase 2 complete. T005 modifies T002's skeleton.
- **US2 (Phase 4)**: Depends on US1 (T005). T006 → T007 (sequential).
- **US3 (Phase 5)**: Depends on US2 (T007). T008 modifies callback chain.
- **US4 (Phase 6)**: Depends on US3 (T008). T009 → T010 (sequential).
- **Polish (Phase 7)**: Depends on US4 (T010). T011 → T012 → T013 (sequential).

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational only. Can be tested independently (card flies to center).
- **US2 (P1)**: Depends on US1 (needs card at center as visual anchor). Can be tested with US1.
- **US3 (P2)**: Depends on US2 (reward stream starts after cost stream). Can be tested with US1+US2.
- **US4 (P2)**: Depends on US3 (exit starts after rewards). Can be tested with all prior stories.

Note: These stories are inherently sequential phases of a single animation. They cannot be parallelized.

### Parallel Opportunities

None — all changes are in `client/views/game_view.py`. The animation phases are sequential by design (each phase triggers the next via callbacks).

---

## Implementation Strategy

### MVP First (User Stories 1+2)

1. Complete Phase 2: Foundational (T001-T004)
2. Complete Phase 3: Card Entrance (T005)
3. Complete Phase 4: Requirements Stream (T006-T007)
4. **STOP and VALIDATE**: Complete a multi-resource quest and verify entrance + stream
5. This delivers the core visual feedback loop (card + cost payment)

### Incremental Delivery

1. Foundational → skeleton works, quest completion still functional
2. Add US1 → card flies to center (immediate visual improvement)
3. Add US2 → resource costs stream to card (core feedback)
4. Add US3 → rewards stream back (full feedback loop)
5. Add US4 → clean exit animation (polished finish)
6. Each increment is a shippable improvement over the previous state

---

## Notes

- All 13 tasks modify or validate `client/views/game_view.py` — no parallel opportunities
- The animation is purely visual; all game state mutations happen in existing `_on_quest_completed` handler
- Resource icon sprites already exist at `client/assets/card_images/icons/`
- Follow the callback chaining pattern from `_start_card_pick_animation` (lines 970-1049)
- The `_stream_resources_to_card` method is reused for both cost and reward streaming (just swap origin/destination)
