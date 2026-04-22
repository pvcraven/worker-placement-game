# Implementation Plan: Building Revamp

**Branch**: `016-building-revamp` | **Date**: 2026-04-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/016-building-revamp/spec.md`

## Summary

Replace all 28 existing buildings with 20 new buildings across 5 categories. Introduce the accumulating-resource mechanic (buildings stock resources each round until visited), VP as a building reward type, owner bonus choices, and spend-to-get-choice buildings. Implement `visitor_reward_special` (draw_contract, draw_intrigue) which exists in the data model but is not yet processed in game logic.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2
**Storage**: In-memory game state (server); JSON configuration files in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (local multiplayer via websockets)
**Project Type**: Desktop game (client-server, local network)
**Performance Goals**: 60 fps client rendering, real-time turn-based game logic
**Constraints**: No external dependencies beyond existing stack
**Scale/Scope**: 2-5 players, 8 rounds, 20 buildings in market

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Accumulation display will use cached `arcade.Text` objects, not primitive draw calls. Building sprites already use SpriteList. |
| II. Pydantic Data Modeling | PASS | BuildingTile model extended with new fields. All config validated through Pydantic. |
| III. Client-Server Separation | PASS | Accumulation logic lives in server/game_engine.py. Client renders state received from server. |
| IV. Test-Driven Game Logic | PASS | New server-side logic (accumulation, VP rewards, owner choices) will have pytest tests. |
| V. Simplicity First | PASS | Extending existing models and patterns rather than introducing new abstractions. |

## Project Structure

### Documentation (this feature)

```text
specs/016-building-revamp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
config/
└── buildings.json           # REPLACE: 28 old buildings → 20 new buildings

shared/
└── card_models.py           # MODIFY: Extend BuildingTile with accumulation fields, VP rewards, owner choice

server/
├── game_engine.py           # MODIFY: Accumulation at round start, VP rewards, owner choice flow,
│                            #         visitor_reward_special processing (draw_contract/draw_intrigue)
├── config_loader.py         # MODIFY: Update validation for new building fields
├── lobby.py                 # MODIFY: Initialize accumulation stock on purchase
└── models/
    └── game.py              # No changes expected (ActionSpace already has building_tile)

client/
└── ui/
    └── board_renderer.py    # MODIFY: Display accumulated resource count on building spaces

tests/
├── test_cards.py            # NO CHANGE: These test contracts, not buildings
└── test_buildings.py        # NEW: Tests for building balance, accumulation, VP rewards
```

**Structure Decision**: Existing single-project structure. No new directories needed. Changes are localized to config, shared models, server logic, and client rendering.

## Key Implementation Decisions

### 1. Accumulating Building Mechanic

The `BuildingTile` model gets new optional fields:
- `accumulation_type`: resource type or "victory_points" (null for non-accumulating buildings)
- `accumulation_per_round`: amount added each round
- `accumulation_initial`: starting stock when purchased
- `accumulated_stock`: current accumulated count (runtime state, starts at 0)

At round start (`_end_round`), after existing VP increment on face-up buildings, iterate all constructed buildings and increment `accumulated_stock` on accumulating buildings.

When a player visits an accumulating building, the `accumulated_stock` is transferred to the visitor (as resources or VP), then reset to zero. The standard `visitor_reward` field stays as `ResourceCost(all zeros)` for accumulating buildings since the dynamic stock replaces it.

### 2. VP as Building Reward

Add `victory_points` field to `ResourceCost` (or handle separately). Since `ResourceCost` is used everywhere for resource math, the simplest approach is to add a `victory_points: int = 0` field to both `visitor_reward` and `owner_bonus` in `BuildingTile`, separate from `ResourceCost`. This avoids breaking existing resource arithmetic.

Alternative: Add VP fields directly to `BuildingTile` as `owner_bonus_vp: int = 0` and `visitor_reward_vp: int = 0`.

Decision: Add `victory_points` to `ResourceCost`. It's the cleanest since `ResourceCost.add()` and `model_dump()` already handle all fields uniformly.

### 3. Owner Bonus Choice

New field on `BuildingTile`: `owner_bonus_choice: ResourceChoiceReward | None = None`. When present, the server prompts the building owner to make a resource choice after a visitor places a worker. This reuses the existing `_send_resource_choice_prompt` infrastructure but targets the owner instead of the visitor.

### 4. visitor_reward_special Implementation

Currently `visitor_reward_special` is stored but never processed for buildings. Need to add handling in `handle_place_worker` after reward granting:
- `"draw_contract"`: Player picks one face-up quest card (same as garage selection flow)
- `"draw_intrigue"`: Player draws one intrigue card from deck

### 5. Spend-to-Get Buildings

Already supported via `visitor_reward_choice` with `cost` field. The C1/C2 buildings use the existing `combo` choice_type with `cost` and `allowed_types` restricted to singers/drummers.

### 6. Building Card Images

New building card PNGs will need to be generated for the 20 new buildings using the existing card generator (`card-generator/generate_cards.py`).

## Complexity Tracking

No constitution violations. All changes extend existing patterns.
