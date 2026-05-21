# Quickstart: Resource Gathering Animation

**Date**: 2026-05-21
**Feature**: 036-resource-gathering-animation

## Overview

Add a resource-flying animation when workers are placed on resource-granting spaces. Icons fly from the building/spot to the player's name area, reusing the quest completion animation infrastructure.

## What to Change

**Single file**: `client/views/game_view.py`

### 1. Add `_start_resource_gathering_animation` helper method

A new method that chains resource animations after the marker lands:

- Accepts: space_id, player_id, reward_granted, owner_bonus, trigger_bonuses, final on_complete callback
- Builds icon path lists via existing `_build_resource_icon_list`
- Gets origin from `board_renderer.get_space_position(space_id)`
- Gets player destination from `_player_marker_positions[player_id]`
- Chains `_stream_resources` calls via cascading `on_all_done` callbacks:
  1. Base reward → player position
  2. Owner bonus → owner position (if non-empty)
  3. Trigger bonuses → player position (if non-empty, sequenced)
- If no animatable resources exist at any stage, skips to next stage immediately

### 2. Modify `_on_worker_placed` handler

- Change the marker animation's `on_complete` callback to call `_start_resource_gathering_animation` instead of directly calling refresh/update
- Move special action handling (quest selection, building purchase highlight modes) into the final animation completion callback so they trigger after the resource animation finishes
- Keep `_apply_reward_to_player` call in its current position (immediate, before animation)

## Animation Parameters (matching quest completion)

| Parameter | Value |
|-----------|-------|
| Icon scale | 0.5 |
| Flight duration | 1.0 second |
| Stagger delay | 0.25 seconds |
| Easing | SINE |
| Origin | `board_renderer.get_space_position(space_id)` |
| Destination | `_player_marker_positions[player_id]` |

## Testing

Manual visual testing:
1. Place worker on permanent spot with resources → icons fly to player name
2. Place worker on constructed building → same animation
3. Place worker on owned building → visitor icons fly to visitor, owner icons fly to owner
4. Place worker triggering plot quest bonuses → base reward + trigger bonus animate in sequence
5. Place worker on quest selection spot (no resources) → no resource animation, quest picker appears
6. Place worker on building purchase spot → resource animation (if any) completes, then purchase mode activates

## Dependencies

None new. All existing infrastructure is reused:
- `_stream_resources` (game_view.py)
- `_build_resource_icon_list` (game_view.py)
- `_RESOURCE_ICON_MAP` (game_view.py)
- `AnimationManager` (animation_manager.py)
- `board_renderer.get_space_position` (board_renderer.py)
