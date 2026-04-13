# Tasks: Multiplayer Worker Placement Game

**Input**: Design documents from `/specs/001-worker-placement-game/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/websocket-messages.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted. Tests can be added later via a separate pass.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, dependencies, and package structure

- [x] T001 Create project directory structure: `server/`, `server/models/`, `client/`, `client/views/`, `client/ui/`, `client/assets/images/`, `client/assets/fonts/`, `client/assets/sounds/`, `shared/`, `config/`, `tests/`, `tests/unit/`, `tests/integration/`, `tests/contract/`
- [x] T002 Create `pyproject.toml` with dependencies: arcade>=3.0, websockets>=12.0, pydantic>=2.0, pytest>=8.0, pytest-asyncio>=0.23
- [x] T003 [P] Create `__init__.py` files for all packages: `server/__init__.py`, `server/models/__init__.py`, `client/__init__.py`, `client/views/__init__.py`, `client/ui/__init__.py`, `shared/__init__.py`
- [x] T004 [P] Create `tests/conftest.py` with shared test fixtures placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models, config system, and networking infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement shared constants (enums, game constants, starting workers) in `shared/constants.py` per data-model.md
- [x] T006 [P] Implement shared card models (ResourceCost, ContractCard, IntrigueCard, BuildingTile, ProducerCard) in `shared/card_models.py` per data-model.md
- [x] T007 [P] Implement shared network message models (all Client→Server and Server→Client Pydantic models with discriminated unions) in `shared/messages.py` per contracts/websocket-messages.md
- [x] T008 Implement server-side game state models (PlayerResources, Player, ActionSpace, GarageSlot, BoardState, GameLog, GameState) in `server/models/game.py` per data-model.md
- [x] T009 [P] Implement config file Pydantic schemas (ContractsConfig, IntrigueConfig, BuildingsConfig, ProducersConfig, BoardConfig, GameRulesConfig) in `server/models/config.py` per data-model.md
- [x] T010 Implement config loader with validation (load all JSON configs, hard errors for structural issues, warnings for suspicious values) in `server/config_loader.py` per FR-026/FR-027/FR-028
- [x] T011 Create `config/game_rules.json` with default game rules (8 rounds, worker scaling, timeouts, player limits) per spec.md
- [x] T012 [P] Create `config/board.json` with 9 permanent action spaces (The Merch Store, Motown, Guitar Center, Talent Show, The Rhythm Pit, Cliffwatch Inn x3, Builder's Hall, Castle Waterdeep, The Garage x3) and building lot count per FR-029/FR-030/FR-031
- [x] T013 [P] Create `config/contracts.json` with 60 contract cards (34 easier ≤9 VP, 26 harder ≥10 VP) across 5 genres (Jazz, Pop, Soul, Funk, Rock) per FR-006
- [x] T014 [P] Create `config/intrigue.json` with 50 intrigue cards (music-industry themed effects: gain resources, steal resources, all-player events, VP bonuses) per FR-011
- [x] T015 [P] Create `config/buildings.json` with 24 building tiles (famous recording studios and music venues) per FR-012
- [x] T016 [P] Create `config/producers.json` with ~11 producer cards (each favoring 2 genres, +4 VP per matching contract) per FR-010
- [x] T017 Implement WebSocket server infrastructure (accept connections, session tracking, message routing, connection lifecycle) in `server/network.py` per research.md architecture
- [x] T018 Implement WebSocket client infrastructure (background thread, thread-safe message queue, connect/disconnect/reconnect) in `client/network_client.py` per research.md architecture
- [x] T019 Implement base Arcade window (resizable, fullscreen support, minimum size enforcement, View switching) in `client/game_window.py` per FR-023/FR-024
- [x] T020 Implement server entry point (asyncio event loop, config loading, WebSocket server start) in `server/main.py`
- [x] T021 Implement client entry point (Arcade window launch, server address config) in `client/main.py`
- [x] T022 Implement game state container (create/get sessions, game code generation, session cleanup on timeout) in `server/game_state.py`

**Checkpoint**: Foundation ready — shared models validated, configs load, server accepts connections, client window opens. User story implementation can now begin.

---

## Phase 3: User Story 1 — Host and Join a Game Lobby (Priority: P1) MVP

**Goal**: Players can create a lobby, join via game code, ready up, and start a game. This is the multiplayer connectivity foundation.

**Independent Test**: One player creates a lobby, others join with the game code. All ready up, host clicks start, all players see the game board initialize.

### Implementation for User Story 1

- [x] T023 [US1] Implement lobby manager (create lobby, join by code, player ready state, start game validation, host privileges) in `server/lobby.py` per FR-002
- [x] T024 [US1] Implement lobby message handlers in `server/network.py`: handle `create_game`, `join_game`, `player_ready`, `start_game` messages and broadcast `game_created`, `player_joined`, `player_ready_update`, `game_started` responses
- [x] T025 [US1] Implement game initialization logic (deal producer cards, set starting workers per player count, initialize board from config, set turn order, transition to PLACEMENT phase) in `server/game_engine.py`
- [x] T026 [US1] Implement state visibility filtering (hide opponent hands, hide producer cards, show only counts for decks) in `server/game_engine.py` for `game_started` and `state_sync` messages
- [x] T027 [P] [US1] Implement main menu view (Create Game / Join Game buttons, server address input, player name input) in `client/views/menu_view.py`
- [x] T028 [P] [US1] Implement lobby view (player list display, ready toggle button, start game button for host, game code display, waiting state) in `client/views/lobby_view.py`
- [x] T029 [US1] Wire client network events to view transitions: menu_view → (create/join) → lobby_view → (game_started) → game_view in `client/game_window.py`

**Checkpoint**: Players can create lobbies, join via code, ready up, and start a game. The game initializes and transitions to the game board.

---

## Phase 4: User Story 2 — Place Workers and Collect Resources (Priority: P1)

**Goal**: Players take turns placing workers on action spaces to collect resources. Core gameplay loop with turn rotation and round management.

**Independent Test**: Start a game, players take turns placing workers on resource spaces (The Merch Store, Arena, etc.), receive correct resources, rounds advance after all workers placed.

### Implementation for User Story 2

- [x] T030 [US2] Implement turn management (current player tracking, turn rotation, skip players with no workers, turn timeout handling) in `server/game_engine.py` per FR-003/FR-017
- [x] T031 [US2] Implement worker placement logic (validate space unoccupied, place worker, grant reward, decrement available workers) in `server/game_engine.py` per FR-003/FR-004
- [x] T032 [US2] Implement round lifecycle (detect all workers placed, return workers at round end, advance round counter, check for game over at round 8) in `server/game_engine.py` per FR-008/FR-009
- [x] T033 [US2] Implement `place_worker` message handler in `server/network.py`: validate and execute placement, broadcast `worker_placed` with reward and next player
- [x] T034 [US2] Implement `round_end` and `game_over` broadcast logic in `server/network.py`
- [x] T035 [US2] Implement game log recording (log each worker placement, round transitions) in `server/game_engine.py` per FR-018
- [x] T036 [US2] Implement board renderer (draw permanent action spaces, worker tokens on spaces, empty/occupied state, building lots) in `client/ui/board_renderer.py`
- [x] T037 [P] [US2] Implement resource bar (display player's Guitarists/red, Bass Players/black, Drummers/white, Singers/purple, Coins/gold with counts) in `client/ui/resource_bar.py` per FR-005
- [x] T038 [P] [US2] Implement game log panel (scrollable action log showing all player actions) in `client/ui/game_log.py` per FR-018
- [x] T039 [US2] Implement game view (compose board renderer, resource bar, game log, player info, turn indicator, click-to-place-worker interaction) in `client/views/game_view.py` per FR-019/FR-025
- [x] T040 [US2] Wire game view to network: send `place_worker` on click, handle `worker_placed`/`round_end`/`game_over` broadcasts, update UI state in `client/views/game_view.py`

**Checkpoint**: Full turn-based worker placement loop works. Players place workers, collect resources, rounds advance, game ends after 8 rounds.

---

## Phase 5: User Story 3 — Complete Quests to Score Victory Points (Priority: P1)

**Goal**: Players spend resources to complete contract cards from their hand, earning Victory Points. End-of-game scoring with Producer card bonuses determines the winner.

**Independent Test**: Give a player resources matching a contract's cost. They complete it, resources deducted, VP awarded. At game end, Producer bonuses applied, winner displayed.

### Implementation for User Story 3

- [x] T041 [US3] Implement quest completion logic (validate resources, deduct cost, award VP + bonus resources, enforce one-per-turn limit, add to completed contracts) in `server/game_engine.py` per FR-007
- [x] T042 [US3] Implement `complete_quest` message handler in `server/network.py`: validate and execute, broadcast `quest_completed` per contracts/websocket-messages.md
- [x] T043 [US3] Implement end-of-game scoring (sum base VP, calculate Producer card bonuses per genre, apply tiebreakers: most Coins → most resources → most quests) in `server/game_engine.py` per FR-010/FR-021
- [x] T044 [US3] Implement `game_over` broadcast with full final scores (base VP, producer bonus, producer card reveal, ranks) in `server/network.py` per contracts/websocket-messages.md
- [x] T045 [US3] Implement card renderer (draw contract cards with genre color, cost, VP, name, description; draw intrigue cards) in `client/ui/card_renderer.py`
- [x] T046 [US3] Implement quest hand display in game view (show player's contract cards, highlight completable quests, click-to-complete interaction) in `client/views/game_view.py`
- [x] T047 [US3] Implement results view (final scores table, Producer card reveals, winner announcement, return-to-menu button) in `client/views/results_view.py`
- [x] T048 [US3] Wire quest completion UI: send `complete_quest` on card click, handle `quest_completed` broadcast, transition to results_view on `game_over` in `client/views/game_view.py`

**Checkpoint**: Players can complete quests for VP. Game ends with correct scoring including Producer bonuses. Winner displayed.

---

## Phase 6: User Story 4 — Acquire New Quests from the Talent Agency (Priority: P2)

**Goal**: Players place workers at Cliffwatch Inn to acquire new contract cards from the face-up display or draw from the deck. Also acquire intrigue cards.

**Independent Test**: Player places worker on Cliffwatch Inn, selects a face-up contract, it moves to their hand, a replacement card is drawn from the deck.

### Implementation for User Story 4

- [x] T049 [US4] Implement Talent Agency logic (face-up contract display, take face-up card, draw from deck, auto-refill face-up slots, handle empty deck) in `server/game_engine.py` per FR-020
- [x] T050 [US4] Implement Cliffwatch Inn action space handler (3 distinct spots: acquire contract from face-up, acquire contract from deck, acquire intrigue card) in `server/game_engine.py`
- [x] T051 [US4] Implement `acquire_contract` and `acquire_intrigue` message handlers in `server/network.py`: validate Cliffwatch Inn placement, execute acquisition, broadcast `contract_acquired`
- [x] T052 [US4] Implement face-up contract display UI (show 5 face-up quest cards at the Talent Agency, click-to-select interaction) in `client/views/game_view.py`
- [x] T053 [US4] Implement contract/intrigue acquisition dialogs (selection modal when placing on Cliffwatch Inn: choose face-up card, draw from deck, or take intrigue) in `client/ui/dialogs.py`
- [x] T054 [US4] Wire acquisition flow: show dialog on Cliffwatch Inn placement, send `acquire_contract`/`acquire_intrigue`, handle broadcasts, update hand display in `client/views/game_view.py`

**Checkpoint**: Quest acquisition works. Face-up display shows 5 cards, players can take cards at Cliffwatch Inn, display auto-refills.

---

## Phase 7: User Story 7 — Gain Additional Worker at Round 5 (Priority: P2)

**Goal**: All players automatically receive one additional worker when round 5 begins, increasing actions for the final 4 rounds.

**Independent Test**: Advance game to end of round 4. When round 5 starts, verify all players' worker counts increase by 1 and the extra worker is available for placement.

### Implementation for User Story 7

- [x] T055 [US7] Implement bonus worker grant logic (at round 5 start, increment all players' total_workers and available_workers by 1) in `server/game_engine.py` per FR-014
- [x] T056 [US7] Implement `bonus_workers_granted` broadcast in `server/network.py` at round 5 transition
- [x] T057 [US7] Handle `bonus_workers_granted` message in client: update worker count display, show notification in `client/views/game_view.py`

**Checkpoint**: Workers correctly increase at round 5 for all players.

---

## Phase 8: User Story 5 — Play Intrigue Cards at The Garage and Reassign Workers (Priority: P2)

**Goal**: Players place workers at The Garage to play intrigue cards. After all workers are placed, a Reassignment Phase lets Garage workers move to other spaces for bonus actions.

**Independent Test**: Player places worker on Garage slot 1, plays an intrigue card (effect resolves). After all workers placed, Reassignment Phase begins: Garage workers reassign in order 1→2→3 to unoccupied spaces.

### Implementation for User Story 5

- [x] T058 [US5] Implement Garage placement logic (validate player has intrigue card, occupy numbered slot, resolve intrigue card effect immediately) in `server/game_engine.py` per FR-011a
- [x] T059 [US5] Implement intrigue card effect resolver (gain_resources, steal_resources, all_players events, vp_bonus, choose_opponent targeting) in `server/game_engine.py` per FR-011
- [x] T060 [US5] Implement Reassignment Phase (trigger after all workers placed if Garage slots occupied, process slots in order 1→2→3, move worker to unoccupied space excluding Garage, grant destination reward, allow quest completion during reassignment) in `server/game_engine.py` per FR-011b/FR-011c
- [x] T061 [US5] Implement `place_worker_garage`, `reassign_worker`, and `choose_intrigue_target` message handlers in `server/network.py`
- [x] T062 [US5] Implement `worker_placed_garage`, `reassignment_phase_start`, `worker_reassigned` broadcast logic in `server/network.py`
- [x] T063 [US5] Implement Garage UI interaction (show 3 numbered slots, intrigue card selection dialog when placing, highlight available slots) in `client/views/game_view.py`
- [x] T064 [US5] Implement Reassignment Phase UI (highlight whose turn to reassign, show available destination spaces, click-to-reassign interaction) in `client/views/game_view.py`
- [x] T065 [US5] Implement intrigue card hand display (show player's intrigue cards, selection for Garage play, target player selection dialog for choose_opponent cards) in `client/ui/dialogs.py`
- [x] T066 [US5] Wire Garage flow: send `place_worker_garage` with card ID, handle intrigue effects, handle reassignment phase transitions and broadcasts in `client/views/game_view.py`

**Checkpoint**: Full Garage mechanic works including intrigue card play and Reassignment Phase with correct slot ordering.

---

## Phase 9: User Story 8 — Reconnect to an In-Progress Game (Priority: P2)

**Goal**: Disconnected players can reconnect to their game and resume play with fully synchronized state.

**Independent Test**: Disconnect a player mid-game (close client). Reopen client, enter game code and player name. Verify they rejoin with correct game state, resources, and hand.

### Implementation for User Story 8

- [x] T067 [US8] Implement disconnect handling (mark player as disconnected, track disconnect time, start turn timeout if it was their turn) in `server/network.py` per FR-016
- [x] T068 [US8] Implement reconnection logic (match by game code + player name + slot index, restore WebSocket association, send full state_sync, resume turn if applicable) in `server/network.py` per FR-016
- [x] T069 [US8] Implement turn timeout and auto-skip (configurable timeout per FR-017, skip disconnected player's turn, broadcast `turn_timeout`, track consecutive timeouts) in `server/game_engine.py`
- [x] T070 [US8] Implement game preservation timeout (abandon game after 30 minutes of all players disconnected, clean up session) in `server/game_state.py`
- [x] T071 [US8] Implement host transfer (if host disconnects, transfer host privileges to next connected player) in `server/lobby.py`
- [x] T072 [US8] Handle `player_disconnected`, `player_reconnected`, `turn_timeout` broadcasts in client: show notifications, update player status indicators in `client/views/game_view.py`
- [x] T073 [US8] Implement reconnection UI flow in client: allow entering game code + name from menu, handle `state_sync` response, rebuild full game view from received state in `client/views/menu_view.py` and `client/views/game_view.py`

**Checkpoint**: Players can disconnect and reconnect without losing game state. Turns auto-skip for disconnected players.

---

## Phase 10: User Story 6 — Construct Buildings for New Action Spaces (Priority: P3)

**Goal**: Players spend Coins at Builder's Hall to purchase building tiles, creating new action spaces. Building owners earn bonuses when others use their buildings.

**Independent Test**: Player places worker at Builder's Hall, purchases a building tile, it appears as a new action space on an empty lot. Another player uses it, original builder receives owner bonus.

### Implementation for User Story 6

- [x] T074 [US6] Implement Builder's Hall action (display available building tiles, purchase with Coins, place on empty lot, create new action space, deduct cost) in `server/game_engine.py` per FR-012
- [x] T075 [US6] Implement building owner bonus (when a non-owner player uses a building space, grant the owner the building's owner_bonus) in `server/game_engine.py` per FR-013
- [x] T076 [US6] Implement `purchase_building` message handler in `server/network.py`: validate Builder's Hall action, sufficient Coins, empty lot; broadcast `building_constructed`
- [x] T077 [US6] Implement building purchase UI (show available building tiles with costs, lot selection, purchase confirmation dialog) in `client/ui/dialogs.py`
- [x] T078 [US6] Update board renderer to display constructed buildings on lots (show building name, reward info, owner indicator) in `client/ui/board_renderer.py`
- [x] T079 [US6] Wire building flow: show building purchase dialog at Builder's Hall, send `purchase_building`, handle `building_constructed` broadcast, add new space to board in `client/views/game_view.py`
- [x] T080 [US6] Display owner bonus notification when another player uses a building in `client/views/game_view.py`

**Checkpoint**: Buildings can be purchased, placed on lots, and used by all players with owner bonuses working correctly.

---

## Phase 11: User Story 9 — Castle Waterdeep / First-Player Marker (Priority: P2)

**Goal**: Players can place a worker at Castle Waterdeep to gain the first-player marker (determining next round's turn order) and draw an intrigue card.

**Independent Test**: Player places worker at Castle Waterdeep, gains first-player marker and 1 intrigue card. Next round, that player goes first.

### Implementation for User Story 9

- [x] T081 [US9] Implement Castle Waterdeep action (grant first-player marker to placing player, draw 1 intrigue card from deck, update turn order for next round) in `server/game_engine.py` per FR-030/FR-032
- [x] T082 [US9] Implement first-player marker tracking and turn order rotation (next round starts with marker holder, clockwise from there) in `server/game_engine.py`
- [x] T083 [US9] Display first-player marker indicator on the current holder in game view UI in `client/views/game_view.py`

**Checkpoint**: First-player marker mechanic works. Turn order correctly rotates based on Castle Waterdeep visits.

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: UI polish, edge case handling, and improvements across all stories

- [x] T084 Implement server-side action validation for all player actions (reject invalid moves, return error codes per contracts/websocket-messages.md error table) in `server/game_engine.py` per FR-022
- [x] T085 Implement client-side error display (show error messages from server, highlight invalid actions) in `client/views/game_view.py`
- [x] T086 Implement responsive UI scaling (virtual coordinate system, proportional layout, minimum size enforcement with "window too small" overlay) in `client/game_window.py` and `client/ui/board_renderer.py` per FR-023/FR-024
- [x] T087 Implement player info panels (show all players' public info: name, VP, resource counts, completed contracts count, worker count, connection status) in `client/views/game_view.py` per FR-019
- [x] T088 Implement ping/pong keepalive for WebSocket connections in `server/network.py` and `client/network_client.py`
- [x] T089 [P] Implement between-turn browsing (allow players to browse their quests, resources, and board when it's not their turn) in `client/views/game_view.py` per FR-025
- [ ] T090 Run end-to-end playtest: create lobby, full 8-round game with 3+ players, verify scoring, all action spaces, Garage reassignment, reconnection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (Lobby) must complete before US2-US9 can be tested end-to-end
  - US2 (Worker Placement) must complete before US3-US9 (all require placing workers)
  - US3 (Quests) can proceed after US2
  - US4 (Talent Agency), US7 (Bonus Worker), US5 (Garage), US9 (Castle Waterdeep) can proceed in parallel after US2
  - US6 (Buildings) can proceed after US2
  - US8 (Reconnection) can proceed after US2
- **Polish (Phase 12)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundational only — no other story dependencies
- **US2 (P1)**: Depends on US1 (need lobby to start a game)
- **US3 (P1)**: Depends on US2 (need resources to complete quests)
- **US4 (P2)**: Depends on US2 (Cliffwatch Inn is an action space)
- **US7 (P2)**: Depends on US2 (modifies worker counts during rounds)
- **US5 (P2)**: Depends on US2 (Garage is an action space) and US4 (intrigue card acquisition at Cliffwatch Inn)
- **US8 (P2)**: Depends on US2 (need active gameplay to test reconnection)
- **US6 (P3)**: Depends on US2 (Builder's Hall is an action space)
- **US9 (P2)**: Depends on US2 (Castle Waterdeep is an action space)

### Within Each User Story

- Server-side logic before client UI
- Message handlers after game logic
- UI components can be parallel where they're in different files
- Wire up / integration tasks last

### Parallel Opportunities

- Phase 2: Config JSON files (T012-T016) can all be written in parallel
- Phase 2: T006, T007, T009 can run in parallel (different shared/ and server/models/ files)
- Phase 3 (US1): T027 and T028 can run in parallel (different client view files)
- Phase 4 (US2): T037 and T038 can run in parallel (different UI component files)
- Phase 6-11 (US4, US7, US5, US8, US6, US9): Phases 7 and 11 can run in parallel; Phase 8 can run in parallel with Phase 10

---

## Parallel Example: Phase 2 (Foundational)

```
# Launch all config files together:
Task: "Create config/board.json" (T012)
Task: "Create config/contracts.json" (T013)
Task: "Create config/intrigue.json" (T014)
Task: "Create config/buildings.json" (T015)
Task: "Create config/producers.json" (T016)

# Launch shared models in parallel:
Task: "Implement shared card models in shared/card_models.py" (T006)
Task: "Implement shared message models in shared/messages.py" (T007)
Task: "Implement config schemas in server/models/config.py" (T009)
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 — Lobby
4. Complete Phase 4: User Story 2 — Worker Placement
5. Complete Phase 5: User Story 3 — Quest Completion + Scoring
6. **STOP and VALIDATE**: Playable game with resource collection and quest completion
7. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Lobby) → Players can connect and start games
3. Add US2 (Worker Placement) → Core gameplay loop works
4. Add US3 (Quests + Scoring) → **MVP! Playable game** with win condition
5. Add US4 (Talent Agency) → Quest acquisition adds strategy
6. Add US7 (Bonus Worker) → Mid-game pacing improvement
7. Add US9 (Castle Waterdeep) → First-player marker adds turn order strategy
8. Add US5 (Garage) → Full intrigue card + reassignment mechanic
9. Add US8 (Reconnection) → Multiplayer resilience
10. Add US6 (Buildings) → Long-term investment strategy
11. Polish → UI refinement, edge cases, playtesting

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable after its dependencies are met
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Config JSON files (T013-T016) contain game content — these can be iterated on throughout development as balance is tuned
- Plot Quests (FR-006a) are deferred to a later phase but the data model supports them from T006 onward
