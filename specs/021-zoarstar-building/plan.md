# Implementation Plan: Shadow Studio Building + Bootleg Recording Intrigue Card

**Branch**: `021-zoarstar-building` | **Date**: 2026-04-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/021-zoarstar-building/spec.md`

## Summary

Add the Shadow Studio building (8 coins, `visitor_reward_special: "copy_occupied_space"`, owner bonus 2 VP) and two "Bootleg Recording" intrigue cards (`effect_type: "copy_occupied_space"`, cost 2 coins). Both share a core mechanic: the player selects an opponent-occupied action space and receives that space's rewards (including specials, accumulated stock, resource choices, owner bonus cascading, and resource triggers) without placing a second worker. A shared `_get_copy_eligible_spaces()` helper and `_resolve_copied_space_rewards()` function implement the mechanic for both delivery paths. New `SelectCopySpaceRequest` / `CopySpacePromptResponse` / `CancelCopySpaceRequest` message types handle the selection flow. Full cancel/unwind support at every deferred step.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows)
**Project Type**: Multiplayer board game (client-server)
**Constraints**: Server-authoritative architecture; all state mutations on server

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Space selection UI will use existing prompt/dialog patterns (arcade.Text, ShapeElementList) |
| II. Pydantic Data Modeling | PASS | New message types as Pydantic models; config entries in JSON with existing model fields |
| III. Client-Server Separation | PASS | All copy logic on server; client renders prompts and sends selection |
| IV. Test-Driven Game Logic | PASS | Tests for building copy, intrigue card copy, cancel/unwind, edge cases |
| V. Simplicity First | PASS | Shared helper reuses existing reward-granting patterns; no new abstractions |
| VI. Server-Authoritative Message Protocol | PASS | New Request/Response pair for copy space selection; broadcast on resolution |
| VII. Config-Driven Game Content | PASS | Building and intrigue card added via JSON config with existing model fields + one new `effect_type` value |
| VIII. Pending State for Deferred Actions | PASS | Uses `pending_placement` with `deferred_action: "copy_space_selection"` for both paths |
| IX. Cancel/Unwind Reversibility | PASS | Cancel returns coins (intrigue path), unwinds placement, uses `_unwind_placement()` |
| X. Post-Action Turn Flow | PASS | After copy resolves, standard `_check_quest_completion()` → `_advance_turn()` |

No violations. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/021-zoarstar-building/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── spec.md              # Feature specification
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (files modified)

```text
config/
├── buildings.json           # Add building_023 (Shadow Studio)
└── intrigue.json            # Add intrigue_053, intrigue_054 (Bootleg Recording)

shared/
├── card_models.py           # No changes needed (BuildingTile already has visitor_reward_special; IntrigueCard already has effect_type/effect_value)
└── messages.py              # Add SelectCopySpaceRequest, CancelCopySpaceRequest, CopySpacePromptResponse

server/
├── models/game.py           # Add pending_copy_source: dict | None to GameState
├── game_engine.py           # Add _get_copy_eligible_spaces(), _resolve_copied_space_rewards(); handle copy_occupied_space in building + intrigue paths; new handlers for select/cancel
└── network.py               # Add _handle_select_copy_space, _handle_cancel_copy_space routes

client/
└── views/game_view.py       # Handle CopySpacePromptResponse (space selection dialog), send select/cancel messages

tests/
└── test_copy_occupied_space.py  # New test file for building + intrigue card copy mechanic

specs/
└── waterdeep-card-mapping.md    # Mark The Zoarstar as DONE
```

**Structure Decision**: All changes are modifications to existing files plus new JSON entries and one new test file. No new modules or packages needed.

## Implementation Approach

### Shared Core: `_get_copy_eligible_spaces()` and `_resolve_copied_space_rewards()`

**`_get_copy_eligible_spaces(state, player) -> list[dict]`** (~15 lines):
- Iterates `state.board.action_spaces` and filters to spaces where:
  - `space.occupied_by is not None`
  - `space.occupied_by != player.player_id`
  - `space.space_type != "backstage"` (backstage slots are separate from action_spaces, so this is implicit)
- Returns list of `{"space_id": ..., "name": ..., "space_type": ..., "reward_preview": ...}` for the prompt

**`_resolve_copied_space_rewards(server, state, player, target_space, source_space_id, pending) -> None`** (~80 lines):
Extracts and applies rewards from `target_space` to `player`. Reuses the same patterns as `handle_reassign_worker` lines 2997-3112:

1. **Base resource reward**: `player.resources.add(target_space.reward)` + build `reward_dict`
2. **Accumulated stock**: If building with `accumulation_type`, drain stock and add to reward
3. **Visitor VP**: If building with `visitor_reward_vp`, grant VP
4. **Building specials** (draw_intrigue, coins_per_building, draw_contract, draw_contract_and_complete):
   - `draw_intrigue`: Draw card, add to hand
   - `coins_per_building`: Grant coins equal to constructed building count
   - `draw_contract` / `draw_contract_and_complete`: Set `pending_building_quest`, return early (deferred)
   - `copy_occupied_space`: If copying Shadow Studio (nested copy), recursively enter copy selection. Edge case — limited by practical board state.
5. **Resource choice**: If building has `visitor_reward_choice`, set `pending_resource_choice`, return early (deferred)
6. **Owner bonus of copied building**: If `target_space.space_type == "building"` and owner exists and is not the copying player, grant owner bonus (resources, VP, specials). This cascading is per FR-008/FR-019.
7. **Resource triggers**: Call `_evaluate_resource_triggers(state, player, reward_cost)` on the copied rewards
8. **Castle special**: If copying castle, grant first player marker + draw intrigue
9. **Garage special**: If copying garage, enter quest selection flow (deferred)
10. **Realtor special**: If copying realtor, enter building purchase flow (deferred)

After resolution (or at each deferred return point), update `state.pending_placement` with the copy-specific data including `source_space_id` (Shadow Studio or backstage slot) and `copied_from_space_id` (the target).

### US1 + US3: Shadow Studio Building (copy_occupied_space special)

**Config** (`config/buildings.json`):
```json
{
  "id": "building_023",
  "name": "Shadow Studio",
  "description": "A mysterious studio that can mirror any other studio's session.",
  "cost_coins": 8,
  "visitor_reward": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "visitor_reward_special": "copy_occupied_space",
  "owner_bonus": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "owner_bonus_vp": 2
}
```

**Server — `handle_place_worker()`** (`server/game_engine.py`):

In the building `visitor_reward_special` handling block (after line 1244), add:

```python
elif special == "copy_occupied_space":
    eligible = _get_copy_eligible_spaces(state, player)
    if not eligible:
        # No valid targets — turn proceeds normally (FR-010)
        pass  # Fall through to _check_quest_completion
    else:
        state.pending_placement = _pending
        state.pending_copy_source = {
            "player_id": player.player_id,
            "source_space_id": msg.space_id,
            "source_type": "building",
            "eligible_spaces": eligible,
        }
        await server.send_to_player(
            player.player_id,
            CopySpacePromptResponse(
                eligible_spaces=eligible,
                source_type="building",
            ),
        )
        return
```

Note: The `_pending` dict and owner bonus for the Shadow Studio itself are already handled by the preceding code. The copy selection is deferred.

### US2: Owner Bonus

No special implementation needed — Shadow Studio's owner bonus (2 VP) is handled by the existing owner bonus block (lines 1252-1286) since `owner_bonus_vp: 2` is set in the building config.

### US5: Bootleg Recording Intrigue Card

**Config** (`config/intrigue.json`):
```json
{
  "id": "intrigue_053",
  "name": "Bootleg Recording",
  "description": "Slip into a rival's studio and bootleg their session. Pay 2 coins to copy any opponent's occupied space.",
  "effect_type": "copy_occupied_space",
  "effect_target": "self",
  "effect_value": {"cost_coins": 2}
},
{
  "id": "intrigue_054",
  "name": "Bootleg Recording",
  "description": "Slip into a rival's studio and bootleg their session. Pay 2 coins to copy any opponent's occupied space.",
  "effect_type": "copy_occupied_space",
  "effect_target": "self",
  "effect_value": {"cost_coins": 2}
}
```

**Server — `_resolve_intrigue_effect()`** (`server/game_engine.py`):

Add new elif at line ~1991 (after `resource_choice` / `resource_choice_multi`):

```python
elif card.effect_type == "copy_occupied_space":
    cost_coins = ev.get("cost_coins", 0)
    if player.resources.coins < cost_coins:
        effect["insufficient_coins"] = True
        return effect
    eligible = _get_copy_eligible_spaces(state, player)
    if not eligible:
        effect["no_valid_targets"] = True
        return effect
    player.resources.coins -= cost_coins
    effect["pending"] = True
    effect["cost_deducted"] = cost_coins
    effect["eligible_spaces"] = eligible
```

**Server — `handle_place_worker_backstage()`** (`server/game_engine.py`):

After `_resolve_intrigue_effect()` call, add handling for the three new states:

1. **`insufficient_coins`**: Unwind backstage placement — return card to hand, free slot, return worker. Send error message.
2. **`no_valid_targets`**: Same unwind. Send error message.
3. **`pending` (copy_occupied_space)**: Set `pending_copy_source` with `source_type: "intrigue"` and `cost_deducted`. Send `CopySpacePromptResponse` to player. Return early.

### New Handlers: `handle_select_copy_space()` and `handle_cancel_copy_space()`

**`handle_select_copy_space(server, conn, msg)`** (~60 lines):

1. Validate `state.pending_copy_source` exists and `player_id` matches
2. Validate `msg.space_id` is in `eligible_spaces`
3. Look up `target_space = state.board.action_spaces[msg.space_id]`
4. Call `_resolve_copied_space_rewards(server, state, player, target_space, ...)`
5. If the resolution is immediate (no deferred action):
   - Broadcast `WorkerPlacedResponse` (for building source) or `WorkerPlacedBackstageResponse` (for intrigue source) with the copied rewards
   - Clear `pending_copy_source`
   - Call `_check_quest_completion()` → `_advance_turn()`
6. If the resolution is deferred (resource choice, quest selection, building purchase):
   - Store the deferred state in `pending_placement`
   - The deferred handler resolves normally and clears pending state on completion

**`handle_cancel_copy_space(server, conn, msg)`** (~30 lines):

1. Read `state.pending_copy_source`
2. If `source_type == "intrigue"` and `cost_deducted > 0`:
   - Return coins: `player.resources.coins += cost_deducted`
3. Call `_unwind_placement(state, player, state.pending_placement)` to free the source space (Shadow Studio or backstage slot) and reverse any already-granted rewards (Shadow Studio's base reward, owner bonus)
4. Clear `pending_copy_source` and `pending_placement`
5. Broadcast `PlacementCancelledResponse`

### New Messages (`shared/messages.py`)

```python
class SelectCopySpaceRequest(BaseModel):
    action: Literal["select_copy_space"] = "select_copy_space"
    space_id: str

class CancelCopySpaceRequest(BaseModel):
    action: Literal["cancel_copy_space"] = "cancel_copy_space"

class CopySpacePromptResponse(BaseModel):
    action: Literal["copy_space_prompt"] = "copy_space_prompt"
    eligible_spaces: list[dict]
    source_type: str  # "building" or "intrigue"
```

Add `SelectCopySpaceRequest` and `CancelCopySpaceRequest` to `ClientMessage` union.

### New Model Field (`server/models/game.py`)

```python
pending_copy_source: dict | None = None
```

Added after `pending_placement` on GameState.

### Network Routing (`server/network.py`)

Add two handler methods:
```python
async def _handle_select_copy_space(self, conn, msg) -> None:
    from server.game_engine import handle_select_copy_space
    await handle_select_copy_space(self, conn, msg)

async def _handle_cancel_copy_space(self, conn, msg) -> None:
    from server.game_engine import handle_cancel_copy_space
    await handle_cancel_copy_space(self, conn, msg)
```

### Client UI (`client/views/game_view.py`)

**`_on_copy_space_prompt(msg)`**: New handler for `CopySpacePromptResponse`:
- Display a selection dialog listing eligible spaces with their names, types, and reward previews
- Similar to `_on_intrigue_target_prompt()` (lines 529-575) but listing spaces instead of players
- `on_select(space_id)` → send `{"action": "select_copy_space", "space_id": space_id}`
- `on_cancel()` → send `{"action": "cancel_copy_space"}`

Register in `_register_message_handlers()` mapping `"copy_space_prompt"` → `_on_copy_space_prompt`.

### Cancel/Unwind Flow Summary

| Cancel Point | Source | Coins Returned | Placement Unwound | Card Returned |
|-------------|--------|----------------|-------------------|---------------|
| Space selection (building) | Shadow Studio | N/A | Yes (Shadow Studio freed) | N/A |
| Space selection (intrigue) | Bootleg Recording | Yes (2 coins) | Yes (backstage slot freed) | Yes (to hand) |
| Deferred action after copy (resource choice, quest selection) | Either | Intrigue: Yes | Yes | Intrigue: Yes |

### Documentation Update

**Spec mapping** (`specs/waterdeep-card-mapping.md`):
- Mark The Zoarstar as DONE with music-themed equivalent (Shadow Studio / Bootleg Recording)
