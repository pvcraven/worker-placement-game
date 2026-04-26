# Tasks: Remaining Special Quest Mechanics

**Input**: Design documents from `/specs/019-remaining-special-quests/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Setup (Shared Schema & Config)

**Purpose**: Add new fields to shared models and tag cards in config

- [X] T001 [P] Add 6 new fields to ContractCard model in shared/card_models.py: `reward_play_intrigue` (int=0), `reward_opponent_gains_coins` (int=0), `reward_extra_worker` (int=0), `reward_choose_resource_per_round` (bool=False), `reward_recall_worker` (bool=False), `reward_use_occupied_building` (bool=False)
- [X] T002 [P] Tag 6 contracts in config/contracts.json with their new field values: contract_jazz_010 (`reward_play_intrigue: 1`), contract_pop_008 (`reward_opponent_gains_coins: 4`), contract_rock_009 (`reward_extra_worker: 1`), contract_soul_007 (`reward_choose_resource_per_round: true`), contract_funk_001 (`reward_recall_worker: true`), contract_funk_005 (`reward_use_occupied_building: true`)

---

## Phase 2: Foundational (Model & Message Updates)

**Purpose**: Add state tracking fields and message types that multiple user stories depend on

- [X] T003 Add `use_occupied_used_this_round: bool = False` field to Player model in server/models/game.py
- [X] T004 Add `also_occupied_by: str | None = None` field to ActionSpace model in server/models/game.py
- [X] T005 Add pending state fields to GameState in server/models/game.py: `pending_play_intrigue` (dict|None=None), `pending_opponent_coins` (dict|None=None), `pending_worker_recall` (dict|None=None), `pending_round_start_choices` (list[str]=Field(default_factory=list))
- [X] T006 Add new message/request types to shared/messages.py: IntriguePlayPromptResponse, PlayIntrigueFromQuestRequest, OpponentChoicePromptResponse, ChooseOpponentRequest, WorkerRecallPromptResponse, RecallWorkerRequest, WorkerRecalledResponse, RoundStartResourceChoicePromptResponse, RoundStartResourceChoiceRequest, RoundStartBonusResponse. Also add new fields to QuestCompletedResponse: `pending_play_intrigue` (bool=False), `opponent_coins_granted` (dict|None=None), `extra_workers_granted` (int=0), `pending_recall` (bool=False). Register all new types in the MESSAGE_TYPE_MAP.
- [X] T007 Add routing for new request types in server/network.py: `play_intrigue_from_quest` → handle_play_intrigue_from_quest, `choose_opponent` → handle_choose_opponent, `recall_worker` → handle_recall_worker, `round_start_resource_choice` → handle_round_start_resource_choice. Import all new handlers from game_engine.

**Checkpoint**: All shared types and state fields are in place — user story implementation can begin

---

## Phase 3: User Story 1 — One-Time Completion Rewards (Priority: P1)

**Goal**: When a player completes "Jailhouse Jazz Session" or "Charity Gala Showcase", the special one-time reward triggers immediately.

**Independent Test**: Complete each quest and verify the special reward fires (play intrigue prompt or opponent coins granted).

### Implementation

- [X] T008 [US1] In server/game_engine.py `handle_complete_quest()`, after the building grant logic (~line 1786) and before the `has_interactive` checks: add reward_play_intrigue handling. If `contract.reward_play_intrigue > 0` and player has intrigue cards, set `state.pending_play_intrigue = {"player_id": player.player_id}`, set `has_interactive = True`, and send `IntriguePlayPromptResponse` to the player with their intrigue hand serialized. If player has no intrigue cards, skip.
- [X] T009 [US1] In server/game_engine.py, add `handle_play_intrigue_from_quest()` handler. Validate `state.pending_play_intrigue` exists, find intrigue card in player hand, remove from hand, call `_resolve_intrigue_effect()`, award `bonus_vp_per_intrigue_played` from completed contracts, log the play. If effect requires targeting (pending), set up `state.pending_intrigue_target` with a `"source": "quest_completion"` flag and send IntrigueTargetPromptResponse. Otherwise clear `pending_play_intrigue` and call `_advance_turn()` or `_finish_reassignment()`. Also update `handle_intrigue_target_selection()` and `handle_cancel_intrigue_target()` to check for source=quest_completion and route correctly after resolution.
- [X] T010 [US1] In server/game_engine.py `handle_complete_quest()`, after play_intrigue handling: add reward_opponent_gains_coins handling. If `contract.reward_opponent_gains_coins > 0`, get opponents list. If exactly 1 opponent, auto-grant coins to them, include in QuestCompletedResponse as `opponent_coins_granted`, log it. If 2+ opponents, set `state.pending_opponent_coins = {"player_id": player.player_id, "coins": contract.reward_opponent_gains_coins}`, set `has_interactive = True`, send `OpponentChoicePromptResponse` with opponent list.
- [X] T011 [US1] In server/game_engine.py, add `handle_choose_opponent()` handler. Validate `state.pending_opponent_coins` exists, validate target is a valid opponent, grant coins to target player, log it, broadcast `QuestCompletedResponse` update or a separate notification, clear `pending_opponent_coins`, call `_advance_turn()` or `_finish_reassignment()`.
- [X] T012 [US1] In client/views/game_view.py, add handler for `intrigue_play_prompt` message: show intrigue card selection dialog (reuse existing intrigue card UI pattern from backstage), send `PlayIntrigueFromQuestRequest` with selected card ID. Add handler for `opponent_choice_prompt` message: show opponent selection dialog, send `ChooseOpponentRequest` with chosen player ID. Update `_on_quest_completed()` to handle new fields (`opponent_coins_granted` — update opponent's coin display; `extra_workers_granted` — update worker count display; `pending_play_intrigue` / `pending_recall` — know that more interaction is coming).

**Checkpoint**: Jailhouse Jazz Session and Charity Gala Showcase are fully playable

---

## Phase 4: User Story 2 — Extra Permanent Worker (Priority: P2)

**Goal**: Completing "Hire a Tour Manager" permanently increases the player's total worker count by 1.

**Independent Test**: Complete the quest and verify worker count increases by 1 on the next round.

### Implementation

- [X] T013 [US2] In server/game_engine.py `handle_complete_quest()`, after opponent_gains_coins handling: add reward_extra_worker handling. If `contract.reward_extra_worker > 0`, increment `player.total_workers` by that amount (do NOT increment `available_workers` — it becomes available next round per FR-006). Set `extra_workers_granted` on the QuestCompletedResponse. Log "gained N extra permanent worker(s)".
- [X] T014 [US2] In client/views/game_view.py `_on_quest_completed()`, if `extra_workers_granted > 0`, update the player's total_workers in the local game state and add a game log entry noting the permanent worker gain.

**Checkpoint**: Hire a Tour Manager is fully playable

---

## Phase 5: User Story 3 — Round-Start Resource Choice (Priority: P3)

**Goal**: After completing "Soul Music Residency", the player is prompted to choose 1 non-coin resource at the start of each subsequent round.

**Independent Test**: Complete the quest, advance to the next round, verify the resource choice prompt appears before the first turn.

### Implementation

- [X] T015 [US3] In server/game_engine.py `_end_round()`, after the RoundEndResponse broadcast (~line 427) and building market broadcast (~line 430): add round-start resource choice logic. Scan all players (in turn order) for completed contracts with `reward_choose_resource_per_round == True`. If any found, set `state.pending_round_start_choices` to the list of those player IDs, then send `RoundStartResourceChoicePromptResponse` to the first player in the list with the contract name. Return early (do NOT proceed to first turn notification yet).
- [X] T016 [US3] In server/game_engine.py, add `handle_round_start_resource_choice()` handler. Validate `state.pending_round_start_choices` is non-empty and requesting player is first in list. Validate `resource_type` is one of guitarists/bass_players/drummers/singers (not coins). Grant 1 unit of chosen resource. Log it. Broadcast `RoundStartBonusResponse`. Remove player from pending list. If more players pending, send prompt to next. If list is now empty, clear pending state and send first-turn notification (call `_notify_turn_if_needed()`).
- [X] T017 [US3] In client/views/game_view.py, add handler for `round_start_resource_choice_prompt` message: show a resource selection dialog with 4 non-coin resource options (Guitarist, Bass Player, Drummer, Singer). On selection, send `RoundStartResourceChoiceRequest`. Add handler for `round_start_bonus` message: update the specified player's resources in local state, add game log entry.

**Checkpoint**: Soul Music Residency is fully playable

---

## Phase 6: User Story 4 — Worker Recall on Completion (Priority: P4)

**Goal**: Completing "Time Warp Remix" immediately prompts the player to recall one placed worker from the board.

**Independent Test**: Complete the quest with workers placed, verify the recall prompt appears and a selected worker is returned.

### Implementation

- [X] T018 [US4] In server/game_engine.py `handle_complete_quest()`, after reward_extra_worker handling: add reward_recall_worker handling. If `contract.reward_recall_worker` is True, find all board action spaces occupied by this player (scan `state.board.action_spaces` for `occupied_by == player.player_id`). If any found, set `state.pending_worker_recall = {"player_id": player.player_id}`, set `has_interactive = True`, send `WorkerRecallPromptResponse` with the list of occupied space IDs and names. If no workers placed, skip. Set `pending_recall=True` on QuestCompletedResponse.
- [X] T019 [US4] In server/game_engine.py, add `handle_recall_worker()` handler. Validate `state.pending_worker_recall` exists and player matches. Validate `msg.space_id` is a valid action space occupied by this player. Set `space.occupied_by = None`. Increment `player.available_workers`. Clear `state.pending_worker_recall`. Log "recalled worker from {space.name}". Broadcast `WorkerRecalledResponse`. Then call `_advance_turn()` or `_finish_reassignment()` depending on game phase.
- [X] T020 [US4] In client/views/game_view.py, add handler for `worker_recall_prompt` message: display a message at the top of the screen ("Select a worker to recall") and highlight the listed spaces as clickable. When player clicks a highlighted space, send `RecallWorkerRequest` with that space_id. Add handler for `worker_recalled` message: update local state to free the space and increment available workers, remove the top-of-screen prompt.

**Checkpoint**: Time Warp Remix is fully playable

---

## Phase 7: User Story 5 — Use Occupied Building (Priority: P5)

**Goal**: After completing "Recover the Master Tapes", the player can once per round place a worker on a building occupied by another player's worker.

**Independent Test**: Complete the quest, place a worker on an occupied building, verify rewards are granted and both workers are visible.

### Implementation

- [X] T021 [US5] In server/game_engine.py, add `_can_use_occupied(player, space, state) -> bool` helper function. Returns True only if: player has a completed contract with `reward_use_occupied_building == True`, `player.use_occupied_used_this_round` is False, `space.space_type == "building"`, and `space.occupied_by != player.player_id` (not own worker).
- [X] T022 [US5] In server/game_engine.py `handle_place_worker()`, modify the occupancy check (~line 889). Instead of immediately returning error when `space.occupied_by is not None`, first call `_can_use_occupied()`. If True, set `player.use_occupied_used_this_round = True`, store original occupant in `space.also_occupied_by = space.occupied_by` (preserving original for display), then set `space.occupied_by = player.player_id` and continue with normal placement flow. If `_can_use_occupied()` returns False, return the existing SPACE_OCCUPIED error.
- [X] T023 [US5] In server/game_engine.py `_end_round()`, after clearing `space.occupied_by = None` (~line 353), also clear `space.also_occupied_by = None`. After `player.completed_quest_this_turn = False` (~line 349), also reset `player.use_occupied_used_this_round = False`.
- [X] T024 [US5] In client/views/game_view.py, update the worker placement logic to recognize that buildings occupied by other players may be valid targets if the local player has the use-occupied ability and hasn't used it this round. When rendering, show both workers on a building that has `also_occupied_by` set.

**Checkpoint**: Recover the Master Tapes is fully playable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Tests, documentation updates, validation

- [X] T025 Create tests/test_special_quests.py with pytest tests covering: reward_play_intrigue triggers prompt when player has intrigue cards, reward_play_intrigue skips when no intrigue cards, reward_opponent_gains_coins auto-grants in 2-player game, reward_opponent_gains_coins prompts in 3+ player game, reward_extra_worker increments total_workers but not available_workers, reward_choose_resource_per_round triggers at round start, reward_recall_worker prompts when workers placed, reward_recall_worker skips when no workers placed, _can_use_occupied validates all conditions, use_occupied_used_this_round resets at round end
- [X] T026 Update specs/waterdeep-card-mapping.md to mark all 6 special quest mechanics as DONE (play_intrigue, opponent_gains_coins, extra_worker, choose_resource_per_round, recall_worker, use_occupied_building)
- [X] T027 Run `pytest tests/` and `ruff check .` from project root — fix any failures or lint errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T001 must be complete before T006 can reference new ContractCard fields)
- **User Stories (Phases 3–7)**: All depend on Phase 2 completion
  - US1–US4 all modify `handle_complete_quest()` so they MUST be sequential
  - US5 modifies `handle_place_worker()` so it can run in parallel with US1–US4
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: First to implement — establishes the quest-completion interactive reward pattern
- **US2 (P2)**: Independent of US1 but adds to same function — implement after US1
- **US3 (P3)**: Independent — modifies `_end_round()` not `handle_complete_quest()`
- **US4 (P4)**: Adds to `handle_complete_quest()` — implement after US2
- **US5 (P5)**: Modifies `handle_place_worker()` — can run in parallel with US1–US4

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- US3 and US5 can run in parallel with other stories (different functions)
- T025, T026 can run in parallel (different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T007)
3. Complete Phase 3: US1 — One-Time Completion Rewards (T008–T012)
4. **STOP and VALIDATE**: Test Jailhouse Jazz Session and Charity Gala Showcase

### Incremental Delivery

1. Setup + Foundational → Schema ready
2. US1 → Play intrigue + opponent coins working
3. US2 → Extra worker working
4. US3 → Round-start resource choice working
5. US4 → Worker recall on completion working
6. US5 → Use occupied building working
7. Polish → Tests pass, docs updated

---

## Notes

- US1–US4 all add code to `handle_complete_quest()` — implement sequentially to avoid merge conflicts
- US5 is the only story touching `handle_place_worker()` — can be developed independently
- The `pending_play_intrigue` flow chains into existing intrigue targeting — test with both targeted and non-targeted intrigue cards
- The round-start resource choice (US3) blocks turn advancement until all choices resolve
- Commit after each user story checkpoint
