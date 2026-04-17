# Implementation Plan: Backstage & Intrigue Mechanics

**Branch**: `006-backstage-intrigue-mechanics` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-backstage-intrigue-mechanics/spec.md`

## Summary

Implement backstage placement with intrigue card selection, starting resources (coins + intrigue cards based on turn order), and worker reassignment after all workers are placed. Most data models and message types already exist — the primary work is wiring up server handlers, client-side click routing, and the intrigue card selection dialog.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: pytest, ruff (linting)
**Target Platform**: Desktop (Windows/macOS/Linux)
**Project Type**: Client-server desktop game
**Performance Goals**: Interactive board game — sub-second response to placements
**Constraints**: Single-process server, in-memory state, no persistence
**Scale/Scope**: 1-5 players per game, 8 rounds

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is not customized (template placeholders only). No gates to enforce. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/006-backstage-intrigue-mechanics/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── websocket-messages.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
server/
├── lobby.py             # Game initialization — add starting resources
├── game_engine.py       # Backstage placement handler, validation
├── network.py           # Route place_worker_backstage messages
└── models/
    └── game.py          # Models already exist (BackstageSlot, Player, etc.)

client/
├── views/
│   └── game_view.py     # Backstage click detection, intrigue dialog, reassignment UI
└── ui/
    └── dialogs.py       # Reuse CardSelectionDialog for intrigue cards

shared/
├── messages.py          # Messages already exist (PlaceWorkerBackstageRequest, etc.)
├── card_models.py       # IntrigueCard model already exists
└── constants.py         # Add starting resource constants

config/
├── intrigue.json        # 50 intrigue cards already defined
└── game_rules.json      # No changes needed
```

**Structure Decision**: Existing project structure. No new files or directories needed — all changes go into existing files.

## Existing Infrastructure (Key Finding)

Most infrastructure for this feature already exists:

| Component | Status | Location |
|-----------|--------|----------|
| `BackstageSlot` model | Exists | server/models/game.py |
| `IntrigueCard` model | Exists | shared/card_models.py |
| `_resolve_intrigue_effect()` | Exists | server/game_engine.py |
| `PlaceWorkerBackstageRequest` | Exists | shared/messages.py |
| `WorkerPlacedBackstageResponse` | Exists | shared/messages.py |
| `ReassignmentPhaseStartResponse` | Exists | shared/messages.py |
| `WorkerReassignedResponse` | Exists | shared/messages.py |
| `handle_reassign_worker()` | Exists | server/game_engine.py |
| `_end_placement_phase()` | Exists | server/game_engine.py |
| `CardSelectionDialog` | Exists | client/ui/dialogs.py |
| `intrigue.json` (50 cards) | Exists | config/intrigue.json |
| Board rendering of backstage slots | Exists | client/ui/board_renderer.py |
| Backstage click detection | Exists | client/ui/board_renderer.py |

**What's missing** (implementation work):
1. Starting resource initialization (coins + intrigue cards in lobby.py)
2. Server handler for `place_worker_backstage` (sequential validation, card validation)
3. Network routing for `place_worker_backstage` messages
4. Client-side backstage click → intrigue dialog → send message flow
5. Client-side reassignment phase UI updates
6. Constants for starting resources

## Complexity Tracking

No constitution violations to justify.
