# Tasks: Quest Reward Expansion

**Input**: Design documents from `/specs/008-quest-reward-expansion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/websocket-messages.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. All directories and files exist.

*(No setup tasks — project structure is already in place.)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add new fields to shared models and message types used by all user stories.

- [x] T001 [P] Add `reward_draw_intrigue: int = 0`, `reward_draw_quests: int = 0`, `reward_quest_draw_mode: str = "random"`, and `reward_building: str | None = None` fields to `ContractCard` in shared/card_models.py.
- [x] T002 [P] Add `QuestRewardChoicePromptResponse` (action: "quest_reward_choice_prompt", fields: reward_type, available_choices list, quest_name), `QuestRewardChoiceRequest` (action: "quest_reward_choice", fields: choice_id), and `QuestRewardChoiceResolvedResponse` (action: "quest_reward_choice_resolved", fields: player_id, reward_type, choice dict, quest_name) to shared/messages.py. Add to ServerMessage/ClientMessage unions. Also add `drawn_intrigue: list[dict] = []`, `drawn_quests: list[dict] = []`, `building_granted: dict | None = None`, and `pending_choice: bool = False` fields to `QuestCompletedResponse`.
- [x] T003 [P] Add `pending_quest_reward: dict | None = None` field to `GameState` in server/models/game.py.
- [x] T004 Add route for `quest_reward_choice` action in server/network.py dispatch, calling `handle_quest_reward_choice` from server/game_engine.py.

**Checkpoint**: Models, messages, and routing ready for user story implementation.

---

## Phase 3: User Story 1 - Quest Rewards Give Resources and Cards (Priority: P1)

**Goal**: Players receive expanded rewards (resources, intrigue card draws, random quest card draws) upon quest completion. Non-interactive rewards resolve immediately.

**Independent Test**: Complete a quest that rewards VP + bonus resources + draw 1 intrigue card. Verify all rewards granted, cards appear in hand, resource bar updates.

### Implementation for User Story 1

- [x] T005 [US1] In server/game_engine.py `handle_complete_quest()`, after the existing VP and bonus_resources application, add reward resolution: if `contract.reward_draw_intrigue > 0`, draw that many intrigue cards from `state.board.intrigue_deck` and append to `player.intrigue_hand`. Collect drawn cards as `drawn_intrigue` list (using `c.model_dump()`).
- [x] T006 [US1] In server/game_engine.py `handle_complete_quest()`, if `contract.reward_draw_quests > 0` and `contract.reward_quest_draw_mode == "random"`, draw that many quest cards using `_draw_from_quest_deck(state)` and append to `player.contract_hand`. Collect drawn cards as `drawn_quests` list (using `c.model_dump()`).
- [x] T007 [US1] In server/game_engine.py `handle_complete_quest()`, if `contract.reward_quest_draw_mode == "choose"` and `contract.reward_draw_quests > 0`, set `state.pending_quest_reward` with player_id, reward_type="choose_quest", available_choices (face-up quests as dicts), and quest_name. Send `QuestRewardChoicePromptResponse` to the active player. Set `pending_choice=True` on the `QuestCompletedResponse` and `next_player_id=None` (don't advance turn yet). Return early before `_check_quest_completion`.
- [x] T008 [US1] In server/game_engine.py `handle_complete_quest()`, update the `QuestCompletedResponse` broadcast to include `drawn_intrigue`, `drawn_quests`, `building_granted=None`, and `pending_choice` fields.
- [x] T009 [US1] In server/game_engine.py, implement `handle_quest_reward_choice()`: validate `pending_quest_reward` exists for this player, validate `choice_id` is in available_choices. For reward_type "choose_quest": find the quest in face-up quests, remove from face-up, add to player's contract_hand, refill face-up from deck. Clear `pending_quest_reward`. Broadcast `QuestRewardChoiceResolvedResponse`. Then call `_check_quest_completion` or `_advance_turn` as appropriate.
- [x] T010 [US1] In client/views/game_view.py `_on_quest_completed()`, add handling for `drawn_intrigue` (append to local player's intrigue_hand if local player, else increment intrigue_hand_count), `drawn_quests` (append to contract_hand or increment contract_hand_count), and `building_granted` (handled in US2). Update resource bar after all changes.
- [x] T011 [US1] In client/views/game_view.py `_handle_message()`, add handler for "quest_reward_choice_prompt" action that calls `_on_quest_reward_choice_prompt(msg)`.
- [x] T012 [US1] In client/views/game_view.py, implement `_on_quest_reward_choice_prompt()`: for reward_type "choose_quest", show a selection dialog (similar to QuestCompletionDialog pattern) listing available quest cards. On select, send `{"action": "quest_reward_choice", "choice_id": selected_id}`.
- [x] T013 [US1] In client/views/game_view.py `_handle_message()`, add handler for "quest_reward_choice_resolved" action that calls `_on_quest_reward_choice_resolved(msg)`.
- [x] T014 [US1] In client/views/game_view.py, implement `_on_quest_reward_choice_resolved()`: for reward_type "choose_quest", add the chosen quest card to the local player's contract_hand (if local player), remove from face-up quests, update board renderer. Log to game_log_panel. Update turn via next_player_id.
- [x] T015 [US1] In client/views/game_view.py `_on_quest_completed()`, update game log to show all reward components (VP, resources, drawn cards) using a helper similar to `_format_intrigue_effect`.

**Checkpoint**: Non-interactive quest rewards (VP, resources, random card draws) work end-to-end. Interactive "choose quest" flow works with dialog, selection, and resolution.

---

## Phase 4: User Story 2 - Quest Rewards Include a Building (Priority: P2)

**Goal**: Quests can reward a free building via "market_choice" (player picks from face-up) or "random_draw" (auto-assign from deck).

**Independent Test**: Complete a quest with a "market_choice" building reward. Verify building selection dialog appears, player can pick a building, building is assigned for free.

### Implementation for User Story 2

- [x] T016 [US2] In server/game_engine.py `handle_complete_quest()`, if `contract.reward_building == "random_draw"`, draw from `state.board.building_deck`, assign to player using the existing building placement logic (create ActionSpace, assign lot), and include the building in `building_granted` on the response. If deck is empty, skip and log.
- [x] T017 [US2] In server/game_engine.py `handle_complete_quest()`, if `contract.reward_building == "market_choice"`, set `state.pending_quest_reward` with reward_type="choose_building", available_choices (face-up buildings as dicts). Send `QuestRewardChoicePromptResponse` to the player. Set `pending_choice=True`, `next_player_id=None`.
- [x] T018 [US2] In server/game_engine.py `handle_quest_reward_choice()`, add handling for reward_type "choose_building": find building in face-up buildings, remove from market, assign to player using building placement logic (create ActionSpace, assign lot, refill market from deck). Broadcast `QuestRewardChoiceResolvedResponse` with building details. Clear pending state, advance turn.
- [x] T019 [US2] In client/views/game_view.py `_on_quest_reward_choice_prompt()`, add handling for reward_type "choose_building": show a building selection dialog listing available buildings with their names and descriptions. On select, send `{"action": "quest_reward_choice", "choice_id": selected_id}`.
- [x] T020 [US2] In client/views/game_view.py `_on_quest_reward_choice_resolved()`, add handling for reward_type "choose_building": add building as a constructed building in local state, update board renderer, update building market display. Log to game_log_panel.
- [x] T021 [US2] In client/views/game_view.py `_on_quest_completed()`, if `building_granted` is not None (random-draw building), add building to local constructed buildings, update board renderer. Log the building grant.

**Checkpoint**: Building rewards work end-to-end. Both market choice and random draw modes function correctly.

---

## Phase 5: User Story 3 - Intrigue Card Reward Unification (Priority: P3)

**Goal**: Ensure intrigue card effects use the same draw functions as quest rewards. Verify existing draw_intrigue and draw_contracts effects work correctly with the shared functions.

**Independent Test**: Play an intrigue card that draws quest cards. Verify cards are drawn and added to hand.

### Implementation for User Story 3

- [x] T022 [US3] In server/game_engine.py, extract a shared `_draw_intrigue_cards(state, player, count)` helper that draws from `state.board.intrigue_deck` and appends to `player.intrigue_hand`, returning drawn card dicts. Use this helper in both `_resolve_intrigue_effect` (draw_intrigue branch) and `handle_complete_quest` (reward_draw_intrigue).
- [x] T023 [US3] In server/game_engine.py, verify `_draw_from_quest_deck` is used by both `_resolve_intrigue_effect` (draw_contracts branch) and `handle_complete_quest` (reward_draw_quests random mode). Refactor if needed to ensure shared usage.

**Checkpoint**: Both intrigue card effects and quest rewards use the same draw functions. No code duplication.

---

## Phase 6: User Story 4 - New Quest Content (Priority: P4)

**Goal**: Add new quest cards to the game configuration that utilize expanded rewards.

**Independent Test**: Start a game and verify new quests appear in the deck with correct reward descriptions.

### Implementation for User Story 4

- [x] T024 [US4] Add at least 6 new quest cards to config/contracts.json utilizing expanded reward types. Include at least: 1 quest with VP + intrigue card draw, 1 quest with VP + random quest card draw, 1 quest with VP + choose quest from face-up, 1 quest with VP + resources + intrigue draw, 1 quest with market_choice building reward, 1 quest with random_draw building reward. Balance costs and rewards appropriately for the game.
- [x] T025 [US4] In client/ui/card_renderer.py, update quest card rendering to display all reward components. Show VP, bonus resources, card draws ("Draw 1 Intrigue Card"), and building rewards ("Free Building from Market") as separate lines below the existing reward display.

**Checkpoint**: New quest content is in the game and displays correctly.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T026 Verify empty deck handling: complete quests with card draw rewards when intrigue/quest decks are empty. Confirm graceful skip and game log notification.
- [x] T027 Verify empty building market/deck handling: complete quests with building rewards when sources are empty. Confirm graceful skip.
- [ ] T028 Run quickstart.md scenarios 1-11 end-to-end and verify all test scenarios pass.
- [ ] T029 Verify Player Overview panel accurately reflects card counts and resources after quest completion with expanded rewards.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately
- **User Story 1 (Phase 3)**: Depends on Phase 2 (T001-T004 for models and messages)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (T009 for handle_quest_reward_choice base implementation)
- **User Story 3 (Phase 5)**: Depends on Phase 3 (needs reward draw code to exist before extracting helpers)
- **User Story 4 (Phase 6)**: Depends on Phase 3 (reward framework must exist for new quests to work)
- **Polish (Phase 7)**: Depends on all user stories being complete

### Within Each User Story

- US1: T005/T006 (server draws) → T007 (server choose flow) → T008 (response update) → T009 (choice handler) → T010-T015 (client handlers)
- US2: T016 (random building) → T017 (market choice server) → T018 (choice handler) → T019-T021 (client handlers)
- US3: T022/T023 (extract shared helpers)
- US4: T024 (config data) → T025 (card display)

### Parallel Opportunities

- T001, T002, T003 can run in parallel (different files: card_models.py, messages.py, game.py)
- T022 and T023 can run in parallel (different code sections)
- T024 and T025 can run in parallel (different files: contracts.json, card_renderer.py)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T004)
2. Complete Phase 3: User Story 1 (T005-T015)
3. **STOP and VALIDATE**: Complete a quest with card draw rewards, verify all rewards granted
4. Non-interactive rewards alone deliver immediate value — quests are more interesting

### Incremental Delivery

1. Foundational → Models and messages ready
2. Add User Story 1 → Card draw rewards work → Validate
3. Add User Story 2 → Building rewards work → Validate
4. Add User Story 3 → Shared draw helpers → Validate
5. Add User Story 4 → New quest content → Validate
6. Polish → Quickstart validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Existing quest data in contracts.json is unchanged — new fields default to 0/None (backward compatible)
- The `pending_quest_reward` state pattern mirrors `pending_intrigue_target` from feature 007
- Building placement logic (lot assignment, ActionSpace creation, market refill) should be extracted from `handle_purchase_building` into a reusable helper for T016/T018
- Commit after each task or logical group
