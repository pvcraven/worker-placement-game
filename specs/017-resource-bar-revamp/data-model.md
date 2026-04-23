# Data Model: Resource Bar Revamp

## Entities

### Resource Icon (PNG asset)

A small PNG image representing a single unit of a resource type, used as a sprite in the bottom panel.

| Field | Description |
|-------|-------------|
| filename | One of: `guitarist.png`, `bass_player.png`, `drummer.png`, `singer.png`, `coin.png` |
| dimensions | 72x72 pixels (2x render size) |
| format | PNG with transparent background |
| visual | Colored shape (square or circle) with black outline |
| location | `client/assets/card_images/icons/` |

### Card Icon (PNG asset)

A miniature playing-card-shaped image used next to quest/intrigue counts.

| Field | Description |
|-------|-------------|
| filename | One of: `quest_icon.png`, `intrigue_icon.png` |
| dimensions | 84x114 pixels (2x _CARD_ICON_W x _CARD_ICON_H) |
| format | PNG with transparent background |
| visual | Card shape with black border, white inner border, colored back, centered letter |
| location | `client/assets/card_images/icons/` |

### ResourceBar State (runtime, in-memory)

Internal state of the resource bar widget during rendering.

| Field | Type | Description |
|-------|------|-------------|
| resources | dict[str, int] | Current resource counts (guitarists, bass_players, drummers, singers, coins) |
| workers_left | int | Number of unplaced workers |
| victory_points | int | Player's VP total |
| intrigue_count | int | Cards in intrigue hand |
| quests_open | int | Active quest count |
| quests_closed | int | Completed quest count |
| player_color | str | Player's color name for marker lookup |

## Relationships

- Resource Icons are loaded once and cached in a SpriteList by the ResourceBar
- Card Icons are loaded once and cached alongside resource icons in the same SpriteList
- Worker Marker PNGs already exist in `markers/` directory and are loaded by color name
- ResourceBar reads player_color from game state (passed through game_view)
