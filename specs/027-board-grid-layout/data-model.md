# Data Model: Board Grid Layout

**Feature**: 027-board-grid-layout
**Date**: 2026-05-06

## Entities

### BoardGrid (client-side only, not persisted)

A layout computation engine. Created per frame when the board area changes.

| Field | Type | Description |
|-------|------|-------------|
| board_x | float | Left edge of board area (pixels) |
| board_y | float | Bottom edge of board area (pixels, Arcade coords) |
| board_w | float | Board area width (pixels) |
| board_h | float | Board area height (pixels) |
| cols | int | Number of grid columns (default: 7) |
| rows | int | Number of grid rows (default: 8) |
| cell_w | float | Computed: board_w / cols |
| cell_h | float | Computed: board_h / rows |
| margin | float | Computed: margin_pct * cell_w |

**Methods**:
- `cell_rect(col, row, col_span, row_span) → (cx, cy, w, h)` — center and dimensions of a grid region, margins inset
- `card_scale(row_span, base_w, base_h) → float` — uniform scale factor to fit card in cell(s)
- `panel_width(panel_cols) → float` — pixel width for side panel

**Validation rules**:
- col: 0.0 ≤ col ≤ 8.0 (float, supports half-integer)
- row: 0.0 ≤ row ≤ 8.0 (float, supports half-integer)
- col_span, row_span: > 0 (float, supports 0.5 increments)

### GridPlacement (data constant, not a class)

A dict mapping element identifiers to grid coordinates. Defined as a module-level constant in `board_renderer.py`.

| Key | Value Type | Example |
|-----|-----------|---------|
| space_id (str) | (col, row, col_span, row_span) | `"merch_store": (0, 0, 1, 1)` |

**Static placements** (from spec placement map):

```python
_GRID_PLACEMENT = {
    # Permanent action spaces — column 0, rows 0-7
    "merch_store":    (0, 0, 1, 1),
    "motown":         (0, 1, 1, 1),
    "guitar_center":  (0, 2, 1, 1),
    "talent_show":    (0, 3, 1, 1),
    "rhythm_pit":     (0, 4, 1, 1),
    "jam_session":    (0, 5, 1, 1),
    "whisper_room":   (0, 6, 1, 1),
    "fastpass":       (0, 7, 1, 1),
    # Top-row action spaces — half-columns, row 0
    "sunset_records": (3.5, 0, 1, 1),
    "the_back_room":  (4.5, 0, 1, 1),
    "the_garage":     (5.5, 0, 1, 1),
    # Backstage slots — column 3, rows 0-2
    "backstage_slot_1": (3, 0, 1, 1),
    "backstage_slot_2": (3, 1, 1, 1),
    "backstage_slot_3": (3, 2, 1, 1),
    # Realtor — column 3, row 4
    "realtor": (3, 4, 1, 1),
}
```

**Dynamic placements** (computed from index):
- Purchased buildings: `col = 1 + (i % 2)`, `row = (i // 2) * 1.5`, span `(1, 1.5)`
- Face-up quests: quests 0-1 at `(4+i, 2, 1, 3)`, quests 2-3 at `(4+(i-2), 5, 1, 3)`
- Building market: `(4+i, 5.5, 1, 1.5)` for i in 0..2

## Relationships

- **BoardGrid** is used by **BoardRenderer** (composition, created in `_rebuild_shapes()`)
- **GridPlacement** is read by **BoardRenderer** to position all static elements
- **BoardGrid.cell_rect()** is called with data from **GridPlacement** to produce pixel coordinates
- **GameView** uses **BoardGrid.panel_width()** to determine side panel width (replacing hardcoded `450 * s`)

## No Server-Side Changes

This feature is entirely client-side. No changes to:
- `server/models/game.py` (GameState, BoardState)
- `shared/messages.py` (Request/Response types)
- `shared/card_models.py` (card data models)
- `config/*.json` (game content files)

## Card Dimension Constants

Updated constants in `shared/constants.py`:

| Constant | Current | New | Notes |
|----------|---------|-----|-------|
| CARD_WIDTH | 200 | 200 | Unchanged — all cards share this width |
| CARD_HEIGHT | 260 | Adjusted | Quest card height (3 rows) |
| BUILDING_CARD_HEIGHT | 170 | Adjusted | Building card height (1.5 rows) |
| SPACE_CARD_HEIGHT | 100 | Adjusted | Space card height (1 row) |

Exact pixel heights will be tuned during implementation to match the grid row proportions while maintaining good visual appearance at 200px width.
