# Message Contracts: Colored Marker Selection

All messages follow Constitution Principle VI (Server-Authoritative Message Protocol).

## Client → Server

### SelectMarkerRequest

Sent when a player clicks a marker color during the selection phase.

```python
class SelectMarkerRequest(BaseModel):
    action: Literal["select_marker"] = "select_marker"
    color: str  # One of MARKER_COLORS
```

**Validation**:
- `color` must be in `MARKER_COLORS`
- Game must be in `MARKER_SELECTION` phase
- Player must not have already selected (`marker_color is None`)
- Color must not be claimed by another player

**Error responses**:
- `"INVALID_ACTION"` if game not in marker selection phase
- `"INVALID_ACTION"` if player already selected a marker
- `"INVALID_ACTION"` if color already claimed by another player

## Server → Client

### MarkerSelectionStartResponse

Broadcast to all players when the game transitions from LOBBY to MARKER_SELECTION.

```python
class MarkerSelectionStartResponse(BaseModel):
    action: Literal["marker_selection_start"] = "marker_selection_start"
    available_colors: list[str]  # All 7 MARKER_COLORS initially
    players: list[dict]  # [{player_id, display_name, marker_color}]
```

**When sent**: After `_initialize_game()` completes, instead of immediately sending `GameStartedResponse`.

### MarkerSelectedResponse

Broadcast to all players when a player successfully selects a marker.

```python
class MarkerSelectedResponse(BaseModel):
    action: Literal["marker_selected"] = "marker_selected"
    player_id: str
    player_name: str
    color: str
    all_selected: bool  # True when this was the last player to pick
```

**When sent**: After server validates and applies a `SelectMarkerRequest`.

**Client behavior**:
- Update the marker dialog to show this player's name under the selected color
- Mark the color as unavailable
- If `all_selected` is True: start a ~1 second display pause, then expect `GameStartedResponse`

## Reconnection

During `MARKER_SELECTION` phase, `StateSyncResponse` already includes the full game state with each player's `marker_color` field. The client can reconstruct the selection dialog state from:
- `state.phase == "marker_selection"` → show selection dialog
- Each player's `marker_color` value → show claimed markers
- Current player's `marker_color` → disable interaction if already selected

Additionally, `_resend_pending_prompts()` in `lobby.py` should send `MarkerSelectionStartResponse` to the reconnecting player if the game is in `MARKER_SELECTION` phase and the player hasn't selected yet.
