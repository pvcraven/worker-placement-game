# Implementation Plan: Sprite Card Rendering

**Branch**: `011-sprite-card-rendering` | **Date**: 2026-04-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-sprite-card-rendering/spec.md`

## Summary

Replace all card rendering (currently done via `CardRenderer` using rect fills, outlines, and cached `arcade.Text` objects) with sprite-based rendering using pre-generated PNG card images. Cards are loaded as `arcade.Sprite` objects, managed in `arcade.SpriteList` instances for batch GPU rendering, and positioned at the same screen coordinates as the current implementation. This affects 5 call sites across 3 files: board quest cards, board building cards, hand panel quest/intrigue cards, and the quest completion dialog.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (existing)
**Storage**: File system — reads PNGs from `client/assets/card_images/`
**Testing**: Manual visual verification (run game, inspect card rendering)
**Target Platform**: Windows desktop (game client)
**Project Type**: Desktop game (Arcade-based)
**Performance Goals**: 60 fps rendering, sprite batch rendering faster than current rect+text approach
**Constraints**: Cards are 190x230 pixels, must use SpriteList for batch rendering (not individual sprite.draw())
**Scale/Scope**: 5 call sites across 3 files (board_renderer.py, game_view.py, dialogs.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applicable? | Status | Notes |
|-----------|-------------|--------|-------|
| I. Arcade Rendering Standards | Yes | PASS | Sprites and sprite lists are the preferred approach per constitution: "Sprites and sprite lists remain the preferred approach for image-based rendering." This change aligns perfectly. |
| II. Pydantic Data Modeling | No | N/A | No data model changes — card data still flows as dicts from game state |
| III. Client-Server Separation | Yes | PASS | Client-only rendering change, no server modifications |
| IV. Test-Driven Game Logic | No | N/A | No game logic changes — purely visual rendering |
| V. Simplicity First | Yes | PASS | Direct replacement of complex rect+text rendering with simpler sprite loading |

No gate violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-sprite-card-rendering/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
client/
├── ui/
│   ├── board_renderer.py    # MODIFY: Replace CardRenderer calls with SpriteList rendering for quest and building cards
│   ├── card_renderer.py     # REMOVE: No longer needed after all call sites are converted
│   ├── dialogs.py           # MODIFY: Replace CardRenderer.draw_contract in QuestCompletionDialog with sprites
│   └── ...
├── views/
│   └── game_view.py         # MODIFY: Replace CardRenderer calls in _draw_hand_panel with sprites
└── assets/
    └── card_images/         # READ: Pre-generated PNG card images (already exists)
        ├── quests/          # 66 quest card PNGs
        ├── buildings/       # 24 building card PNGs
        ├── intrigue/        # 50 intrigue card PNGs
        └── producers/       # 11 producer card PNGs
```

**Structure Decision**: No new files or directories. Modify 3 existing files to use sprites instead of CardRenderer. Remove card_renderer.py after all conversions are complete.

### SpriteList Organization

One SpriteList per rendering context:
- `BoardRenderer._quest_sprite_list` — face-up quest cards on the board
- `BoardRenderer._building_sprite_list` — face-up building cards on the board
- `GameView._hand_sprite_list` — quest or intrigue cards in the hand panel
- `QuestCompletionDialog._quest_sprite_list` — quest cards in the completion dialog

This approach (per-context, not per-type) is chosen because:
- Each context has independent lifecycle (board is persistent, hand panel toggles, dialog is ephemeral)
- Each context needs independent position calculations
- Sprites are added/removed when the context's card set changes, not globally

### Highlight Approach

Since arcade sprites don't have a built-in outline feature, highlights will be drawn as `arcade.draw_rect_outline()` over the sprite position. This is acceptable because:
- Only 1-2 cards are highlighted at a time (minimal draw calls)
- The constitution allows primitive draws for non-batch scenarios
- Alternative (separate highlight sprites) would add unnecessary complexity
