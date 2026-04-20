# Research: Board Layout Scaling

**Feature**: 013-board-layout-scaling  
**Date**: 2026-04-20

## R-001: Arcade Sprite Scaling Approach

**Decision**: Use `sprite.scale` property to dynamically scale card sprites based on a uniform scale factor derived from `window.ui_scale`.

**Rationale**: The existing `GameWindow` already computes `ui_scale = min(scale_x, scale_y)` where `scale_x = width / DESIGN_WIDTH` and `scale_y = height / DESIGN_HEIGHT`. This factor is broadcast on every `on_resize`. Applying it to sprite `.scale` is the natural Arcade idiom and was validated in `test_card_scaling.py`.

**Alternatives considered**:
- Viewport scaling (Arcade camera/projection): Adds complexity, may blur text rendering, and fights against Arcade's UI widget system which operates in screen coordinates.
- Redrawing cards at different resolutions: Wasteful — PNGs are pre-rendered at sufficient resolution for ~2x scaling.

## R-002: Aspect Ratio Preservation Strategy

**Decision**: Compute a uniform scale factor `s = min(window_width / DESIGN_WIDTH, window_height / DESIGN_HEIGHT)`. The effective content area is `(DESIGN_WIDTH * s, DESIGN_HEIGHT * s)`, anchored at the top-left of the window. All layout uses this content rect instead of raw window dimensions.

**Rationale**: The user specified no stretching and top-left anchoring. Using `min()` ensures the content fits within the window without distortion. The `GameWindow` already computes `ui_scale` this way — we extend its use to all layout code.

**Alternatives considered**:
- Letterboxing with centered content: User explicitly requested top-left anchoring, not centered.
- Allowing stretch in one axis: Rejected — user wants consistent aspect ratio.

## R-003: Text Scaling Strategy

**Decision**: Multiply all font sizes by `ui_scale`. Clamp to a minimum of 8pt to prevent illegibility. All text objects are already created via cached `_text()` helpers — the scale factor is applied at creation time by passing `font_size=int(base_size * scale)`.

**Rationale**: Arcade's `arcade.Text` objects cache GPU buffers. The existing `_text()` pattern in `game_view.py`, `game_log.py`, and `resource_bar.py` creates/updates cached text objects each frame. Scaling the font_size parameter scales the rendered text proportionally.

**Alternatives considered**:
- Using Arcade's `Text.scale` property: Does not exist; text is rendered at a fixed font size and must be recreated if size changes.
- CSS-style relative units: Not applicable to Arcade.

## R-004: Two-Column Building Layout

**Decision**: Change constructed building grid from 5 rows × N columns to N rows × 2 columns. Buildings fill column-first: first column top-to-bottom, then second column.

**Rationale**: Current layout uses `row = i % 5, col = i // 5` which gives 5-row columns. The spec requires two columns. New formula: `col = i % 2, row = i // 2`. Starting X position shifts right from permanent spaces. Column spacing adjusts to fit within the board area.

**Alternatives considered**:
- Keeping 5-column layout with smaller cards: Still wastes vertical space and the spec explicitly requires two columns.
- Dynamic column count based on window size: Over-engineering — spec says exactly two columns.

## R-005: Building VP/Owner Text Positioning Fix

**Decision**: Recompute VP and owner text positions every time the board layout rebuilds (when `_shapes_dirty` or draw rect changes). Text positions derived from the computed building sprite positions, not from stale cached values.

**Rationale**: Currently `_building_vp_texts` and `_building_owner_texts` are cached and only rebuilt when data changes (`_building_vp_dirty`, `_building_owner_dirty`). On window resize, positions become stale. Fix: always recalculate text positions in the draw method using current building positions.

**Alternatives considered**:
- Mark text dirty on resize: Adds flag management complexity. Simpler to always compute positions from current sprite positions.

## R-006: Game Log Panel Scaling

**Decision**: The game log panel dimensions scale proportionally via `ui_scale`. Width becomes `450 * ui_scale`, positioned at `content_width - log_width`. Font sizes scale accordingly. Line height scales with font size.

**Rationale**: Currently hardcoded to 450px width. Scaling by `ui_scale` keeps it proportional to the overall layout.

**Alternatives considered**:
- Fixed-ratio panel (e.g., always 25% of content width): Could make the panel too wide or too narrow. Proportional scaling from the design resolution is more predictable.

## R-007: Dialog Box Scaling

**Decision**: Pass `ui_scale` to dialog classes. Scale `width`, `height`, `font_size`, `space_between`, and padding parameters by `ui_scale`. For `CardSpriteSelectionDialog`, scale card sprite `.scale` property and spacing.

**Rationale**: Dialogs use Arcade's `UIManager` widgets (UIFlatButton, UILabel, UIBoxLayout) with hardcoded pixel dimensions. Multiplying these dimensions by `ui_scale` scales them proportionally.

**Alternatives considered**:
- Rebuilding dialogs on resize: Dialogs are ephemeral overlays created on demand. They use the current window size at creation time, so they naturally get the right scale if the scale factor is applied at construction.

## R-008: Handling `arcade.draw_circle_filled` (Worker Tokens)

**Decision**: Worker token circles (drawn via `arcade.draw_circle_filled`) must also scale their radius and position with `ui_scale`. This is a constitution violation (`draw_circle_filled` is a primitive draw call), but it's existing code — this feature does not introduce it. The scaling change will apply `ui_scale` to the radius and offset values.

**Rationale**: Replacing all primitive draw calls with ShapeElementList is out of scope for this feature. The existing calls remain, but their positions and sizes will correctly scale.

**Alternatives considered**:
- Replacing circles with sprites: Out of scope — would be a separate cleanup task.
- Adding to ShapeElementList: The circles need to reflect dynamic state (which player occupies which space), making static shape lists awkward for this use case.
