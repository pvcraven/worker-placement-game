# Worker Placement Game Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-14

## Active Technologies
- Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (validation) (002-garage-quest-display)
- In-memory game state (server); JSON configuration (game content) (002-garage-quest-display)
- Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (data validation/serialization) (003-building-purchase)
- In-memory game state (server); JSON configuration files (game content) (003-building-purchase)

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
- 003-building-purchase: Added Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
- 002-garage-quest-display: Added Python 3.12+ + Arcade (client UI), websockets (networking), Pydantic (validation)

- 001-worker-placement-game: Added Python 3.12+ + Arcade (graphics/client UI), websockets (async networking), Pydantic (data validation/serialization)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
