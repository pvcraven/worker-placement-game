# Implementation Plan: Card Image Generator

**Branch**: `010-card-image-generator` | **Date**: 2026-04-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-card-image-generator/spec.md`

## Summary

Create a standalone Pillow-based script in `card-generator/` that reads all card JSON configs, renders each card as a 190x230 PNG with a parchment-colored rounded rectangle on a transparent background, and saves them to `client/assets/card_images/` organized by card type. Reuses existing Pydantic models from `shared/card_models.py` for data loading.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Pillow (PIL), Pydantic v2 (existing), shared/card_models.py (existing)
**Storage**: File system — reads JSON from `config/`, writes PNGs to `client/assets/card_images/`
**Testing**: Manual visual verification (run script, inspect output images)
**Target Platform**: Windows desktop (developer tool)
**Project Type**: CLI script/tool
**Performance Goals**: <30 seconds for 151 card images
**Constraints**: 190x230 pixel output, transparent PNG, parchment background with rounded corners
**Scale/Scope**: 151 total cards (66 quests + 24 buildings + 50 intrigue + 11 producers)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applicable? | Status | Notes |
|-----------|-------------|--------|-------|
| I. Arcade Rendering | No | N/A | Standalone Pillow script, not Arcade client rendering |
| II. Pydantic Data Modeling | Yes | PASS | Reuses existing models from `shared/card_models.py` and `server/models/config.py` |
| III. Client-Server Separation | No | N/A | Standalone tool, does not modify game state |
| IV. Test-Driven Game Logic | No | N/A | No game logic involved |
| V. Simplicity First | Yes | PASS | Single script, reuses existing models, no new abstractions |

No gate violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/010-card-image-generator/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
card-generator/
├── generate_cards.py    # Main script — reads JSON, renders PNGs via Pillow

config/                  # Existing — read-only input
├── contracts.json
├── buildings.json
├── intrigue.json
└── producers.json

shared/                  # Existing — reused for Pydantic models
├── card_models.py       # ContractCard, IntrigueCard, BuildingTile, ProducerCard
└── constants.py         # Genre enum, colors

server/models/           # Existing — reused for config loading
└── config.py            # ContractsConfig, IntrigueConfig, BuildingsConfig, ProducersConfig

client/assets/card_images/   # Generated output (gitignored)
├── quests/              # 66 quest card PNGs
├── buildings/           # 24 building card PNGs
├── intrigue/            # 50 intrigue card PNGs
└── producers/           # 11 producer card PNGs
```

**Structure Decision**: Single script in `card-generator/` directory. No package structure needed — this is a standalone generation tool. Imports shared models via Python path manipulation (sys.path).
