# Data Model: Building Acquisition Animation

**Date**: 2026-05-18 | **Branch**: `035-building-acquisition-animation`

## Overview

This feature is client-side only — no new data entities or server-side model changes are required. The animation uses existing message types and board state.

## Existing Entities (No Changes)

### BuildingConstructedResponse
Carries all data needed for face-up purchase animation: `building_id`, `lot_index`, `building_tile`.

### QuestCompletedResponse
Field `building_granted` (dict | None) carries: `building_id`, `building_name`, `lot_index`, `space_id`, `visitor_reward`, `owner_bonus`, `accumulated_vp`.

### QuestRewardChoiceResolvedResponse
Field `choice` carries the same building assignment data when `reward_type == "choose_building"`.

### BoardRenderer
Existing internal state used by animation:
- `_bld_positions: list[tuple[float, float]]` — screen positions of face-up building cards
- `_grid: BoardGrid` — converts grid coordinates to pixel positions via `cell_rect()`

## New Public Method (BoardRenderer)

### get_building_card_info(building_id) → tuple[float, float, float] | None
Returns `(center_x, center_y, scale)` for a face-up building card, matching the pattern of existing `get_quest_card_info()`. Used by animation setup to determine the origin position for market-purchase animations.

## Animation Data Flow

```
Server Response → Client Handler → AnimationEvent → AnimationManager.animate()
                                                          ↓
                                                    on_complete callback
                                                          ↓
                                                  Update game_state + _refresh_board()
```

No new persistent state. Animation sprites are transient (created for the animation, removed on completion).
