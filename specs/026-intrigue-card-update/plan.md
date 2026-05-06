# Implementation Plan: Intrigue Card Update

**Branch**: `026-intrigue-card-update` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/026-intrigue-card-update/spec.md`

## Summary

Add 14 new intrigue cards across 5 categories (no-effect, draw-1-intrigue, reset-quests, reset-buildings, first-player-marker) and implement a global deck reshuffle mechanic for quests and buildings. The `draw_intrigue` effect type already exists and handles the draw-1-intrigue cards with zero new server code. Three new effect types (`no_effect`, `reset_quests`, `reset_buildings`, `first_player_marker`) need handlers in `_resolve_intrigue_effect()`. A `building_discard` list and `_draw_from_building_deck()` helper need to be added to support building reshuffle.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade client)
**Project Type**: Multiplayer board game (client/server)
**Performance Goals**: Card effects resolve instantly within normal turn resolution
**Constraints**: Must follow existing `effect_type` pattern in `_resolve_intrigue_effect()`; must handle deck depletion gracefully
**Scale/Scope**: 14 new JSON entries, 3 new effect handlers, 1 new model field, 1 new helper function

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | N/A | No new rendering code; existing client handles intrigue card display |
| II. Pydantic Data Modeling | PASS | Uses existing IntrigueCard Pydantic model; new `building_discard` field on BoardState |
| III. Client-Server Separation | PASS | Server resolves all effects; client updates from broadcast responses |
| IV. Test-Driven Game Logic | PASS | Existing test suite validates intrigue flow; new card count verified implicitly |
| V. Simplicity First | PASS | Reuses existing effect_type string pattern; no new abstractions |
| VI. Server-Authoritative Message Protocol | PASS | Uses existing `WorkerPlacedBackstageResponse` for effect results; `FaceUpQuestsUpdatedResponse` and `BuildingMarketUpdateResponse` for display updates |
| VII. Config-Driven Game Content | PASS | All 14 cards are JSON entries; server branches on `effect_type` field values, not card IDs |
| VIII. Pending State for Deferred Actions | N/A | All new effects resolve immediately (no player choices needed) |
| IX. Cancel/Unwind Reversibility | N/A | No multi-step interactions; immediate effects |
| X. Post-Action Turn Flow | PASS | Standard backstage flow: play card → resolve effect → broadcast |

All gates pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/026-intrigue-card-update/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (files to modify)

```text
config/
  intrigue.json            # Add 14 new intrigue card entries

server/
  game_engine.py           # Add 3 new effect handlers in _resolve_intrigue_effect() (~line 2371):
                           #   1. "no_effect" — do nothing, return empty details
                           #   2. "reset_quests" — discard face-up quests, refill from deck
                           #   3. "reset_buildings" — discard face-up buildings, refill from deck
                           #   4. "first_player_marker" — set first player for next round
                           # Add _draw_from_building_deck() helper (~line 73, near _draw_from_quest_deck)
                           # Add completed-quest exclusion filter in _draw_from_quest_deck()
                           # Update existing building purchase/refill to use building_discard
  models/game.py           # Add building_discard field to BoardState

card-generator/
  generate_cards.py        # Add icon rendering for new effect types in:
                           #   _draw_intrigue_effect_icons() (~line 1190)
                           #   _intrigue_effect_summary() (~line 1143)
```

**Structure Decision**: All changes fit within the existing project structure. No new files or directories needed in the source tree.

## Design Decisions

### D1: Reuse existing `draw_intrigue` effect for draw-1-intrigue cards

**Decision**: The 4 draw-1-intrigue cards use `effect_type: "draw_intrigue"` with `effect_value: {"count": 1}`. Zero new server code needed.

**Rationale**: The existing handler at game_engine.py:2403-2413 already loops `range(count)` and pops from `state.board.intrigue_deck`. Using count=1 works out of the box.

### D2: New `building_discard` field on BoardState

**Decision**: Add `building_discard: list[BuildingTile] = Field(default_factory=list)` to BoardState.

**Rationale**: Quest reshuffle already works via `quest_discard`. Buildings need the same mechanism. The field stores buildings removed from the face-up display that aren't purchased — available for reshuffle when the deck runs out.

### D3: Global reshuffle via `_draw_from_building_deck()` helper

**Decision**: Create `_draw_from_building_deck(state)` mirroring the existing `_draw_from_quest_deck(state)`. When building deck is empty and discard has cards, shuffle discard into deck and draw.

**Rationale**: The reshuffle mechanic applies globally (per spec clarification), so all building draws should go through this helper — including the existing building purchase refill logic.

### D4: Completed-quest exclusion in reshuffle

**Decision**: Before reshuffling `quest_discard` into `quest_deck`, filter out any quests whose IDs appear in any player's `completed_contracts`.

**Rationale**: Completed quests should never re-enter circulation. While they shouldn't normally be in the discard pile, the spec explicitly requires this safety check.

### D5: Effect handlers — inline in `_resolve_intrigue_effect()`

**Decision**: Add new elif branches in the existing handler rather than extracting shared functions from existing space handlers.

**Rationale**: The reset-quests space handler (game_engine.py:1847-1875) and castle first-player handler (game_engine.py:1071-1078) have the right logic, but extracting shared functions would modify tested code. Duplicating 4-5 lines per effect is safer and follows Constitution Principle V (Simplicity First).

### D6: Broadcasting reset effects

**Decision**: Reset-quests and reset-buildings effects trigger the existing `FaceUpQuestsUpdatedResponse` and `BuildingMarketUpdateResponse` broadcasts from within `_resolve_intrigue_effect()`.

**Rationale**: All clients already handle these broadcast types. No new message types needed.

## Complexity Tracking

No violations to justify.
