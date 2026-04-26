# Implementation Plan: Resource Trigger Plot Quests

**Branch**: `018-resource-trigger-plots` | **Date**: 2026-04-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/018-resource-trigger-plots/spec.md`

## Summary

Implement 5 resource trigger plot quest cards that grant automatic bonuses whenever the player gains a specific resource type from a board action. Three cards grant extra resources, one draws an intrigue card, and one prompts an optional resource swap. Follows the established plot quest bonus pattern (data-driven fields on ContractCard, evaluated at action time).

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source), websockets, Pydantic v2
**Storage**: In-memory game state; JSON config files in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade client) + headless server
**Project Type**: Multiplayer board game (client-server)
**Constraints**: Server-authoritative state; no direct client state mutation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | No new rendering needed — trigger bonuses flow through existing resource bar updates |
| II. Pydantic Data Modeling | PASS | New fields on ContractCard (Pydantic model). New message fields on existing Pydantic response models. |
| III. Client-Server Separation | PASS | Trigger logic lives in server/game_engine.py. Client only reads broadcast data. Shared models in shared/. |
| IV. Test-Driven Game Logic | PASS | Trigger logic is testable via pytest without Arcade dependency. |
| V. Simplicity First | PASS | Data-driven fields on existing models. One helper function. Reuses existing ResourceChoicePrompt for swap. |

## Project Structure

### Documentation (this feature)

```text
specs/018-resource-trigger-plots/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── spec.md              # Feature specification
```

### Source Code (files to modify)

```text
shared/
├── card_models.py         # Add 4 trigger fields to ContractCard
└── messages.py            # Add trigger_bonuses field to 2 response types

config/
└── contracts.json         # Tag 5 cards with trigger data

server/
└── game_engine.py         # Add _evaluate_resource_triggers() helper,
                           #   hook into handle_place_worker() and
                           #   handle_reassign_worker(), handle swap prompt

client/views/
└── game_view.py           # Read trigger_bonuses from responses,
                           #   update resources, game log display

tests/
└── test_resource_triggers.py  # New test file for trigger logic
```

## Implementation Details

### Phase 1: Data Model (shared/card_models.py)

Add to `ContractCard`:
```python
resource_trigger_type: str | None = None
resource_trigger_bonus: ResourceCost = Field(default_factory=ResourceCost)
resource_trigger_draw_intrigue: int = 0
resource_trigger_is_swap: bool = False
```

### Phase 2: Card Data (config/contracts.json)

Tag 5 existing cards:
- `contract_rock_001`: `resource_trigger_type: "guitarists"`, `resource_trigger_bonus: {guitarists: 1}`
- `contract_funk_002`: `resource_trigger_type: "guitarists"`, `resource_trigger_draw_intrigue: 1`
- `contract_soul_004`: `resource_trigger_type: "singers"`, `resource_trigger_is_swap: true`
- `contract_jazz_002`: `resource_trigger_type: "bass_players"`, `resource_trigger_bonus: {coins: 2}`
- `contract_pop_010`: `resource_trigger_type: "coins"`, `resource_trigger_bonus: {bass_players: 1}`

### Phase 3: Messages (shared/messages.py)

Add to `WorkerPlacedResponse` and `WorkerReassignedResponse`:
```python
trigger_bonuses: list[dict] = Field(default_factory=list)
```

### Phase 4: Server Logic (server/game_engine.py)

**Helper function** `_evaluate_resource_triggers(state, player, reward)`:
1. For each resource type in `reward` where amount > 0:
2. Scan `player.completed_contracts` for matching `resource_trigger_type`
3. For each match:
   - If `resource_trigger_bonus` has any nonzero values → add to player resources
   - If `resource_trigger_draw_intrigue > 0` → draw intrigue cards
   - If `resource_trigger_is_swap` → flag for interactive prompt (handled separately)
4. Return `(trigger_results: list[dict], pending_swap: dict | None)`

**Hook points**:
- `handle_place_worker()`: Call after line 817 (`player.resources.add(space.reward)`), also consider accumulating building stock. Pass `trigger_bonuses` in broadcast.
- `handle_reassign_worker()`: Call after line 2281 (`player.resources.add(target.reward)`). Pass `trigger_bonuses` in broadcast.

**Swap handling**:
- If a swap trigger is pending, store it in a new `state.pending_resource_trigger_swap` dict.
- Send `ResourceChoicePromptResponse` with `choice_type = "exchange"`, `is_spend = True`, `allowed_types` = all non-Singer resource types the player owns, `pick_count = 1`.
- On resolution (`handle_resource_choice()`), deduct the chosen resource and add 1 Singer.
- The player can skip the swap.

**Cancellation**:
- Store trigger bonus details in the relevant pending state.
- On cancel, reverse: deduct bonus resources, remove drawn intrigue cards (if trackable), reverse swap.

### Phase 5: Client (client/views/game_view.py)

- `_on_worker_placed()`: Read `trigger_bonuses` from message. For each entry, add bonus resources to player state. Update game log.
- `_on_worker_reassigned()`: Same pattern.
- Swap prompt: Already handled by existing `_on_resource_choice_prompt()` flow.

### Phase 6: Tests

Test cases for:
- Each of the 5 trigger types fires correctly
- No trigger without completed plot quest
- Multiple triggers on same resource type
- No cascade
- No trigger from non-board-action sources
- Cancellation reversal
