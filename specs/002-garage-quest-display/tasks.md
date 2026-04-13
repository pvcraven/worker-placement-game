# Tasks: Garage Quest Display Rework

**Input**: Design documents from `/specs/002-garage-quest-display/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story. US2 (renaming) is foundational since all other work depends on consistent naming. US3 (face-up display) precedes US1 (spot actions) because quest selection requires the face-up display to exist.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational — Rename Cliffwatch Inn → The Garage, Garage → Backstage (US2)

**Goal**: Eliminate naming confusion by renaming all references across config, server, shared, and client code.

**Independent Test**: Search codebase for "cliffwatch" (should return 0 results outside specs/). Search for old "garage" references that should now be "backstage." All existing game mechanics should still work after rename.

- [X] T001 [US2] Rename GARAGE_SLOTS to BACKSTAGE_SLOTS in shared/constants.py
- [X] T002 [US2] Rename GarageSlot class to BackstageSlot, garage_slots field to backstage_slots in server/models/game.py
- [X] T003 [US2] Rename cliffwatch_inn_1/2/3 space IDs to the_garage_1/2/3, update names and space_type from "cliffwatch" to "garage" in config/board.json. Rename any space_type "garage" references (for intrigue/reassignment) to "backstage"
- [X] T004 [US2] Rename PlaceWorkerGarageRequest to PlaceWorkerBackstageRequest and WorkerPlacedGarageResponse to WorkerPlacedBackstageResponse in shared/messages.py. Update action strings from "place_worker_garage"/"worker_placed_garage" to "place_worker_backstage"/"worker_placed_backstage"
- [X] T005 [US2] Update server/lobby.py — change GarageSlot import to BackstageSlot, GARAGE_SLOTS to BACKSTAGE_SLOTS, update board.garage_slots to board.backstage_slots
- [X] T006 [US2] Update server/game_engine.py — rename all garage_slots references to backstage_slots, update space_type checks from "garage" to "backstage", update handle_place_worker_garage to handle_place_worker_backstage, update log messages from "Garage" to "Backstage"
- [X] T007 [US2] Update server/network.py — rename _handle_place_worker_garage to _handle_place_worker_backstage, update message routing
- [X] T008 [US2] Update client/ui/board_renderer.py — rename cliffwatch_inn_1/2/3 in _SPACE_LAYOUT to the_garage_1/2/3, rename _GARAGE_LAYOUT to _BACKSTAGE_LAYOUT, update "THE GARAGE" label to "BACKSTAGE", update garage_slot_ prefix in space IDs
- [X] T009 [US2] Update client/views/game_view.py — rename "worker_placed_garage" handler to "worker_placed_backstage", update _on_worker_placed_garage method name and log messages from "Garage" to "Backstage"
- [X] T010 [US2] Update server/models/config.py — update any board config schema references from "cliffwatch" to "garage" space type, add "backstage" as valid space type
- [X] T011 [US2] Update README.md — change "Use the Garage to play intrigue cards" to reference "Backstage"

**Checkpoint**: All renames complete. Existing game mechanics (Backstage intrigue/reassignment) work as before with new names. No "cliffwatch" or old "garage" references remain in non-spec code.

---

## Phase 2: Face-Up Quest Display + Deck Mechanics (US3)

**Goal**: Add four face-up quest cards drawn from a shuffled deck, with discard pile and reshuffle mechanics.

**Independent Test**: Start a game and verify four quest cards are displayed face-up. Verify state sync includes face-up card data.

- [X] T012 [US3] Add face_up_quests (list[ContractCard]), quest_deck (list[ContractCard]), and quest_discard (list[ContractCard]) fields to BoardState in server/models/game.py
- [X] T013 [US3] Add FACE_UP_QUEST_COUNT = 4 constant in shared/constants.py
- [X] T014 [US3] Implement quest deck initialization in server/lobby.py — shuffle all contract cards into quest_deck during _initialize_game(), draw 4 cards into face_up_quests
- [X] T015 [US3] Implement _draw_from_quest_deck() helper in server/game_engine.py — checks deck, reshuffles discard pile if empty, returns a card or None
- [X] T016 [US3] Add FaceUpQuestsUpdatedResponse message type in shared/messages.py with action "face_up_quests_updated" and face_up_quests list field
- [X] T017 [US3] Update _filter_state_for_player() in server/lobby.py to include face_up_quests in state sync (visible to all players). Exclude quest_deck and quest_discard from client state.
- [X] T018 [US3] Render face-up quest cards near The Garage area in client/ui/board_renderer.py — draw 4 card slots using CardRenderer, show card details (name, genre, cost, VP)
- [X] T019 [US3] Handle "face_up_quests_updated" message in client/views/game_view.py — update local state and trigger board re-render

**Checkpoint**: Game starts with 4 face-up quest cards visible to all players. Cards display correctly with name, genre, cost, VP.

---

## Phase 3: Garage Spot Actions + Quest Selection (US1)

**Goal**: Implement three distinct Garage spots — Spot 1 (quest + 2 coins), Spot 2 (quest + intrigue), Spot 3 (reset display) — with interactive card selection for Spots 1 & 2.

**Independent Test**: Place a worker on each Garage spot. Verify Spot 1 grants quest + coins, Spot 2 grants quest + intrigue card, Spot 3 discards and redraws. Verify deck reshuffle when deck is empty.

- [X] T020 [US1] Update config/board.json — change the three garage spots to have distinct reward_special values: "quest_and_coins" (Spot 1), "quest_and_intrigue" (Spot 2), "reset_quests" (Spot 3). Update display names to "The Garage (Spot 1: Quest + Coins)", "The Garage (Spot 2: Quest + Intrigue)", "The Garage (Spot 3: Reset)"
- [X] T021 [US1] Add SelectQuestCardRequest message in shared/messages.py with action "select_quest_card" and card_id field
- [X] T022 [US1] Add QuestCardSelectedResponse message in shared/messages.py with action "quest_card_selected", player_id, card_id, spot_number, bonus_reward, next_player_id fields
- [X] T023 [US1] Add QuestsResetResponse message in shared/messages.py with action "quests_reset", player_id, deck_reshuffled, next_player_id fields
- [X] T024 [US1] Implement handle_place_worker_garage() in server/game_engine.py for "garage" space_type — for Spots 1 & 2: place worker, set player state to "awaiting_quest_selection", send face-up cards. For Spot 3: place worker, discard face-up cards, draw 4 new cards, broadcast quests_reset and face_up_quests_updated, advance turn
- [X] T025 [US1] Implement handle_select_quest_card() in server/game_engine.py — validate card is in face_up_quests and player is awaiting selection, move card to player hand, grant bonus (Spot 1: 2 coins, Spot 2: draw 1 intrigue), draw replacement card, broadcast quest_card_selected and face_up_quests_updated, advance turn
- [X] T026 [US1] Route "select_quest_card" message in server/network.py to game_engine handler
- [X] T027 [US1] Implement quest card selection dialog in client/ui/dialogs.py — show face-up quest cards, let player click to select one, send SelectQuestCardRequest
- [X] T028 [US1] Handle "quest_card_selected" and "quests_reset" messages in client/views/game_view.py — update game log, refresh board display
- [X] T029 [US1] Update board_renderer.py to show distinct labels/rewards for each Garage spot (Spot 1: "+2$", Spot 2: "+Intrigue", Spot 3: "Reset")
- [X] T030 [US1] Trigger quest selection dialog in game_view.py when player places worker on Garage Spot 1 or 2 — intercept the worker_placed response for garage space_type and show dialog

**Checkpoint**: All three Garage spots work correctly. Quest selection dialog appears for Spots 1 & 2. Spot 3 resets the display. Deck reshuffles from discard when empty.

---

## Phase 4: Player Hand Display Toggle

**Goal**: Add toggle buttons for viewing the player's own quest and intrigue cards, hidden by default.

- [X] T031 [P] Add "My Quests" toggle button in client/views/game_view.py — UIFlatButton positioned above resource bar, toggles an overlay panel showing player's quest cards using CardRenderer
- [X] T032 [P] Add "My Intrigue" toggle button in client/views/game_view.py — UIFlatButton positioned next to "My Quests", toggles an overlay panel showing player's intrigue cards using CardRenderer
- [X] T033 Ensure hand panels only show the current player's cards (data already filtered by server) in client/views/game_view.py — verify _filter_state_for_player() excludes opponent hands

**Checkpoint**: Players can toggle visibility of their own quest and intrigue card hands. Other players' cards are never visible.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T034 Update game log messages throughout server/game_engine.py to use new Garage spot names and Backstage terminology consistently
- [X] T035 Verify the existing Backstage intrigue/reassignment flow still works end-to-end after all renames in server/game_engine.py
- [X] T036 Run quickstart.md scenarios manually — validate all 5 integration scenarios pass
- [X] T037 Verify card privacy — confirm other players cannot see quest or intrigue hands via state sync inspection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Rename/US2)**: No dependencies — can start immediately. BLOCKS all other phases.
- **Phase 2 (Face-Up Display/US3)**: Depends on Phase 1 completion.
- **Phase 3 (Spot Actions/US1)**: Depends on Phase 2 completion (needs face-up display and deck mechanics).
- **Phase 4 (Hand Toggle)**: Depends on Phase 1 only. Can run in parallel with Phases 2-3.
- **Phase 5 (Polish)**: Depends on all previous phases.

### User Story Dependencies

- **US2 (Rename)**: Foundational — must complete first
- **US3 (Face-Up Display)**: Depends on US2 (naming must be correct)
- **US1 (Spot Actions)**: Depends on US3 (face-up display must exist for quest selection)

### Parallel Opportunities

- Within Phase 1: T001-T011 must be sequential (cross-file rename consistency)
- Within Phase 2: T012-T13 can run in parallel, T16-T17 can run in parallel
- Phase 4 (T031-T032) can run in parallel with Phases 2-3

---

## Implementation Strategy

### MVP First (Face-Up Display + Spot 1)

1. Complete Phase 1: Rename everything
2. Complete Phase 2: Face-up display visible on board
3. Implement T020-T025 from Phase 3: Spot 1 (quest + coins) working
4. **STOP and VALIDATE**: Can a player see face-up quests and select one?

### Incremental Delivery

1. Phase 1 → Naming is clean
2. Phase 2 → Face-up cards visible to all players
3. Phase 3 → All three Garage spots functional with quest selection
4. Phase 4 → Players can view their own hands
5. Phase 5 → Polish and validation

---

## Notes

- This is a modification to an existing codebase, not a new project. All tasks modify existing files.
- The rename (Phase 1) touches many files but each change is straightforward find-and-replace style.
- The face-up display (Phase 2) introduces new server state that propagates to all clients.
- Quest selection (Phase 3) introduces a new two-phase interaction pattern (place worker → select card).
- Hand toggle (Phase 4) is purely client-side UI with no server changes needed.
