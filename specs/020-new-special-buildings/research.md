# Research: New Special Buildings

## R1: How to count player-purchased buildings

**Decision**: Use `len(state.board.constructed_buildings)` to count all purchased buildings in play.

**Rationale**: `state.board.constructed_buildings` is a `list[str]` of space IDs for every building purchased by any player. This list already exists and is maintained by `handle_purchase_building()` (line 2370 in game_engine.py). It counts all player-purchased buildings regardless of owner, which is exactly what "building tiles in play" means.

**Alternatives considered**:
- Counting `action_spaces` where `space_type == "building"` — rejected because it would also require filtering and is less direct.
- Adding a separate counter — rejected because the data already exists.

## R2: How to implement the building-count visitor reward

**Decision**: Add a new `visitor_reward_special` value: `"coins_per_building"`. Handle it in `handle_place_worker()` alongside existing special reward processing (around line 1066-1088).

**Rationale**: The existing pattern for special visitor rewards uses string-based dispatch on `visitor_reward_special`. Adding a new value follows the established pattern without modifying the building data model. The reward calculation is `len(state.board.constructed_buildings)` coins.

**Alternatives considered**:
- Adding a new boolean field like `reward_coins_per_building` — rejected because the existing `visitor_reward_special` pattern handles this cleanly.
- Computing at config load time — rejected because the count must be dynamic (calculated at visit time).

## R3: How to implement the showcase building (draw contract + optional immediate completion)

**Decision**: Add a new `visitor_reward_special` value: `"draw_contract_and_complete"`. The server flow:
1. Player selects a face-up contract (reuse existing `handle_select_quest_card` selection UI)
2. Server adds the contract to the player's hand
3. Server draws a replacement from the deck
4. Server marks the contract as eligible for +4 VP bonus (via a new pending state field)
5. Server calls `_check_quest_completion()` — the normal quest completion flow runs
6. If the player completes the bonus-eligible contract, +4 VP is added
7. If they complete a different contract or skip, no bonus

**Rationale**: This reuses the existing quest completion flow (FR-005). The key insight is that after the contract is added to the player's hand, `_check_quest_completion()` already knows how to find completable quests and prompt the player. We only need to track which contract (if any) has the bonus, so the server can add +4 VP if that specific contract is completed.

**Alternatives considered**:
- A completely new flow with separate messages — rejected because the spec explicitly requires reusing the existing quest completion window.
- Handling the bonus purely on the client — rejected because the server must be authoritative for VP.

## R4: Client-side "+4VP bonus" text display

**Decision**: The server sends the bonus-eligible contract ID in the `QuestCompletionPromptResponse` (new optional field `bonus_quest_id` and `bonus_vp`). The client renders "+4VP bonus" text under that specific contract card in the quest completion window.

**Rationale**: The server already sends `completable_quests` in the prompt. Adding the bonus contract ID lets the client annotate the correct card without any new dialog. If the bonus contract isn't in the completable list (player can't afford it), the field is omitted and no annotation appears.

**Alternatives considered**:
- Sending a separate message — rejected because it would complicate the flow and require client-side state coordination.

## R5: Tracking the bonus-eligible contract

**Decision**: Add `pending_showcase_bonus: dict | None = None` to GameState. When a contract is drawn from the showcase building, set it to `{"player_id": ..., "contract_id": ..., "bonus_vp": 4}`. In `handle_complete_quest()`, if the completed contract matches the pending bonus, add the VP. Clear the pending state after quest completion resolves (whether bonus was awarded or not).

**Rationale**: Follows the existing `pending_*` pattern used throughout the codebase (pending_play_intrigue, pending_opponent_coins, etc.). The pending state is cleared when the quest completion phase ends, regardless of which quest was completed.

**Alternatives considered**:
- Storing the bonus on the contract itself — rejected because it would persist incorrectly if the contract is completed later in a normal turn.
