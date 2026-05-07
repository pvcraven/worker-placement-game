# Research: Board Grid Layout

**Feature**: 027-board-grid-layout
**Date**: 2026-05-06

## R1: Grid Coordinate System — Row 0 Top vs Bottom

**Decision**: Row 0 = top of board (Merch Store). Internally invert for Arcade's bottom-left origin.

**Rationale**: The spec placement map lists Merch Store at row 0 (top) and FastPass at row 7 (bottom). This matches the intuitive reading order and the existing `_SPACE_LAYOUT` where higher Y fractions = higher on screen. Since Arcade uses bottom-left origin, the grid converts: `pixel_y = board_y + board_h - (row + row_span) * cell_h`.

**Alternatives considered**:
- Row 0 = bottom (matches Arcade native coords): Rejected — makes the placement map confusing and inverts the spec table.

## R2: Half-Integer Coordinate Implementation

**Decision**: Accept float col/row values directly. `cell_rect(col=3.5, row=0)` computes `center_x = board_x + (3.5 + 0.5) * cell_w` naturally — no special half-integer logic needed.

**Rationale**: Since grid positions are multiplied by cell_w/cell_h, any float value "just works" mathematically. No need for a separate half-grid mode or snapping logic.

**Alternatives considered**:
- Separate half-grid enum/flag: Rejected — adds complexity for no benefit when float math handles it.
- Snap to nearest 0.5: Rejected — the spec says only integer and half-integer positions, but enforcing this adds validation without value.

## R3: Uniform Card Scaling Approach

**Decision**: Compute one `card_scale` factor from the grid cell dimensions and base card width. All card types use this same factor. Height differences come from the PNG image height, not from different scale factors.

**Rationale**: FR-014 requires all cards scale by the same uniform factor. If `cell_w` (minus margin) is the target width, then `scale = (cell_w - 2*margin) / CARD_WIDTH`. A space card (1 row) will be shorter than a quest card (3 rows) because the PNG height differs, but both are scaled by the same factor.

**Alternatives considered**:
- Scale per card type (fit each to its cell): Rejected — violates FR-014.
- Scale by height instead of width: Rejected — width is the constraining dimension since all cards share base width.

## R4: Margin Implementation

**Decision**: Percentage-based margin of 2% of cell width, applied as inset on all four sides of each cell.

**Rationale**: FR-013 specifies percentage-based margin. Using cell width (not cell height) keeps horizontal and vertical margins visually similar since cells are roughly square-ish. The content area within a cell is `(cell_w - 2*margin, cell_h - 2*margin)` where `margin = 0.02 * cell_w`.

**Alternatives considered**:
- Margin as % of board width: Rejected — margin would be the same absolute size for all cells, making it disproportionate for the narrow left column vs. wide center.
- Fixed pixel margin: Rejected — doesn't scale with window size.

## R5: BoardGrid Lifetime and Caching

**Decision**: Create a new `BoardGrid` instance whenever the board area changes (in `_rebuild_shapes()`). Store as `self._grid`. Reuse across `draw()` and `_update_workers()` until next rebuild.

**Rationale**: The grid parameters only change on window resize or first draw. Creating a new instance is cheap (a few multiplications). Storing it avoids passing `x, y, w, h` through every positioning call.

**Alternatives considered**:
- Global singleton: Rejected — grid depends on board area which changes with window size.
- Recalculate per call: Rejected — wasteful, grid params are stable within a frame.

## R6: Side Panel Width Derivation

**Decision**: Compute the full 9-column grid width first, then `panel_width = 2/9 * total_available_width`. The board area gets the remaining 7/9.

**Rationale**: Currently `log_w = int(450 * s)` is hardcoded. The grid-based approach makes the panel exactly 2 grid columns wide, scaling proportionally with the board. In `game_view.py`, the layout becomes: `total_w = cw`, `cell_w = total_w / 9`, `log_w = int(2 * cell_w)`, `board_w = cw - log_w`.

**Alternatives considered**:
- Keep hardcoded 450px: Rejected — violates FR-002 requiring panel = 2 grid columns.
- Let board_renderer compute panel width: Rejected — game_view owns the overall layout division.

## R7: Card Image Generation Changes

**Decision**: All card types generated with `CARD_WIDTH = 200` base width. Heights adjusted per type:
- Space cards (1 row): height = `CARD_WIDTH * (cell_h / cell_w)` ≈ computed at generation time
- Building/market cards (1.5 rows): height = 1.5× space height
- Quest cards (3 rows): height = 3× space height

**Rationale**: FR-015 requires same base width. The card generator already uses CARD_WIDTH. The height ratios (1:1.5:3) match the grid row spans. Exact pixel heights will be tuned to look good at the 200px width.

**Alternatives considered**:
- Generate at cell-pixel size: Rejected — cell size varies with window; PNGs are fixed assets.
- Different widths per type: Rejected — violates FR-015.

## R8: Existing _SPACE_LAYOUT Replacement

**Decision**: Replace `_SPACE_LAYOUT` dict (fractional positions) with a placement map that uses grid coordinates. The new map is a dict of `{space_id: (col, row, col_span, row_span)}`. Dynamic elements (face-up quests, buildings, constructed buildings) compute their grid positions from index and the placement map.

**Rationale**: The current dict maps space_id to (x_frac, y_frac). The grid system maps to (col, row). Same pattern, different coordinate space. Backstage slots, quests, and buildings compute positions from their index in the list, which maps naturally to grid column/row arithmetic.

**Alternatives considered**:
- Keep _SPACE_LAYOUT and add grid on top: Rejected — maintains two positioning systems, defeating the purpose.
