# Data Model: Board Layout Optimization

## Client-Side State (game_view.py)

### Highlight State

New transient UI state for inline card selection. Not persisted, not sent to server.

| Field | Type | Description |
|-------|------|-------------|
| `_highlight_mode` | `str \| None` | Active mode: `"quest_selection"`, `"building_purchase"`, or `None` |
| `_highlighted_ids` | `list[str]` | Card IDs currently highlighted (quest IDs or building IDs) |
| `_cancel_sprite` | `arcade.Sprite \| None` | Cancel button sprite loaded from `cancel.png` |

### State Transitions

```
None -> "quest_selection"     : Worker placed on garage space
None -> "building_purchase"   : Worker placed on realtor space
"quest_selection" -> None     : Quest card clicked OR cancel clicked
"building_purchase" -> None   : Building card clicked OR cancel clicked
```

## Board Layout Coordinates

### Updated _SPACE_LAYOUT

| Space ID | Old Position | New Position | Notes |
|----------|-------------|-------------|-------|
| merch_store | (0.08, 0.90) | (0.08, 0.92) | Shifted up |
| motown | (0.08, 0.80) | (0.08, 0.82) | Shifted up |
| guitar_center | (0.08, 0.70) | (0.08, 0.72) | Shifted up |
| talent_show | (0.08, 0.60) | (0.08, 0.62) | Shifted up |
| rhythm_pit | (0.08, 0.50) | (0.08, 0.52) | Shifted up |
| castle_waterdeep | (0.08, 0.40) | (0.08, 0.42) | Shifted up |
| realtor | (0.08, 0.30) | (0.38, 0.18) | Moved near buildings |
| the_garage_1 | (0.38, 0.87) | (0.38, 0.92) | Shifted up |
| the_garage_2 | (0.52, 0.87) | (0.52, 0.92) | Shifted up |
| the_garage_3 | (0.66, 0.87) | (0.66, 0.92) | Shifted up |

### Updated _BACKSTAGE_LAYOUT

| Slot | Old Position | New Position | Notes |
|------|-------------|-------------|-------|
| backstage_1 | (0.38, 0.33) | (0.08, 0.32) | Moved to left column |
| backstage_2 | (0.52, 0.33) | (0.08, 0.22) | Moved to left column |
| backstage_3 | (0.66, 0.33) | (0.08, 0.12) | Moved to left column |

### Card Display Areas

| Area | Proportional Y | Content |
|------|---------------|---------|
| Quest cards | ~0.68 | 4 face-up quest cards centered at x=0.52 |
| Building cards | ~0.30 | 3 face-up building cards centered at x=0.52 |

## Existing Entities (Unchanged)

No server-side data model changes. All existing entities (ActionSpace, BuildingTile, ContractCard, etc.) remain unchanged. The board.json configuration is unchanged.
