# Implementation Plan: Resource Distribution Buildings

**Branch**: `040-resource-distribution-buildings` | **Date**: 2026-06-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/040-resource-distribution-buildings/spec.md`

## Summary

Add 5 new "resource distribution" buildings from the Undermountain expansion (UN-1 through UN-5). Each costs 7 coins. When visited, the building gives the visitor resources AND triggers a placement phase where the building owner selects other action spaces to receive additional resources from the supply. Placed resources display as icons on the target spaces and persist until collected by a future visitor. The mechanic is expressed through 3 new fields on BuildingTile, a placed_resources dict on ActionSpace, and a pending_resource_distribution state on GameState.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state (server); JSON configuration files in `config/`
**Testing**: pytest + ruff (`cd src && pytest && ruff check .`)
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Client-server board game (Arcade UI + WebSocket server)
**Performance Goals**: Standard board game responsiveness (<1s turn resolution)
**Constraints**: Must follow existing patterns for building visit flow, pending state, message protocol
**Scale/Scope**: 5 new buildings, 1 new mechanic, ~10 files modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering | **PASS** | Resource icons rendered via ShapeElementList (colored squares) + arcade.Text for counts. No draw_ calls. |
| II. Pydantic Data Modeling | **PASS** | New fields on existing Pydantic models (BuildingTile, ActionSpace, GameState). New message types as Pydantic models. |
| III. Client-Server Separation | **PASS** | Distribution logic lives in server/game_engine.py. Client renders state and sends selection requests. Shared models in shared/. |
| IV. Test-Driven Game Logic | **PASS** | Tests for distribution trigger, space selection validation, resource collection, edge cases. |
| V. Simplicity First | **PASS** | Three flat fields on BuildingTile (no new abstractions). Dict for placed_resources. Existing patterns reused. |
| VI. Server-Authoritative Message Protocol | **PASS** | New Request/Response pair: ResourceDistributionRequest → ResourceDistributionResolvedResponse. Prompt sent to selecting player, resolution broadcast to all. |
| VII. Config-Driven Game Content | **PASS** | Mechanic parameterized by distribute_resource_type, distribute_per_space, distribute_space_count fields. No hard-coded building IDs. |
| VIII. Pending State for Deferred Actions | **PASS** | pending_resource_distribution stores selection state between messages. Cleared on completion or cancel. |
| IX. Cancel/Unwind Reversibility | **PASS** | pending_placement already captures distribution context. Cancel reverses placement. Distribution selections are additive — cancel clears pending and removes any resources already placed on spaces during this phase. |
| X. Post-Action Turn Flow | **PASS** | After final distribution selection: check quest completion → advance turn. Standard flow. |

**Result**: All 10 principles pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/040-resource-distribution-buildings/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: research decisions
├── data-model.md        # Phase 1: entity changes
├── quickstart.md        # Phase 1: implementation guide
├── contracts/
│   └── messages.md      # Phase 1: message protocol contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
shared/
├── card_models.py         # BuildingTile: +3 distribution fields
├── messages.py            # +3 new message types, WorkerPlacedResponse extended

server/
├── models/
│   └── game.py            # ActionSpace: +placed_resources, GameState: +pending_resource_distribution
├── game_engine.py         # Distribution trigger, selection handler, collection on visit
└── models/config.py       # Validation (cost range already includes 7)

client/
├── ui/board_renderer.py   # Render placed resource icons on spaces
└── views/game_view.py     # Handle new message types, update local state

config/
└── buildings.json         # +5 new building entries

card-generator/
└── generate_cards.py      # Generate PNGs for 5 new buildings with "Place:" line

tests/
└── (new test files)       # Distribution mechanic tests
```

**Structure Decision**: All changes extend existing files in the established project structure. No new directories or modules needed.

## Complexity Tracking

No constitution violations — this section is not applicable.
