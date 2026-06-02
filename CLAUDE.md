# Worker Placement Game Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-06-02

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
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2 (012-resource-choice-rewards)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (013-board-layout-scaling)
- N/A (client-side rendering only) (013-board-layout-scaling)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (014-tabbed-side-panel)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (015-final-score-screen)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2 (016-building-revamp)
- In-memory game state (server); JSON configuration files in `config/` (016-building-revamp)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL) for card/icon generation, Pydantic v2 (017-resource-bar-revamp)
- File system — reads/writes PNGs in `client/assets/card_images/` (017-resource-bar-revamp)
- In-memory game state; JSON config files in `config/` (018-resource-trigger-plots)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2 (019-remaining-special-quests)
- In-memory game state; JSON configuration in `config/` (019-remaining-special-quests)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2 (021-zoarstar-building)
- Python 3.12+ + Arcade (local source), websockets, Pydantic v2, Pillow (card generation) (022-resource-choice-building)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2 (023-info-dialog)
- N/A (client-side UI only) (023-info-dialog)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation) (025-intrigue-draw-building)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation) (026-intrigue-card-update)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pydantic v2, Pillow (card generation) (027-board-grid-layout)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2 (028-client-reconnect)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (ease, Easing) (029-marker-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease) (030-card-pick-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL), Pydantic v2, websockets (032-intrigue-card-animation)
- In-memory game state; JSON config; PNG image files (032-intrigue-card-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (for marker PNG generation) (033-colored-marker-selection)
- In-memory game state (server); PNG image files (marker assets) (033-colored-marker-selection)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease), Pydantic v2 (034-quest-completion-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease) (035-building-acquisition-animation)
- N/A (client-side animation only) (035-building-acquisition-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease) (036-resource-gathering-animation)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL) for card image generation, Pydantic v2 (037-backstage-closed-cards)
- File system — reads/writes PNGs in `client/assets/card_images/spaces/` (037-backstage-closed-cards)
- Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation) (038-intrigue-quest-space)
- Python 3.12+ + Pydantic v2, Pillow (card image generation), Arcade (local source) (039-tier1-quest-expansion)

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
- 039-tier1-quest-expansion: Added Python 3.12+ + Pydantic v2, Pillow (card image generation), Arcade (local source)
- 038-intrigue-quest-space: Added Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation)
- 037-backstage-closed-cards: Added Python 3.12+ + Arcade (local source at C:\Users\PaCra\Projects\arcade), Pillow (PIL) for card image generation, Pydantic v2


<!-- MANUAL ADDITIONS START -->

## Game Content

- **Quests** (called "contracts" in code): `config/contracts.json` — 60 quest cards defining costs, rewards, and victory points. The terms "quest" and "contract" are interchangeable; the user-facing name is "quest" but the code/data model uses "contract".
- **Intrigue cards**: `config/intrigue.json` — intrigue card definitions.
- **Buildings**: `config/buildings.json` — purchasable building definitions.
- **Board spaces**: `config/board.json` — permanent board spaces and building lot count.
- **Game rules**: `config/game_rules.json` — round count, starting resources, etc.
- **Producers**: `config/producers.json` — producer card definitions.

<!-- MANUAL ADDITIONS END -->
