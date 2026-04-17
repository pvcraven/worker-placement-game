# Data Model: Board Layout Optimization

**Date**: 2026-04-16 | **Branch**: `004-board-layout-optimization`

## Entity Changes

### No Data Model Changes

This feature is entirely client-side UI/rendering changes plus a rename. No new fields, entities, or state transitions are introduced.

### ActionSpaceConfig (server/models/config.py) — Rename Only

The `real_estate_listings` entry in board.json changes to `realtor`:
- `space_id`: "real_estate_listings" → "realtor"
- `name`: "Real Estate Listings" → "Realtor"
- `space_type`: "real_estate_listings" → "realtor"

### Client State — No Change

The `_face_up_buildings` and `_building_deck_remaining` fields already exist on `GameView`. The new popup panel reads from these same fields. No new client state is needed.

### Toggle State — Existing Pattern Extended

The existing `_show_quests_hand` and `_show_intrigue_hand` booleans in `GameView` are joined by a new `_show_building_market` boolean. Only one can be true at a time (mutual exclusion enforced in toggle methods).

## Relationships

```
GameView
  ├── _show_quests_hand: bool
  ├── _show_intrigue_hand: bool
  ├── _show_building_market: bool    # NEW toggle
  ├── _face_up_buildings: list[dict] # existing, used by popup
  └── _building_deck_remaining: int  # existing, used by popup

BoardRenderer
  ├── _shape_list: ShapeElementList  # NEW batched shapes
  └── _shapes_dirty: bool           # NEW rebuild flag
```

## Validation Rules

- Only one panel toggle may be True at a time
- Shape list must be rebuilt when `update_board()` is called with new state
