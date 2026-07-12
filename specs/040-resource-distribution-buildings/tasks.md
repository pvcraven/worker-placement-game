# Tasks: Resource Distribution Buildings

**Input**: Design documents from `/specs/040-resource-distribution-buildings/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/messages.md, quickstart.md

**Tests**: Included — server-side game logic requires automated test coverage per Constitution IV.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Data Model, Messages, Config)

**Purpose**: Add all shared data model fields, message types, and building config entries that every user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T001 [P] Add `distribute_resource_type` (str | None), `distribute_per_space` (int, default 0), and `distribute_space_count` (int, default 0) fields to the BuildingTile model in shared/card_models.py
- [x] T002 [P] Add `placed_resources: dict[str, int]` field (default empty dict) to ActionSpace model in server/models/game.py
- [x] T003 [P] Add `pending_resource_distribution: dict | None` field (default None) to GameState model in server/models/game.py
- [x] T004 [P] Add three new message types to shared/messages.py: `ResourceDistributionPromptResponse` (action: "resource_distribution_prompt", fields: player_id, resource_type, per_space, remaining_selections, eligible_spaces, selected_spaces), `ResourceDistributionRequest` (action: "resource_distribution_select", fields: space_id), and `ResourceDistributionResolvedResponse` (action: "resource_distribution_resolved", fields: space_id, resource_type, quantity, all_placed_resources). Also add `collected_placed_resources: dict | None` field to WorkerPlacedResponse.
- [x] T005 Add 5 new building entries to config/buildings.json: building_024 (guitarist distribution, 7 coins, visitor: 4 guitarists, distribute: 1 guitarist on 2 spaces, owner: 2 guitarists), building_025 (coin distribution, 7 coins, visitor: 8 coins, distribute: 2 coins on 2 spaces, owner: 4 coins), building_026 (singer distribution, 7 coins, visitor: 2 singers, distribute: 1 singer on 1 space, owner: 1 singer), building_027 (bass player distribution, 7 coins, visitor: 4 bass_players, distribute: 1 bass_player on 2 spaces, owner: 2 bass_players), building_028 (drummer distribution, 7 coins, visitor: 2 drummers, distribute: 1 drummer on 1 space, owner: 1 drummer). Use placeholder names (TBD music-themed names). Include distribute_resource_type, distribute_per_space, distribute_space_count fields on each.

**Checkpoint**: Data model, messages, and config are ready. All user stories can now proceed.

---

## Phase 2: User Story 2 - Collect Placed Resources (Priority: P1) 🎯 MVP

**Goal**: When a player visits any action space that has placed resources, they automatically receive all placed resources in addition to the space's normal reward. Placed resources are cleared after collection. This is separate from accumulated stock.

**Independent Test**: Pre-set placed_resources on a space in a test, visit the space, verify the visitor receives the placed resources and the space is cleared.

### Tests for User Story 2

- [x] T006 [P] [US2] Write test in tests/ for placed resource collection: test that visiting a space with placed_resources grants those resources to the visitor, clears placed_resources, and does NOT affect accumulated_stock. Test multiple resource types stacking. Test that placed_resources persist across rounds (not cleared at round end).

### Implementation for User Story 2

- [x] T007 [US2] In server/game_engine.py handle_place_worker(), after accumulated stock collection (around line 1661-1676), add logic to check the action space's placed_resources dict. If non-empty, add each resource type/quantity to the visiting player's resources, then clear placed_resources to empty dict. Include the collected resources in the WorkerPlacedResponse as collected_placed_resources.
- [x] T008 [US2] In server/game_engine.py, verify that the round-end logic (around line 560-570) does NOT clear placed_resources — only accumulated_stock gets replenished. Placed resources must persist across rounds.
- [x] T009 [P] [US2] In client/views/game_view.py, handle the new `collected_placed_resources` field in WorkerPlacedResponse. Update the local game state to clear placed_resources from the visited space. Display the collected resources to the player (can reuse existing resource grant display logic).

**Checkpoint**: Players can collect placed resources from any action space. The collection mechanic works end-to-end.

---

## Phase 3: User Story 1 - Visit a Resource Distribution Building (Priority: P1)

**Goal**: When a player visits a distribution building, they receive visitor rewards, owner gets bonus, and then the building owner (or visitor if unowned) is prompted to select target action spaces where additional resources are placed from the supply.

**Independent Test**: Visit a distribution building, verify visitor rewards are granted, owner is prompted for space selection, resources appear on selected spaces.

**Depends on**: US2 (collection mechanic must work for placed resources to be meaningful)

### Tests for User Story 1

- [x] T010 [P] [US1] Write test in tests/ for distribution building visit flow: test that visiting a distribution building grants visitor_reward, triggers pending_resource_distribution state with correct fields (player_id, building_space_id, resource_type, per_space, remaining_selections, selected_spaces). Test owner vs visitor selection (owner selects if owned, visitor selects if unowned).

- [x] T011 [P] [US1] Write test in tests/ for resource distribution selection: test that selecting a valid space places the correct resources on that space, decrements remaining_selections, and after all selections are made clears pending_resource_distribution and advances the turn. Test that selecting the building being visited is rejected. Test that selecting an already-selected space is rejected. Test that each distributed resource goes to a different space.

### Implementation for User Story 1

- [x] T012 [US1] In server/game_engine.py handle_place_worker(), after processing building tile rewards, detect distribution buildings by checking `building_tile.distribute_resource_type is not None`. When detected, create `pending_resource_distribution` dict on game state with fields: player_id (owner if owned, visitor if not), building_space_id (the visited space), resource_type, per_space, remaining_selections (= distribute_space_count), selected_spaces (empty list). Do NOT advance the turn yet — the distribution phase must complete first.

- [x] T013 [US1] In server/game_engine.py, add a new handler for ResourceDistributionRequest messages. Validate: pending_resource_distribution is active, requesting player matches pending player_id, space_id is valid (exists, not the building being visited, not already in selected_spaces). On valid selection: add per_space quantity of resource_type to the target space's placed_resources dict, add space_id to selected_spaces, decrement remaining_selections. Broadcast ResourceDistributionResolvedResponse.

- [x] T014 [US1] In server/game_engine.py distribution handler, after a valid selection: if remaining_selections > 0, send another ResourceDistributionPromptResponse with updated eligible_spaces (excluding visited building and already-selected spaces). If remaining_selections == 0, clear pending_resource_distribution and proceed with standard post-action turn flow (check quest completion, advance turn).

- [x] T015 [US1] In server/game_engine.py, build the eligible_spaces list for ResourceDistributionPromptResponse: include all action spaces on the board (permanent spaces + constructed buildings) EXCEPT the building being visited and any spaces already in selected_spaces. Send as list of {space_id, name} dicts.

- [x] T016 [US1] In server/network.py, register the new "resource_distribution_select" action in the message dispatch to route to the new handler in game_engine.py.

- [x] T017 [US1] In client/views/game_view.py, handle ResourceDistributionPromptResponse: store the distribution state (eligible spaces, resource type, remaining selections). Handle ResourceDistributionResolvedResponse: update the local board state to add placed_resources to the target space.

**Checkpoint**: The full distribution flow works: visit building → owner selects spaces → resources placed → turn advances.

---

## Phase 4: User Story 4 - Owner Selects Target Spaces (Priority: P2)

**Goal**: The building owner is presented with a selection interface showing eligible action spaces. They pick the required number of distinct spaces via UI interaction.

**Independent Test**: After a distribution building visit, verify the owner sees selectable spaces and can click to choose them.

**Depends on**: US1 (the server-side distribution flow must be in place)

### Implementation for User Story 4

- [x] T018 [US4] In client/views/game_view.py, when a ResourceDistributionPromptResponse is received and this player is the selecting player, present a selection UI. This should highlight eligible spaces on the board and allow the player to click on a space to select it. On click, send ResourceDistributionRequest with the selected space_id.

- [x] T019 [US4] In client/views/game_view.py, add visual feedback during selection: highlight eligible spaces (e.g., glow or border), show what resource will be placed and how many selections remain. After each selection is confirmed (ResourceDistributionResolvedResponse), update the UI to reflect the placed resources and remaining selections.

- [x] T020 [US4] In client/views/game_view.py, handle the case where the selecting player is not the current active player (owner is a different player). Ensure the non-active player can interact with the selection UI while other players wait.

**Checkpoint**: The selection UI works — owners can click on board spaces to place resources.

---

## Phase 5: User Story 3 - Visual Display of Placed Resources (Priority: P1)

**Goal**: Resource icons are rendered on action spaces that have placed resources, positioned below the worker token area. All players can see them.

**Independent Test**: Place resources on a space via the distribution flow, verify colored resource icons appear on that space's card on the board.

**Depends on**: US2 (client state tracking for placed_resources)

### Implementation for User Story 3

- [x] T021 [US3] In client/ui/board_renderer.py, add a method to render placed resource icons on action spaces. For each action space with non-empty placed_resources, draw colored squares (matching the existing resource color scheme: orange=guitarists, black=bass_players, purple=drummers, white=singers, gold=coins) below the worker token area. Use ShapeElementList for the squares and arcade.Text for count labels. Show count next to each resource type icon (e.g., "x2" if quantity > 1).

- [x] T022 [US3] In client/ui/board_renderer.py, call the placed resource rendering method for both permanent board spaces and constructed buildings. Ensure placed resources display correctly on any space type. Position icons below the worker marker area, stacking vertically if multiple resource types exist on the same space.

- [x] T023 [US3] In client/views/game_view.py, ensure the local board state tracks placed_resources for all spaces. When ResourceDistributionResolvedResponse is received, update placed_resources on the target space. When WorkerPlacedResponse is received with collected_placed_resources, clear placed_resources from the visited space.

**Checkpoint**: Placed resources are visible on the board. Players can see which spaces have bonus resources.

---

## Phase 6: User Story 5 - Five Themed Resource Distribution Buildings (Priority: P2)

**Goal**: Generate card images for the 5 new distribution buildings with correct visual layout including a "Place:" text line with resource icons.

**Independent Test**: Run the card generator, verify 5 new building PNGs are created with correct cost, visitor reward, "Place:" line, and owner bonus sections.

### Implementation for User Story 5

- [x] T024 [US5] In card-generator/generate_cards.py, add support for the distribute fields when generating building card images. After the visitor reward section, add a "Place:" line that shows the resource icon and distribution pattern (e.g., "Place: [orange square] on 2 spaces" for UN-1). Use the existing _draw_reward_line() pattern and resource symbol drawing functions.

- [x] T025 [US5] Choose music-themed names for the 5 buildings and update config/buildings.json with final names and descriptions. Update the building table in spec.md accordingly.

- [x] T026 [US5] Run the card image generator to produce PNG files for building_024 through building_028 in client/assets/card_images/buildings/. Verify each card shows: cost diamond (7 coins), building name, visitor reward with resource icons, "Place:" line with distribution info, and owner bonus.

**Checkpoint**: All 5 distribution building cards are generated and display correctly in the building market.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, edge case handling, and test suite completion.

- [x] T027 Write tests for edge cases: distribution when fewer eligible spaces exist than required (resources forfeited), stacking placed resources from multiple visits, placed resources on accumulation buildings (separate pools), owner disconnection during selection (timeout handling).
- [x] T028 Add cancel/unwind support for the distribution phase: if the player's placement is cancelled (via existing cancel flow), any resources already placed during the current distribution phase must be removed from target spaces. Update pending_placement to track distribution side effects.
- [x] T029 Run full test suite: `cd src && pytest && ruff check .` — fix any failures or lint issues.
- [ ] T030 Manual integration test: start server + client, purchase a distribution building, visit it, complete space selection, verify resources appear on spaces, visit a space with placed resources, verify collection works and icons clear.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies — start immediately
- **US2 Collection (Phase 2)**: Depends on Phase 1 completion
- **US1 Distribution (Phase 3)**: Depends on Phase 1 + Phase 2
- **US4 Selection UI (Phase 4)**: Depends on Phase 3 (server flow)
- **US3 Visual Display (Phase 5)**: Depends on Phase 2 (client state tracking) — can run in parallel with Phase 3/4
- **US5 Building Content (Phase 6)**: Depends on Phase 1 (config entries) — can run in parallel with Phases 2-5
- **Polish (Phase 7)**: Depends on all prior phases

### User Story Dependencies

- **US2 (Collection)**: Foundation only — independently testable with manually set placed_resources
- **US1 (Distribution)**: Depends on US2 (placed resources must be collectible to validate the flow)
- **US3 (Visual Display)**: Depends on US2 client state — can parallelize with US1/US4
- **US4 (Selection UI)**: Depends on US1 (server-side distribution flow)
- **US5 (Building Content)**: Independent — only needs foundation config entries

### Within Each User Story

- Tests written first (where included)
- Model/data changes before logic
- Server before client
- Core implementation before integration

### Parallel Opportunities

- T001, T002, T003, T004 can all run in parallel (different files)
- T006 and T009 can run in parallel (different files: tests/ and client/)
- T010, T011 can run in parallel (different test files)
- US3 (Phase 5) can run in parallel with US4 (Phase 4)
- US5 (Phase 6) can run in parallel with US1-US4 (Phases 2-5)

---

## Parallel Example: Phase 1 (Foundational)

```
All run in parallel (different files):
  T001: shared/card_models.py — BuildingTile distribute fields
  T002: server/models/game.py — ActionSpace.placed_resources
  T003: server/models/game.py — GameState.pending_resource_distribution
  T004: shared/messages.py — New message types
```

Note: T002 and T003 modify the same file but different models — can be done sequentially as one task or split.

---

## Implementation Strategy

### MVP First (US2 + US1 = Collection + Distribution)

1. Complete Phase 1: Foundational
2. Complete Phase 2: US2 (Collection) — test with manually placed resources
3. Complete Phase 3: US1 (Distribution flow) — now the full cycle works server-side
4. **STOP and VALIDATE**: Test the distribution → collection cycle via server tests
5. Continue with US4 (Selection UI) + US3 (Visual Display) in parallel

### Incremental Delivery

1. Foundation → model/config ready
2. US2 (Collection) → players can collect from spaces with placed resources
3. US1 (Distribution) → full server-side flow works
4. US4 + US3 in parallel → UI for selection + visual display of placed resources
5. US5 (Building Content) → card images for the 5 buildings
6. Polish → edge cases, cancel flow, final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Building names are TBD — use placeholder names initially, finalize in US5
- The distribution flow mirrors existing patterns: pending state → prompt → request → resolve → advance turn
- Resource icons use programmatic colored squares (not separate PNG assets)
- Commit after each task or logical group
