# Implementation Plan: Board Layout Optimization

**Branch**: `009-board-layout-optimization` | **Date**: 2026-04-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-board-layout-optimization/spec.md`

## Summary

Reorganize the game board to always display buildings for sale (removing the popup dialog), reposition quest cards, backstage slots, and the Realtor space. Replace popup-based quest and building selection with an inline highlight-and-click pattern using a cancel button graphic.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source), websockets, Pydantic v2
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade window)
**Project Type**: Desktop game (client-server)
**Performance Goals**: 60 fps rendering, immediate UI response to clicks
**Constraints**: All board elements must fit without overlap at default window size
**Scale/Scope**: 2-5 players, single game board

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Will use `arcade.Text` cached objects and `ShapeElementList` for all new rendering. Highlight borders via shape lists. |
| II. Pydantic Data Modeling | PASS | No new network messages needed — reusing existing quest selection and building purchase protocol. Highlight state is client-only UI state. |
| III. Client-Server Separation | PASS | All changes are client-side rendering/layout. Server protocol unchanged. |
| IV. Test-Driven Game Logic | PASS | No server-side game logic changes. |
| V. Simplicity First | PASS | Removing popup dialogs simplifies the UI. Highlight state is a simple boolean + list of IDs. |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/009-board-layout-optimization/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
client/
├── ui/
│   ├── board_renderer.py    # MODIFY: new layout positions, building card rendering, highlight drawing
│   ├── card_renderer.py     # No changes expected
│   └── dialogs.py           # MODIFY: remove QuestCompletionDialog (replaced by inline highlight)
├── views/
│   └── game_view.py         # MODIFY: remove Real Estate button/panel, add highlight state management,
│                            #          cancel button rendering, click routing for highlighted cards
├── assets/
│   └── cancel.png           # ADD: red cancel button graphic
config/
└── board.json               # No changes (space definitions unchanged)
server/
└── (no changes)             # Server protocol unchanged
shared/
└── (no changes)             # No new messages needed
```

**Structure Decision**: Pure client-side refactor. All changes are in `client/ui/board_renderer.py` and `client/views/game_view.py`. No new files except the cancel button asset.

## New Board Layout Design

### Current Layout (proportional coordinates)

```text
Left column (x=0.08):        Center top (y=0.87):         Right area (x=0.22+):
  merch_store   (0.08, 0.90)   the_garage_1 (0.38, 0.87)   constructed buildings
  motown        (0.08, 0.80)   the_garage_2 (0.52, 0.87)   (grid starting x=0.22)
  guitar_center (0.08, 0.70)   the_garage_3 (0.66, 0.87)
  talent_show   (0.08, 0.60)                               Center (y=0.60):
  rhythm_pit    (0.08, 0.50)   Backstage (y=0.33):          face-up quest cards
  castle        (0.08, 0.40)   slot_1 (0.38, 0.33)
  realtor       (0.08, 0.30)   slot_2 (0.52, 0.33)
                               slot_3 (0.66, 0.33)
```

### Proposed Layout

```text
Left column (x=0.08):        Center-top (y=0.92):          Right area (x=0.22+):
  merch_store   (0.08, 0.92)   the_garage_1 (0.38, 0.92)   constructed buildings
  motown        (0.08, 0.82)   the_garage_2 (0.52, 0.92)   (grid starting x=0.22)
  guitar_center (0.08, 0.72)   the_garage_3 (0.66, 0.92)
  talent_show   (0.08, 0.62)                               Center-upper (y=0.68):
  rhythm_pit    (0.08, 0.52)   Face-up quest cards           face-up quest cards
  castle        (0.08, 0.42)   (rendered at ~y=0.68)
  backstage_1   (0.08, 0.32)                               Center-lower (y=0.30):
  backstage_2   (0.08, 0.22)   Realtor (near buildings):     face-up buildings
  backstage_3   (0.08, 0.12)   realtor  (0.38, 0.18)        (rendered at ~y=0.30)
```

Key changes:
- Move everything up slightly to make room for buildings at bottom
- Move backstage slots to left column (below permanent spaces)
- Move Realtor near the building display area
- Buildings rendered as cards using CardRenderer (similar to quest cards)
- Quest cards stay centered but shift up

### Highlight State Model

Client-only state managed in `game_view.py`:

```
_highlight_mode: str | None  # "quest_selection" or "building_purchase" or None
_highlighted_ids: list[str]  # IDs of cards that are selectable
_cancel_button_rect: tuple   # (left, bottom, width, height) for cancel.png hit area
```

## Complexity Tracking

No constitution violations. No complexity tracking needed.
