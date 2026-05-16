# Implementation Plan: Colored Marker Selection

**Branch**: `033-colored-marker-selection` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/033-colored-marker-selection/spec.md`

## Summary

Add a pre-game marker selection phase where each player chooses from seven colored markers (green, red, purple, blue, pink, lilac, orange). The selection is first-come-first-served with server-authoritative conflict resolution. After all players pick, a 1-second pause shows the final assignments before the game starts. Selected colors replace the current index-based color assignment throughout the game.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (for marker PNG generation)
**Storage**: In-memory game state (server); PNG image files (marker assets)
**Testing**: pytest + ruff from project root
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Multiplayer game (client-server)
**Performance Goals**: Marker selections reflected on all clients within 1 second
**Constraints**: Max 5 players, 7 available colors, first-come-first-served conflict resolution
**Scale/Scope**: 2-5 concurrent players per game session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Selection dialog will use arcade.gui (UIAnchorLayout) + ShapeElementList for markers, arcade.Text for labels. No primitive draw calls. |
| II. Pydantic Data Modeling | PASS | New message types (SelectMarkerRequest, MarkerSelectionStartResponse, MarkerSelectedResponse) are Pydantic models in shared/messages.py. Player.marker_color is a Pydantic field. |
| III. Client-Server Separation | PASS | Server validates selections and broadcasts results. Client only renders state received from server. Shared message types in shared/messages.py. |
| IV. Test-Driven Game Logic | PASS | Server-side selection logic (conflict resolution, phase transitions) will have pytest tests. Tests do not depend on Arcade. |
| V. Simplicity First | PASS | Minimal additions: 1 new phase, 1 new field on Player, 3 new message types, 1 new dialog class. No new abstractions or dependencies. |
| VI. Server-Authoritative Message Protocol | PASS | SelectMarkerRequest → server validates → broadcasts MarkerSelectedResponse. First-come-first-served resolved on server. |
| VII. Config-Driven Game Content | PASS | Marker colors defined as constants (MARKER_COLORS list), not hard-coded per card. No new config JSON files needed. |
| VIII. Pending State for Deferred Actions | N/A | No multi-step deferred actions — selection is a single request/response. |
| IX. Cancel/Unwind Reversibility | N/A | Marker selection is irreversible by design (spec says selection is final). |
| X. Post-Action Turn Flow | N/A | Marker selection happens before turns begin. The transition to PLACEMENT phase triggers the standard turn flow. |

## Project Structure

### Documentation (this feature)

```text
specs/033-colored-marker-selection/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── messages.md      # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
shared/
├── constants.py          # Add MARKER_SELECTION to GamePhase, add MARKER_COLORS list
└── messages.py           # Add SelectMarkerRequest, MarkerSelectionStartResponse, MarkerSelectedResponse

server/
├── models/game.py        # Add marker_color field to Player
├── lobby.py              # Insert marker selection phase in start_game flow, add select_marker handler
└── network.py            # Route select_marker action to handler

client/
├── ui/
│   ├── board_renderer.py # Replace index-based color with player marker_color lookup
│   └── marker_selection_dialog.py  # New: marker selection dialog UI
├── views/game_view.py    # Handle marker_selection_start and marker_selected messages, show/dismiss dialog
└── assets/card_images/markers/
    ├── worker_pink.png   # New marker PNG
    └── worker_lilac.png  # New marker PNG

tests/
└── test_marker_selection.py  # New: server-side selection logic tests
```

**Structure Decision**: Standard single-project structure. All changes fit within existing directories. One new file (`marker_selection_dialog.py`) and one new test file. Two new PNG assets.
