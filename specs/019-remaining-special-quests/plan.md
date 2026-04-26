# Implementation Plan: Remaining Special Quest Mechanics

**Branch**: `019-remaining-special-quests` | **Date**: 2026-04-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/019-remaining-special-quests/spec.md`

## Summary

Implement 6 remaining special quest mechanics: 2 one-time completion rewards (play intrigue, opponent gains coins) and 4 persistent plot quest abilities (extra worker, round-start resource, worker recall, use occupied building). These complete the full quest card set so all 60 cards are playable.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop
**Project Type**: Desktop game (client-server, local multiplayer)
**Constraints**: Server-authoritative architecture; all state mutations on server; client renders from broadcast messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | New UI elements (recall button, opponent chooser) will use `arcade.Text` and `ShapeElementList`, no draw calls |
| II. Pydantic Data Modeling | PASS | New fields on ContractCard, Player, GameState use Pydantic models. New message types use BaseModel |
| III. Client-Server Separation | PASS | All mechanics live in server/game_engine.py. Client only renders state from broadcasts |
| IV. Test-Driven Game Logic | PASS | Each mechanic gets server-side pytest tests |
| V. Simplicity First | PASS | Each mechanic is minimal — data-driven fields, simple boolean flags, no new abstractions |

## Project Structure

### Documentation (this feature)

```text
specs/019-remaining-special-quests/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── tasks.md             # Created by /speckit.tasks
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
shared/
├── card_models.py       # ContractCard: 4 new fields
├── messages.py          # New/updated response types
└── constants.py         # No changes needed

server/
├── game_engine.py       # Core: 6 mechanics + round-start hook
└── models/
    └── game.py          # Player: 2 new flags; GameState: 2 new pending dicts

client/
└── views/
    └── game_view.py     # Client handlers for new messages

config/
└── contracts.json       # Tag 6 cards with new fields

tests/
└── test_special_quests.py  # New test file

specs/
└── waterdeep-card-mapping.md  # Update status of 6 mechanics to DONE
```

**Structure Decision**: All changes fit within the existing project structure. No new modules or packages needed.

## Detailed Design

### User Story 1: One-Time Completion Rewards (P1)

#### 1a. Play Intrigue on Completion (contract_jazz_010)

**Card data**: `reward_play_intrigue: 1` (already in contracts.json, needs schema field)

**Server flow** in `handle_complete_quest()` after existing reward grants (line ~1786):
1. If `contract.reward_play_intrigue > 0` and player has intrigue cards in hand:
   - Set `state.pending_play_intrigue = {"player_id": player.player_id, "count": contract.reward_play_intrigue}`
   - Set `has_interactive = True` on QuestCompletedResponse
   - Send `IntriguePlayPromptResponse` to the completing player with their intrigue hand
2. If player has no intrigue cards: skip (no prompt, no blocking)
3. When player selects a card: reuse the existing `_resolve_intrigue_effect()` flow from backstage
   - This requires a new handler `handle_play_intrigue_from_quest()` that:
     - Validates the pending state
     - Removes card from hand, resolves effect
     - Awards plot quest bonus VP if applicable (bonus_vp_per_intrigue_played)
     - If targeting needed, chains to existing IntrigueTargetPromptResponse flow
     - On resolution, calls `_advance_turn()` or `_finish_reassignment()`

**New message**: `IntriguePlayPromptResponse` — tells client to show intrigue card selection dialog
**New request**: `PlayIntrigueFromQuestRequest` — player's intrigue card choice
**Updated message**: `QuestCompletedResponse` — add `pending_play_intrigue: bool = False` field

#### 1b. Opponent Gains Coins (contract_pop_008)

**Card data**: `reward_opponent_gains_coins: 4` (already in contracts.json, needs schema field)

**Server flow** in `handle_complete_quest()` after existing reward grants:
1. If `contract.reward_opponent_gains_coins > 0`:
   - Count opponents (all players except completing player)
   - If exactly 1 opponent: auto-grant coins, no prompt needed
   - If 2+ opponents: set `state.pending_opponent_coins = {"player_id": player.player_id, "coins": contract.reward_opponent_gains_coins}`, send `OpponentChoicePromptResponse`, set `has_interactive = True`
2. Broadcast includes which opponent received coins

**New message**: `OpponentChoicePromptResponse` — list of opponents to choose from
**New request**: `ChooseOpponentRequest` — player picks who gets the coins
**Updated message**: `QuestCompletedResponse` — add `opponent_coins_granted: dict | None = None`

### User Story 2: Extra Permanent Worker (P2, contract_rock_009)

**Card data**: `reward_extra_worker: 1` (new field, add to contracts.json)

**Server flow** in `handle_complete_quest()`:
1. If `contract.reward_extra_worker > 0`:
   - `player.total_workers += contract.reward_extra_worker`
   - Do NOT add to `available_workers` this round (FR-006: available next round)
   - Log the gain

**Updated message**: `QuestCompletedResponse` — add `extra_workers_granted: int = 0`

**Client**: Display "Gained 1 extra permanent worker" in game log. Update worker count display.

### User Story 3: Round-Start Resource Choice (P3, contract_soul_007)

**Card data**: `reward_choose_resource_per_round: bool = True` (new field)

**Server flow** — new section in `_end_round()` after round advancement (line ~372), before turn order:
1. For each player (in turn order), scan `completed_contracts` for `reward_choose_resource_per_round`
2. If any player has this benefit, set `state.pending_round_start_choices` with the list of players needing choices
3. Send `RoundStartResourceChoicePromptResponse` to the first pending player
4. New handler `handle_round_start_resource_choice()`:
   - Validate the pending state, validate chosen resource is non-coin
   - Grant 1 unit of chosen resource, log it
   - Broadcast `RoundStartBonusResponse` with `{player_id, resource_type, amount}`
   - If more players pending, prompt next player
   - If all resolved, clear pending state (round proceeds normally to first turn)

**New messages**:
- `RoundStartResourceChoicePromptResponse` — prompt player to pick a non-coin resource
- `RoundStartResourceChoiceRequest` — player's resource selection
- `RoundStartBonusResponse` — broadcast per-player resource grant

### User Story 4: Worker Recall on Completion (P4, contract_funk_001)

**Card data**: `reward_recall_worker: bool = True` (new field — one-time completion effect)

**Server flow** in `handle_complete_quest()` after existing reward grants:
1. If `contract.reward_recall_worker` and player has at least one worker placed on a board action space:
   - Set `state.pending_worker_recall = {"player_id": player.player_id}`
   - Set `has_interactive = True` on QuestCompletedResponse
   - Send `WorkerRecallPromptResponse` to the completing player with list of their occupied spaces
2. If player has no workers on the board: skip (no prompt, no blocking)
3. New handler `handle_recall_worker(server, conn, msg)`:
   - Validate pending state exists
   - Validate the target space is occupied by this player's worker
   - Free the space (`space.occupied_by = None`)
   - `player.available_workers += 1`
   - Clear `state.pending_worker_recall`
   - Broadcast `WorkerRecalledResponse`
   - Continue to `_advance_turn()` or `_finish_reassignment()`

**New message**: `WorkerRecallPromptResponse` — tells client to show "click a space" prompt with list of player's occupied spaces
**New request**: `RecallWorkerRequest` with `space_id: str`
**New message**: `WorkerRecalledResponse` with `player_id`, `space_id`

**Client**:
- On `WorkerRecallPromptResponse`: show message at top of screen ("Select a worker to recall"), highlight player's occupied spaces as clickable
- On click: send `RecallWorkerRequest` with that space_id
- On `WorkerRecalledResponse`: update local state (free space, increment available workers)

### User Story 5: Use Occupied Building (P5, contract_funk_005)

**Card data**: `reward_use_occupied_building: bool = True` (new field)

**Player state**: Add `use_occupied_used_this_round: bool = False` to Player model

**Server flow** — modify `handle_place_worker()` occupancy check (line 889):
1. Current check: `if space.occupied_by is not None: → error`
2. New check:
   ```
   if space.occupied_by is not None:
       if not _can_use_occupied(player, space, state):
           → error "SPACE_OCCUPIED"
       else:
           player.use_occupied_used_this_round = True
           # Don't clear space.occupied_by — both workers coexist
           # Continue with normal placement flow
   ```
3. `_can_use_occupied(player, space, state)` checks:
   - Player has completed contract with `reward_use_occupied_building`
   - `not player.use_occupied_used_this_round`
   - `space.space_type == "building"` (not permanent/castle/backstage)
   - `space.occupied_by != player.player_id` (not own worker)
4. The space needs to support multiple occupants. Change `occupied_by: str | None` to track dual occupation. Simplest approach: add `second_occupied_by: str | None = None` to ActionSpace, since at most 2 can occupy via this ability. When clearing at round end, clear both.

**Alternative (simpler)**: Since workers are returned at round end and the only effect is "can I place here", we can use a list or just track the second placement separately. Let's use `occupied_by_list: list[str] = []` on ActionSpace? No — that's a bigger refactor. Instead: keep `occupied_by` as the first occupant, add `also_occupied_by: str | None = None`. At round end, clear both.

In `_end_round()`: also clear `space.also_occupied_by = None`

5. In `_end_round()` line 349: reset `player.use_occupied_used_this_round = False`

**Client**: When building is occupied by another player but player has unused use-occupied ability, show it as a valid placement option (not grayed out).

### Cross-Cutting: Update waterdeep-card-mapping.md

After all mechanics are implemented, update `specs/waterdeep-card-mapping.md` to mark all 6 mechanics as DONE.

## File Changes Summary

| File | Changes |
|------|---------|
| `shared/card_models.py` | 5 new fields on ContractCard |
| `config/contracts.json` | 6 cards tagged with new fields |
| `server/models/game.py` | 1 new Player field, 3 new GameState pending dicts, 1 new ActionSpace field |
| `shared/messages.py` | ~5 new message/request types, updates to QuestCompletedResponse |
| `server/game_engine.py` | Quest completion rewards, round-start hook, recall handler, occupied-building override |
| `server/network.py` | Route new request types to handlers |
| `client/views/game_view.py` | Handle new response types, recall UI, occupied-building highlighting |
| `tests/test_special_quests.py` | Tests for all 6 mechanics |
| `specs/waterdeep-card-mapping.md` | Mark 6 mechanics as DONE |

## Complexity Tracking

No constitution violations. All changes fit within existing patterns.
