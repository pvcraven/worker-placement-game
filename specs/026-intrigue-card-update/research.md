# Research: Intrigue Card Update

## R1: Existing intrigue card effect handler

**Decision**: Add new effect types (`no_effect`, `reset_quests`, `reset_buildings`, `first_player_marker`) to `_resolve_intrigue_effect()` in game_engine.py (~line 2371). The existing `draw_intrigue` effect type already handles drawing intrigue cards with a `count` parameter, so the "draw 1 intrigue" cards (US2) require zero new server code — they just use `effect_type: "draw_intrigue"` with `effect_value: {"count": 1}`.

**Rationale**: The effect resolver at game_engine.py:2371-2468 uses an if-elif chain on `card.effect_type`. Currently handles 11 effect types. Adding 3 new types (no_effect, reset_quests, reset_buildings, first_player_marker) follows the existing pattern. The `draw_intrigue` handler at line 2403 already loops `range(count)` and pops from the intrigue deck, so `{"count": 1}` works immediately.

**Alternatives considered**:
- Using `gain_resources` with all zeros for no-effect: would work but misrepresents intent and card image generation wouldn't know it's a "do nothing" card
- Creating a generic `reset_display` effect: over-engineering when quests and buildings have different discard/deck structures

## R2: Quest deck reshuffle — already implemented

**Decision**: The existing `_draw_from_quest_deck()` at game_engine.py:73-81 already reshuffles `quest_discard` into `quest_deck` when the deck is empty. The `quest_discard` field already exists on `BoardState` (server/models/game.py:121). Need to add a safety check to exclude completed quests from the reshuffle.

**Rationale**: Lines 75-78 already move `quest_discard` → `quest_deck`, clear discard, and shuffle. Completed quests live in each player's `completed_contracts` list and should never enter the discard pile — but the spec requires a safety exclusion to prevent any edge-case bugs.

**Alternatives considered**:
- Trusting that completed quests never enter discard: simpler but fragile if future features change quest lifecycle
- Adding the exclusion filter: cheap safety net, spec requires it

## R3: Building deck — no discard pile exists

**Decision**: Add `building_discard: list[BuildingTile]` to `BoardState` and create a `_draw_from_building_deck()` helper (mirroring `_draw_from_quest_deck()`) that reshuffles discard into deck when empty.

**Rationale**: The current building system has no discard pile — buildings are either in the deck, face-up, or purchased (on a player's board). When the building deck runs out, no more buildings appear. For the reset-buildings card to work with reshuffle, we need a discard pile to hold buildings removed from the face-up display.

**Alternatives considered**:
- No discard pile, just empty display when deck runs out: user explicitly requested reshuffle behavior
- Reusing purchased buildings in reshuffle: not applicable since purchased buildings are in play on the board

## R4: Reset quests — existing space handler as template

**Decision**: The "reset quests" logic already exists in a special space handler at game_engine.py:1847-1875. The intrigue card handler will use the same pattern: move face-up quests to discard, clear display, draw new cards via `_draw_from_quest_deck()`, broadcast `FaceUpQuestsUpdatedResponse`.

**Rationale**: The existing handler does exactly what the intrigue card needs. Rather than extracting a shared function (which would touch existing tested code), the intrigue handler will replicate the 5-line core logic.

**Alternatives considered**:
- Extracting a shared `_reset_face_up_quests()` function: cleaner but riskier — modifying existing handlers for a new feature
- Calling the space handler directly: not possible since it's embedded in the place-worker flow

## R5: Reset buildings — new handler needed

**Decision**: Create reset-buildings logic as a new branch in `_resolve_intrigue_effect()`. Move face-up buildings to `building_discard`, clear display, draw new buildings via the new `_draw_from_building_deck()`, broadcast `BuildingMarketUpdateResponse`.

**Rationale**: No existing reset-buildings handler exists. The pattern mirrors the quest reset logic but uses building-specific data structures and broadcast messages.

## R6: First player marker — reuse castle logic

**Decision**: Add `first_player_marker` branch in `_resolve_intrigue_effect()`. Clear `has_first_player_marker` from all players, set it on the playing player, update `state.board.first_player_id`. This is the same logic as the castle handler at game_engine.py:1071-1078 but without the intrigue card draw bonus.

**Rationale**: The castle handler's first-player logic is 4 lines. Duplicating in the intrigue effect resolver is simpler and safer than extracting a shared function.

## R7: Card image generation

**Decision**: Add new branches in `_draw_intrigue_effect_icons()` (game_engine.py:1190-1314) and `_intrigue_effect_summary()` (game_engine.py:1143-1180) for each new effect type.

**Rationale**: Each effect type needs a visual icon on the card image and a text summary. The no_effect type shows a shrug or "no effect" text. reset_quests shows quest card icons with a refresh arrow. reset_buildings shows building icons with a refresh arrow. first_player_marker shows a "1st" badge or star icon.

## R8: Client-side handling for new effects

**Decision**: The client handler `_on_worker_placed_backstage()` processes the `effect_details` dict from the server response. For `no_effect`, no client changes needed (the card is already removed from hand by the server). For `draw_intrigue`, already handled. For `reset_quests` and `reset_buildings`, the existing `FaceUpQuestsUpdatedResponse` and `BuildingMarketUpdateResponse` broadcasts handle updating all clients. For `first_player_marker`, the effect_details will include the update and clients read from the next `RoundEndResponse`.

**Rationale**: Most new effects are handled by existing broadcast mechanisms. The intrigue effect resolver on the server is authoritative — clients just need to update their local state from broadcast messages they already handle.
