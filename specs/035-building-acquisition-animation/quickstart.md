# Quickstart: Building Acquisition Animation

**Branch**: `035-building-acquisition-animation`

## What This Feature Does

Adds visual animations when players acquire buildings:
- **Market purchase**: Building card flies from the market (right side) to the player's constructed buildings area (left side)
- **Deck draw**: Building card flies up from the lower-right corner to the constructed buildings area

## Files to Modify

### Client (animation logic)
- `client/ui/board_renderer.py` — Add `get_building_card_info()` public method for position lookup
- `client/views/game_view.py` — Add animation setup methods and modify three response handlers:
  - `_on_building_constructed()` — wrap with animation for market purchases
  - `_on_quest_completed()` — add animation for `building_granted` rewards
  - `_on_quest_reward_choice_resolved()` — add animation for market-choice building rewards

### No Server Changes
This is purely a client-side visual enhancement.

## Key Patterns to Follow

1. **Animation setup**: Create `AnimationEvent`, enqueue via `event_queue.enqueue()`
2. **Sprite creation**: `arcade.Sprite(image_path, scale=scale)`
3. **Position lookup**: Use `board_renderer.get_building_card_info(building_id)` for origin, compute lot position for destination
4. **State update timing**: Move `_refresh_board()` and state mutation into `on_complete` callback
5. **Easing**: Use `Easing.SINE` for smooth movement (consistent with card-pick animation)

## How to Test

1. Start server: `cd src && python -m server`
2. Start client(s): `cd src && python -m client`
3. Test market purchase: Place worker on Realtor → buy a face-up building → observe animation
4. Test deck draw: Complete a quest that grants a random building → observe animation from lower-right
5. Test multiplayer: Connect two clients, acquire building on one, verify animation on both
