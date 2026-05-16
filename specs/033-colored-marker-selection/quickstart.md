# Quickstart: Colored Marker Selection

## Integration Scenarios

### Scenario 1: Normal Game Start (Happy Path)

1. Host creates game, players join and ready up
2. Host clicks Start
3. Server runs `_initialize_game()` (deals cards, sets up board)
4. Server sets `phase = MARKER_SELECTION`
5. Server broadcasts `MarkerSelectionStartResponse` with all 7 colors available
6. Each client shows the marker selection dialog
7. Players click colors one by one
8. For each selection: server validates → sets `player.marker_color` → broadcasts `MarkerSelectedResponse`
9. After last player selects (`all_selected: true`): clients show final assignments for ~1 second
10. Server sends `GameStartedResponse` to each player (filtered state includes `marker_color`)
11. Clients dismiss dialog, render board with chosen colors

### Scenario 2: Conflict Resolution

1. Player A and Player B both click "green" at nearly the same time
2. Server processes Player A's `SelectMarkerRequest` first → accepts, broadcasts
3. Server processes Player B's request → color already claimed → sends `ErrorResponse`
4. Player B's client shows "green" as unavailable (already updated from Player A's broadcast)
5. Player B selects a different color

### Scenario 3: Reconnection During Selection

1. Player C disconnects during marker selection
2. Other players continue selecting
3. Player C reconnects → receives `StateSyncResponse`
4. Client sees `phase: "marker_selection"` → shows marker dialog
5. Client reads each player's `marker_color` from state → shows already-claimed markers
6. Player C's `marker_color` is `null` → dialog is interactive, player can pick

### Scenario 4: Board Rendering with Chosen Colors

1. Game starts, board renders
2. `BoardRenderer` looks up each player's `marker_color` from game state
3. Maps color name → arcade color value using `MARKER_COLOR_MAP`
4. Renders worker tokens in chosen colors instead of index-based colors
5. All player-identifying UI uses the chosen color

## Key Integration Points

| Component | File | Change |
|-----------|------|--------|
| GamePhase enum | `shared/constants.py` | Add `MARKER_SELECTION` |
| Player model | `server/models/game.py` | Add `marker_color: str \| None` |
| Message types | `shared/messages.py` | Add 3 new message types |
| Game start flow | `server/lobby.py` | Insert selection phase |
| Selection handler | `server/lobby.py` | New `select_marker()` handler |
| Message dispatch | `server/network.py` | Route `select_marker` action |
| Selection dialog | `client/ui/marker_selection_dialog.py` | New dialog class |
| Game view | `client/views/game_view.py` | Handle new messages, show dialog |
| Board renderer | `client/ui/board_renderer.py` | Use player color instead of index |
| Marker assets | `client/assets/card_images/markers/` | Add pink + lilac PNGs |
| Reconnect | `server/lobby.py` | Handle reconnect during selection |
