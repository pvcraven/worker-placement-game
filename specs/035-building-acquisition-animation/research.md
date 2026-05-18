# Research: Building Acquisition Animation

**Date**: 2026-05-18 | **Branch**: `035-building-acquisition-animation`

## R1: Animation Framework & Patterns

**Decision**: Reuse the existing `AnimationManager` with callback chaining, matching the established card animation pattern.

**Rationale**: The project already has a mature animation system used for card picks, quest completion, intrigue draws, and marker movement. All use the same `AnimationManager.animate()` API with `on_complete` callbacks for sequencing. Building acquisition animation should follow this same pattern for consistency and minimal code surface.

**Alternatives considered**:
- New animation subsystem — rejected; unnecessary complexity, violates Simplicity First principle
- CSS/tweening library — rejected; project uses Arcade's native easing system

**Key API**: `AnimationManager.animate(sprite, start, end, duration, easing, start_scale, end_scale, sound, on_complete)`

## R2: Building Acquisition Message Types

**Decision**: Three existing response types already distinguish acquisition source — no new messages needed.

**Rationale**: The client can determine animation origin from the message type:

| Source | Message Type | Animation Origin |
|--------|-------------|-----------------|
| Market purchase | `BuildingConstructedResponse` | Face-up market position (right side) |
| Random draw (quest reward) | `QuestCompletedResponse.building_granted` | Lower-right corner (deck) |
| Market choice (quest reward) | `QuestRewardChoiceResolvedResponse` (reward_type="choose_building") | Face-up market position (right side) |

**Alternatives considered**:
- Add explicit `source` field to responses — rejected; message type already provides this discrimination, and adding fields requires server changes for a client-only feature
- Infer from `cost_coins == 0` — rejected; fragile and could break if free buildings are added

## R3: Board Position Access

**Decision**: Add a public `get_building_card_info()` method to `BoardRenderer` (similar to existing `get_quest_card_info()`) and compute lot destination from lot_index.

**Rationale**: Face-up building positions are stored in `_bld_positions` (private). A public accessor is needed for animation setup. Constructed building lot positions can be computed from lot_index using the grid math already in the renderer.

**Key positions**:
- Face-up buildings: Columns 4+i, Row 5.5 (1×2 grid cells)
- Constructed lots: Column 1+(j%2), Row (j//2)*2 (1×2 grid cells)
- Lower-right corner (deck origin): `(board_x + board_width, board_y)` or grid cell (6, 7)

## R4: Animation Design — Simplified Pattern

**Decision**: Use a simple single-stage fly animation (no center pause) for building acquisition.

**Rationale**: Quest/intrigue card animations pause at center to let players read the card. Buildings are already visible in the market before purchase, so a center pause adds no value. A direct fly from origin to destination is cleaner and faster. This matches the marker animation pattern (single stage, ~0.75–1.0s).

**Alternatives considered**:
- 3-stage enter/pause/exit like quest cards — rejected; buildings don't need a "reveal" moment since they're already face-up or the info is shown in the quest completion
- Instant placement (current behavior) — rejected; user specifically requested animation

## R5: Timing of State Update vs. Animation

**Decision**: Defer board refresh until animation completes (via `on_complete` callback).

**Rationale**: FR-005 requires buildings become functional only after animation completes. Currently, handlers call `_refresh_board()` immediately. The animation must run first, with the state update and refresh moved into the `on_complete` callback. The game state dict can be updated immediately (it's just a render cache), but the visual refresh must wait.

**Alternatives considered**:
- Update state immediately but hide the building sprite until animation ends — rejected; more complex, risks flicker
- Use a separate "pending" sprite layer — rejected; unnecessary when callback timing solves the problem

## R6: Market Update Timing

**Decision**: For face-up purchases, the animated building sprite should disappear from the market immediately (or at animation start), and the market should refresh when the `BuildingMarketUpdateResponse` arrives (which follows shortly after `BuildingConstructedResponse`).

**Rationale**: The market card is the animation source — it "lifts off" from the market. The market update message arrives separately and will fill the gap with a replacement card. No special handling needed; the existing `_on_building_market_update` handler already refreshes the market display.
