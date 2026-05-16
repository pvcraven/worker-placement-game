# Tasks: Intrigue Card Animation

**Input**: Design documents from `/specs/032-intrigue-card-animation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec — test tasks omitted. Server message changes should be validated by existing tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No project initialization needed — all infrastructure exists. This phase covers shared prerequisite work.

- [x] T001 [P] Generate full-size face-down intrigue card image (`intrigue_back.png`) by adding `generate_intrigue_back()` function to card-generator/generate_cards.py — create 400×500 px image with black border → white border → dark gray (60,60,60) fill → centered "I" in parchment color, output to client/assets/card_images/intrigue/intrigue_back.png, and call from main
- [x] T002 [P] Add `intrigue_card_id: str = ""` and `intrigue_card_name: str = ""` fields to `IntrigueEffectResolvedResponse` in shared/messages.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Server-side changes that MUST be complete before client animation work can proceed

**⚠️ CRITICAL**: No user story work on play animations (US3) can begin until this phase is complete

- [x] T003 Update `handle_choose_intrigue_target()` in server/game_engine.py to include `intrigue_card_id` and `intrigue_card_name` fields when broadcasting `IntrigueEffectResolvedResponse` — read card data from `state.pending_intrigue_target`
- [x] T004 Update `handle_play_intrigue_from_quest()` in server/game_engine.py to broadcast `IntrigueEffectResolvedResponse` for non-targeting intrigue effects (currently only calls `_advance_after_quest_rewards()` without notifying other clients) — include the played card's ID and name
- [x] T005 Run `cd src && pytest && ruff check .` to verify server changes pass existing tests

**Checkpoint**: Server now always broadcasts intrigue card details when intrigue is played. Client animation work can begin.

---

## Phase 3: User Story 4 - Full-Size Face-Down Card Image (Priority: P1) 🎯 MVP

**Goal**: A full-size face-down intrigue card image exists at the correct dimensions, visually consistent with existing intrigue card styling.

**Independent Test**: Run `cd card-generator && python generate_cards.py` and verify `client/assets/card_images/intrigue/intrigue_back.png` exists at 400×500 px.

- [x] T006 [US4] Run `cd card-generator && python generate_cards.py` and visually verify the generated intrigue_back.png in client/assets/card_images/intrigue/ — confirm it is 400×500, has the "I" letter centered, and looks consistent with face-up intrigue cards

**Checkpoint**: Face-down image asset ready. Draw animations for opponents can now use it.

---

## Phase 4: User Story 1 - Draw Intrigue Card Animation (Own Card) (Priority: P1)

**Goal**: When the local player draws an intrigue card, a face-up card flies from lower-right to center (2× scale, pause) to upper-left player info area, with card drag sound.

**Independent Test**: Start a game, complete a quest with intrigue reward, and verify the face-up animation plays for the drawing player.

### Implementation for User Story 1

- [x] T007 [US1] Add `_start_intrigue_draw_animation(card_id, pid, event)` function to client/views/game_view.py — load face-up sprite from `client/assets/card_images/intrigue/{card_id}.png` (when pid == local player) or face-down from `intrigue_back.png` (opponent), chain 3 animations: entry from (window.width-100, 100) to center at 0.5s SINE with scale→scale*2 and card sound, pause at center for 2.0s LINEAR, exit from center to `_player_marker_positions[pid]` at 0.75s QUAD_IN with scale back to original, set event.done on complete
- [x] T008 [US1] Modify `_on_quest_completed()` in client/views/game_view.py — after processing `drawn_intrigue` list, for each drawn intrigue card create an `AnimationEvent` whose setup calls `_start_intrigue_draw_animation(card["id"], pid, event)` and enqueue it via `self.event_queue.enqueue()`
- [ ] T009 [US1] Manually test: start server + client, complete a quest that grants intrigue cards, verify animation shows face-up card flying lower-right → center (2× scale, 2s pause) → upper-left with card1.mp3 sound

**Checkpoint**: Local player draw animation works. Can independently test quest reward intrigue draws.

---

## Phase 5: User Story 2 - Draw Intrigue Card Animation (Opponent's Card) (Priority: P1)

**Goal**: When an opponent draws an intrigue card, a face-down card (intrigue_back.png) flies the same path with sound, so the viewer knows a card was drawn but cannot see it.

**Independent Test**: Start two clients, have one complete a quest with intrigue reward, verify the other sees face-down animation.

### Implementation for User Story 2

- [ ] T010 [US2] Verify `_start_intrigue_draw_animation()` from T007 already handles the opponent case (pid != local player → uses intrigue_back.png) — no additional implementation expected, just confirm the branching logic is correct
- [ ] T011 [US2] Manually test with two clients: have player A complete a quest with intrigue reward, verify player B sees face-down card animation (intrigue_back.png) flying lower-right → center → upper-left with sound

**Checkpoint**: Both own-card and opponent-card draw animations work correctly.

---

## Phase 6: User Story 3 - Play Intrigue Card Animation (Priority: P2)

**Goal**: When any player plays an intrigue card, all players see a face-up card fly from upper-left player info area to center (2× scale, pause) to lower-right, with sound.

**Independent Test**: Play an intrigue card and verify all connected clients see the face-up play animation.

### Implementation for User Story 3

- [x] T012 [US3] Add `_start_intrigue_play_animation(card_id, pid, event)` function to client/views/game_view.py — always load face-up sprite from `client/assets/card_images/intrigue/{card_id}.png`, chain 3 animations: entry from `_player_marker_positions[pid]` to center at 0.5s SINE with scale→scale*2 and card sound, pause at center for 2.0s LINEAR, exit from center to (window.width-100, 100) at 0.75s QUAD_IN with scale back to original, set event.done on complete
- [x] T013 [US3] Modify `_on_intrigue_effect_resolved()` in client/views/game_view.py — before processing the effect, if `intrigue_card_id` is present in the message, create an `AnimationEvent` whose setup calls `_start_intrigue_play_animation(card_id, player_id, event)` and enqueue it; then queue subsequent effect processing after the animation
- [x] T014 [US3] Handle backstage intrigue play animation in the backstage handler in client/views/game_view.py — when `WorkerPlacedBackstageResponse` is received with an intrigue card that has a targeting effect, queue the play animation using `intrigue_card["id"]` and `player_id` before processing the effect
- [ ] T015 [US3] Manually test: start server + two clients, play an intrigue card (both targeting and non-targeting types), verify all clients see face-up card flying upper-left → center (2× scale, 2s pause) → lower-right with sound, followed by correct effect resolution

**Checkpoint**: All intrigue card animations (draw and play) working for all scenarios.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T016 Run `cd src && pytest && ruff check .` to verify all changes pass tests and linting
- [ ] T017 End-to-end test: run a full multiplayer game exercising all intrigue animation paths — quest reward draws (own + opponent), backstage draws, targeting plays, non-targeting plays, multiple sequential draws — verify no animation glitches, sound plays correctly, event queue sequencing works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — T001 and T002 can start immediately and run in parallel
- **Phase 2 (Foundational)**: T003/T004 depend on T002 (message model change). T005 depends on T003/T004.
- **Phase 3 (US4)**: Depends on T001 (face-down image generation). Can run in parallel with Phase 2.
- **Phase 4 (US1)**: Depends on Phase 3 (face-down image exists) for opponent path, but own-card path only needs face-up images (already exist). Can start after T001.
- **Phase 5 (US2)**: Depends on Phase 4 (US1 animation function). Primarily a verification phase.
- **Phase 6 (US3)**: Depends on Phase 2 (server broadcasts card details) and Phase 4 (animation pattern established).
- **Phase 7 (Polish)**: Depends on all prior phases.

### User Story Dependencies

- **US4 (Face-Down Image)**: Independent — only needs card generator
- **US1 (Own Draw Animation)**: Depends on US4 for face-down path, but own-card path is independent
- **US2 (Opponent Draw Animation)**: Depends on US1 (shares animation function) and US4 (needs face-down image)
- **US3 (Play Animation)**: Depends on Phase 2 (server changes) — independent of US1/US2 otherwise

### Within Each User Story

- Implementation before manual testing
- Server changes (Phase 2) before play animation client work (US3)

### Parallel Opportunities

- T001 (face-down image) and T002 (message model) can run in parallel
- T003 and T004 can run in parallel (different server handler functions)
- US4 verification (T006) can run in parallel with Phase 2 server work
- US1 and US3 implementation can partially overlap — T007 and T012 touch the same file but add independent functions

---

## Parallel Example: Phase 1

```
# Launch both setup tasks together:
Task T001: "Generate intrigue_back.png in card-generator/generate_cards.py"
Task T002: "Add fields to IntrigueEffectResolvedResponse in shared/messages.py"
```

## Parallel Example: Phase 2

```
# Launch both server handler updates together:
Task T003: "Update handle_choose_intrigue_target() in server/game_engine.py"
Task T004: "Update handle_play_intrigue_from_quest() in server/game_engine.py"
```

---

## Implementation Strategy

### MVP First (User Story 4 + User Story 1)

1. Complete T001 (face-down image generation)
2. Complete T002 (message model — can parallel with T001)
3. Run card generator, verify image (T006)
4. Implement draw animation function + hook (T007, T008)
5. **STOP and VALIDATE**: Test own-card draw animation independently (T009)

### Incremental Delivery

1. T001 + T002 → Setup complete
2. T006 → Face-down image verified (US4 done)
3. T007 + T008 + T009 → Own-card draw animation works (US1 done)
4. T010 + T011 → Opponent draw animation verified (US2 done)
5. T003 + T004 + T005 → Server play broadcasts ready
6. T012 + T013 + T014 + T015 → Play animation works (US3 done)
7. T016 + T017 → Full validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 share the same animation function — US2 is primarily a verification phase
- Sound integration is built into the animation functions (T007, T012) via the existing `self._card_sound`
- The event queue integration is built into T008, T013, and T014 — no separate task needed
- Commit after each task or logical group
