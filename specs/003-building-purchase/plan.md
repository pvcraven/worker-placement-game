# Implementation Plan: Building Purchase System

**Branch**: `003-building-purchase` | **Date**: 2026-04-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-building-purchase/spec.md`

## Summary

Implement a complete building purchase system: rearrange permanent action spaces into a single column, rename Builder's Hall to Real Estate Listings, introduce a 3-face-up building market with VP accumulation, create a purchase dialog in the client UI, and ensure purchased buildings function as action spaces with visitor rewards and owner bonuses.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration files (game content)
**Testing**: pytest + pytest-asyncio
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Client-server game (Arcade desktop client + async websocket server)
**Performance Goals**: 60 fps client rendering, <100ms server response
**Constraints**: All game state is authoritative on the server; client is a thin rendering layer
**Scale/Scope**: 2-5 players per game, single server instance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is a template with no specific gates defined. No violations to check. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/003-building-purchase/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
config/
├── board.json              # Rename builders_hall → real_estate_listings
└── buildings.json          # Already exists, 24 buildings with music names

shared/
├── card_models.py          # BuildingTile model — add accumulated_vp field
├── messages.py             # Add BuildingMarketUpdate, modify PurchaseBuildingRequest
└── constants.py            # Add FACE_UP_BUILDING_COUNT = 3

server/
├── models/
│   └── game.py             # BoardState — add building_deck, face_up_buildings, modify building_supply
├── lobby.py                # _initialize_game — set up deck + 3 face-up market
├── game_engine.py          # Modify purchase flow, add VP increment at round end
└── network.py              # Route new message types

client/
├── ui/
│   ├── board_renderer.py   # Rearrange _SPACE_LAYOUT to single column, render market
│   └── dialogs.py          # Add BuildingPurchaseDialog
└── views/
    └── game_view.py        # Handle purchase dialog trigger, market updates

tests/
├── test_building_purchase.py   # Purchase flow, validation, VP
├── test_board_layout.py        # Layout position assertions
└── test_owner_bonus.py         # Visitor/owner reward logic
```

**Structure Decision**: Existing client-server split with shared models. Changes span all three layers (shared models, server logic, client UI) plus config files. No new top-level directories needed.

## Complexity Tracking

No constitution violations to justify.
