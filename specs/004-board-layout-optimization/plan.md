# Implementation Plan: Board Layout Optimization

**Branch**: `004-board-layout-optimization` | **Date**: 2026-04-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-board-layout-optimization/spec.md`

## Summary

Optimize the game board layout by removing redundant labels, renaming "Real Estate Listings" space to "Realtor", converting the inline building market to a toggle popup panel, and batching all static board shapes into a `ShapeElementList` for GPU-accelerated rendering.

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
specs/004-board-layout-optimization/
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
├── board.json              # Rename real_estate_listings → realtor

client/
├── ui/
│   ├── board_renderer.py   # Remove labels, shift layout, batch shapes, remove inline market
│   └── dialogs.py          # Update purchase dialog title
└── views/
    └── game_view.py        # Add "Real Estate Listings" button + popup, rename references

server/
├── game_engine.py          # Rename real_estate_listings → realtor in string references
```

**Structure Decision**: Existing client-server split with shared models. Changes are concentrated in the client UI layer (3 files) with minor rename changes in config (1 file) and server (1 file). No new files needed.

## Complexity Tracking

No constitution violations to justify.
