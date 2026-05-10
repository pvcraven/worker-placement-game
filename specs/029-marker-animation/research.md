# Research: Marker Placement Animation

## 1. Arcade Easing API

**Decision**: Use `arcade.anim.ease()` with `Easing.SINE` for all animations.

**Rationale**: The project already includes working examples (`easing_example_1.py`, `easing_example_2.py`) demonstrating the API. `arcade.anim.ease(start, end, start_time, end_time, current_time, func=Easing.SINE)` provides exactly the interpolation needed — two-axis position easing with configurable curve. No external dependency needed.

**Alternatives considered**:
- Custom interpolation math: More control but reinvents the wheel when Arcade provides it.
- Arcade's `AnimatedTimeBasedSprite`: Designed for frame-based sprite animation, not position easing.

**API signature**:
```python
from arcade.anim import ease, Easing

eased_value = ease(
    start_value,     # float - start position (x or y)
    end_value,       # float - end position (x or y)
    start_time,      # float - when animation started (elapsed time)
    end_time,        # float - when animation ends (start_time + duration)
    current_time,    # float - current elapsed time
    func=Easing.SINE # easing curve
)
```

## 2. Player List Rendering (Current State)

**Decision**: Replace `arcade.draw_circle_filled()` with worker marker sprites in `_draw_player_list()`.

**Rationale**: The current implementation (game_view.py:2909) uses a primitive draw call which also violates Constitution Principle I (Arcade Rendering Standards). Replacing with sprites both fulfills the feature requirement and fixes the constitution violation. Player positions are computed dynamically each frame based on text width — we need to store these positions for animation origin lookup.

**Current code flow**:
- `_draw_player_list(ch, status_h, s)` iterates `turn_order`
- Circle position: `(list_x + circle_r, row_top)` per player
- `list_x` advances horizontally based on text width
- No pre-stored positions — recalculated each frame

**Implementation approach**: Cache player marker positions in a dict (`_player_marker_positions: dict[str, tuple[float, float]]`) during `_draw_player_list()`, updated each frame. Animation manager reads from this dict for origin coordinates.

## 3. Worker Placement Flow (Client Side)

**Decision**: Hook animation into `_on_worker_placed()` before `_refresh_board()`.

**Rationale**: When `_on_worker_placed()` runs, we know the `player_id` and `space_id`. We can compute the animation start position (from player marker position dict) and end position (from board renderer space coordinates) before calling `_refresh_board()`. The animation sprite is separate from the board renderer's worker sprites — it's a temporary overlay that flies to the destination. When the animation completes, the board renderer's normal static worker sprite is already in place.

**Flow**:
1. `_on_worker_placed(msg)` fires
2. Look up origin coords from `_player_marker_positions[player_id]`
3. Look up target coords from `board_renderer.get_space_position(space_id)`
4. Create animation sprite + queue animation
5. Call `_refresh_board()` — static worker appears immediately at destination
6. Animation overlays on top, giving visual impression of movement
7. On completion, animation sprite is removed (static sprite remains)

**Note**: The board renderer already shows the worker at the destination instantly. The animation is purely visual overlay. During animation, both the static marker and the flying marker are visible — the flying marker is more prominent and draws attention. This is acceptable and simpler than delaying the static placement.

## 4. Worker Recall Flow (Client Side)

**Decision**: Hook animation into `_on_round_end()` before clearing workers.

**Rationale**: `_on_round_end()` (game_view.py:1831-1895) clears all `occupied_by` fields and calls `_refresh_board()`, which removes all worker sprites. For recall animation, we need to capture current worker positions before clearing, queue animations from those positions back to each player's name area, then clear the board. The animations play as visual overlay while the board state is already clean.

**Flow**:
1. `_on_round_end(msg)` fires
2. Before clearing state: snapshot current worker positions from board renderer
3. Queue reverse animations (board position → player name position) for each worker
4. Clear board state and call `_refresh_board()` (removes static sprites)
5. Animations play as overlay, each marker flying back to its owner's name

## 5. Worker Reassignment Flow (Client Side)

**Decision**: Hook animation into `_on_worker_reassigned()`.

**Rationale**: `_on_worker_reassigned()` (game_view.py:1648-1747) clears the backstage slot and occupies the target space. For animation, we need the backstage slot's board position (origin) and the target space position (destination). The flow mirrors normal placement but with a different origin.

**Flow**:
1. `_on_worker_reassigned(msg)` fires with `from_slot` and `to_space_id`
2. Look up backstage slot position from board renderer
3. Look up target space position from board renderer
4. Queue animation from backstage position to target position
5. Update board state and call `_refresh_board()`

## 6. Sound System

**Decision**: Load `tick_001.ogg` in `GameView.__init__()` and pass to animation manager.

**Rationale**: The existing sound pattern loads sounds in `__init__` (game_view.py:60-65) and plays via `arcade.play_sound()`. No sound manager exists. For this feature, add `self._tick_sound = arcade.load_sound("client/assets/sounds/tick_001.ogg")` and have the animation manager call `arcade.play_sound()` when an animation with a sound starts.

**File confirmed**: `client/assets/sounds/tick_001.ogg` exists (4.4 KB OGG Vorbis).

## 7. Animation Architecture

**Decision**: Create `AnimationManager` class in `client/ui/animation_manager.py`.

**Rationale**: The spec requires a reusable animation system (FR-007, User Story 4). A dedicated manager class with a list of active animations, updated per-frame in `on_update()`, provides clean separation. Each animation is a dataclass holding sprite, start/end positions, timing, easing function, and optional sound.

**Alternatives considered**:
- Inline animation in GameView: Simpler but not reusable for future card animations.
- Arcade's built-in animation system: Designed for frame-based sprite animation, not position easing.

**Note on Principle V (Simplicity/YAGNI)**: The user explicitly requested the abstraction for future card animation reuse. This is a deliberate design choice, not speculation. The abstraction is minimal — one manager class and one animation dataclass.
