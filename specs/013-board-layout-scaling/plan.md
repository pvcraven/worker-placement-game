# Implementation Plan: Board Layout Scaling

**Branch**: `pvcraven/013-board-layout-scaling` | **Date**: 2026-04-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-board-layout-scaling/spec.md`

## Summary

Scale all visual elements (cards, text, panels, dialogs) proportionally with the game window using a uniform scale factor derived from the design resolution (1920×1080). Maintain aspect ratio on non-proportional windows by anchoring content to the top-left. Reorganize constructed buildings into a two-column grid layout. Fix VP/Owner text positioning to stay anchored to building cards at all sizes.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2  
**Storage**: N/A (client-side rendering only)  
**Testing**: pytest + ruff  
**Target Platform**: Windows desktop (resizable window, 1024×768 minimum)  
**Project Type**: Desktop game (client/server architecture, this feature is client-only)  
**Performance Goals**: 60 fps maintained during and after resize  
**Constraints**: Must use `arcade.Text` for all text (Constitution I), no primitive draw calls for new code  
**Scale/Scope**: 6 client-side files modified, ~300 lines changed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | **PASS** | All new text uses `arcade.Text`. Existing `draw_circle_filled` calls for worker tokens are pre-existing and out of scope to refactor. No new primitive draw calls introduced. |
| II. Pydantic Data Modeling | **PASS** | No new data crosses boundaries. This is purely client-side rendering. |
| III. Client-Server Separation | **PASS** | All changes are in `client/`. No server modifications. No game state mutations. |
| IV. Test-Driven Game Logic | **PASS** | No game logic changes. Layout is visual-only. Existing tests remain valid. |
| V. Simplicity First | **PASS** | Single scale factor (`ui_scale`) drives all scaling. No new abstractions. No new dependencies. |

**Post-Phase 1 re-check**: All gates pass. No constitution violations in the design.

## Project Structure

### Documentation (this feature)

```text
specs/013-board-layout-scaling/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
client/
├── game_window.py          # Add content_width/content_height properties
├── ui/
│   ├── board_renderer.py   # Sprite scaling, two-column buildings, scaled text
│   ├── dialogs.py          # Scale dialog dimensions, sprites, buttons, fonts
│   ├── game_log.py         # Scale panel dimensions, font sizes, line height
│   └── resource_bar.py     # Scale font sizes, element positions
└── views/
    └── game_view.py        # Use content rect for layout, scale panels
```

**Structure Decision**: All changes fit within the existing `client/` package. No new files or packages needed. The existing file structure cleanly separates concerns — window management, board rendering, UI panels, dialogs, and view orchestration.

## Implementation Design

### Phase 1: Core Scaling Infrastructure (FR-012, FR-007)

**File: `client/game_window.py`**

Add computed `content_width` and `content_height` properties that represent the aspect-ratio-preserved content area:

```python
@property
def content_width(self) -> float:
    return DESIGN_WIDTH * self.ui_scale

@property
def content_height(self) -> float:
    return DESIGN_HEIGHT * self.ui_scale
```

The `ui_scale` is already computed as `min(scale_x, scale_y)`. These properties give all downstream code a content rect that:
- Scales uniformly (no distortion)
- Is always ≤ the actual window dimensions
- Anchors to the bottom-left in Arcade's coordinate system (y=0 at bottom), which maps to top-left visually when the status bar is at the top

### Phase 2: Board Renderer Scaling (FR-001, FR-002, FR-003, FR-004, FR-005, FR-008)

**File: `client/ui/board_renderer.py`**

**Sprite Scaling (FR-001, FR-002)**:
- Accept `scale` parameter in `draw()` and `_rebuild_shapes()`
- Apply `sprite.scale = scale` to all card sprites after creation
- Clamp scale to [0.3, 2.0] range
- Scale all card dimension constants by the scale factor for position calculations:
  ```python
  card_w = _CARD_WIDTH * scale
  card_h = _CARD_HEIGHT * scale
  bld_h = _BUILDING_CARD_HEIGHT * scale
  space_h = _SPACE_CARD_HEIGHT * scale
  ```
- Scale spacing values (`_CARD_SPACING`, inter-card gaps) proportionally

**Two-Column Building Layout (FR-003, FR-004)**:
- Reduce left-column margin: permanent spaces shift left (e.g., x=0.05 instead of 0.08)
- Building grid changes from `row = i % 5, col = i // 5` to `col = i % 2, row = i // 2`
- Building start position and column spacing adjusted to fit two columns between permanent spaces and the quest/backstage area
- Building column spacing proportional to board width

**VP/Owner Text Fix (FR-005)**:
- Always recompute text positions in `draw()` based on current building sprite positions
- Remove dependency on stale cached positions
- Scale font sizes by the scale factor: `font_size=max(8, int(12 * scale))`

**Worker Token Scaling**:
- Scale circle radius: `radius = max(5, int(9 * scale))`
- Scale position offsets proportionally

### Phase 3: Text Scaling (FR-009, FR-010)

**Files: `board_renderer.py`, `game_log.py`, `resource_bar.py`, `game_view.py`**

All font sizes multiplied by `ui_scale` with a minimum of 8pt:
```python
font_size = max(8, int(base_font_size * scale))
```

Base font sizes (at 1920×1080):
- Status bar: 16pt
- Resource bar labels: 16pt
- Game log title: 16pt
- Game log entries: 12pt
- Building VP/Owner: 12pt
- Dialog titles: 16pt
- Dialog buttons: 14pt

### Phase 4: Game Log Panel Scaling (FR-006)

**File: `client/ui/game_log.py`**

- Accept `scale` parameter in `draw()`
- Scale line_height: `line_height = max(14, int(22 * scale))`
- Scale title and entry font sizes
- Scale padding and margins

**File: `client/views/game_view.py`**

- Log panel width: `int(450 * ui_scale)`
- Log panel positioned at `content_width - log_width`
- Log panel height: `content_height - resource_bar_height - status_bar_height`

### Phase 5: Resource Bar and Status Bar Scaling

**File: `client/ui/resource_bar.py`**

- Accept `scale` parameter in `draw()`
- Scale font sizes: `max(8, int(16 * scale))`
- Scale swatch dimensions: `int(20 * scale)`
- Scale position offsets proportionally

**File: `client/views/game_view.py`**

- Resource bar height: `int(100 * ui_scale)`
- Status bar height: `int(50 * ui_scale)`
- Both use `content_width` for width
- All text in status bar scaled by `ui_scale`

### Phase 6: Dialog Box Scaling (FR-011)

**File: `client/ui/dialogs.py`**

For all dialog classes, scale dimensions and fonts by `ui_scale`:

**CardSpriteSelectionDialog**:
- Scale `_CARD_SPACING` by ui_scale
- Scale panel dimensions, card sprite `.scale`, button sizes, font sizes
- Scale cancel button dimensions

**UIManager-based dialogs** (CardSelectionDialog, BuildingPurchaseDialog, PlayerTargetDialog, RewardChoiceDialog, ResourceChoiceDialog, ConfirmDialog):
- Scale `width` and `height` parameters of UIFlatButton
- Scale `font_size` parameters of UILabel
- Scale `space_between` in UIBoxLayout
- Scale `padding` values

### Phase 7: Game View Layout Orchestration

**File: `client/views/game_view.py`**

Update `on_draw()` to use content rect instead of raw window dimensions:

```python
def on_draw(self):
    self.clear()
    s = self.window.ui_scale
    cw = self.window.content_width
    ch = self.window.content_height
    
    bar_h = int(100 * s)
    status_h = int(50 * s)
    log_w = int(450 * s)
    board_w = cw - log_w
    board_h = ch - bar_h - status_h
    
    self.board_renderer.draw(0, bar_h, board_w, board_h, scale=s, ...)
    self.resource_bar.draw(0, 0, cw, bar_h, scale=s, ...)
    self.game_log_panel.draw(cw - log_w, bar_h, log_w, board_h, scale=s)
    # Status bar at top of content area
    # ...
```

Update hand panel and player overview overlays to use `content_width` and `content_height` for sizing and positioning.

Update button row positioning to scale with `ui_scale`.

## Complexity Tracking

No constitution violations requiring justification.
