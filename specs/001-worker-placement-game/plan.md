# Implementation Plan: Multiplayer Worker Placement Game

**Branch**: `001-worker-placement-game` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-worker-placement-game/spec.md`

## Summary

Build a multiplayer worker placement board game with a music industry theme. Players are Record Labels assembling bands by collecting musician resources and completing contracts. The system consists of a headless Python server managing authoritative game state and Arcade-based graphical clients connected via WebSocket, exchanging JSON messages validated with Pydantic. All game content (contracts, intrigue cards, buildings, producers) is loaded from external JSON configuration files for easy balance iteration.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (graphics/client UI), websockets (async networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration files (game content)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Desktop (Windows, macOS, Linux)
**Project Type**: Client-server multiplayer game (headless server + graphical desktop client)
**Performance Goals**: <2 second action propagation to all clients; support 10 concurrent game sessions
**Constraints**: Turn-based (no frame-critical latency); responsive UI from minimum size to fullscreen
**Scale/Scope**: 2-5 players per session; 10 concurrent sessions; ~195 content cards total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is a template with no specific gates defined. No violations to check. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/001-worker-placement-game/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
server/
├── __init__.py
├── main.py                # Server entry point (asyncio + websockets)
├── game_engine.py         # Core game logic (turn management, rules, scoring)
├── game_state.py          # Authoritative game state container
├── lobby.py               # Lobby creation, join, ready-up management
├── config_loader.py       # JSON config loading + Pydantic validation
├── network.py             # WebSocket server, session management, message routing
└── models/
    ├── __init__.py
    ├── game.py            # Game state Pydantic models (Player, Board, Round)
    ├── cards.py           # Card/content Pydantic models (Contract, Intrigue, Building, Producer)
    ├── messages.py        # Network message Pydantic models (requests + responses)
    └── config.py          # Configuration file Pydantic models (validation schemas)

client/
├── __init__.py
├── main.py                # Client entry point (Arcade window launch)
├── game_window.py         # Main Arcade Window subclass (resize, fullscreen)
├── network_client.py      # WebSocket client (background thread + message queue)
├── views/
│   ├── __init__.py
│   ├── menu_view.py       # Main menu (create/join game)
│   ├── lobby_view.py      # Lobby waiting room (player list, ready, start)
│   ├── game_view.py       # Main game board (worker placement, actions, game log)
│   └── results_view.py    # End-of-game scoring and winner display
├── ui/
│   ├── __init__.py
│   ├── board_renderer.py  # Board layout and action space rendering
│   ├── card_renderer.py   # Contract/intrigue card display and interaction
│   ├── resource_bar.py    # Player resource display (musicians + coins)
│   ├── game_log.py        # Scrollable action log panel
│   └── dialogs.py         # Modal dialogs (quest completion, card selection, etc.)
└── assets/
    ├── images/            # Sprites, board art, card art
    ├── fonts/             # Custom fonts
    └── sounds/            # Sound effects (optional)

shared/
├── __init__.py
├── messages.py            # Shared Pydantic message models (imported by server + client)
├── card_models.py         # Shared card attribute models (imported by server + client)
└── constants.py           # Shared constants (resource types, colors, limits)

config/
├── contracts.json         # 60 contract (quest) cards
├── intrigue.json          # 50 intrigue cards
├── buildings.json         # 24 building tiles
├── producers.json         # ~11 producer cards
├── board.json             # Board layout: permanent action spaces + building lots
└── game_rules.json        # Round count, worker scaling, turn timeout, etc.

tests/
├── conftest.py            # Shared fixtures
├── unit/
│   ├── test_game_engine.py
│   ├── test_game_state.py
│   ├── test_config_loader.py
│   └── test_models.py
├── integration/
│   ├── test_lobby_flow.py
│   ├── test_game_flow.py
│   ├── test_reconnection.py
│   └── test_reassignment.py
└── contract/
    ├── test_message_schema.py
    └── test_config_schema.py
```

**Structure Decision**: Client-server split with a `shared/` package for Pydantic models used by both sides. The `config/` directory at project root holds all data-driven game content. The server is a standalone asyncio application; the client is an Arcade desktop application. Both import from `shared/`.

## Complexity Tracking

No constitution violations to justify.
