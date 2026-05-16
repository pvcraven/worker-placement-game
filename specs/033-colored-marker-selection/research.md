# Research: Colored Marker Selection

## Current Color System

**Decision**: Replace index-based color assignment with player-chosen colors from a fixed palette of seven.

**Rationale**: Currently `board_renderer.py` assigns colors by player `slot_index` from a hardcoded list of 5 (`_PLAYER_COLORS`, `_COLOR_NAMES`). The new feature lets players choose their own color from 7 options, making the assignment personal and accommodating the full 5-player max with room to spare.

**Current state**:
- `client/ui/board_renderer.py` lines 43-51: `_PLAYER_COLORS` and `_COLOR_NAMES` (5 entries)
- Marker PNGs: `client/assets/card_images/markers/worker_{red,blue,green,orange,purple}.png`
- Player model (`server/models/game.py`): No `marker_color` field
- `shared/constants.py`: `GamePhase` has LOBBY, PLACEMENT, REASSIGNMENT, ROUND_END, GAME_OVER — no MARKER_SELECTION
- `shared/messages.py`: No marker selection message types
- `server/lobby.py`: `start_game()` calls `_initialize_game()` then immediately sends `GameStartedResponse`

**Alternatives considered**: Assign colors randomly instead of letting players choose — rejected because the spec requires player agency in selection.

## New Game Phase

**Decision**: Add `MARKER_SELECTION` to `GamePhase` enum, inserted between LOBBY and PLACEMENT.

**Rationale**: The selection phase needs its own distinct state so the server can track which phase the game is in, the client can show the selection dialog, and reconnection during selection works correctly via `StateSyncResponse`.

**Alternatives considered**: Use a flag on GameState (e.g., `marker_selection_active: bool`) instead of a new phase — rejected because a proper phase is cleaner for reconnection logic and follows existing patterns.

## Marker Assets

**Decision**: Generate 2 new marker PNGs (pink, lilac) using Pillow, matching the existing marker style. Keep existing 5 markers.

**Rationale**: 5 of the 7 colors already have PNGs. Pink and lilac need to be created to match. The existing card image generator uses Pillow for similar tasks.

**Files needed**:
- `client/assets/card_images/markers/worker_pink.png`
- `client/assets/card_images/markers/worker_lilac.png`

## Selection Dialog

**Decision**: Create a new `MarkerSelectionDialog` class in `client/ui/` using `arcade.gui.UIAnchorLayout` with the show/hide pattern used by `InfoDialog`.

**Rationale**: The existing dialog system (`info_dialog.py`, `dialogs.py`) uses Arcade's GUI anchoring. The marker dialog follows the same pattern but with interactive click targets (7 colored circles/markers) rather than just text display.

**Alternatives considered**: Reuse the existing `dialogs.py` infrastructure — partially applicable but marker selection needs custom layout with clickable color targets and dynamic state (claimed/unclaimed markers).

## Message Protocol

**Decision**: Add 3 new message types following the Request → Handler → Broadcast pattern from Constitution Principle VI.

**Rationale**: First-come-first-served conflict resolution must be server-authoritative. The server validates each selection (unclaimed check) and broadcasts the result to all clients.

**New messages**:
1. `SelectMarkerRequest` (client → server): `{action: "select_marker", color: str}`
2. `MarkerSelectedResponse` (server → all): `{action: "marker_selected", player_id: str, color: str, all_selected: bool}`
3. `MarkerSelectionStartResponse` (server → all): `{action: "marker_selection_start", available_colors: list[str], players: list[dict]}`

## Server Flow Changes

**Decision**: Insert marker selection phase between `_initialize_game()` and sending `GameStartedResponse` in `lobby.py`.

**Rationale**: The flow becomes:
1. Host clicks Start → `_initialize_game()` runs (deals cards, sets up board)
2. Server sets `phase = MARKER_SELECTION` and broadcasts `MarkerSelectionStartResponse`
3. Each player sends `SelectMarkerRequest`
4. Server validates, stores color on Player model, broadcasts `MarkerSelectedResponse`
5. When all players selected → server waits ~1 second → sets `phase = PLACEMENT` → sends `GameStartedResponse`

**Alternatives considered**: Run selection before `_initialize_game()` — rejected because the game state needs to exist for reconnection to work during selection.

## Player Model Changes

**Decision**: Add `marker_color: str | None = None` field to the `Player` model.

**Rationale**: The color must persist on the player for the entire game — used by board rendering, any future player-identifying UI elements, and included in state sync for reconnection.

## Board Renderer Changes

**Decision**: Replace index-based `_PLAYER_COLORS` lookup with a lookup from `player.marker_color`.

**Rationale**: Once players choose colors, the renderer should use those instead of slot-index mapping. The `_PLAYER_COLORS` list becomes a fallback/lookup table mapping color names to arcade color values. Update `_COLOR_NAMES` and `_PLAYER_COLORS` to include all 7 colors.

## Reconnection During Selection

**Decision**: Handle reconnection during `MARKER_SELECTION` phase by re-sending `MarkerSelectionStartResponse` with current selection state.

**Rationale**: Constitution Principle VI requires `StateSyncResponse` to fully restore state on reconnect. During marker selection, the reconnecting player needs to see which markers are already claimed and be able to select their own (if they haven't yet).
