# Tasks: Building Purchase System

**Input**: Design documents from `/specs/003-building-purchase/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Configuration changes and rename that affect multiple downstream tasks

- [ ] T001 Rename builders_hall to real_estate_listings in config/board.json (space_id, name, space_type)
- [ ] T002 [P] Add accumulated_vp field (int, default 0) to BuildingTile model in shared/card_models.py
- [ ] T003 [P] Add FACE_UP_BUILDING_COUNT = 3 constant to shared/constants.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared model and server changes that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Replace building_supply with building_deck (list[BuildingTile]) and face_up_buildings (list[BuildingTile]) in BoardState model in server/models/game.py
- [ ] T005 Add BuildingMarketUpdate message type (action="building_market_update", face_up_buildings list, deck_remaining int) to shared/messages.py
- [ ] T006 Modify PurchaseBuildingRequest in shared/messages.py — remove lot_index field (server auto-assigns)
- [ ] T007 Update _initialize_game in server/lobby.py — shuffle buildings into building_deck, draw 3 to face_up_buildings with accumulated_vp=1, remove old building_supply setup
- [ ] T008 Update _filter_state_for_player in server/lobby.py — hide building_deck contents (show count only), expose face_up_buildings fully
- [ ] T009 Update handle_purchase_building in server/game_engine.py — search face_up_buildings instead of building_supply, auto-assign next lot from building_lots, award accumulated_vp to buyer (player.victory_points += building.accumulated_vp), draw replacement from building_deck with accumulated_vp=1
- [ ] T010 Send BuildingMarketUpdate broadcast after purchase completes in server/game_engine.py
- [ ] T011 Add VP increment logic to _end_round in server/game_engine.py — iterate face_up_buildings, increment accumulated_vp by 1 on each, broadcast BuildingMarketUpdate
- [ ] T012 Send initial BuildingMarketUpdate to all clients after game start in server/lobby.py
- [ ] T013 Update all references from builders_hall to real_estate_listings in server/game_engine.py (space_type checks, reward_special handling)
- [ ] T014 Route building_market_update message type in server/network.py (if needed for server→client broadcast registration)

**Checkpoint**: Foundation ready — model changes, server logic, and message contracts are in place

---

## Phase 3: User Story 1 — Rearrange Permanent Spaces to Single Column (Priority: P1) MVP

**Goal**: All permanent action spaces display in a single left column with tighter spacing, freeing the second column for purchased buildings

**Independent Test**: Launch a new game and verify all permanent spaces appear in one column on the left, tightly packed, with the second column area empty

### Implementation for User Story 1

- [ ] T015 [US1] Update _SPACE_LAYOUT dict in client/ui/board_renderer.py — move all permanent spaces (merch_store, motown, guitar_center, talent_show, rhythm_pit, castle_waterdeep, real_estate_listings) to a single column at x≈0.08 with y positions from 0.88 down to 0.12 at ~0.10 increments
- [ ] T016 [US1] Update constructed buildings rendering in BoardRenderer.draw in client/ui/board_renderer.py — change building_start_x from 0.70 to 0.22 (the freed second column position), keep 5-row layout with overflow to x=0.36+

**Checkpoint**: Permanent spaces render in a single column, second column is free for buildings

---

## Phase 4: User Story 2 — Place Worker on Real Estate Listings and Purchase a Building (Priority: P1)

**Goal**: Player places worker on Real Estate Listings, sees face-up buildings with cost/VP/rewards, selects and purchases one, building appears on board in second column

**Independent Test**: Start a game, place worker on Real Estate Listings, select a building, confirm purchase. Verify: coins deducted, VP awarded, building appears on board, replacement drawn from deck

### Implementation for User Story 2

- [ ] T017 [US2] Create BuildingPurchaseDialog class in client/ui/dialogs.py — show up to 3 building cards with name, coin cost, accumulated VP, visitor reward, owner bonus; highlight affordable buildings, gray out unaffordable; confirm and cancel buttons
- [ ] T018 [US2] Handle BuildingMarketUpdate message in client/views/game_view.py — store face_up_buildings and deck_remaining in local state for rendering and dialog use
- [ ] T019 [US2] Render building market display on the board in client/ui/board_renderer.py — show the 3 face-up buildings with their VP badges somewhere visible (e.g., near Real Estate Listings or in a dedicated market area)
- [ ] T020 [US2] Trigger BuildingPurchaseDialog when worker is placed on real_estate_listings space in client/views/game_view.py — detect reward_special="purchase_building" after WorkerPlacedResponse, show dialog with current face_up_buildings and player's coin count
- [ ] T021 [US2] Handle dialog confirm in client/views/game_view.py — send PurchaseBuildingRequest with selected building_id to server
- [ ] T022 [US2] Handle dialog cancel in client/views/game_view.py — close dialog, no action taken
- [ ] T023 [US2] Handle BuildingConstructedResponse in client/views/game_view.py — update local board state, add new building to constructed_buildings, log purchase in game log
- [ ] T024 [US2] Display error message when player cannot afford selected building in client/ui/dialogs.py or client/views/game_view.py — show insufficient coins feedback
- [ ] T025 [US2] Handle empty market edge case — if no face_up_buildings exist when landing on Real Estate Listings, show informational message instead of purchase dialog

**Checkpoint**: Full purchase flow works end-to-end — select, confirm/cancel, coins deducted, VP awarded, building placed, market refreshed

---

## Phase 5: User Story 3 — Land on a Purchased Building as a Visitor (Priority: P2)

**Goal**: When a non-owner lands on a purchased building, visitor gets the building's reward and owner gets the owner bonus. Owner landing on own building gets visitor reward but no owner bonus.

**Independent Test**: Player A purchases a building. Player B places worker on it. Verify Player B gets visitor reward, Player A gets owner bonus. Then Player A lands on own building — verify visitor reward granted, no owner bonus.

### Implementation for User Story 3

- [ ] T026 [US3] Verify existing owner bonus logic in handle_place_worker (server/game_engine.py lines 317-320) works correctly with new building ActionSpace creation — the space_type must be "building" and building_tile must be set
- [ ] T027 [US3] Verify owner bonus logic in handle_reassign_worker (server/game_engine.py lines 1000-1004) works correctly with new building spaces
- [ ] T028 [US3] Add game log entry when owner bonus is triggered in server/game_engine.py — log which owner received what bonus from which visitor
- [ ] T029 [US3] Display owner bonus notification in client/views/game_view.py — when WorkerPlacedResponse indicates a building was visited, show a log entry for the owner bonus if applicable

**Checkpoint**: Visitor/owner reward mechanics work correctly for all purchased buildings

---

## Phase 6: User Story 4 — Building Specs Driven by JSON Configuration (Priority: P2)

**Goal**: All building data is loaded from buildings.json, rewards match config exactly, and cost range is validated

**Independent Test**: Modify a building's rewards in buildings.json, restart game, verify the change is reflected in the purchase dialog and when landing on the building

### Implementation for User Story 4

- [ ] T030 [US4] Add config validation for cost_coins range (3-8) in BuildingsConfig validator in server/models/config.py
- [ ] T031 [US4] Verify all 24 buildings in config/buildings.json have cost_coins in 3-8 range and owner_bonus total is less than visitor_reward total — fix any violations
- [ ] T032 [US4] Verify building rewards loaded from JSON match exactly what is granted on placement — trace from config load through to ActionSpace creation to reward granting in server/game_engine.py

**Checkpoint**: Building data is fully JSON-driven and validated on load

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and final validation

- [ ] T033 Handle edge case: all building lots occupied — disable purchase or show message in purchase dialog
- [ ] T034 Handle edge case: deck exhausted with fewer than 3 face-up buildings — ensure market renders correctly with 0-2 buildings
- [ ] T035 Verify round-end VP increment displays correctly in market — after round ends, face-up buildings should show updated VP values
- [ ] T036 Run manual quickstart.md validation — walk through the complete test flow documented in quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 Layout (Phase 3)**: Depends on Foundational — client-only changes
- **US2 Purchase Flow (Phase 4)**: Depends on Foundational — needs model + server changes in place
- **US3 Visitor/Owner (Phase 5)**: Depends on Foundational — existing logic, mostly verification
- **US4 JSON Config (Phase 6)**: Depends on Foundational — config validation
- **Polish (Phase 7)**: Depends on US1 + US2 minimum

### User Story Dependencies

- **US1 (Layout)**: Independent — client rendering only, no dependency on other stories
- **US2 (Purchase)**: Independent — can be tested with any layout, but visually benefits from US1
- **US3 (Visitor/Owner)**: Requires US2 — needs purchased buildings to exist on the board
- **US4 (JSON Config)**: Independent — config validation, can run anytime after Foundational

### Within Each User Story

- Models/config before server logic
- Server logic before client UI
- Core flow before edge cases

### Parallel Opportunities

- T002 and T003 can run in parallel (different files)
- US1 (Phase 3) and US2 (Phase 4) can proceed in parallel after Foundational
- US3 and US4 can proceed in parallel
- Within US2: T017 (dialog) and T018/T019 (market rendering) can proceed in parallel

---

## Parallel Example: User Story 2

```text
# These can run in parallel (different files):
T017: Create BuildingPurchaseDialog in client/ui/dialogs.py
T018: Handle BuildingMarketUpdate in client/views/game_view.py
T019: Render building market display in client/ui/board_renderer.py

# Then sequentially:
T020: Trigger dialog on real_estate_listings placement (depends on T017, T018)
T021: Handle dialog confirm (depends on T020)
T022: Handle dialog cancel (depends on T020)
T023: Handle BuildingConstructedResponse (depends on T018)
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup (rename, model field)
2. Complete Phase 2: Foundational (server logic, messages)
3. Complete Phase 3: US1 — Layout rearrangement
4. Complete Phase 4: US2 — Purchase flow
5. **STOP and VALIDATE**: Test purchase flow end-to-end
6. Buildings can be purchased and placed on the board

### Incremental Delivery

1. Setup + Foundational → Model and server ready
2. US1 (Layout) → Board looks correct, single column
3. US2 (Purchase) → Full purchase flow works (MVP!)
4. US3 (Visitor/Owner) → Buildings generate passive income
5. US4 (JSON Config) → Config validation hardened
6. Polish → Edge cases handled

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Existing server code (owner bonus, building placement) is largely functional — US3 is primarily verification
- The building_supply → building_deck + face_up_buildings migration is the most impactful foundational change
- Client changes are concentrated in 3 files: board_renderer.py, dialogs.py, game_view.py
