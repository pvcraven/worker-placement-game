# Implementation Plan: Tier 1 Quest Card Expansion

**Branch**: `039-tier1-quest-expansion` | **Date**: 2026-06-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/039-tier1-quest-expansion/spec.md`

## Summary

Add 15 new quest cards (simple cost→VP+bonus mechanics) to the game's contract pool, expanding from 60 to 75 cards. Includes 5 "mega quests" (40 VP each, one per genre). All cards use existing data model fields — no new code paths, server logic, or Pydantic fields required. The main work is JSON data entry, card image regeneration, and adjusting one test that asserts equal cards per genre.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Pydantic v2, Pillow (card image generation), Arcade (local source)
**Storage**: JSON config files in `config/`
**Testing**: pytest + ruff (`cd src && pytest && ruff check .`)
**Target Platform**: Windows desktop (Arcade client)
**Project Type**: Multiplayer board game (client/server)
**Performance Goals**: N/A — data-only change
**Constraints**: None — all 15 cards fit existing ContractCard model fields
**Scale/Scope**: 15 new JSON entries, 1 test update, card image regeneration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | N/A | No rendering code changes |
| II. Pydantic Data Modeling | Pass | Uses existing `ContractCard` model, `ContractsConfig` validation |
| III. Client-Server Separation | Pass | Only `config/contracts.json` changes — loaded by both client (image gen) and server (game engine) |
| IV. Test-Driven Game Logic | Pass | Existing tests cover contract validation; `test_equal_cards_per_genre` must be updated for uneven genre counts |
| V. Simplicity First | Pass | Pure data addition, no new abstractions |
| VI. Server-Authoritative Protocol | N/A | No new messages |
| VII. Config-Driven Game Content | Pass | New content added as JSON entries in `config/contracts.json` — exactly as prescribed |
| VIII. Pending State | N/A | No deferred actions |
| IX. Cancel/Unwind | N/A | No cancellable actions |
| X. Post-Action Turn Flow | N/A | No new turn flow |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/039-tier1-quest-expansion/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (minimal — no unknowns)
├── data-model.md        # Phase 1 output (contract card data)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files touched)

```text
config/
└── contracts.json           # ADD 15 new contract entries

tests/
└── test_cards.py            # UPDATE test_equal_cards_per_genre assertion

card-generator/
└── generate_cards.py        # RUN to regenerate card images (no code changes)

client/assets/card_images/
└── quests/                  # OUTPUT: 15 new PNG card images

specs/card_reference/
└── quest_implementation_analysis.md  # UPDATE: mark implemented cards, add TBD note
```

**Structure Decision**: No new directories or files created (aside from generated PNGs). All changes go into existing files.

## Key Implementation Details

### ContractCard Fields Used

All 15 new cards use only these existing fields — no new Pydantic fields needed:

```
id, name, description, genre, cost, victory_points, bonus_resources, is_plot_quest
```

Every new card has `is_plot_quest: false` and no ongoing benefit fields.

### Card ID Convention

Follow existing pattern: `contract_{genre}_{NNN}` where NNN continues from the last ID per genre.

| Genre | Current Last ID | New IDs |
|-------|----------------|---------|
| Pop   | contract_pop_012 | contract_pop_013 through contract_pop_016 |
| Rock  | contract_rock_012 | contract_rock_013 through contract_rock_015 |
| Soul  | contract_soul_012 | contract_soul_013 through contract_soul_015 |
| Funk  | contract_funk_012 | contract_funk_013 through contract_funk_014 |
| Jazz  | contract_jazz_012 | contract_jazz_013 through contract_jazz_015 |

### Test Impact Analysis

| Test | Impact | Action |
|------|--------|--------|
| `test_equal_cards_per_genre` | **FAILS** — genres now have unequal counts (14-16) | Update to check minimum count per genre instead of exact equality |
| `test_genre_total_benefit_balanced` | May shift — verify spread ≤ 10.0 still holds | Run and verify |
| `test_all_cards_have_minimum_benefit` | Should pass — all new cards have benefit ≥ 1.0 | Run and verify |
| `test_benefit_not_more_than_four_and_half_times_cost` | Should pass — mega quests are ~4.0x ratio | Run and verify |
| `test_soul_requires_most_singers` | Should pass — new Soul cards maintain singer dominance | Run and verify |
| `test_funk_requires_most_drummers` | Should pass — new Funk cards maintain drummer dominance | Run and verify |
| `test_rock_requires_most_guitarists` | Should pass — new Rock cards maintain guitarist dominance | Run and verify |
| `test_pop_requires_most_coins` | Should pass — new Pop cards add 15 coins total to costs | Run and verify |
| `test_jazz_requires_most_bass_players` | Should pass — new Jazz cards add 14 bass players to costs | Run and verify |

### Mega Quest Balance Verification

All mega quests have ~4.0x benefit/cost ratio (under the 4.5x cap):

| Card | Cost Points | VP | Benefit | Ratio |
|------|------------|-----|---------|-------|
| Global Pop Domination | 8.0 | 40 | 32.0 | 4.00x |
| Rock Legends World Tour | 8.0 | 40 | 32.0 | 4.00x |
| Soul Music Magnum Opus | 8.0 | 40 | 32.0 | 4.00x |
| Funkadelic Magnum Opus | 8.0 | 40 | 32.0 | 4.00x |
| Jazz Empire Conspiracy | 8.75 | 40 | 31.25 | 3.57x |

(Resource point weights: singers=1.0, drummers=1.0, guitarists=0.5, bass_players=0.5, coins=0.25)

## Complexity Tracking

No constitution violations — table not needed.
