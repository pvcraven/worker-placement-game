# Data Model: Colored Marker Selection

## Entities

### MarkerColor (Enum/Constants)

Fixed set of seven available marker colors.

| Color  | Arcade Color Value        |
|--------|---------------------------|
| green  | arcade.color.GREEN        |
| red    | arcade.color.RED          |
| purple | arcade.color.PURPLE       |
| blue   | arcade.color.BLUE         |
| pink   | arcade.color.PINK         |
| lilac  | (186, 147, 216) — custom  |
| orange | arcade.color.ORANGE       |

**Location**: `shared/constants.py` — add `MARKER_COLORS: list[str]` constant.

### Player (Modified)

Add one field to the existing `Player` model in `server/models/game.py`:

| Field        | Type          | Default | Description                              |
|--------------|---------------|---------|------------------------------------------|
| marker_color | str \| None   | None    | Chosen marker color name (e.g., "green") |

**Validation**: Must be one of the seven `MARKER_COLORS` values or `None` (not yet selected).

**Lifecycle**:
- `None` during LOBBY phase
- Set during MARKER_SELECTION phase when player picks a color
- Immutable after selection (persists through PLACEMENT → GAME_OVER)

### GamePhase (Modified)

Add `MARKER_SELECTION = "marker_selection"` to the `GamePhase` StrEnum in `shared/constants.py`.

**Phase order**: LOBBY → MARKER_SELECTION → PLACEMENT → REASSIGNMENT → ROUND_END → GAME_OVER

### GameState (No Model Changes)

No new fields needed on `GameState`. The marker selection state is derivable from:
- `state.phase == GamePhase.MARKER_SELECTION` — indicates selection is active
- `player.marker_color is not None` — indicates player has selected
- All players having `marker_color is not None` — indicates selection is complete

## Relationships

```
GameState 1──* Player
Player *──1 MarkerColor (via marker_color field)
GamePhase controls which interactions are valid
```

## State Transitions

```
LOBBY ──[host starts game]──> MARKER_SELECTION
MARKER_SELECTION ──[all players selected + 1s pause]──> PLACEMENT
```

During MARKER_SELECTION:
- Player sends SelectMarkerRequest with a color
- Server checks: color not already claimed by another player
- If valid: sets player.marker_color, broadcasts MarkerSelectedResponse
- If invalid (already claimed): sends ErrorResponse, player must pick again
- When all players have marker_color set: start 1-second timer, then transition to PLACEMENT
