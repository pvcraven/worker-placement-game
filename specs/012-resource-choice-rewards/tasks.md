# Tasks: Resource Choice Rewards

**Input**: Design documents from `specs/012-resource-choice-rewards/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create test infrastructure for the feature

- [X] T001 Create test file skeleton with helper fixtures at tests/test_resource_choice.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models and message types that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add ResourceBundle and ResourceChoiceReward Pydantic models to shared/card_models.py — ResourceBundle has label (str) and resources (ResourceCost); ResourceChoiceReward has choice_type (str, one of "pick"/"bundle"/"combo"/"exchange"), allowed_types (list[str]), pick_count (int, default 1), total (int, default 0), bundles (list[ResourceBundle]), cost (ResourceCost), gain_count (int, default 0), others_pick_count (int, default 0). Add optional visitor_reward_choice (ResourceChoiceReward | None = None) field to BuildingTile. Add optional choice_reward (ResourceChoiceReward | None = None) field to IntrigueCard.
- [X] T003 [P] Add three new message types to shared/messages.py — ResourceChoicePromptResponse (server→client: prompt_id, player_id, choice_type, title, description, allowed_types, pick_count, total, bundles, is_spend), ResourceChoiceRequest (client→server: prompt_id, chosen_resources dict), ResourceChoiceResolvedResponse (server→client: player_id, chosen_resources, is_spend, source_description, next_player_id). Register all three in ClientMessage/ServerMessage unions.
- [X] T004 [P] Add pending_resource_choice (dict | None = None) field to GameState in server/models/game.py

**Checkpoint**: Foundation ready — all shared types and message protocol in place

---

## Phase 3: User Story 1 — Simple Resource Choice (Priority: P1) MVP

**Goal**: Player picks N resources from an allowed set when visiting a building. Covers "pick 1 of S/D/G/B + 2 coins" and "pick 2 non-coin resources" scenarios.

**Independent Test**: Place worker on a pick-mode building. Dialog appears with resource type buttons. Select one. Resource added to player total, fixed reward also granted.

- [X] T005 [US1] Write pytest tests for pick-mode resource choice validation and granting in tests/test_resource_choice.py — test valid pick (1 resource, type in allowed list), test valid multi-pick (2 resources), test reject wrong type, test reject wrong count, test fixed reward granted alongside choice, test cost deduction if configured
- [X] T006 [US1] Implement _send_resource_choice_prompt() helper in server/game_engine.py — builds ResourceChoicePromptResponse from a ResourceChoiceReward config and sends to the choosing player via WebSocket. Sets pending_resource_choice on GameState with prompt_id, player_id, choice config, source info, is_spend flag.
- [X] T007 [US1] Implement handle_resource_choice() in server/game_engine.py — dispatches on `resource_choice` client message. For pick mode: validates chosen_resources total equals pick_count, all types are in allowed_types, all values are positive ints. On valid: calls player.resources.add() with chosen ResourceCost, clears pending_resource_choice, broadcasts ResourceChoiceResolvedResponse, advances turn. On invalid: sends ErrorResponse, does not clear pending state.
- [X] T008 [US1] Integrate choice reward detection into handle_place_worker() in server/game_engine.py — after granting fixed visitor_reward, check if space has building_tile with visitor_reward_choice. If so: call _send_resource_choice_prompt() instead of advancing turn. Also integrate into worker reassignment flow in handle_reassign_worker(). Add `resource_choice` case to message dispatch in handle_message().
- [X] T009 [US1] Add ResourceChoiceDialog class with pick mode to client/ui/dialogs.py — constructor takes title, description, choice_type, allowed_types, pick_count, on_select callback, ui_manager. Pick mode renders one button per allowed type; each click adds 1 to a running selection dict. Shows running count label. When pick_count reached, auto-confirms and calls on_select(chosen_resources_dict). Include a reset button to clear current selections.
- [X] T010 [US1] Add resource_choice_prompt and resource_choice_resolved handlers to client/views/game_view.py — on resource_choice_prompt: if player_id matches local player, create and show ResourceChoiceDialog with data from prompt; on_select callback sends ResourceChoiceRequest via network. On resource_choice_resolved: update local player resources, update resource panel, add game log entry, advance local turn state if next_player_id provided.
- [X] T011 [P] [US1] Add 2 pick-mode buildings to config/buildings.json — building_025 "Musician's Union Hall" (cost 4, visitor_reward: {coins: 2}, visitor_reward_choice: {choice_type: "pick", allowed_types: ["guitarists","bass_players","drummers","singers"], pick_count: 1}, owner_bonus: {coins: 1}) and building_026 "Open Audition Stage" (cost 5, visitor_reward_choice: {choice_type: "pick", allowed_types: ["guitarists","bass_players","drummers","singers"], pick_count: 2}, owner_bonus: {coins: 1})
- [X] T012 [US1] Update card image generator to display choice rewards on building cards in card-generator/generate_cards.py — when a building has visitor_reward_choice, render choice description text (e.g., "Pick 1: G/B/D/S + 2$") instead of fixed reward amounts. Handle all choice_types: pick shows "Pick N: types", bundle shows "Choose 1 of:", combo shows "Combo N: types", exchange shows "Trade N → M".

**Checkpoint**: Pick-mode buildings work end-to-end. Player visits building, sees choice dialog, picks resources, resources granted.

---

## Phase 4: User Story 2 — Predefined Option Selection (Priority: P2)

**Goal**: Player plays an intrigue card that presents predefined mutually exclusive reward bundles and picks one.

**Independent Test**: Play an intrigue card with bundle options. Dialog shows each bundle as a button. Select one. Exact bundle resources granted.

- [X] T013 [US2] Write pytest tests for bundle-mode validation in tests/test_resource_choice.py — test valid bundle selection matches a defined bundle exactly, test reject selection that doesn't match any bundle, test all bundles are valid ResourceCost instances
- [X] T014 [US2] Add bundle mode validation branch in handle_resource_choice() in server/game_engine.py — for choice_type "bundle": verify chosen_resources exactly matches one of the predefined bundles (compare as ResourceCost). On match: grant that bundle. On no match: send ErrorResponse.
- [X] T015 [US2] Integrate choice_reward detection for intrigue cards in server/game_engine.py — in _resolve_intrigue_effect(), when effect_type is "resource_choice" and card has choice_reward: call _send_resource_choice_prompt() with the choice config instead of directly granting resources. Set source_type to "intrigue" in pending state.
- [X] T016 [US2] Add bundle mode rendering to ResourceChoiceDialog in client/ui/dialogs.py — when choice_type is "bundle": render one button per bundle showing the label (e.g., "2 Guitarists", "4 Coins"). Single click selects that bundle and calls on_select with the bundle's resources dict. No counter needed.
- [X] T017 [P] [US2] Add intrigue card with bundle choice (intrigue_051 "Talent Scout's Find") to config/intrigue.json — effect_type: "resource_choice", effect_target: "self", choice_reward with choice_type "bundle" and 5 bundles: {singers: 1}, {drummers: 1}, {guitarists: 2}, {bass_players: 2}, {coins: 4}

**Checkpoint**: Bundle-mode intrigue cards work end-to-end. Card played, dialog shows options, player picks one, resources granted.

---

## Phase 5: User Story 3 — Constrained Combo Choice (Priority: P3)

**Goal**: Player visits a building, pays a cost, then allocates a point total across allowed resource types.

**Independent Test**: Place worker on combo building. 2 coins deducted. Dialog shows +/- controls for guitarists and bass players with total=4 constraint. Allocate 3G+1B, confirm. Resources granted.

- [X] T018 [US3] Write pytest tests for combo-mode validation in tests/test_resource_choice.py — test valid combo (total equals required), test reject combo exceeding total, test reject combo under total, test reject disallowed types, test cost deducted before prompt sent, test insufficient funds blocks placement
- [X] T019 [US3] Add combo mode validation and cost deduction in server/game_engine.py — in handle_place_worker(): if choice has cost, verify player can_afford() before placing worker; if not, send ErrorResponse and abort. In handle_resource_choice() for choice_type "combo": validate sum of chosen_resources equals total, all types in allowed_types. Cost is already deducted at placement time.
- [X] T020 [US3] Add combo mode rendering to ResourceChoiceDialog in client/ui/dialogs.py — when choice_type is "combo": render a row per allowed type with type label, current count, +/- buttons. Show "Total: X / Y" label. Plus button disabled when total reached. Minus button disabled at 0. Confirm button enabled only when total equals required. On confirm: call on_select with chosen_resources dict.
- [X] T021 [P] [US3] Add combo building (building_027 "Guitar & Bass Workshop") to config/buildings.json — cost_coins: 6, visitor_reward_choice: {choice_type: "combo", allowed_types: ["guitarists","bass_players"], total: 4, cost: {coins: 2}}, owner_bonus: {coins: 2}

**Checkpoint**: Combo buildings work end-to-end. Cost deducted, player allocates total across types, resources granted.

---

## Phase 6: User Story 4 — Resource Exchange (Priority: P4)

**Goal**: Player visits a building and turns in N resources, then selects M resources to gain. Two-phase prompt flow.

**Independent Test**: Place worker on exchange building. First dialog: pick 2 non-coin resources to turn in. Confirm. Resources deducted. Second dialog: pick 3 non-coin resources to gain. Confirm. Resources added.

- [X] T022 [US4] Write pytest tests for exchange-mode (two-phase) in tests/test_resource_choice.py — test spend phase validates player owns resources, test spend phase deducts correctly, test gain phase prompt sent after spend resolves, test gain phase grants correctly, test insufficient resources blocks placement, test full exchange flow end-to-end
- [X] T023 [US4] Implement exchange mode in server/game_engine.py — in handle_place_worker(): for choice_type "exchange", verify player has at least pick_count non-coin resources; if not, reject. Send spend prompt with is_spend=true. In handle_resource_choice() for exchange: if phase is "spend", validate player owns chosen resources and total equals pick_count, deduct resources, then send gain prompt (is_spend=false, pick_count=gain_count). If phase is "gain", validate total equals gain_count, grant resources, clear pending, advance turn.
- [X] T024 [US4] Handle sequential spend/gain prompts in client/views/game_view.py — when a resource_choice_resolved arrives with is_spend=true and a subsequent resource_choice_prompt arrives, display the gain dialog. Update local resource display after each phase.
- [X] T025 [P] [US4] Add exchange building (building_028 "Talent Agency") to config/buildings.json — cost_coins: 7, visitor_reward_choice: {choice_type: "exchange", allowed_types: ["guitarists","bass_players","drummers","singers"], pick_count: 2, gain_count: 3}, owner_bonus: {coins: 2}

**Checkpoint**: Exchange buildings work end-to-end. Two-phase spend/gain flow, resources correctly deducted and granted.

---

## Phase 7: User Story 5 — Multi-Player Resource Choice (Priority: P5)

**Goal**: An intrigue card grants the playing player a resource choice, then each other player also receives a (smaller) choice in turn order.

**Independent Test**: 3-player game. Play multi-player intrigue card. Player A picks 2 non-coin resources. Then Player B is prompted to pick 1. Then Player C is prompted to pick 1. All receive their selections.

- [X] T026 [US5] Write pytest tests for multi-player choice sequencing in tests/test_resource_choice.py — test main player prompted first with pick_count, test other players prompted in turn order with others_pick_count, test each player's selection granted independently, test game advances only after all players have chosen, test 2-player game (main + 1 other)
- [X] T027 [US5] Implement multi-player prompt sequencing in server/game_engine.py — in _resolve_intrigue_effect() for effect_type "resource_choice_multi": send prompt to main player with pick_count, store remaining_players (other players in turn order) and others_pick_count in pending state. In handle_resource_choice(): after main player resolves, pop next from remaining_players and send prompt with others_pick_count. After last player resolves, clear pending, advance turn.
- [X] T028 [US5] Handle receiving a resource choice prompt when it's not the local player's placement turn in client/views/game_view.py — the prompt arrives for the local player even during another player's turn. Show the dialog, send the response. Other players see a "Player X is choosing..." status message while waiting.
- [X] T029 [P] [US5] Add multi-player intrigue card (intrigue_052 "Industry Showcase") to config/intrigue.json — effect_type: "resource_choice_multi", effect_target: "all", choice_reward: {choice_type: "pick", allowed_types: ["guitarists","bass_players","drummers","singers"], pick_count: 2, others_pick_count: 1}

**Checkpoint**: Multi-player intrigue cards work end-to-end. Sequential prompts to all players, resources granted, game advances.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Card images, full validation, cleanup

- [X] T030 [P] Generate card images for all new buildings and intrigue cards by running card-generator/generate_cards.py
- [X] T031 Run full test suite with `cd src && pytest && ruff check .` and fix any failures
- [ ] T032 Run quickstart.md validation scenarios end-to-end in a live game session

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–7)**: All depend on Foundational phase completion
  - US1 (P1): Must complete before US2-US5 (establishes core dialog and handler pattern)
  - US2 (P2): Depends on US1 (extends handle_resource_choice and dialog)
  - US3 (P3): Depends on US1 (extends handle_resource_choice and dialog)
  - US4 (P4): Depends on US1 (extends exchange flow on top of pick mode)
  - US5 (P5): Depends on US1 (extends multi-player on top of pick mode)
  - US2, US3 can be done in parallel after US1
  - US4, US5 can be done in parallel after US1
- **Polish (Phase 8)**: Depends on all user stories

### Within Each User Story

- Tests written first (constitutionally required)
- Server logic before client integration
- Config additions can be done in parallel with implementation
- Story complete before moving to next priority

### Parallel Opportunities

- T003, T004 can run in parallel within Phase 2 (different files)
- T011 (config) can run in parallel with T006-T010 (implementation) in US1
- T017 (config) can run in parallel with T013-T016 (implementation) in US2
- T021 (config) can run in parallel with T018-T020 (implementation) in US3
- T025 (config) can run in parallel with T022-T024 (implementation) in US4
- T029 (config) can run in parallel with T026-T028 (implementation) in US5
- US2 and US3 can run in parallel after US1 completes
- US4 and US5 can run in parallel after US1 completes

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (pick mode)
4. **STOP and VALIDATE**: Test pick-mode buildings in a live game
5. Deliverable: Players can pick resources from choice buildings

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (pick mode) → Core dialog and handler working (MVP)
3. US2 (bundles) → Intrigue card choices working
4. US3 (combo) → Constrained allocation working
5. US4 (exchange) → Two-phase trade working
6. US5 (multi-player) → Full multi-player choice working
7. Polish → Card images, full validation
