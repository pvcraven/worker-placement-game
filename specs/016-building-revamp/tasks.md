# Tasks: Building Revamp

**Input**: Design documents from `specs/016-building-revamp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Run and report existing tests before any changes

- [X] T001 Run existing tests with `python -m pytest tests/ -v` and `ruff check .` from project root. Report results. Do NOT modify any tests.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend data models and config to support all new building mechanics. MUST complete before any user story work.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Extend `BuildingTile` in `shared/card_models.py` with new fields: `accumulation_type: str | None = None`, `accumulation_per_round: int = 0`, `accumulation_initial: int = 0`, `accumulated_stock: int = 0`, `visitor_reward_vp: int = 0`, `owner_bonus_vp: int = 0`, `owner_bonus_choice: ResourceChoiceReward | None = None`. All fields must have defaults so existing code is unaffected.
- [X] T003 Update building validation in `server/config_loader.py` to accept and validate the new BuildingTile fields: if `accumulation_type` is set then `accumulation_per_round` must be > 0; if null then both `accumulation_per_round` and `accumulation_initial` must be 0; `visitor_reward_vp` and `owner_bonus_vp` must be >= 0; `cost_coins` range should allow 3-8.
- [X] T004 Write new `config/buildings.json` replacing all 28 existing buildings with 20 new buildings per spec. Reuse existing building names from current buildings.json where thematically fitting, assign new music-venue names for remainder. All 20 buildings must have correct IDs (building_001 through building_020), costs, visitor_reward, owner_bonus, specials, choices, accumulation fields, and VP fields as defined in spec Categories A-E.
- [X] T005 Run tests again with `python -m pytest tests/ -v` and `ruff check .` to verify foundational changes don't break anything. Report results.

**Checkpoint**: Models extended, config validated, 20 new buildings defined. All existing tests pass.

---

## Phase 3: User Story 1 - Accumulating Resource Buildings (Priority: P1)

**Goal**: Buildings that stock resources each round until a visitor collects them. 6 accumulating buildings (Category A).

**Independent Test**: Purchase an accumulating building, advance rounds without visiting, visit it, verify accumulated resources are received and stock resets to zero.

### Implementation for User Story 1

- [X] T006 [US1] In `server/game_engine.py` `_end_round()`, after the existing face-up building VP increment (line ~328), add a loop over all constructed buildings (`state.board.constructed_buildings`) that have `accumulation_type` set. For each, increment `building_tile.accumulated_stock` by `building_tile.accumulation_per_round`. Access constructed buildings via `state.board.action_spaces[space_id].building_tile`.
- [X] T007 [US1] In `server/game_engine.py` `handle_place_worker()`, after granting `space.reward` (line ~783), check if `space.building_tile` has `accumulation_type` set. If so, grant the `accumulated_stock` to the visitor: if `accumulation_type` is a resource key (guitarists, bass_players, etc.), add that many of that resource to `player.resources`; if `accumulation_type` is "victory_points", add to `player.victory_points`. Then reset `space.building_tile.accumulated_stock = 0`. Include this info in the reward broadcast.
- [X] T008 [US1] In `server/game_engine.py` `handle_purchase_building()` (line ~1821), after creating the building ActionSpace, set `tile.accumulated_stock = tile.accumulation_initial` for accumulating buildings. This ensures purchased buildings start with their initial stock.
- [X] T009 [US1] In `server/game_engine.py` `_assign_building_to_player()` (line ~94), ensure that when a building is assigned via non-purchase means (e.g., quest reward calling `_grant_free_building`), `accumulated_stock` remains at its default of 0 (do NOT set it to `accumulation_initial`). Verify the existing flow already leaves it at 0 since the Pydantic default is 0.
- [X] T010 [US1] In `client/ui/board_renderer.py`, add display of accumulated stock on constructed accumulating buildings. After drawing each constructed building sprite, if the building has `accumulation_type` set and `accumulated_stock > 0`, draw a small text badge (using cached `arcade.Text`) showing the stock count. The accumulated stock data must be included in the building market broadcast — update `_broadcast_building_market` in `server/game_engine.py` and the `WorkerPlacedResponse` to include constructed building state if needed.
- [X] T011 [US1] Write test in `tests/test_buildings.py`: test that accumulated_stock increments correctly at round start, resets to 0 on visit, and starts at accumulation_initial on purchase. Test that free building acquisition starts at 0.

**Checkpoint**: Accumulating buildings fully functional. Stock grows each round, resets on visit, displays on board.

---

## Phase 4: User Story 2 - Standard Reward Buildings (Priority: P2)

**Goal**: Buildings with straightforward resource rewards including draw_contract and draw_intrigue specials. Buildings B1-B3 and related standard buildings.

**Independent Test**: Purchase a standard building, visit it, verify correct resources and special rewards (quest pick, intrigue draw) are granted.

### Implementation for User Story 2

- [X] T012 [US2] In `server/game_engine.py` `handle_place_worker()`, add processing for `visitor_reward_special` on building spaces. After granting `space.reward` and before owner bonus, check `space.building_tile.visitor_reward_special`: if `"draw_contract"`, prompt the player to pick one face-up quest card (reuse the quest selection flow from garage handling but for a single pick); if `"draw_intrigue"`, draw the top intrigue card from `state.board.intrigue_deck` and add to `player.intrigue_hand`, then broadcast the update.
- [X] T013 [US2] Verify buildings B1 (1 singer + draw_contract, owner: 2 coins), B2 (1 drummer + draw_intrigue, owner: 1 intrigue card), and B3 (2 bassists + 2 coins, owner: 1 bassist) work correctly by manual testing or adding tests in `tests/test_buildings.py`.

**Checkpoint**: Standard buildings grant correct resources and specials. draw_contract and draw_intrigue work on buildings.

---

## Phase 5: User Story 3 - Resource Choice Buildings (Priority: P3)

**Goal**: Buildings where visitors choose resources: pick from allowed types, spend coins to get choices. Buildings B5, B6, C1, C2, E2.

**Independent Test**: Visit a choice building, make a selection, verify correct resources granted.

### Implementation for User Story 3

- [X] T014 [US3] Verify that buildings B5 (pick 1 of G/B/S/D + 2 coins), B6 (1 guitarist + pick 1 of G/B/D/S), C1 (spend 2 coins, combo 2 from singers/drummers), C2 (spend 4 coins, combo 4 from singers/drummers), and E2 (pick any 2, owner picks any 1) have correct `visitor_reward_choice` configurations in `config/buildings.json`. The existing choice types ("pick", "combo") and affordability checks in game_engine.py should handle these without code changes.
- [X] T015 [US3] For building E2 (pick any 2 resources, owner picks any 1 resource), the owner's pick requires `owner_bonus_choice` handling which depends on US4. Mark E2's owner choice as dependent on Phase 6. The visitor side (pick any 2) works with existing "pick" choice_type.

**Checkpoint**: Visitor-side resource choices work for all choice buildings. Owner choice on E2 deferred to US4.

---

## Phase 6: User Story 4 - Multi-Resource Buildings with Owner Choice (Priority: P4)

**Goal**: Owner receives a choice prompt when another player visits their building. Buildings B4, D1-D4, E2 owner side.

**Independent Test**: Player A owns building, Player B visits, Player A gets prompted to choose between two resource types.

### Implementation for User Story 4

- [X] T016 [US4] In `server/game_engine.py` `handle_place_worker()`, in the owner bonus section (line ~828), after granting `owner_bonus` resources, check if `space.building_tile.owner_bonus_choice` is not None. If so, send a `ResourceChoicePrompt` to the building OWNER (not the visitor). Set `state.pending_resource_choice` to track that the owner is making a choice. The choice uses existing `ResourceChoiceReward` with `choice_type="pick"`, `pick_count=1`, and the allowed types from the building config.
- [X] T017 [US4] In `server/game_engine.py` resource choice response handler (`handle_resource_choice_response`), handle the case where the choice was for an owner bonus. The response should grant the chosen resource to the building owner (not the current turn player). After granting, continue normal flow (check quest completion, advance turn).
- [X] T018 [US4] Verify buildings B4 (owner choice G or B), D1 (owner choice G or S), D2 (owner choice B or D), D3 (owner choice B or S), D4 (owner choice G or D), and E2 (owner picks any 1) have correct `owner_bonus_choice` in `config/buildings.json` and that the owner choice prompt appears correctly.

**Checkpoint**: Owner bonus choices work for all buildings that have them. Owner gets prompted, selects, receives correct resource.

---

## Phase 7: User Story 5 - Exchange Buildings (Priority: P5)

**Goal**: Building E1 where visitor returns 2 resources and picks 3. Rebalance of existing Talent Agency pattern.

**Independent Test**: Visit exchange building, return 2 resources, pick 3, verify transaction.

### Implementation for User Story 5

- [X] T019 [US5] Verify building E1 (return any 2, pick any 3, owner gets 2 coins) has correct `visitor_reward_choice` with `choice_type="exchange"`, `pick_count=2`, `gain_count=3`, `allowed_types=["guitarists","bass_players","drummers","singers"]` in `config/buildings.json`. The existing exchange handling in game_engine.py should process this without code changes — the exchange flow was fixed in a previous feature.

**Checkpoint**: Exchange building works correctly with existing exchange mechanic.

---

## Phase 8: User Story 6 - VP-Awarding Buildings (Priority: P6)

**Goal**: Buildings that grant VP as visitor reward or owner bonus. VP accumulation building (A4 owner gets 2 VP, A6 accumulates VP, B5 owner gets 2 VP).

**Independent Test**: Visit a VP-granting building, verify player VP total increases.

### Implementation for User Story 6

- [X] T020 [US6] In `server/game_engine.py` `handle_place_worker()`, after granting `space.reward` and handling accumulation, check `space.building_tile.visitor_reward_vp`. If > 0, add that amount to `player.victory_points`. Include VP in the reward broadcast.
- [X] T021 [US6] In `server/game_engine.py` owner bonus section, after granting `owner_bonus` resources, check `space.building_tile.owner_bonus_vp`. If > 0, add that amount to `owner.victory_points`. Include VP in the owner bonus broadcast.
- [X] T022 [US6] Verify that the accumulating VP building (A6) correctly accumulates "victory_points" type, grants accumulated VP to visitor, and also triggers `visitor_reward_special: "draw_contract"` for quest picking. The A6 building in config must have both `accumulation_type: "victory_points"` and `visitor_reward_special: "draw_contract"`.
- [X] T023 [US6] Write test in `tests/test_buildings.py`: test that VP owner bonus and visitor VP rewards are correctly added to player.victory_points.

**Checkpoint**: VP rewards work for all buildings. VP appears in player totals and final score screen.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Card images, final validation, cleanup

- [X] T024 [P] Update `card-generator/generate_cards.py` to generate PNG card images for all 20 new buildings. Remove old building images from `client/assets/card_images/buildings/` directory. Run the generator to produce new images.
- [X] T025 [P] Run full test suite with `python -m pytest tests/ -v && ruff check .` and report results. Verify existing contract card tests still pass, new building tests pass, no ruff violations.
- [ ] T026 Run the game manually (server + client) and test at least one building from each category (A, B, C, D, E) to verify end-to-end functionality. Verify accumulation display, owner choice prompt, VP awards, and draw_contract/draw_intrigue work in actual gameplay.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — run immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 Accumulating (Phase 3)**: Depends on Phase 2 — core mechanic
- **US2 Standard (Phase 4)**: Depends on Phase 2 — needs visitor_reward_special
- **US3 Choice (Phase 5)**: Depends on Phase 2 — mostly config, existing mechanics
- **US4 Owner Choice (Phase 6)**: Depends on Phase 2 — new server logic
- **US5 Exchange (Phase 7)**: Depends on Phase 2 — existing exchange mechanic
- **US6 VP Awards (Phase 8)**: Depends on Phase 2 — new VP handling
- **Polish (Phase 9)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Foundational only — no cross-story dependencies
- **US2 (P2)**: Foundational only — no cross-story dependencies
- **US3 (P3)**: E2 owner choice depends on US4 (owner_bonus_choice implementation)
- **US4 (P4)**: Foundational only — no cross-story dependencies
- **US5 (P5)**: Foundational only — no cross-story dependencies
- **US6 (P6)**: Accumulation VP depends on US1 (accumulation mechanic). draw_contract depends on US2 (visitor_reward_special)

### Within Each User Story

- Config (buildings.json) before server logic
- Server logic before client rendering
- Core implementation before tests

### Parallel Opportunities

- After Phase 2 completes, US1-US5 can proceed in parallel (different code paths)
- US6 should follow US1 and US2 since it depends on accumulation and visitor_reward_special
- T024 (card images) can run in parallel with any user story work
- T025 (test suite) can run in parallel with T024

---

## Parallel Example: After Foundational Phase

```text
# These can run in parallel after Phase 2:
US1: T006-T011 (accumulation mechanic in game_engine.py)
US2: T012-T013 (visitor_reward_special in game_engine.py)
US4: T016-T018 (owner choice in game_engine.py)
US5: T019 (exchange config verification)

# After US1 and US2 complete:
US6: T020-T023 (VP rewards, depends on accumulation + visitor_reward_special)

# After US4 completes:
US3: T015 (E2 owner choice side)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Report existing test results
2. Complete Phase 2: Extend models, write new buildings.json
3. Complete Phase 3: Accumulating buildings work end-to-end
4. **STOP and VALIDATE**: Test accumulation mechanic independently
5. Continue with remaining stories

### Incremental Delivery

1. Phase 2 → Foundation ready (all 20 buildings loadable)
2. Add US1 → Accumulation works → Test
3. Add US2 → Standard specials work → Test
4. Add US4 → Owner choices work → Test
5. Add US3/US5 → Choice/exchange config verified → Test
6. Add US6 → VP rewards work → Test
7. Phase 9 → Card images generated, final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Existing tests (test_cards.py) test contracts not buildings — they should pass unchanged
- Buildings.json is a full replacement: 28 old → 20 new
- visitor_reward_special (draw_contract/draw_intrigue) exists in data model but was never implemented in game logic — US2 implements it
- Owner bonus choice is a NEW mechanic — US4 implements it
- VP as building reward is NEW — US6 implements it
