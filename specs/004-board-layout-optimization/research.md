# Research: Board Layout Optimization

**Date**: 2026-04-16 | **Branch**: `004-board-layout-optimization`

## R1: ShapeElementList API for Batched Rendering

**Decision**: Use `arcade.shape_list.ShapeElementList` to batch all static board shapes (filled rectangles, outlined rectangles).

**Rationale**: The API is straightforward — create `Shape` objects via factory functions, `append()` them to a `ShapeElementList`, and call `draw()` once per frame. The list handles VBO management internally. Shapes are created once and stored on the GPU.

**Key API**:
- `arcade.shape_list.create_rectangle_filled(cx, cy, w, h, color)` → `Shape`
- `arcade.shape_list.create_rectangle_outline(cx, cy, w, h, color, border_width)` → `Shape`
- `ShapeElementList.append(shape)` — add a shape
- `ShapeElementList.draw()` — draw all shapes in one batch
- `ShapeElementList.clear()` — remove all shapes (call before rebuilding)

**Pattern**: Build the shape list once in `update_board()`. Call `draw()` each frame. Rebuild (clear + re-add) when board state changes (worker placed, building constructed).

**Alternatives considered**:
- Pyglet shapes — rejected; arcade's ShapeElementList is the native approach for this engine
- Keep immediate-mode draws — rejected; this is the optimization the spec requires

## R2: Rename Scope — real_estate_listings → realtor

**Decision**: Full rename of space_id, space_type, display name, and all code references from `real_estate_listings` to `realtor`.

**Rationale**: Per clarification, user wants consistent naming between display and code. Since the previous rename (builders_hall → real_estate_listings) just happened, better to settle on the final name now.

**Files requiring changes**:
- `config/board.json`: space_id, name, space_type (3 values)
- `server/game_engine.py`: 4 references (2 string literals, 2 comments)
- `client/ui/board_renderer.py`: 1 reference in `_SPACE_LAYOUT` dict key
- `client/views/game_view.py`: 1 comment reference

**Alternatives considered**: Display-name-only rename — rejected per user clarification

## R3: Building Market Popup — Rendering Pattern

**Decision**: Follow the existing hand panel pattern in `GameView._draw_hand_panel()` — semi-transparent background, centered content, toggle behavior matching My Quests/My Intrigue.

**Rationale**: The hand panel already implements the exact UX pattern needed: toggle button, only-one-open-at-a-time, semi-transparent overlay. Reusing this pattern ensures visual consistency.

**Key differences from hand panels**:
- Building cards show different fields: name, genre, cost, VP, visitor reward, owner bonus, description
- Data source is `_face_up_buildings` list + `_building_deck_remaining` count
- No card selection action from this panel (purchase is done via the Realtor space dialog)

**Alternatives considered**:
- UIManager-based popup — rejected because hand panels already use immediate-mode drawing and it works well
- Separate view/screen — rejected; popup overlay is more natural for glanceable info

## R4: Label Removal and Vertical Space Recovery

**Decision**: Remove the three heading labels ("THE BOARD", "THE GARAGE", "BACKSTAGE") and shift all Y positions upward. Backstage slots get self-describing labels "Backstage N".

**Rationale**: The labels consume vertical space without adding information (the sections are visually obvious from their content). Backstage slots are not obviously backstage without the heading, so they get self-describing labels.

**Layout impact**: Removing the labels frees approximately 10-15% of vertical space. All proportional Y positions in `_SPACE_LAYOUT` and `_BACKSTAGE_LAYOUT` need adjustment upward.

**Alternatives considered**: None — direct user requirement.

## R5: Purchase Dialog Title

**Decision**: Rename the `BuildingPurchaseDialog` title from "Purchase a Building" to "Real Estate Listings" to match the new naming scheme.

**Rationale**: The "Real Estate Listings" name moves from the board space (now "Realtor") to the market/purchase interface.

**Alternatives considered**: None — direct user requirement.
