# Implementation Plan: Building Acquisition Animation

**Branch**: `035-building-acquisition-animation` | **Date**: 2026-05-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/035-building-acquisition-animation/spec.md`

## Summary

Add client-side animations for building acquisition: face-up market purchases animate from the market position (right) to the constructed buildings area (left); deck-drawn buildings animate from the lower-right corner upward to the lot position. Uses the existing `AnimationManager` and `EventQueue` with callback chaining, matching the established card animation pattern. No server changes required.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease)
**Storage**: N/A (client-side animation only)
**Testing**: pytest + ruff (server logic only; animation tested manually)
**Target Platform**: Desktop (Windows/Linux/macOS)
**Project Type**: Desktop game (client-server)
**Performance Goals**: 60 fps during animation
**Constraints**: Animation must not block game state updates; must integrate with existing event queue
**Scale/Scope**: 3 response handlers modified, 1 new board_renderer method, 1-2 new animation setup methods

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Uses `arcade.Sprite` for animation, no draw calls |
| II. Pydantic Data Modeling | PASS | No new data models; existing message types unchanged |
| III. Client-Server Separation | PASS | Client-only change; no game state mutation in client |
| IV. Test-Driven Game Logic | PASS | No server logic changes; no new tests needed |
| V. Simplicity First | PASS | Reuses existing AnimationManager; single-stage fly animation |
| VI. Server-Authoritative Protocol | PASS | No new messages; client reacts to existing responses |
| VII. Config-Driven Content | N/A | No content changes |
| VIII. Pending State | N/A | No deferred actions |
| IX. Cancel/Unwind | N/A | Animations are fire-and-forget visual effects |
| X. Post-Action Turn Flow | PASS | Turn flow unchanged; animation is cosmetic overlay |

**Post-Phase 1 re-check**: All gates still pass. No design decisions introduced violations.

## Project Structure

### Documentation (this feature)

```text
specs/035-building-acquisition-animation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (files to modify)

```text
client/
  ui/
    board_renderer.py    # Add get_building_card_info() method
  views/
    game_view.py         # Add animation methods, modify 3 response handlers
```

**Structure Decision**: No new files. All changes are additions to existing client modules, following the established animation integration pattern.

## Implementation Design

### Step 1: Add `get_building_card_info()` to BoardRenderer

Add a public method mirroring `get_quest_card_info()` that returns `(center_x, center_y, scale)` for a face-up building by its building_id. This gives animation setup code the origin position for market-purchase animations.

Also add a `get_building_lot_position(lot_index)` method that computes the screen position for a constructed building lot, used as the animation destination.

### Step 2: Add Building Animation Setup Methods to GameView

Create `_start_building_purchase_animation(building_id, lot_index, building_tile, event)`:
- Look up origin from `board_renderer.get_building_card_info(building_id)`
- Look up destination from `board_renderer.get_building_lot_position(lot_index)`
- Create sprite from building image
- Single-stage `animate()` call: origin → destination, ~0.75s, `Easing.SINE`
- `on_complete`: update game state, call `_refresh_board()`, set `event.done = True`

Create `_start_building_draw_animation(building_id, lot_index, building_tile, event)`:
- Origin: lower-right corner of the board/screen
- Destination: same lot position computation
- Same animation pattern but from different origin
- Small start scale → normal end scale for a "flying in" effect

### Step 3: Modify `_on_building_constructed()` Handler

Currently updates state and calls `_refresh_board()` immediately. Change to:
1. Extract animation-relevant fields (building_id, lot_index, building_tile)
2. Create `AnimationEvent` with setup function that calls `_start_building_purchase_animation()`
3. Move state update + `_refresh_board()` into `on_complete` callback
4. Enqueue the event

### Step 4: Modify `_on_quest_completed()` Handler (building_granted path)

When `building_granted` is present in the response:
1. Extract building data from `building_granted` dict
2. Create `AnimationEvent` with setup function that calls `_start_building_draw_animation()`
3. Move building state update into `on_complete` callback
4. Enqueue the event after the quest completion animation

### Step 5: Modify `_on_quest_reward_choice_resolved()` Handler (choose_building path)

When `reward_type == "choose_building"`:
1. Extract building data from `choice` dict
2. Create `AnimationEvent` with setup function that calls `_start_building_purchase_animation()` (origin is market, same as regular purchase)
3. Move building state update into `on_complete` callback
4. Enqueue the event

### Step 6: Manual Testing

Test all three acquisition paths:
- Market purchase via Realtor action space
- Random draw from quest reward completion
- Market choice from quest reward
- Verify multiplayer visibility (two clients)
- Verify animation queuing with rapid acquisitions

## Complexity Tracking

No constitution violations. No complexity justifications needed.
