# Quickstart: Board Layout Scaling

**Feature**: 013-board-layout-scaling  
**Date**: 2026-04-20

## What This Feature Does

Scales all visual elements (cards, text, panels, dialogs) proportionally with the game window size, maintains aspect ratio on non-proportional windows, and reorganizes constructed buildings into a two-column layout.

## Key Files to Modify

1. **`client/game_window.py`** — Add `content_width`/`content_height` properties
2. **`client/ui/board_renderer.py`** — Add sprite scaling, two-column buildings, scaled text
3. **`client/views/game_view.py`** — Use content rect for layout, scale panels and status bar
4. **`client/ui/game_log.py`** — Scale panel dimensions, font sizes, line height
5. **`client/ui/resource_bar.py`** — Scale font sizes and element positions
6. **`client/ui/dialogs.py`** — Scale dialog dimensions, card sprites, button sizes, fonts

## Architecture

The scaling approach centers on a single scale factor: `ui_scale = min(window_w / 1920, window_h / 1080)`.

```
GameWindow.ui_scale
    │
    ├── GameView.on_draw()
    │     ├── content_w = 1920 * ui_scale
    │     ├── content_h = 1080 * ui_scale
    │     ├── board area = (0, resource_bar_h, content_w - log_w, content_h - bar_h - status_h)
    │     ├── game log  = (content_w - log_w, resource_bar_h, log_w, content_h - bar_h - status_h)
    │     ├── resource bar = (0, 0, content_w, 100 * ui_scale)
    │     └── status bar = (0, content_h - status_h, content_w, status_h)
    │
    ├── BoardRenderer.draw(x, y, w, h)
    │     ├── sprite.scale = ui_scale (clamped 0.3–2.0)
    │     ├── positions = proportional × (w, h)
    │     └── font_size = base_size * ui_scale (min 8pt)
    │
    └── Dialogs (created with current ui_scale)
          ├── button width/height *= ui_scale
          ├── font_size *= ui_scale
          └── card sprite.scale = ui_scale
```

## How to Test

1. Start server and client: `cd src && python -m server.main` + `cd src && python -m client.main`
2. Resize the window — all elements should scale proportionally
3. Make window very wide — content should stay at top-left, not stretch
4. Make window very tall — content should stay at top-left, not stretch
5. Construct buildings — should appear in two columns
6. Resize after buildings constructed — VP/Owner text stays anchored
7. Open dialogs at different sizes — should scale with window

## Running Tests

```bash
cd src && pytest && ruff check .
```
