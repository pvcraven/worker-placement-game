# Implementation Plan: New Special Buildings

**Branch**: `020-new-special-buildings` | **Date**: 2026-04-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/020-new-special-buildings/spec.md`

## Summary

Add two new purchasable buildings to the game: a "Royalty Collection" building (awards 1 coin per building in play) and an "Audition Showcase" building (draw a face-up contract, optionally complete immediately for +4 VP bonus). The Royalty Collection building uses a new `visitor_reward_special` value with a simple building-count calculation. The Audition Showcase reuses the existing quest completion window, adding bonus VP tracking via a new pending state field.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source), websockets, Pydantic v2
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows)
**Project Type**: Multiplayer board game (client-server)
**Constraints**: Server-authoritative architecture; all state mutations on server

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | No new draw calls; "+4VP bonus" text will use `arcade.Text` |
| II. Pydantic Data Modeling | PASS | New fields added to existing Pydantic models; new buildings in JSON config |
| III. Client-Server Separation | PASS | All reward logic on server; client renders messages |
| IV. Test-Driven Game Logic | PASS | Tests for both building mechanics |
| V. Simplicity First | PASS | Reuses existing quest completion flow; no new abstractions |

No violations. All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/020-new-special-buildings/
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
└── buildings.json           # Add 2 new building entries

shared/
├── card_models.py           # No changes needed (BuildingTile model already has visitor_reward_special)
└── messages.py              # Add bonus fields to QuestCompletionPromptResponse, QuestCompletedResponse

server/
├── models/game.py           # Add pending_showcase_bonus to GameState
└── game_engine.py           # Handle coins_per_building, draw_contract_and_complete, bonus VP in quest completion

client/
└── views/game_view.py       # Render "+4VP bonus" text in quest completion window

tests/
└── test_special_buildings.py # New test file for both buildings

specs/
└── waterdeep-card-mapping.md # Mark Stone House + Heroes' Garden as DONE
```

**Structure Decision**: All changes are modifications to existing files plus two new JSON entries and one new test file. No new modules or packages needed.

## Implementation Approach

### US1: Royalty Collection Building (coins_per_building)

**Server changes** (`server/game_engine.py`):
- In `handle_place_worker()`, after the existing `draw_intrigue` special handling (~line 1086), add a case for `visitor_reward_special == "coins_per_building"`:
  - Calculate `coin_count = len(state.board.constructed_buildings)`
  - Add `coin_count` to `player.resources.coins`
  - Include in the reward dict for the broadcast

**Config** (`config/buildings.json`):
- Add `building_021` with `visitor_reward_special: "coins_per_building"`, `owner_bonus: {coins: 2}`, `cost_coins: 4`

**No client changes needed** — coins are granted via standard reward processing and the existing WorkerPlacedResponse already carries the reward totals.

### US2: Audition Showcase Building (draw_contract_and_complete)

**Server changes** (`server/game_engine.py`):
- In `handle_place_worker()`, add a case for `visitor_reward_special == "draw_contract_and_complete"`:
  - Enter quest selection highlight mode (same as `draw_contract` but with a flag)
  - RETURN early (selection is deferred)
- In `handle_select_quest_card()` or a new handler, when the showcase flow is active:
  - Add selected contract to player's hand
  - Draw replacement from deck
  - Set `state.pending_showcase_bonus = {"player_id": player.player_id, "contract_id": contract.id, "bonus_vp": 4}`
  - Call `_check_quest_completion()` — this sends the prompt with completable quests
- Modify `_check_quest_completion()` to include `bonus_quest_id` and `bonus_vp` in `QuestCompletionPromptResponse` when `pending_showcase_bonus` is set and the bonus contract is in the completable list
- In `handle_complete_quest()`, after base VP award, check if `state.pending_showcase_bonus` matches the completed contract — if so, add bonus VP
- Clear `pending_showcase_bonus` when quest completion phase ends (in `_advance_turn` or `handle_skip_quest_completion`)

**Server model** (`server/models/game.py`):
- Add `pending_showcase_bonus: dict | None = None` to GameState

**Messages** (`shared/messages.py`):
- Add `bonus_quest_id: str | None = None` and `bonus_vp: int = 0` to `QuestCompletionPromptResponse`
- Add `showcase_bonus_vp: int = 0` to `QuestCompletedResponse`

**Client** (`client/views/game_view.py`):
- In the quest completion window rendering, if `bonus_quest_id` matches a displayed contract, render "+4VP bonus" text underneath that card

**Config** (`config/buildings.json`):
- Add `building_022` with `visitor_reward_special: "draw_contract_and_complete"`, `owner_bonus_vp: 2`, `cost_coins: 4`

### Documentation Update

**Spec mapping** (`specs/waterdeep-card-mapping.md`):
- Update the building mapping section to mark The Stone House and Heroes' Garden as DONE with their music-themed equivalents (Royalty Collection / Audition Showcase)
