# Research: Resource Gathering Animation

**Date**: 2026-05-21
**Feature**: 036-resource-gathering-animation

## Research Tasks

### RT-1: Can existing `_stream_resources` be reused directly?

**Decision**: Yes — reuse directly with no modifications.

**Rationale**: `_stream_resources` accepts generic parameters: `icon_paths` (list of PNG paths), `origin` (x,y), `destination` (x,y), and `on_all_done` (callback). It handles staggered icon creation (scale 0.5), flight animation (1.0s, SINE easing), delay sprites (0.25s stagger), and completion tracking via a remaining counter. These are exactly the parameters the spec requires. No changes needed to the method itself.

**Alternatives considered**: Creating a separate resource animation method for worker placement — rejected because the behavior is identical to quest completion streaming.

### RT-2: Can existing `_build_resource_icon_list` be reused?

**Decision**: Yes — reuse directly.

**Rationale**: The method iterates `_RESOURCE_ICON_MAP` and expands the reward dict into a flat list of icon paths. It already handles all five resource types (guitarists, bass_players, drummers, singers, coins) and naturally skips resources with zero count. Victory points are not in `_RESOURCE_ICON_MAP` so they're excluded automatically — matching the spec's requirement to skip VP animation.

### RT-3: Where should the animation originate from?

**Decision**: Use `board_renderer.get_space_position(space_id)` as the animation origin.

**Rationale**: This method already resolves pixel coordinates for both permanent spaces (via `_GRID_PLACEMENT` dict) and constructed buildings (via `constructed_buildings` list index calculation). It returns the same position used as the marker animation's target, so the resource icons will fly from exactly where the marker lands.

### RT-4: Where should the animation fly to?

**Decision**: Use `_player_marker_positions[player_id]` as the animation destination.

**Rationale**: This dict is populated every frame in `_draw_player_list()` with the screen coordinates of each player's marker in the turn-order panel at the top-left. This is the same position used as the origin for marker placement animations and the destination for quest completion reward streaming. It represents the "player's name area" referenced in the spec.

### RT-5: How to chain multiple animations (base reward → owner bonus → trigger bonuses)?

**Decision**: Use cascading `on_all_done` callbacks — each animation's completion callback starts the next one.

**Rationale**: `_stream_resources` already accepts an `on_all_done` callback. By composing these:
- Base reward's `on_all_done` → start owner bonus stream (or skip if empty)
- Owner bonus's `on_all_done` → start trigger bonus streams (or skip if empty)
- Final `on_all_done` → original completion logic (refresh board, update current player)

This matches the existing pattern used in quest completion animation where card entry → cost stream → reward stream → card exit are chained via callbacks.

**Alternatives considered**: Using EventQueue to sequence separate AnimationEvent instances for each phase — rejected because the marker animation already provides the callback entry point, and _stream_resources handles its own completion tracking internally.

### RT-6: Should special action setup be deferred until after resource animation?

**Decision**: Yes — move special action handling into the final animation callback.

**Rationale**: FR-003 requires the resource animation to complete before special interactions begin. Currently, quest selection and building purchase highlight modes are set up synchronously in `_on_worker_placed` after queueing the marker animation (not in its callback). Moving this setup into the final `on_all_done` callback ensures the animation fully completes before the player is prompted for special actions. The reward application (`_apply_reward_to_player`) should remain immediate since it updates the data model (the animation is purely visual).

### RT-7: What happens for spaces with no animatable resources?

**Decision**: The helper method immediately calls the completion callback, resulting in the same behavior as today.

**Rationale**: `_build_resource_icon_list` returns an empty list when the reward dict has zero for all icon-mapped resources. The helper method checks for an empty list and skips calling `_stream_resources`, directly invoking the final callback. This handles: VP-only rewards, special-action-only spaces, and zero-reward spaces.
