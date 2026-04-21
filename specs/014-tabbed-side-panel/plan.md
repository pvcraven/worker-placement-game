# Implementation Plan: Tabbed Side Panel

**Branch**: `014-tabbed-side-panel` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/014-tabbed-side-panel/spec.md`

## Summary

Convert the right-side panel from a fixed game log into a tabbed interface with five selectable views: Game Log, My Quests, My Intrigue, Completed Quests, and Producer. Replace the existing dialog-based overlay buttons with tab buttons at the top of the panel. Card views use a two-column grid layout. Tabs remain functional even when modal dialogs are displayed.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2
**Storage**: N/A (client-side rendering only)
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Desktop game (client-server, Arcade UI)
**Performance Goals**: 60 fps, tab switching within same frame
**Constraints**: All text via `arcade.Text`, all shapes via `ShapeElementList`, no primitive draw calls
**Scale/Scope**: Single right-side panel, 5 tab views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Tab bar and content will use `arcade.Text` for text, `ShapeElementList` for backgrounds, sprites for cards. No primitive draw calls. |
| II. Pydantic Data Modeling | PASS | No new network messages or cross-boundary data. Tab state is local to the client UI. |
| III. Client-Server Separation | PASS | Purely client-side UI change. No server modifications. Tab state doesn't affect game state. |
| IV. Test-Driven Game Logic | PASS | No server-side game logic changes. Existing tests remain valid. |
| V. Simplicity First | PASS | Consolidates 5 overlay toggles + 5 draw methods into 1 tabbed panel class. Net reduction in complexity. |

## Project Structure

### Documentation (this feature)

```text
specs/014-tabbed-side-panel/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
client/
├── ui/
│   ├── board_renderer.py     # Unchanged
│   ├── dialogs.py            # Unchanged
│   ├── game_log.py           # Modified — remove title drawing, accept reduced height
│   ├── resource_bar.py       # Unchanged
│   └── tabbed_panel.py       # NEW — TabbedPanel class with tab bar + content rendering
├── views/
│   └── game_view.py          # Modified — replace overlay toggles/draws with TabbedPanel
tests/
└── (no new tests — client-only UI, no game logic changes)
```

**Structure Decision**: Existing flat `client/ui/` layout. New file `tabbed_panel.py` sits alongside `game_log.py` and the other UI modules. The `GameLogPanel` is composed into `TabbedPanel` rather than replaced, preserving its scrolling logic.
