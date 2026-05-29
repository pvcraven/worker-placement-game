# Tasks: The Green Room — Intrigue Quest Space

**Input**: Design documents from `/specs/038-intrigue-quest-space/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included for server-side game logic per Constitution Principle IV (Test-Driven Game Logic).

**Organization**: Tasks grouped by user story. US1 and US2 are combined (both P1, same handler code).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Config)

**Purpose**: Add The Green Room space definition to board config

- [X] T001 Add The Green Room permanent space entry to config/board.json with `space_id: "the_green_room"`, `name: "The Green Room"`, `space_type: "permanent"`, `reward: {}`, `reward_special: "play_intrigue_and_quest"`, `slots: 1`. Insert after the existing VIP Entrance entry in the permanent_spaces array.

**Checkpoint**: Config entry exists and loads without validation errors

---

## Phase 2: User Story 1+2 — Play Intrigue and Select Quest + Cancel/Back-Out (Priority: P1) MVP

**Goal**: Players can place a worker on The Green Room, play an intrigue card (with animation), then select a face-up quest card. Players with no intrigue cards are rejected. Players can back out before committing the intrigue card play.

**Independent Test**: Place worker on The Green Room with intrigue cards in hand → play one → select quest. Also test: placement rejected when no intrigue cards; cancel before playing intrigue returns worker.

### Implementation

- [X] T002 [US1] Add `play_intrigue_and_quest` routing in `handle_place_worker()` in server/game_engine.py. Before the garage check (~line 1741), add a branch for `space.reward_special == "play_intrigue_and_quest"` that: validates player has intrigue cards (reject with error if not), sets `pending_placement`, sets `pending_play_intrigue = {"player_id": player.player_id, "source": "green_room"}`, logs event, broadcasts `WorkerPlacedResponse` with empty reward and `next_player_id=None`, sends `IntriguePlayPromptResponse` with player's intrigue hand to the placing player.

- [X] T003 [US1] Modify `handle_play_intrigue_from_quest()` in server/game_engine.py to support green_room source. Before clearing `pending_play_intrigue` (~line 4678), capture `source = state.pending_play_intrigue.get("source")`. After clearing: when `effect_details.get("pending")` is true, add `"source": source or "quest_completion"` to the `pending_intrigue_target` dict. When effect resolves immediately (non-pending path): if `source == "green_room"`, return without calling `_advance_after_quest_rewards()` (keep `pending_placement` active so client transitions to quest selection); otherwise call `_advance_after_quest_rewards()` as before.

- [X] T004 [US1] Update intrigue target resolution handlers for green_room source in server/game_engine.py. In `handle_choose_intrigue_target()` (~line 4228): after resolving the target effect, check `pending.get("source") == "green_room"` — if so, skip `_check_quest_completion()` and return (keeping pending_placement for quest selection). In `handle_cancel_intrigue_target()` (~line 4374): if source is `"green_room"`, unwind placement via `_unwind_placement()`, clear `pending_intrigue_target` and `pending_placement`, broadcast `PlacementCancelledResponse`, and return.

- [X] T005 [US1] Update `handle_select_quest_card()` in server/game_engine.py to handle The Green Room. In the spot determination logic (~line 2170), add: `elif spot_special == "play_intrigue_and_quest": spot_num = 3` and `bonus_reward = {}` (no additional bonus — the intrigue effect was the reward). Ensure the post-selection flow calls `_check_quest_completion()` then `_advance_turn()` as normal.

- [X] T006 [US2] Add cancel support for green_room placement in server/game_engine.py. Verify or add logic so that when `pending_play_intrigue` has `source == "green_room"` and the player sends a `CancelPlacementRequest`, the handler: clears `pending_play_intrigue`, calls `_unwind_placement()` to reverse worker placement, broadcasts `PlacementCancelledResponse` with the `space_id`. Check existing cancel handlers (search for `CancelPlacementRequest` routing) and add the green_room case if not already covered.

- [X] T007 [US1] Verify reconnection support for green_room pending state in server/lobby.py. The existing reconnection logic (~line 590) already re-sends `IntriguePlayPromptResponse` when `pending_play_intrigue` is set. Verify this works with the new `"source": "green_room"` field — no code change should be needed, but confirm by reading the reconnection handler and testing.

- [X] T008 [P] [US1] Add server tests for The Green Room in tests/test_green_room.py. Test cases: (1) placement succeeds when player has intrigue cards, sets pending states correctly; (2) placement rejected with error when player has no intrigue cards; (3) intrigue play resolves and transitions to quest selection (pending_placement stays active); (4) quest selection after intrigue play completes the turn correctly; (5) cancel before intrigue play unwinds placement; (6) targeted intrigue effect chains correctly (pending_intrigue_target with green_room source); (7) cancel during target selection unwinds placement.

**Checkpoint**: The Green Room is fully functional server-side. Players can place → play intrigue → select quest, or back out at any point before intrigue play. Tests pass.

---

## Phase 3: User Story 3 — The Green Room Card Appearance (Priority: P2)

**Goal**: Generate a card image for The Green Room that shows "Play" with an intrigue card icon plus a quest card icon, styled like "The Back Room."

**Independent Test**: Run card generator and visually verify the_green_room.png shows "Play [intrigue icon]" and a quest icon with blue band and correct layout.

### Implementation

- [X] T009 [P] [US3] Add `play_intrigue_and_quest` card generation case in card-generator/generate_cards.py. In `generate_space_cards()` (~line 1706 area), add an `elif special == "play_intrigue_and_quest":` block that draws: "Play" text followed by intrigue card icon (`_draw_intrigue_card_icon()`), then a quest card icon (`_draw_quest_card_icon()`) below or beside it. Use the same blue band color (50, 70, 100) as "The Back Room". Output to `client/assets/card_images/spaces/the_green_room.png`.

- [X] T010 [US3] Run the card generator script to produce the_green_room.png and visually verify the output matches the design (Play text + intrigue icon + quest icon, blue header band, "The Green Room" title).

**Checkpoint**: Card image generated and looks correct. Visually distinguishes "play intrigue" from "draw intrigue."

---

## Phase 4: User Story 4 — Board Layout Rearrangement (Priority: P2)

**Goal**: Rearrange the 9 permanent spaces into a 3x3 grid. Constructed buildings display below with pagination.

**Independent Test**: Load a game and verify all 9 permanent spaces render in 3 columns x 3 rows, constructed buildings appear below, pagination works.

### Implementation

- [X] T011 [P] [US4] Update `_GRID_PLACEMENT` dict in client/ui/board_renderer.py to arrange 9 permanent spaces in a 3x3 grid. Map: merch_store (0,0), motown (1,0), guitar_center (2,0), talent_show (0,1), rhythm_pit (1,1), jam_session (2,1), whisper_room (0,2), vip_entrance (1,2), the_green_room (2,2). Keep garage, backstage, and realtor positions unchanged or adjusted to avoid overlap.

- [X] T012 [US4] Reposition constructed buildings below the 3x3 grid in client/ui/board_renderer.py. Update the building rendering loop (~line 530-561) to place buildings starting at row 3 (below the permanent spaces grid), using 3 columns (0-2) instead of the current 2 columns (1-2). Update `_BUILDINGS_PER_PAGE` if the new layout fits more or fewer buildings per page. Update the column/row calculation: `col = j % 3`, `row = 3 + (j // 3) * 2`.

- [X] T013 [US4] Update worker/marker positioning for the new 3x3 layout in client/ui/board_renderer.py. The `_update_workers()` method (~line 649) reads from `_GRID_PLACEMENT` so marker positions should follow automatically, but verify that the token_offset calculations work correctly for the wider grid. Also verify `get_space_position()` returns correct pixel coordinates for the new positions.

- [X] T014 [US4] Verify face-up quest and building card positions in client/ui/board_renderer.py. Ensure `get_quest_card_info()` and `get_building_card_info()` return correct positions that don't overlap with the new 3x3 grid or repositioned buildings. Adjust if needed.

**Checkpoint**: Board displays 9 permanent spaces in 3x3 grid. Buildings paginate correctly below. No overlapping sprites.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation, testing, cleanup

- [X] T015 Run full test suite and linting: `cd src && pytest && ruff check .` — fix any failures or lint errors introduced by this feature.
- [X] T016 Visual end-to-end test: start server and client, place worker on The Green Room, play an intrigue card (verify animation plays), select a quest card (verify animation plays), confirm turn advances correctly. Test cancel path. Test with no intrigue cards.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1+US2 (Phase 2)**: Depends on Phase 1 (board.json config)
- **US3 (Phase 3)**: Depends on Phase 1 only — can run in parallel with Phase 2
- **US4 (Phase 4)**: Depends on Phase 1 only — can run in parallel with Phase 2 and Phase 3
- **Polish (Phase 5)**: Depends on all prior phases

### User Story Dependencies

- **US1+US2 (P1)**: Can start after Phase 1 — no dependencies on US3 or US4
- **US3 (P2)**: Can start after Phase 1 — independent of server logic
- **US4 (P2)**: Can start after Phase 1 — independent of server logic and card generation

### Within Each User Story

- T002 before T003 (routing before chaining)
- T003 before T004 (intrigue play before target resolution)
- T005 can run in parallel with T003/T004 (different function)
- T006 after T002 (cancel needs placement handler)
- T007 after T002 (verify after handler exists)
- T008 can start in parallel (test file is independent)

### Parallel Opportunities

```
After Phase 1 completes, three independent tracks can run simultaneously:

Track A (Server): T002 → T003 → T004 → T005 → T006 → T007
Track B (Card):   T009 → T010
Track C (Layout): T011 → T012 → T013 → T014
Track D (Tests):  T008 (parallel, but validate after Track A)
```

---

## Parallel Example: Phase 2 (US1+US2)

```
# These can run in parallel (different functions/files):
T005: Update handle_select_quest_card() for play_intrigue_and_quest spot
T008: Add server tests for The Green Room in tests/test_green_room.py

# These run after Phase 1 completes (parallel tracks):
T009: Card image generation (card-generator/generate_cards.py)
T011: Board layout update (client/ui/board_renderer.py)
```

---

## Implementation Strategy

### MVP First (US1+US2 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: US1+US2 server logic (T002–T008)
3. **STOP and VALIDATE**: Test The Green Room server-side with existing card placeholder
4. The space is fully playable even without the custom card image or layout changes

### Incremental Delivery

1. Phase 1 → Config ready
2. Phase 2 (US1+US2) → Core gameplay works (MVP)
3. Phase 3 (US3) → Card looks correct
4. Phase 4 (US4) → Board layout rearranged
5. Phase 5 → Polish and final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 are combined because the cancel logic (US2) is implemented in the same handler functions as the placement logic (US1)
- The server logic reuses existing flows: `pending_play_intrigue`, `_resolve_intrigue_effect()`, `handle_select_quest_card()` — no new message types
- Commit after each task or logical group
- Constitution compliance verified in plan.md (all 10 principles pass)
