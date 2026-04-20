# Data Model: Board Layout Scaling

**Feature**: 013-board-layout-scaling  
**Date**: 2026-04-20

## Overview

This feature is purely client-side rendering. No new data entities, database tables, or network messages are introduced. The changes affect how existing data is visually laid out.

## Modified Entities

### GameWindow (existing)

| Field | Type | Change |
|-------|------|--------|
| `scale_x` | float | Existing — no change |
| `scale_y` | float | Existing — no change |
| `ui_scale` | float | Existing — becomes the primary scale factor for all layout |
| `content_width` | float | **New** — `DESIGN_WIDTH * ui_scale` |
| `content_height` | float | **New** — `DESIGN_HEIGHT * ui_scale` |

### BoardRenderer (existing)

| Field | Type | Change |
|-------|------|--------|
| `_card_scale` | float | **New** — derived from `ui_scale`, clamped [0.3, 2.0] |
| `_SPACE_LAYOUT` | dict | **Modified** — permanent spaces shift left with reduced margins |
| Building grid | formula | **Modified** — from 5-row×N-col to N-row×2-col |

### Layout Constants (existing module-level)

| Constant | Current | New |
|----------|---------|-----|
| `_CARD_WIDTH` | 190 (fixed px) | 190 (base, multiplied by `_card_scale` at render time) |
| `_CARD_HEIGHT` | 230 (fixed px) | 230 (base, multiplied by `_card_scale` at render time) |
| `_BUILDING_CARD_HEIGHT` | 150 (fixed px) | 150 (base, multiplied by `_card_scale` at render time) |
| `_SPACE_CARD_HEIGHT` | 100 (fixed px) | 100 (base, multiplied by `_card_scale` at render time) |

## Relationships

No new relationships. All entities remain the same — only their visual representation changes.

## State Transitions

No new state transitions. The `_shapes_dirty` flag already triggers re-layout on window resize via `draw_rect != _last_draw_rect`.
