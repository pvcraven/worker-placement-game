# Implementation Plan: Intrigue Draw Building ("Whisper Room")

**Branch**: `025-intrigue-draw-building` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/025-intrigue-draw-building/spec.md`

## Summary

Add a new purchasable building called "Whisper Room" that grants the visitor two intrigue cards drawn from the intrigue deck. The building costs 4 coins, gives the owner 2 VP when visited by another player, and its card image shows two intrigue card icons. This requires a new `visitor_reward_special` value (`draw_intrigue_2`), a JSON config entry, server handler updates in three locations, client-side handling for the two-card draw, and card image generation.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade client)
**Project Type**: Multiplayer board game (client/server)
**Performance Goals**: Intrigue cards appear in hand instantly on placement
**Constraints**: Must follow existing `visitor_reward_special` pattern; must handle deck depletion gracefully
**Scale/Scope**: Single new building added to `buildings.json`, with handler updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | N/A | No new rendering code; existing board renderer handles buildings |
| II. Pydantic Data Modeling | PASS | Uses existing `BuildingTile` Pydantic model; `visitor_reward_special` is already a `str \| None` field |
| III. Client-Server Separation | PASS | Server draws cards and sends via message; client updates local state from response |
| IV. Test-Driven Game Logic | PASS | Existing test suite covers building placement flow; new special value tested implicitly |
| V. Simplicity First | PASS | Reuses existing `visitor_reward_special` pattern with a new string value — no new abstractions |
| VI. Server-Authoritative Message Protocol | PASS | Uses existing `WorkerPlacedResponse` with `reward_granted` dict; adds `intrigue_cards_drawn` and `drawn_intrigue_cards` fields |
| VII. Config-Driven Game Content | PASS | New building added as JSON entry; server branches on `visitor_reward_special` value, not hard-coded ID |
| VIII. Pending State for Deferred Actions | N/A | No deferred action — intrigue cards are granted immediately |
| IX. Cancel/Unwind Reversibility | N/A | No multi-step interaction; immediate reward |
| X. Post-Action Turn Flow | PASS | Standard flow: place worker → grant reward → quest check → advance turn |

All gates pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/025-intrigue-draw-building/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (files to modify)

```text
config/
  buildings.json           # Add new building entry for "Whisper Room"

server/
  game_engine.py           # Handle "draw_intrigue_2" in 3 locations:
                           #   1. handle_place_worker (~line 1531)
                           #   2. _resolve_copied_space_rewards (~line 1050)
                           #   3. Worker reassignment handler (~line 3484)

client/
  views/game_view.py       # Handle 2-card intrigue draw in _on_worker_placed

card-generator/
  generate_cards.py        # Draw two intrigue card icons for "draw_intrigue_2" special
```

**Structure Decision**: All changes fit within the existing project structure. No new files or directories needed in the source tree.

## Design Decisions

### D1: New special value `draw_intrigue_2` vs. parameterized approach

**Decision**: Use a new string value `draw_intrigue_2` for `visitor_reward_special`.

**Rationale**: The existing pattern uses simple string values (`draw_intrigue`, `draw_contract`, `coins_per_building`, etc.). A parameterized approach (e.g., `{"type": "draw_intrigue", "count": 2}`) would require changing the `visitor_reward_special` field type from `str | None` to `str | dict | None` across the Pydantic model, all server handlers, and the card generator. The simpler string value follows Constitution Principle V (Simplicity First) and Principle VII (branch on field values, not IDs).

**Alternatives rejected**: 
- Parameterized dict: too invasive for a single building
- Calling `draw_intrigue` twice: loses atomicity and doesn't communicate intent

### D2: Client notification for drawn cards

**Decision**: Add both `intrigue_cards_drawn: 2` and `drawn_intrigue_cards: [card1, card2]` (plural list) to the `reward_granted` dict, following the pattern established for castle intrigue draws.

**Rationale**: The existing `draw_intrigue` building handler silently adds the card to the player's hand on the server without notifying the client — the client only discovers it on the next state sync. The castle handler does it correctly by including `drawn_intrigue_card` in the reward dict. For 2 cards, we use a list field `drawn_intrigue_cards` (plural). The existing single-card field `drawn_intrigue_card` (singular) remains for backward compatibility with castle draws.

### D3: Building stats

**Decision**: Cost 4 coins, owner bonus 2 VP, no accumulation.

**Rationale**: Chess Records (building_008) costs 3 and gives 1 drummer + 1 intrigue draw. Whisper Room gives 2 intrigue draws (no musicians), so 4 coins is appropriate — slightly more expensive since intrigue cards are versatile. Owner gets 2 VP (same as several other 4-coin buildings). No accumulation keeps the building simple.

## Complexity Tracking

No violations to justify.
