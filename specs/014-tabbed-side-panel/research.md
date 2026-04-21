# Research: Tabbed Side Panel

## Decision 1: Tab Bar Rendering Approach

**Decision**: Use `ShapeElementList` for tab bar backgrounds and `arcade.Text` for tab labels, cached and rebuilt only on resize or tab change.

**Rationale**: Follows Constitution Principle I (Arcade Rendering Standards). The tab bar has a fixed number of elements (5 tabs) that only change visual state (active/inactive) on click. Caching shapes and text objects avoids per-frame GPU overhead.

**Alternatives considered**:
- `arcade.gui.UIManager` buttons: Would layer on top of the panel rather than integrating into it. Harder to control precise positioning and styling within the panel. The existing button row already uses UIManager — duplicating it inside the panel would conflict.
- Raw draw calls: Prohibited by constitution.

## Decision 2: Panel Architecture — Composition vs. Replacement

**Decision**: Create a new `TabbedPanel` class that composes the existing `GameLogPanel` for the Game Log tab, and renders card sprite lists and producer sprites directly for the other tabs.

**Rationale**: The `GameLogPanel` already handles scrollable text entries, text caching, and auto-scroll. Rewriting it would be unnecessary duplication. The other tabs (cards, producer) are simpler — they render sprite grids or a single sprite, which the panel can handle directly without separate classes.

**Alternatives considered**:
- Subclassing `GameLogPanel`: Wrong — the other tabs have nothing to do with log entries.
- Creating 5 separate panel classes: Over-engineered for views that are essentially "render N sprites in a grid."

## Decision 3: Tab Switching and Dialog Independence

**Decision**: Tab state is a simple string enum on `TabbedPanel`. Switching tabs only changes which content is drawn — it does not interact with dialog visibility or game state at all.

**Rationale**: Dialogs are drawn independently in `game_view.on_draw()` as overlays on top of the panel. Since tab switching only changes what `TabbedPanel.draw()` renders (below the dialog layer), dialogs naturally remain unaffected. No special handling needed.

## Decision 4: Card Layout — Two-Column Grid

**Decision**: Cards are rendered as sprites in a 2-column grid. Card scale is computed from the panel width: `card_scale = (panel_w / 2 - margins) / card_base_width`. Rows stack vertically downward.

**Rationale**: The panel is `450 * scale` pixels wide. At standard scale, that's 450px — enough for two ~190px cards with ~35px margins each. Cards are pre-rendered PNGs loaded as sprites, consistent with the existing board renderer pattern.

## Decision 5: Removing Old Overlay Buttons and Draw Methods

**Decision**: Remove the 4 dialog-toggle buttons ("My Quests", "My Intrigue", "Completed Quests", "Producer") and their corresponding `_toggle_*`, `_draw_*_panel` methods from `game_view.py`. Keep "Player Overview" as a separate button since the spec excludes it from the tabs.

**Rationale**: These buttons and overlays are fully replaced by the tab bar. Leaving them would create redundant UI paths and confuse users. Player Overview remains separate per the spec assumption.
