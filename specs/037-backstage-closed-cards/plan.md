# Implementation Plan: Backstage Closed Cards

**Branch**: `037-backstage-closed-cards` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/037-backstage-closed-cards/spec.md`

## Summary

During the reassignment phase, backstage slot cards currently show "Play Intrigue" even though backstage is unavailable. This feature generates "CLOSED" variant card images (dark red text with a box border) and swaps the backstage sprite list between normal and closed variants based on the current game phase.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL) for card image generation, Pydantic v2
**Storage**: File system — reads/writes PNGs in `client/assets/card_images/spaces/`
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Desktop multiplayer game (client/server)
**Performance Goals**: Sprite list swap must be instantaneous (no per-frame overhead)
**Constraints**: N/A (client-side visual only)
**Scale/Scope**: 3 backstage slot cards, 2 variants each (normal + closed)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Uses pre-generated PNG sprites in a SpriteList — no primitive draw calls |
| II. Pydantic Data Modeling | PASS | No new data models needed — purely visual |
| III. Client-Server Separation | PASS | No server changes — client reads existing `game_state["phase"]` |
| IV. Test-Driven Game Logic | PASS | No game logic changes — no new tests required |
| V. Simplicity First | PASS | Swapping a pre-built sprite list is the simplest approach |
| VI. Server-Authoritative Message Protocol | PASS | No new messages — uses existing phase field |
| VII. Config-Driven Game Content | PASS | No config changes needed |
| VIII. Pending State | N/A | No pending state involved |
| IX. Cancel/Unwind | N/A | No cancel flow involved |
| X. Post-Action Turn Flow | N/A | No turn flow changes |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/037-backstage-closed-cards/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
card-generator/
  generate_cards.py         # Add closed variant generation alongside existing backstage cards

client/
  assets/card_images/spaces/
    backstage_slot_1.png          # Existing normal card
    backstage_slot_2.png          # Existing normal card
    backstage_slot_3.png          # Existing normal card
    backstage_slot_1_closed.png   # NEW: closed variant
    backstage_slot_2_closed.png   # NEW: closed variant
    backstage_slot_3_closed.png   # NEW: closed variant
  ui/
    board_renderer.py       # Build both normal and closed sprite lists; add swap method
  views/
    game_view.py            # Call swap method on phase transitions
```

**Structure Decision**: No new files or directories needed. Changes are additions to existing files: card generation, board renderer, and game view.

## Implementation Approach

### 1. Card Image Generation (`card-generator/generate_cards.py`)

After the existing backstage card loop (~line 1830), add a second loop generating closed variants:
- Same card base, same band color `(100, 50, 50)`, same "Backstage N" title
- Replace "Play Intrigue" body text with "CLOSED" in dark red (e.g., `(180, 40, 40)`)
- Draw a rectangular box border around the "CLOSED" text using PIL `draw.rectangle()` with outline only
- Save as `backstage_slot_{N}_closed.png`

### 2. Board Renderer (`client/ui/board_renderer.py`)

In `_build_board_layout()`:
- Build a second sprite list `self._backstage_closed_sprite_list` using card IDs `backstage_slot_1_closed`, etc., at the same positions and scale as the normal backstage sprite list
- Default to showing the normal list

Add a method `swap_backstage_cards(closed: bool)`:
- Sets an internal flag `self._backstage_closed = closed`
- The `draw()` method already draws `self._backstage_sprite_list` — change it to draw either the normal or closed list based on the flag

### 3. Game View (`client/views/game_view.py`)

In `_on_reassignment_phase_start()` (~line 2711):
- Call `self.board_renderer.swap_backstage_cards(closed=True)`

In `_on_round_end()` (~line 2951):
- Call `self.board_renderer.swap_backstage_cards(closed=False)`

For reconnect: in the state sync handler, check `game_state["phase"]` and call `swap_backstage_cards()` accordingly.
