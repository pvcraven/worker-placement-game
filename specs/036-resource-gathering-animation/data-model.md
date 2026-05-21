# Data Model: Resource Gathering Animation

**Date**: 2026-05-21
**Feature**: 036-resource-gathering-animation

## No New Entities

This feature is purely client-side animation. No new data models, messages, or state fields are required.

## Existing Entities Used (unchanged)

### WorkerPlacedResponse (shared/messages.py)

Already contains all data needed for animation:

| Field | Type | Usage |
|-------|------|-------|
| `player_id` | str | Look up destination position in `_player_marker_positions` |
| `space_id` | str | Look up origin position via `board_renderer.get_space_position()` |
| `reward_granted` | dict | Base resources to animate (guitarists, bass_players, etc.) |
| `owner_bonus` | dict | Owner's bonus resources to animate to owner's position |
| `trigger_bonuses` | list[dict] | Trigger bonus resources to animate after base reward |

### _RESOURCE_ICON_MAP (client/views/game_view.py)

Maps resource keys to icon PNG paths. Already covers all animatable resources:

| Key | Icon Path |
|-----|-----------|
| guitarists | client/assets/card_images/icons/guitarist.png |
| bass_players | client/assets/card_images/icons/bass_player.png |
| drummers | client/assets/card_images/icons/drummer.png |
| singers | client/assets/card_images/icons/singer.png |
| coins | client/assets/card_images/icons/coin.png |

### _player_marker_positions (client/views/game_view.py)

Dict mapping `player_id → (x, y)` screen coordinates. Updated every frame. Used as animation destination.

## State Transitions

None. The animation is cosmetic and does not affect game state. Resource counts are updated immediately via `_apply_reward_to_player` (existing behavior, unchanged). The animation provides visual feedback after the data is already applied.
