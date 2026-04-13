# Implementation Plan: Garage Quest Display Rework

**Branch**: `002-garage-quest-display` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-garage-quest-display/spec.md`

## Summary

Rework the quest acquisition area by renaming "Cliffwatch Inn" to "The Garage" with three distinct action spots (quest+coins, quest+intrigue, reset), adding a face-up display of four quest cards with deck/discard reshuffle mechanics. Rename the old "Garage" (intrigue/reassignment) to "Backstage." Add toggle-based player hand display for quest and intrigue cards with card privacy enforcement.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (validation)
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Desktop (Windows, macOS, Linux)
**Project Type**: Client-server multiplayer game (modification to existing codebase)
**Performance Goals**: <2 second state propagation to all clients
**Constraints**: Must be backwards-compatible with existing game mechanics (Backstage reassignment, building construction, etc.)
**Scale/Scope**: Modification across ~15 files; no new dependencies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution is a template with no specific gates defined. No violations to check. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/002-garage-quest-display/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (existing — files to modify)

```text
# Configuration
config/board.json              # Rename spaces, add distinct spot types

# Server
server/models/game.py          # Rename GarageSlot→BackstageSlot, add face-up display + deck state
server/models/config.py        # Update board config schema for new space types
server/lobby.py                # Initialize quest deck, face-up display, backstage slots
server/game_engine.py          # New handlers for garage spots, deck draw/discard/reshuffle
server/network.py              # Route new message types

# Shared
shared/messages.py             # New messages: garage spot actions, face-up updates, hand display
shared/constants.py            # Add FACE_UP_QUEST_COUNT = 4, rename GARAGE_SLOTS

# Client
client/ui/board_renderer.py    # Rename labels, render face-up quest cards at The Garage
client/ui/card_renderer.py     # May need minor updates for face-up card sizing
client/views/game_view.py      # Handle new messages, add toggle buttons, quest selection flow
client/ui/dialogs.py           # Quest selection dialog for Spots 1 & 2

# Documentation
README.md                      # Update Backstage reference
```

**Structure Decision**: No new files needed. All changes are modifications to existing files in the established client/server/shared/config structure.

## Rename Map

All renames needed across the codebase:

| Old Name | New Name | Scope |
|----------|----------|-------|
| `cliffwatch_inn_1/2/3` (space IDs) | `the_garage_1/2/3` | config/board.json, board_renderer.py |
| `"Cliffwatch Inn (Slot N)"` (display) | `"The Garage (Spot N)"` | config/board.json |
| `space_type: "cliffwatch"` | `space_type: "garage"` | config/board.json, game_engine.py |
| `GarageSlot` (class) | `BackstageSlot` | server/models/game.py, lobby.py, game_engine.py |
| `garage_slots` (field) | `backstage_slots` | server/models/game.py, lobby.py, game_engine.py |
| `GARAGE_SLOTS` (constant) | `BACKSTAGE_SLOTS` | shared/constants.py, lobby.py |
| `place_worker_garage` (action) | `place_worker_backstage` | shared/messages.py, network.py, game_engine.py, game_view.py |
| `worker_placed_garage` (action) | `worker_placed_backstage` | shared/messages.py, game_engine.py, game_view.py |
| `"THE GARAGE"` (board label) | `"BACKSTAGE"` | board_renderer.py |
| `_GARAGE_LAYOUT` (constant) | `_BACKSTAGE_LAYOUT` | board_renderer.py |

## Key Design Decisions

1. **Quest Deck as Server State**: The quest deck, discard pile, and face-up display are managed entirely on the server. Clients receive face-up card data in state syncs and targeted messages.

2. **Face-Up Display in Board State**: The four face-up quest cards are stored in `BoardState` alongside action spaces. All clients see the same cards. Card selection is a new client→server→client message flow.

3. **Deck Reshuffle Trigger**: When a draw is attempted and the deck is empty, automatically shuffle the discard pile into a new deck before drawing. This is transparent to the player.

4. **Toggle Buttons as Client-Only UI**: The quest/intrigue hand toggle buttons are purely client-side UI. The server already sends hand data to each player; the client just controls visibility.

5. **Spot 3 (Reset) Has No Card Selection**: Unlike Spots 1 and 2, Spot 3 is a simple action with no interactive follow-up. The server discards and redraws automatically.
