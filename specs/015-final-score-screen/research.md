# Research: Final Score Screen

**Feature**: 015-final-score-screen
**Date**: 2026-04-21

## R1: Existing Results Screen

**Decision**: Replace the existing `results_view.py` flow with an in-game dialog inside `game_view.py`.

**Rationale**: The spec requires a dialog "similar to Player Overview" — an overlay on the game board, not a separate view. The existing `results_view.py` navigates away from the game view entirely. The new dialog keeps the player in context and supports two modes (manual toggle and game-over).

**Current flow**: `game_over` message → `window.show_results()` → `ResultsView` → "Return to Menu" disconnects.

**New flow**: `game_over` message → set `_game_over_final = True` and show dialog in `game_view` → "Close" → navigate to lobby (not menu).

**Alternatives considered**:
- Modify existing `ResultsView` — rejected because spec requires an overlay dialog within the game view, not a separate view. Also need to support manual toggle during gameplay.
- Keep both ResultsView and new dialog — rejected for simplicity (Principle V). The new dialog fully replaces ResultsView.

## R2: VP Calculation Location

**Decision**: Server calculates authoritative final scores (for game-over). Client calculates estimated scores for the manual toggle during gameplay.

**Rationale**:
- Server already calculates `base_vp` and `producer_bonus` in `_end_game()` (game_engine.py:355-413). Adding `resource_vp` here is natural.
- During gameplay, opponent producer cards are hidden (`_filter_state_for_player` sets them to None). The manual toggle can show game VP and resource VP for all players, but genre bonus VP is only available for the local player. For opponents, genre bonus shows as "?" or is omitted until game-over.
- This respects Principle III (client-server separation): authoritative scoring on server, display-only on client.

**Alternatives considered**:
- Client-only calculation — rejected because it would require revealing opponent producer cards during gameplay, breaking the hidden-information rule.
- Server-only (no manual toggle scores) — rejected because the spec requires the button to work during gameplay.

## R3: FinalPlayerScore Model Extension

**Decision**: Add `resource_vp` field to `FinalPlayerScore` in `shared/messages.py`. Rename `base_vp` to `game_vp` for clarity matching the spec terminology.

**Rationale**: The spec defines three VP categories: Game VP, Genre Bonus VP, Resource VP. The current `FinalPlayerScore` has `base_vp` (game VP) and `producer_bonus` (genre bonus VP) but no resource VP. Adding it maintains the Pydantic model pattern (Principle II).

**Current FinalPlayerScore fields**: player_id, player_name, base_vp, producer_bonus, producer_card, total_vp, rank.
**New fields**: resource_vp (int). Also rename base_vp → game_vp, producer_bonus → genre_bonus_vp for spec alignment.

## R4: Dialog Layout

**Decision**: Horizontal layout with one column per player, each containing producer card sprite on top, then text rows below for VP breakdown. Follows the Player Overview dialog style (dark background, white border, centered).

**Rationale**: The spec says "one column per player" with producer card image and scoring rows. The Player Overview uses arcade.Text objects (cached), ShapeElementList for backgrounds, matching Constitution Principle I.

**Layout per player column**:
1. "WINNER" text (if applicable, above card)
2. Producer card sprite (or "No Producer" placeholder text)
3. Player name (bold)
4. Game VP: `XX`
5. Genre Bonus: `XX`
6. Resource VP: `XX`
7. Total: `XX` (bold)

**Close button**: Rendered at bottom-center of dialog using a UIFlatButton in self.ui manager or drawn as a clickable rectangle with hit-test.

## R5: Game-Over vs Manual Toggle Behavior

**Decision**: Use a two-flag system: `_show_final_screen` (dialog visible) and `_game_over_final` (game has ended). The dialog rendering is the same for both modes; only the Close button behavior differs.

**Rationale**: Single rendering path keeps code simple (Principle V). The mode flag only affects what Close does.

- Manual toggle: `_show_final_screen = True`, `_game_over_final = False` → Close sets `_show_final_screen = False`
- Game-over: `_show_final_screen = True`, `_game_over_final = True` → Close navigates to lobby
- Toggle button: If `_game_over_final`, the toggle button is ignored

## R6: Lobby Navigation on Game-Over Close

**Decision**: On Close during game-over, call `self.window.network.disconnect()` then `self.window.show_lobby()`.

**Rationale**: The spec says "user goes back to lobby." The existing results_view calls `show_menu()` (main menu), but the spec explicitly says lobby. Using `show_lobby()` which already exists on `GameWindow`.

**Alternative considered**: Navigate to menu like current ResultsView — rejected because spec explicitly says lobby.
