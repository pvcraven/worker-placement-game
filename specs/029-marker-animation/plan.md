# Implementation Plan: Marker Placement Animation

**Branch**: `029-marker-animation` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/029-marker-animation/spec.md`

## Summary

Add animated worker marker placement to the game. Replace colored circles in the player list with worker marker sprites. When workers are placed, animate the marker from the player's name area to the board spot using sine easing with a tick sound effect. Animate recall (round end) in reverse and reassignment from backstage slots. Build a reusable AnimationManager that future card animations can leverage.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (ease, Easing)
**Storage**: N/A (client-side rendering only)
**Testing**: pytest + ruff (server-only tests; this feature is client-side)
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Desktop game (client-server)
**Performance Goals**: 60 fps maintained during animations
**Constraints**: Animations must be non-blocking; game state updates immediately
**Scale/Scope**: 1-5 players, up to ~15 worker sprites animating during recall

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | **FIX REQUIRED** | Current `_draw_player_list()` uses `arcade.draw_circle_filled()` — must replace with sprites. This feature resolves the violation. |
| II. Pydantic Data Modeling | PASS | No new network/config data. Animation is client-only. |
| III. Client-Server Separation | PASS | All changes are client-side. No game state mutation from client. |
| IV. Test-Driven Game Logic | PASS | No server game logic changes. |
| V. Simplicity First | JUSTIFIED | User explicitly requested animation abstraction for future card animation reuse. Abstraction is minimal (one manager class, one dataclass). |
| VI. Server-Authoritative Protocol | PASS | No new messages. Using existing worker_placed, worker_reassigned, round_end responses. |
| VII. Config-Driven Content | N/A | No new game content. |
| VIII. Pending State | N/A | No deferred actions. |
| IX. Cancel/Unwind | PASS | Animation cancellation simply removes sprites — no game state to unwind. |
| X. Post-Action Turn Flow | N/A | No turn flow changes. |

**Post-design re-check**: All principles pass. Principle I violation is resolved by this feature.

## Project Structure

### Documentation (this feature)

```text
specs/029-marker-animation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (files to create/modify)

```text
client/
├── ui/
│   ├── animation_manager.py    # NEW — AnimationManager + EaseAnimation
│   └── board_renderer.py       # MODIFY — expose space position lookup method
├── views/
│   └── game_view.py            # MODIFY — integrate animations, replace circles with sprites
└── assets/
    └── sounds/
        └── tick_001.ogg        # EXISTS — sound effect for animations
```

**Structure Decision**: Single new file (`animation_manager.py`) in the existing `client/ui/` package. All other changes are modifications to existing files. No new packages or directories needed.

## Implementation Phases

### Phase A: Animation Infrastructure (FR-007)

**New file: `client/ui/animation_manager.py`**

Create `EaseAnimation` dataclass and `AnimationManager` class:
- `EaseAnimation`: holds sprite, start/end positions, timing, easing, optional sound, optional on_complete callback
- `AnimationManager`: manages list of active animations, SpriteList for rendering
  - `animate()`: create sprite, set initial position, queue animation, play sound
  - `update(delta_time)`: advance elapsed time, interpolate positions with `arcade.anim.ease()`, remove completed animations
  - `draw()`: render all animating sprites via SpriteList
  - `clear()`: cancel all active animations

### Phase B: Player List Marker Sprites (FR-001)

**Modify: `client/views/game_view.py` — `_draw_player_list()`**

- Replace `arcade.draw_circle_filled()` with worker marker sprites
- Create/cache `arcade.Sprite` per player using `board_renderer._get_worker_texture(color_name)`
- Store player marker positions in `_player_marker_positions: dict[str, tuple[float, float]]` each frame
- Scale sprites to match the current circle size (`max(4, int(7 * s))` diameter)
- Add marker sprites to a dedicated SpriteList for proper rendering

### Phase C: Placement Animation (FR-002, FR-003, FR-004, FR-005, FR-011)

**Modify: `client/views/game_view.py` — `_on_worker_placed()`**

- Load `tick_001.ogg` sound in `__init__`
- After receiving placement message, before `_refresh_board()`:
  - Look up origin position from `_player_marker_positions[player_id]`
  - Look up target position from board renderer (expose `get_space_position(space_id)` method)
  - Create worker marker sprite (from texture cache)
  - Queue animation via `animation_manager.animate()` with Easing.SINE and tick sound

**Modify: `client/ui/board_renderer.py`**

- Add `get_space_position(space_id) -> tuple[float, float] | None` method
- Returns the pixel coordinates for a given action space, backstage slot, or constructed building
- Uses existing `_GRID_PLACEMENT` and grid calculations

**Modify: `client/views/game_view.py` — `on_update()` and `on_draw()`**

- Add `animation_manager.update(delta_time)` call in `on_update()`
- Add `animation_manager.draw()` call in `on_draw()` after board rendering, before UI overlays

### Phase D: Recall Animation (FR-012, FR-013)

**Modify: `client/views/game_view.py` — `_on_round_end()`**

- Before clearing worker state: snapshot all current worker positions and their owning player IDs from board state
- For each occupied space: queue reverse animation (space position → player marker position) with tick sound
- Then proceed with existing board clearing logic

### Phase E: Reassignment Animation (FR-014, FR-015)

**Modify: `client/views/game_view.py` — `_on_worker_reassigned()`**

- Before `_refresh_board()`:
  - Look up origin position from backstage slot position via board renderer
  - Look up target position from target action space via board renderer
  - Queue animation from backstage to target with tick sound

### Phase F: Edge Cases (FR-006, FR-008, FR-009, FR-010)

- Window resize: animations use positions computed at queue time; if window resizes mid-animation, the animation completes at the original computed position (acceptable behavior)
- Placement cancel: add `animation_manager.clear()` call in `_on_placement_cancelled()`
- Multiple simultaneous: already supported by AnimationManager's list-based design
- Responsiveness: animations are non-blocking (just sprite position updates in `on_update()`)

## Key Design Decisions

1. **Animation as visual overlay**: Game state updates immediately when server confirms. The animation sprite is a separate overlay that flies to the destination. The static worker marker appears at the destination instantly (via `_refresh_board()`). During animation, both are visible — the flying marker draws attention. This avoids complexity of delaying state updates.

2. **Per-frame position lookup**: Player marker positions are recalculated each frame in `_draw_player_list()` and stored in a dict. The animation manager doesn't need to know about the player list layout — it just receives start/end coordinates at queue time.

3. **Sound on animation start**: The tick sound plays when the animation begins (not on completion). This provides immediate audio feedback matching the visual "departure" of the marker.

4. **Separate SpriteList for animations**: The AnimationManager owns its own SpriteList, drawn in `on_draw()` after the board but before UI panels. This ensures animations render above board elements but below dialogs.

## Complexity Tracking

No constitution violations requiring justification. The Principle V (Simplicity) exception for the animation abstraction is user-requested and minimal.
