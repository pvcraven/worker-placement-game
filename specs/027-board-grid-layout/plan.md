# Implementation Plan: Board Grid Layout

**Branch**: `027-board-grid-layout` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/027-board-grid-layout/spec.md`

## Summary

Replace the ad-hoc fractional positioning system in `board_renderer.py` with a grid-based layout engine. The board area (between top resource bar and bottom status bar, excluding side panel) becomes a 7-column × 8-row grid. The side panel occupies 2 additional columns (9 total). All board elements are positioned through a shared `BoardGrid` utility that converts grid coordinates (col, row, col_span, row_span) to pixel positions. Half-integer coordinates are supported (e.g., col 3.5). Buildings change from 2-row to 1.5-row height. All card types share the same base image width.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: pytest + ruff (`cd src && pytest && ruff check .`)
**Target Platform**: Windows desktop (Arcade window)
**Project Type**: Desktop game (client-server, local)
**Performance Goals**: 60 fps rendering, no visible jitter on resize
**Constraints**: All rendering via arcade.Text, ShapeElementList, SpriteList (no primitive draw calls per constitution)
**Scale/Scope**: Single board renderer file (~700 lines), game_view integration, card generator updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Grid utility computes coordinates only; rendering continues via SpriteList/ShapeElementList/arcade.Text |
| II. Pydantic Data Modeling | PASS | No new network/config data structures needed. Grid is client-side layout math only |
| III. Client-Server Separation | PASS | Grid layout is purely client-side. No server changes. Board state format unchanged |
| IV. Test-Driven Game Logic | PASS | No server logic changes. Client layout not covered by pytest (visual verification) |
| V. Simplicity First | PASS | Single utility class replaces scattered positioning constants. No over-engineering |
| VI. Server-Authoritative Protocol | N/A | No message changes |
| VII. Config-Driven Content | PASS | Grid positions defined as data (placement map), not hard-coded per-element logic |
| VIII. Pending State | N/A | No server interaction changes |
| IX. Cancel/Unwind | N/A | No server interaction changes |
| X. Post-Action Turn Flow | N/A | No server interaction changes |

All gates pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/027-board-grid-layout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
client/
  ui/
    board_grid.py          # NEW — BoardGrid utility class
    board_renderer.py      # MODIFIED — refactored to use BoardGrid
  views/
    game_view.py           # MODIFIED — pass grid-derived panel width
shared/
  constants.py             # MODIFIED — consolidate card dimensions
card-generator/
  generate_cards.py        # MODIFIED — uniform base width for all card types
```

**Structure Decision**: No new directories. The grid utility lives alongside `board_renderer.py` in `client/ui/` as a sibling module. This follows the existing pattern where `tabbed_panel.py`, `resource_bar.py`, and `board_renderer.py` all live in `client/ui/`.

## Key Design Decisions

### 1. BoardGrid Utility Class

A new `BoardGrid` class in `client/ui/board_grid.py` encapsulates all grid-to-pixel math:

```python
class BoardGrid:
    """Converts grid coordinates to pixel positions within the board area."""
    
    def __init__(self, x: float, y: float, w: float, h: float, 
                 cols: int = 7, rows: int = 8, margin_pct: float = 0.02):
        # Board area origin and dimensions
        # Compute cell_w = w / cols, cell_h = h / rows
        # margin = margin_pct * cell_w
    
    def cell_rect(self, col: float, row: float, 
                  col_span: float = 1.0, row_span: float = 1.0
                  ) -> tuple[float, float, float, float]:
        """Return (center_x, center_y, width, height) for a grid region.
        
        Supports half-integer col/row (e.g., 3.5, 1.5).
        Width/height account for margin (content area inside margin).
        """
    
    def card_scale(self, row_span: float, base_width: int, base_height: int
                   ) -> float:
        """Compute uniform scale factor to fit a card image into a cell.
        
        All card types use the same base_width. Height varies by type.
        Returns scale that fits the card within the cell while maintaining
        aspect ratio.
        """
    
    @property
    def cell_width(self) -> float: ...
    
    @property
    def cell_height(self) -> float: ...
    
    def panel_width(self, panel_cols: int = 2) -> float:
        """Width of the side panel (panel_cols * cell_w)."""
```

**Why a class, not functions**: The grid parameters (x, y, w, h, cell sizes) are computed once per frame and reused for every element. A class avoids recomputing them on each call.

**Why separate file**: board_renderer.py is already ~700 lines. The grid utility is a distinct concern (coordinate math vs. rendering).

### 2. Coordinate System

Row 0 is the **top** of the board (matching the spec table where Merch Store is row 0). Since Arcade uses bottom-left origin, the grid internally inverts: `pixel_y = board_top - row * cell_h`.

### 3. Placement Data

The placement map from the spec becomes a data structure (dict or list of tuples) in `board_renderer.py`, replacing the current `_SPACE_LAYOUT` dict and scattered positioning constants. Each entry: `(element_id, col, row, col_span, row_span)`.

### 4. Card Image Dimensions

All card PNGs will be generated with the same base width (CARD_WIDTH = 200px). Heights:
- Space cards: 1-row equivalent height
- Building cards: 1.5-row equivalent height  
- Quest cards: 3-row equivalent height
- Building market cards: 1.5-row equivalent height

The `card_scale()` method ensures all cards scale by the same factor relative to the grid cell size.

### 5. Side Panel Width

Currently hardcoded as `int(450 * s)` in game_view.py. Will be derived from the grid: `grid.panel_width(2)` where 2 = number of panel columns. The grid computes this as `2 * (total_width / 9)` since the full layout is 9 columns wide (7 board + 2 panel).

### 6. Refactoring Strategy

The refactor touches 3 parallel code locations in board_renderer.py that must stay in sync:
1. `_rebuild_shapes()` — builds sprite lists and computes positions
2. `draw()` — uses cached sprite lists and positions
3. `_update_workers()` — positions worker tokens on cards

All three currently duplicate positioning math. After the refactor, all three call `BoardGrid.cell_rect()` with the same grid coordinates, eliminating the duplication.

### 7. Click Detection

`_space_rects` (used by `get_space_at()`) will be populated from grid coordinates during `_rebuild_shapes()`. The rect format `(x, y, w, h)` is unchanged — only the source of the values changes.

## Files Modified

| File | Type | Changes |
|------|------|---------|
| `client/ui/board_grid.py` | NEW | BoardGrid utility class (~80 lines) |
| `client/ui/board_renderer.py` | MODIFIED | Replace _SPACE_LAYOUT, _BACKSTAGE_Y, and all positioning math with BoardGrid calls. Define placement map data. Refactor _rebuild_shapes(), draw(), _update_workers() |
| `client/views/game_view.py` | MODIFIED | Derive `log_w` (side panel width) from grid cell size instead of hardcoded `450 * s` |
| `shared/constants.py` | MODIFIED | Add/update card height constants for uniform base width system |
| `card-generator/generate_cards.py` | MODIFIED | Generate all card types with same CARD_WIDTH base; adjust heights for space (1-row), building (1.5-row), quest (3-row) |

## Verification

1. **Grid alignment**: Start a game. All elements visually snap to grid positions with uniform spacing.
2. **Resize**: Drag window edges. All elements reposition without overlap or jitter.
3. **Click detection**: Click on every space type (permanent, backstage, realtor, quests, buildings). All register correctly.
4. **Worker tokens**: Place workers on all space types. Tokens appear at correct positions.
5. **Side panel**: Panel width scales proportionally with board grid.
6. **Card images**: Regenerate cards. All types have same width, proportional heights.
7. **Tests**: `cd src && pytest && ruff check .` — all pass.
