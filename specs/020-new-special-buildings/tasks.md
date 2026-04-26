# Tasks: New Special Buildings

**Input**: Design documents from `/specs/020-new-special-buildings/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)

---

## Phase 1: Setup (Config)

**Purpose**: Add the two new building entries to the game configuration

- [ ] T001 [P] Add building_021 "Royalty Collection" entry to config/buildings.json with `visitor_reward_special: "coins_per_building"`, `owner_bonus: {coins: 2}`, `cost_coins: 4`, all other rewards zero, no accumulation
- [ ] T002 [P] Add building_022 "Audition Showcase" entry to config/buildings.json with `visitor_reward_special: "draw_contract_and_complete"`, `owner_bonus_vp: 2`, `cost_coins: 4`, all other rewards zero, no accumulation

---

## Phase 2: Foundational (Model & Message Updates)

**Purpose**: Add state tracking fields and message fields that both user stories depend on

- [ ] T003 Add `pending_showcase_bonus: dict | None = None` field to GameState in server/models/game.py
- [ ] T004 Add `bonus_quest_id: str | None = None` and `bonus_vp: int = 0` fields to QuestCompletionPromptResponse in shared/messages.py
- [ ] T005 Add `showcase_bonus_vp: int = 0` field to QuestCompletedResponse in shared/messages.py

**Checkpoint**: All shared types and state fields are in place — user story implementation can begin

---

## Phase 3: User Story 1 — Royalty Collection Building (Priority: P1)

**Goal**: When a player visits the Royalty Collection building, they receive 1 coin per player-purchased building in play. Owner gets 2 coins when another player visits.

**Independent Test**: Purchase building_021, place a worker on it with N buildings in play, verify N coins awarded. Verify owner bonus of 2 coins when a different player visits.

### Implementation

- [ ] T006 [US1] In server/game_engine.py `handle_place_worker()`, after the existing `draw_intrigue` visitor_reward_special handling (~line 1086-1088), add a case for `visitor_reward_special == "coins_per_building"`: calculate `coin_count = len(state.board.constructed_buildings)`, add `coin_count` to `player.resources.coins`, and include in the reward dict for the WorkerPlacedResponse broadcast. No early return — continue to owner bonus and quest completion check as normal.

**Checkpoint**: Royalty Collection building is fully playable

---

## Phase 4: User Story 2 — Audition Showcase Building (Priority: P2)

**Goal**: When a player visits the Audition Showcase building, they select a face-up contract, it goes to their hand, and they get the chance to immediately complete it for +4 VP bonus via the existing quest completion window.

**Independent Test**: Purchase building_022, place a worker on it, select a face-up contract. If completable, verify "+4VP bonus" text appears in quest completion window and +4 VP is awarded on completion. If not completable, verify contract goes to hand with no bonus.

### Implementation

- [ ] T007 [US2] In server/game_engine.py `handle_place_worker()`, add a case for `visitor_reward_special == "draw_contract_and_complete"`: process owner bonus first (since we return early), then send a `QuestSelectionPromptResponse` to the player with the face-up contracts (same as the existing `draw_contract` flow). Set a flag to distinguish this from regular quest selection — store `state.pending_showcase_bonus = {"player_id": player.player_id, "contract_id": None, "bonus_vp": 4}` (contract_id is filled in after selection). Return early.
- [ ] T008 [US2] In server/game_engine.py `handle_select_quest_card()`, add handling for when `state.pending_showcase_bonus` is set and `contract_id` is None (meaning we're in the showcase selection phase): after adding the selected contract to the player's hand and drawing a replacement, set `state.pending_showcase_bonus["contract_id"] = contract.id`. Then call `_check_quest_completion()` instead of the normal quest selection follow-up.
- [ ] T009 [US2] In server/game_engine.py `_check_quest_completion()`, after building the `completable` list: if `state.pending_showcase_bonus` is set and has a `contract_id`, check if that contract ID is in the completable list. If so, pass `bonus_quest_id=contract_id` and `bonus_vp=4` in the `QuestCompletionPromptResponse`. If not (bonus contract isn't completable), pass no bonus fields. If no quests are completable at all, clear `state.pending_showcase_bonus` before advancing turn.
- [ ] T010 [US2] In server/game_engine.py `handle_complete_quest()`, after the base VP award and plot quest bonus calculation: check if `state.pending_showcase_bonus` is set and `pending_showcase_bonus["contract_id"] == contract.id`. If so, add `pending_showcase_bonus["bonus_vp"]` (4) to `player.victory_points`, set `showcase_bonus_vp = 4` for the response, and log "earned N bonus VP from Audition Showcase". Clear `state.pending_showcase_bonus`.
- [ ] T011 [US2] In server/game_engine.py `handle_skip_quest_completion()` and `_advance_turn()`: clear `state.pending_showcase_bonus` if it is set (player skipped or completed a different quest — no bonus awarded).
- [ ] T012 [US2] In client/views/game_view.py, update the quest completion prompt handler to read `bonus_quest_id` and `bonus_vp` from the `QuestCompletionPromptResponse`. When rendering completable quest cards, if a card's ID matches `bonus_quest_id`, render "+4VP bonus" text (using `arcade.Text`) underneath that card. Store the bonus info so it can be included in game log on completion.
- [ ] T013 [US2] In client/views/game_view.py `_on_quest_completed()`, if `showcase_bonus_vp > 0` in the response, include "+N bonus VP from building" in the game log entry and update the player's VP display.

**Checkpoint**: Audition Showcase building is fully playable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Tests, documentation updates, validation

- [ ] T014 [P] Create tests/test_special_buildings.py with pytest tests covering: coins_per_building awards correct count, coins_per_building count is dynamic (changes as buildings are purchased), owner bonus does not trigger on self-visit, showcase bonus sets pending state correctly, showcase bonus +4 VP awarded when bonus contract completed, showcase bonus NOT awarded when different contract completed, showcase bonus cleared on skip, showcase with no completable quests advances turn
- [ ] T015 [P] Update specs/waterdeep-card-mapping.md to mark The Stone House and Heroes' Garden as DONE with their music-themed equivalents (Royalty Collection / Audition Showcase)
- [ ] T016 Run `pytest tests/` and `ruff check .` from project root — fix any failures or lint errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (building entries must exist before server logic references them)
- **User Stories (Phases 3–4)**: All depend on Phase 2 completion
  - US1 and US2 modify different code paths in `handle_place_worker()` so they CAN run in parallel
  - US2 also modifies `_check_quest_completion()`, `handle_complete_quest()`, `handle_skip_quest_completion()`, and `_advance_turn()` — these are unique to US2
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **US1 (P1)**: Adds a case to `handle_place_worker()` — no dependency on US2
- **US2 (P2)**: Adds a case to `handle_place_worker()`, modifies quest completion flow — no dependency on US1

### Parallel Opportunities

- T001 and T002 can run in parallel (same file but independent entries)
- T004 and T005 can run in parallel (same file but different models)
- US1 and US2 can run in parallel (different code paths)
- T014 and T015 can run in parallel (different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T005)
3. Complete Phase 3: US1 — Royalty Collection (T006)
4. **STOP and VALIDATE**: Test building_021 with varying building counts

### Incremental Delivery

1. Setup + Foundational → Config and schema ready
2. US1 → Royalty Collection building working
3. US2 → Audition Showcase building working
4. Polish → Tests pass, docs updated

---

## Notes

- US1 is a single-task implementation (T006) — the building-count reward is simple arithmetic
- US2 is multi-task because it introduces a new pending state flow that interacts with quest completion
- The `draw_contract_and_complete` flow reuses the existing `draw_contract` quest selection UI — the key difference is what happens after selection (bonus tracking + quest completion check instead of just adding to hand)
- Commit after each user story checkpoint
