# Data Model: Tabbed Side Panel

## Entities

### TabbedPanel (client-side only)

The central UI component replacing the fixed game log panel and dialog overlays.

**Fields**:
- `active_tab: str` — Currently selected tab identifier. One of: `"game_log"`, `"my_quests"`, `"my_intrigue"`, `"completed_quests"`, `"producer"`. Default: `"game_log"`.
- `game_log_panel: GameLogPanel` — Composed instance of the existing scrollable log panel.
- `_tab_shape_list: ShapeElementList` — Cached shape list for tab bar backgrounds.
- `_tab_texts: list[arcade.Text]` — Cached text objects for tab labels.
- `_content_sprite_list: SpriteList` — Cached sprite list for card/producer rendering in current tab.
- `_tab_rects: dict[str, tuple[float, float, float, float]]` — Hit-test rectangles for each tab button (x, y, w, h).
- `_text_cache: dict[str, arcade.Text]` — Cached text objects for title and empty-state messages.

**Methods**:
- `draw(x, y, w, h, player_data, scale)` — Draws tab bar, title, and active content.
- `on_click(x, y) -> bool` — Hit-tests tab bar; switches `active_tab` if hit. Returns True if a tab was clicked.
- `update_game_log(panel: GameLogPanel)` — Updates the composed game log reference.

### Tab (conceptual, not a separate class)

A tab is a visual button in the tab bar. Represented by:
- Position and size in `_tab_rects`
- Label text in `_tab_texts`
- Active/inactive visual state derived from comparing `active_tab` to the tab's identifier

## Relationships

- `TabbedPanel` **composes** one `GameLogPanel` (for the game log tab).
- `TabbedPanel` **reads** player data (quest hand, intrigue hand, completed quests, producer card) passed from `GameView` on each draw call.
- `TabbedPanel` is **owned by** `GameView` (replaces `game_log_panel` field and overlay toggle state).
- Dialogs remain **independent** of `TabbedPanel` — they are drawn as overlays by `GameView.on_draw()` and are not affected by tab state.

## State Transitions

```
active_tab: "game_log" (default)
    ──click "My Quests"──▶ "my_quests"
    ──click "My Intrigue"──▶ "my_intrigue"
    ──click "Completed Quests"──▶ "completed_quests"
    ──click "Producer"──▶ "producer"
    ──click "Game Log"──▶ "game_log"
```

All transitions are instant (same frame). No animations. No server communication.
