# Data Model: Marker Placement Animation

## Entities

### EaseAnimation

Represents a single sprite moving from one position to another over time using an easing function.

| Attribute      | Type                  | Description                                                      |
|----------------|-----------------------|------------------------------------------------------------------|
| sprite         | arcade.Sprite         | The sprite being animated (created per animation, removed on completion) |
| start_x        | float                 | Starting X position (screen coordinates)                        |
| start_y        | float                 | Starting Y position (screen coordinates)                        |
| end_x          | float                 | Target X position (screen coordinates)                          |
| end_y          | float                 | Target Y position (screen coordinates)                          |
| start_time     | float                 | Elapsed game time when animation began                          |
| duration       | float                 | Animation duration in seconds                                    |
| easing         | Easing                | Easing function (e.g., Easing.SINE)                             |
| sound          | arcade.Sound or None  | Sound to play when animation starts                             |
| on_complete    | callback or None      | Optional callback invoked when animation finishes               |

**Lifecycle**: Created → Active (updating position each frame) → Completed (sprite removed, callback invoked)

### AnimationManager

Manages a collection of active animations, updating them per-frame and cleaning up completed ones.

| Attribute        | Type                    | Description                                              |
|------------------|-------------------------|----------------------------------------------------------|
| _animations      | list[EaseAnimation]     | Currently active animations                               |
| _sprite_list     | arcade.SpriteList       | SpriteList for all animating sprites (for batch rendering) |
| _elapsed         | float                   | Running elapsed time (accumulated delta_time)             |

**Methods**:
- `animate(sprite, start, end, duration, easing, sound, on_complete)` — queue a new animation
- `update(delta_time)` — advance all active animations, remove completed ones
- `draw()` — render all animating sprites
- `clear()` — cancel all active animations immediately

### Player Marker Positions (stored on GameView)

A dict mapping player IDs to their current marker sprite position in the player list area.

| Attribute                | Type                           | Description                                   |
|--------------------------|--------------------------------|-----------------------------------------------|
| _player_marker_positions | dict[str, tuple[float, float]] | player_id → (x, y) screen position of marker  |
| _player_marker_sprites   | dict[str, arcade.Sprite]       | player_id → cached marker sprite in player list |

Updated each frame in `_draw_player_list()`. Read by animation queueing code to determine animation origins.

## Relationships

```
GameView
  ├── AnimationManager (owns, created in _build_ui)
  │     ├── EaseAnimation[] (manages lifecycle)
  │     └── SpriteList (renders animating sprites)
  ├── _player_marker_positions (dict, updated in _draw_player_list)
  ├── _player_marker_sprites (dict, worker sprites in player list)
  └── BoardRenderer (existing, provides space positions)
```

## State Transitions

```
Animation States:
  Created ─── update() called ──→ Active (position interpolating)
  Active ──── elapsed >= duration ──→ Completed (sprite removed, callback fired)
  Active ──── clear() called ──→ Cancelled (sprite removed, no callback)
```

## No Server-Side Changes

This feature is entirely client-side. No new Pydantic models, network messages, or server state changes are needed. All existing messages (`worker_placed`, `worker_reassigned`, `round_end`) already carry sufficient data.
