# Quickstart: Marker Placement Animation

## What This Feature Does

Adds animated worker marker placement to the board game. When a worker is placed on a board spot, the marker visually flies from the player's name area to the target spot using smooth sine easing, accompanied by a tick sound. In multiplayer, you see other players' markers animate from their names. Workers animate back on recall, and reassigned workers animate from backstage slots to their target.

## Key Files

| File | Role |
|------|------|
| `client/ui/animation_manager.py` | **NEW** — AnimationManager + EaseAnimation |
| `client/views/game_view.py` | Integrate animations into placement, recall, reassignment handlers |
| `client/ui/board_renderer.py` | Expose space position lookup for animation targets |

## How It Works

1. **AnimationManager** lives on GameView, updated each frame in `on_update()`, drawn in `on_draw()`
2. When a placement/recall/reassignment message arrives, an animation is queued with start position, end position, sine easing, and the tick sound
3. Game state updates immediately (animation is purely visual overlay)
4. AnimationManager interpolates sprite positions each frame using `arcade.anim.ease()`
5. On completion, the animation sprite is removed (the static worker marker is already in place)

## Running

```bash
# Start server
cd src && python -m server.network

# Start client (separate terminal)
cd src && python -m client.game_window
```

Place a worker on any spot — you should see the marker animate from your name to the spot with a tick sound.

## Testing

This feature is client-side only. Manual testing:
- Place workers and verify animation from player name → spot
- Watch other player's placements in multiplayer
- Complete a round and verify recall animation (spot → player name)
- Use backstage slots and verify reassignment animation (backstage → target)
- Resize window during animation — should complete without glitches

## Extending

To add a new animation type (e.g., cards), use the AnimationManager:

```python
sprite = arcade.Sprite(texture)
self.animation_manager.animate(
    sprite=sprite,
    start=(from_x, from_y),
    end=(to_x, to_y),
    duration=1.0,
    easing=Easing.SINE,
    sound=some_sound,
)
```
