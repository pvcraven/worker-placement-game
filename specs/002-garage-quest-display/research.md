# Research: Garage Quest Display Rework

**Date**: 2026-04-13 | **Feature**: 002-garage-quest-display

## 1. Deck Reshuffle Mechanics

**Decision**: Automatic reshuffle of discard pile into deck when a draw is attempted and the deck is empty.

**Rationale**: This is the standard approach in card games (e.g., Dominion, Clank!). The reshuffle happens lazily — only when a draw is needed and the deck is empty — rather than proactively monitoring deck size. This simplifies the logic to a single check at draw time.

**Alternatives considered**:
- Proactive reshuffle when deck hits 0 — rejected because it reshuffles unnecessarily (deck may not be drawn from again that round).
- No reshuffle, deck depletion is permanent — rejected per user clarification that discarded cards should recycle.

**Implementation approach**: Extract a `_draw_from_quest_deck()` helper in game_engine.py that checks deck emptiness, reshuffles discard pile if needed, then draws. All quest draws go through this single function.

## 2. Face-Up Card Selection Flow

**Decision**: Two-phase interaction for Spots 1 and 2: (1) place worker on spot → server acknowledges and sends face-up cards, (2) player selects a card → server validates and resolves.

**Rationale**: The player needs to see the available face-up cards and choose one. This requires a client→server→client round trip. The existing `PlaceWorkerRequest` flow places the worker, then a new `SelectQuestCardRequest` message handles the card pick.

**Alternatives considered**:
- Single message with card selection included — rejected because the player needs to see and choose interactively, not pre-select.
- Automatic card assignment (random) — rejected because strategic card selection is a core mechanic.

## 3. Rename Strategy

**Decision**: Rename all identifiers in a single pass — space IDs, class names, constants, message types, and display strings — rather than using aliases or compatibility layers.

**Rationale**: This is a development-phase change with no external consumers. A clean rename avoids confusion from having both old and new names coexisting. The rename map in plan.md lists every identifier that changes.

**Alternatives considered**:
- Alias old names to new (backwards compat) — rejected because there are no external consumers and it adds complexity.
- Rename only display strings, keep code identifiers — rejected because the code should match the game's terminology for maintainability.

## 4. Toggle Button UI Pattern

**Decision**: Use Arcade's UIFlatButton as toggle buttons positioned at the bottom of the game view, above the resource bar. Toggling shows/hides an overlay panel with scrollable card display.

**Rationale**: Arcade's GUI toolkit supports flat buttons and layout management. An overlay panel avoids permanently reducing the board area. The existing `CardRenderer` class already handles drawing quest and intrigue cards.

**Alternatives considered**:
- Side panel (always visible) — rejected per user clarification that hand should be hidden by default.
- Tab-based panel — equivalent complexity to toggle buttons but less familiar UX.

## 5. Card Privacy

**Decision**: Server already filters state per player (see `_filter_state_for_player()` in lobby.py). Quest and intrigue hands are only sent to the owning player. No additional server changes needed for privacy.

**Rationale**: The existing `_filter_state_for_player()` method hides opponent hand contents. The toggle buttons are client-side only — they show/hide data the client already has.

**Alternatives considered**: None — the architecture already supports this.
