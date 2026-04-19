# Worker Placement Game Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-18

## Active Technologies
- Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (validation) (002-garage-quest-display)
- In-memory game state (server); JSON configuration (game content) (002-garage-quest-display)
- Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (data validation/serialization) (003-building-purchase)
- In-memory game state (server); JSON configuration files (game content) (003-building-purchase)
- Python 3.12+ + Arcade (local source), websockets, Pydantic v2 (009-board-layout-optimization)
- Python 3.12+ + Pillow (PIL), Pydantic v2 (existing), shared/card_models.py (existing) (010-card-image-generator)
- File system — reads JSON from `config/`, writes PNGs to `client/assets/card_images/` (010-card-image-generator)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (existing) (011-sprite-card-rendering)
- File system — reads PNGs from `client/assets/card_images/` (011-sprite-card-rendering)

- Python 3.12+ + Arcade (graphics/client UI), websockets (async networking), Pydantic (data validation/serialization) (001-worker-placement-game)

## Project Structure

```text
src/
tests/
```

## Commands

cd src && pytest && ruff check .

## Code Style

Python 3.12+: Follow standard conventions

## Recent Changes
- 011-sprite-card-rendering: Added Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (existing)
- 010-card-image-generator: Added Python 3.12+ + Pillow (PIL), Pydantic v2 (existing), shared/card_models.py (existing)
- 009-board-layout-optimization: Added Python 3.12+ + Arcade (local source), websockets, Pydantic v2


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
