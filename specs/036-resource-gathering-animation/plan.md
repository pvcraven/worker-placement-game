# Implementation Plan: Resource Gathering Animation

**Branch**: `036-resource-gathering-animation` | **Date**: 2026-05-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/036-resource-gathering-animation/spec.md`

## Summary

Add visual feedback when workers are placed on resource-granting spaces. After the worker marker animation lands on a building or permanent spot, resource icons fly from the space position to the player's name area in the top-left corner. Reuses the existing `_stream_resources` method and `AnimationManager` infrastructure from the quest completion animation, matching its timing (1.0s per icon, 0.25s stagger, SINE easing) and sprite scale (0.5).

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease)
**Storage**: N/A (client-side animation only)
**Testing**: pytest + ruff (server logic only; animation is visual-only, tested manually)
**Target Platform**: Desktop (Windows)
**Project Type**: Desktop game (client/server)
**Performance Goals**: 60 fps maintained during animation
**Constraints**: Must reuse existing animation infrastructure; no new server messages or game state changes
**Scale/Scope**: Single file change (game_view.py) to modify the `_on_worker_placed` handler's animation chain

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Uses sprites via AnimationManager (cached sprite lists), no primitive draw calls |
| II. Pydantic Data Modeling | N/A | No new data crossing boundaries; reuses existing WorkerPlacedResponse fields |
| III. Client-Server Separation | PASS | Purely client-side animation; no game logic changes; server already sends all needed data (reward_granted, owner_bonus, trigger_bonuses) |
| IV. Test-Driven Game Logic | N/A | No server-side changes; animation is visual-only |
| V. Simplicity First | PASS | Reuses existing `_stream_resources`, `_build_resource_icon_list`, and `AnimationManager`; no new abstractions |
| VI. Server-Authoritative Message Protocol | PASS | No new messages; uses existing WorkerPlacedResponse fields |
| VII. Config-Driven Game Content | N/A | No new game content |
| VIII. Pending State | N/A | No deferred player actions |
| IX. Cancel/Unwind | N/A | Animation is cosmetic; no state to unwind |
| X. Post-Action Turn Flow | N/A | Server turn flow unchanged |

**Result**: All gates pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/036-resource-gathering-animation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
client/
  views/
    game_view.py          # Modified: _on_worker_placed handler, new _start_resource_gathering_animation method
  ui/
    animation_manager.py  # Unchanged (reused)
    event_queue.py         # Unchanged (reused)
  assets/
    card_images/
      icons/              # Unchanged (existing resource icons reused)
```

**Structure Decision**: Single-file modification to `client/views/game_view.py`. The existing animation infrastructure (`AnimationManager`, `_stream_resources`, `_build_resource_icon_list`, `_RESOURCE_ICON_MAP`) is fully reusable. No new files needed.

## Design

### Integration Point

The `_on_worker_placed` handler (game_view.py:387-603) currently queues a marker animation with an `on_complete` callback that immediately refreshes the board and updates the current player. The resource animation inserts into this callback chain:

**Current flow:**
```
marker animation → on_complete: refresh board + update current player
```

**New flow:**
```
marker animation → on_complete: resource stream animation(s) → then: refresh board + update current player + special actions
```

### Animation Chain Sequence

When a worker is placed and the marker animation completes:

1. **Base reward animation**: If `reward_granted` contains animatable resources (guitarists, bass_players, drummers, singers, coins), stream resource icons from the space position to the placing player's marker position using `_stream_resources` with the same parameters as quest completion (scale 0.5, duration 1.0s, stagger 0.25s, SINE easing).

2. **Owner bonus animation** (if applicable): If `owner_bonus` contains resources, stream those icons from the space position to the building owner's marker position.

3. **Trigger bonus animation** (if applicable): If `trigger_bonuses` list is non-empty, stream each trigger's bonus resources from the space position to the placing player's marker position, sequenced after the previous animation.

4. **Completion**: After all resource animations finish (or immediately if no animatable resources), call the original completion logic: refresh board, update current player, and proceed with special actions.

### Key Reuse

| Existing Code | Reuse |
|---------------|-------|
| `_stream_resources(icon_paths, origin, destination, on_all_done)` | Direct call — handles staggered icon animation |
| `_build_resource_icon_list(resources)` | Direct call — converts reward dict to icon paths list |
| `_RESOURCE_ICON_MAP` | Already maps all 5 resource types to icon PNGs |
| `AnimationManager.animate()` | Called internally by `_stream_resources` |
| `_player_marker_positions[pid]` | Provides destination (player name area) |
| `board_renderer.get_space_position(space_id)` | Provides origin (building/spot position) |

### Skipping Animation

No animation plays when:
- `reward_granted` has zero values for all icon-mapped resources (guitarists, bass_players, drummers, singers, coins)
- Victory points are in the reward but no other resources (no VP icon)
- The reward is exclusively a special action (quest selection, building purchase, intrigue draw)

### Implementation Approach

Add a helper method `_start_resource_gathering_animation` that:
1. Receives the space_id, player_id, reward_granted, owner_bonus, trigger_bonuses, and the final on_complete callback
2. Builds the chain of `_stream_resources` calls with cascading `on_all_done` callbacks
3. Handles the case where no animatable resources exist (calls on_complete immediately)

Modify `_on_worker_placed` to:
1. Replace the current marker animation's `on_complete` lambda with one that calls `_start_resource_gathering_animation`
2. Pass the original completion logic (refresh board, update current player) as the final callback
3. Move special action setup (quest selection, building purchase highlight modes) into the final callback so they trigger after animations complete (per FR-003)
