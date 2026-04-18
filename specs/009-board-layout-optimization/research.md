# Research: Board Layout Optimization

## Decision 1: Board Layout Proportional Coordinates

**Decision**: Reorganize the board by moving backstage slots to the left column, shifting quest cards up, and placing buildings in the lower-center area.

**Rationale**: The left column currently has 7 spaces (merch_store through realtor) occupying y=0.90 to y=0.30. Adding 3 backstage slots below (y=0.32, 0.22, 0.12) keeps all non-card action spaces in the left column. This frees the center-bottom for building card display, mirroring the quest card area above.

**Alternatives considered**:
- Backstage in a row across the bottom: rejected because it competes with the resource bar (y=0 to y=100px).
- Backstage remaining in center: rejected because it blocks the building card area.
- Buildings on the right side: rejected because constructed buildings already occupy that area.

## Decision 2: Highlight Rendering Approach

**Decision**: Draw yellow highlight rectangles around selectable cards using arcade draw calls in the board renderer's draw loop. Manage highlight state in game_view.py.

**Rationale**: Cards are already drawn by CardRenderer with a `highlight` parameter. We can pass `highlight=True` for cards whose ID is in the highlight list. The cancel button is a sprite loaded from `cancel.png`.

**Alternatives considered**:
- Overlay transparent colored panels: more complex, same visual effect.
- Animate highlights with pulsing: unnecessary complexity per constitution principle V.

## Decision 3: Cancel Button Implementation

**Decision**: Load `cancel.png` as an arcade.Sprite, position it in the lower-left corner (above the resource bar), show/hide based on highlight mode state.

**Rationale**: Using a sprite is the standard Arcade approach for image-based UI elements. Position in lower-left avoids overlapping the game log panel (right side) and board content (center).

**Alternatives considered**:
- arcade.gui UIFlatButton with red styling: functional but doesn't use the custom graphic as specified.
- Drawing the cancel icon with shapes: more code, worse appearance.

## Decision 4: Building Card Rendering

**Decision**: Render face-up buildings using a new `draw_building` method in CardRenderer, similar to `draw_contract` but showing building-specific info (cost in coins, visitor reward, owner bonus, VP).

**Rationale**: Reusing the card rendering pattern ensures visual consistency. Buildings have different data (coin cost vs. resource cost, owner bonus) so a dedicated method is cleaner than overloading draw_contract.

**Alternatives considered**:
- Reuse the existing building market panel text layout: rejected because the panel is being removed.
- Use draw_contract with building data shoe-horned in: rejected because fields don't map cleanly.

## Decision 5: Server Protocol

**Decision**: No server changes needed. The existing messages (select_quest_card, cancel_quest_selection, purchase_building, cancel_purchase_building) already support the needed interactions.

**Rationale**: The change is purely about how the client presents the selection UI — the data exchange with the server remains identical.
