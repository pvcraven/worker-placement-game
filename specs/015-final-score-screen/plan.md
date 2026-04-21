# Implementation Plan: Final Score Screen

**Branch**: `015-final-score-screen` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-final-score-screen/spec.md`

## Summary

Add a final score dialog overlay to the game view that shows a VP breakdown for every player: producer card, game VP, genre bonus VP, resource VP, and total VP. The dialog can be toggled via a "Final Screen" button during gameplay, and appears automatically when the game ends. The winner (highest total VP) is highlighted with "WINNER" above their producer card. On game-over, the Close button navigates to the lobby; on manual toggle, it simply closes the dialog.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Desktop multiplayer game (client + server)
**Performance Goals**: 60 fps rendering
**Constraints**: Must follow Constitution Principle I (arcade.Text, ShapeElementList, sprites only — no primitive draw calls)
**Scale/Scope**: 2-6 players per game

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Dialog will use arcade.Text (cached), ShapeElementList for backgrounds, Sprite for producer cards. No primitive draw calls. |
| II. Pydantic Data Modeling | PASS | FinalPlayerScore model extended with resource_vp field. All data crosses network boundary via Pydantic models. |
| III. Client-Server Separation | PASS | Authoritative VP calculation stays in server/_end_game. Client calculates estimated scores for manual toggle only. |
| IV. Test-Driven Game Logic | PASS | Server-side resource_vp calculation will have pytest tests. |
| V. Simplicity First | PASS | Single dialog with two-flag system (show/game_over) instead of separate views. Replaces existing ResultsView. |

## Project Structure

### Documentation (this feature)

```text
specs/015-final-score-screen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
shared/
├── messages.py          # MODIFY: Update FinalPlayerScore (add resource_vp, rename fields)
└── card_models.py       # READ ONLY: ProducerCard, ContractCard, Genre

server/
├── game_engine.py       # MODIFY: Update _end_game() to calculate resource_vp
└── models/
    └── game.py          # READ ONLY: Player, PlayerResources

client/
├── views/
│   ├── game_view.py     # MODIFY: Add Final Screen button, dialog, game-over handler
│   └── results_view.py  # DEPRECATE: Replaced by in-game dialog
└── game_window.py       # READ ONLY: show_lobby() already exists

tests/
└── test_game_engine.py  # MODIFY: Add tests for resource_vp calculation
```

**Structure Decision**: No new files needed. Changes are modifications to existing files in the established project structure.

## Key Design Decisions

### 1. Replace ResultsView with In-Game Dialog

The existing `results_view.py` navigates away from the game entirely. The new approach keeps the final score as an overlay dialog within `game_view.py`, consistent with the Player Overview pattern. The `game_over` message handler in game_view will set flags instead of calling `window.show_results()`.

### 2. Two-Flag State System

```
_show_final_screen: bool  — controls dialog visibility
_game_over_final: bool    — controls Close behavior and toggle-lock
```

- Manual toggle: sets `_show_final_screen`, `_game_over_final` stays False
- Game-over: sets both to True
- Close during manual: clears `_show_final_screen`
- Close during game-over: disconnects and navigates to lobby
- Toggle button ignored when `_game_over_final` is True

### 3. Data Sources by Mode

| Mode | Data Source | Genre Bonus for Opponents |
|------|-----------|--------------------------|
| Manual toggle | Client-side calculation from game_state dict | Hidden ("?" — producer cards not revealed) |
| Game-over | Server-provided FinalPlayerScore list | Visible (all data revealed) |

### 4. FinalPlayerScore Field Renames

To align with spec terminology:
- `base_vp` → `game_vp`
- `producer_bonus` → `genre_bonus_vp`
- New field: `resource_vp`
- `total_vp` now = `game_vp + genre_bonus_vp + resource_vp`

This is a breaking change to the message format. Update all references in server (game_engine.py) and client (game_view.py game_over handler, results_view.py if kept).

### 5. Resource VP Calculation

```
resource_vp = guitarists + bass_players + drummers + singers + floor(coins / 2)
```

Calculated in server `_end_game()` for authoritative results and in client for manual toggle estimates.

### 6. Dialog Rendering

- Dark semi-transparent background rectangle (full screen overlay)
- Centered panel with white border
- Player columns laid out horizontally, evenly spaced
- Each column: "WINNER" text (conditional) → producer card sprite → player name → VP breakdown rows → total
- "Close" button at bottom center
- All text via cached arcade.Text objects (Principle I)
- Background shapes via ShapeElementList (Principle I)
- Producer cards via Sprite/SpriteList (Principle I)
