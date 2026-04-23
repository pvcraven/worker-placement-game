# Implementation Plan: Resource Bar Revamp

**Branch**: `017-resource-bar-revamp` | **Date**: 2026-04-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/017-resource-bar-revamp/spec.md`

## Summary

Replace the bottom resource panel's dark background and drawn primitives with a parchment-styled panel using pre-generated PNG sprite icons for resources, card icons for quest/intrigue counts, and the player's worker marker next to "workers left". All rendering uses cached SpriteLists to avoid per-frame recreation.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL) for card/icon generation, Pydantic v2
**Storage**: File system — reads/writes PNGs in `client/assets/card_images/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade window)
**Project Type**: Desktop game (client-server, local)
**Performance Goals**: 60 fps rendering; SpriteList reuse eliminates per-frame overhead
**Constraints**: Resource bar must scale with window size; fallback to drawn shapes if PNGs missing
**Scale/Scope**: Single file change (resource_bar.py) + card generator additions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Will use arcade.Text (cached), SpriteList for icons. No primitive draw calls for final rendering. Fallback path may use shape list for missing PNGs. |
| II. Pydantic Data Modeling | PASS | No new data boundaries crossed. Resource dict is internal to client rendering. |
| III. Client-Server Separation | PASS | All changes are client-side rendering. No game state modification. |
| IV. Test-Driven Game Logic | PASS | No server game logic changes. Card generator is a build-time tool. |
| V. Simplicity First | PASS | Straightforward sprite swap. No new abstractions or patterns. |

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/017-resource-bar-revamp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
card-generator/
└── generate_cards.py          # Add resource icon + standalone card icon PNG generation

client/
├── assets/
│   └── card_images/
│       ├── icons/             # NEW: resource icon PNGs (guitarist.png, etc.)
│       │   ├── guitarist.png
│       │   ├── bass_player.png
│       │   ├── drummer.png
│       │   ├── singer.png
│       │   ├── coin.png
│       │   ├── quest_icon.png
│       │   └── intrigue_icon.png
│       └── markers/           # Existing: worker_red.png, etc.
├── ui/
│   └── resource_bar.py        # MODIFY: parchment bg, sprite-based icons, cached SpriteList
└── views/
    └── game_view.py           # MODIFY: pass player_color to resource_bar
```

**Structure Decision**: Modify existing files. One new subdirectory `icons/` under `card_images/` for the small resource/card icon PNGs. No new modules or abstractions.
