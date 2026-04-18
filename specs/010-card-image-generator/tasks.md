# Tasks: Card Image Generator

**Input**: Design documents from `/specs/010-card-image-generator/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not requested. No test tasks generated.

**Organization**: Tasks grouped by user story. All changes are in card-generator/ and project config — no server or client code changes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create project structure and add Pillow dependency

- [X] T001 Create `card-generator/` directory at project root
- [X] T002 Add `pillow` to dependencies list in pyproject.toml
- [X] T003 Add `client/assets/card_images/` to .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the script scaffold with shared rendering helpers — required by all user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create `card-generator/generate_cards.py` with: sys.path setup to import from project root, imports of Pydantic config models from `server/models/config.py`, output directory constants for each card type (`client/assets/card_images/quests/`, `buildings/`, `intrigue/`, `producers/`), and a `main()` function that creates output directories and calls each card-type generator
- [X] T005 Define rendering constants in `card-generator/generate_cards.py`: CARD_WIDTH=190, CARD_HEIGHT=230, PARCHMENT_COLOR=(235, 220, 185), TEXT_COLOR=(60, 40, 20), CORNER_RADIUS=12, GENRE_COLORS dict mapping Genre enum values to RGB tuples (jazz=blue, pop=magenta, soul=purple, funk=amber, rock=crimson)
- [X] T006 Implement shared helper functions in `card-generator/generate_cards.py`: `create_card_base()` that returns an RGBA Image with transparent background and a parchment rounded rectangle drawn via `ImageDraw.rounded_rectangle()`; `format_resources(cost: ResourceCost)` that returns a compact string like "1G 1B 2D"; `draw_text_centered(draw, text, y, font, color)` that draws horizontally centered text at a given y position

**Checkpoint**: Script runs without errors, creates empty output directories, helper functions defined.

---

## Phase 3: User Story 1 - Generate Quest Card Images (Priority: P1)

**Goal**: Render all 66 quest contract cards as PNGs with genre band, name, cost, VP, bonuses, description

**Independent Test**: Run script, verify 66 PNGs in `client/assets/card_images/quests/`, each showing readable card data with genre-colored header band on parchment background

### Implementation for User Story 1

- [X] T007 [US1] Implement `generate_quest_cards()` in `card-generator/generate_cards.py`: load `config/contracts.json` via ContractsConfig, iterate over contracts, for each card call `create_card_base()` then draw: genre-colored header band at top with genre text, card name (truncated at 20 chars with ".."), cost line using `format_resources()`, VP value prominently, bonus rewards line (bonus resources, draw intrigue/quests, free building), description text (multi-line, wrapped to card width), plot quest marker if `is_plot_quest` is true, ongoing benefit if present. Save as `{card.id}.png` in `client/assets/card_images/quests/`
- [X] T008 [US1] Run script and visually verify quest card output per quickstart.md scenario 2: check contract_jazz_001.png for genre band, name, cost, VP, bonus, description readability

**Checkpoint**: 66 quest card PNGs generated with correct visual layout.

---

## Phase 4: User Story 2 - Generate Building Card Images (Priority: P2)

**Goal**: Render all 24 building cards as PNGs with name, cost, visitor reward, owner bonus, description

**Independent Test**: Run script, verify 24 PNGs in `client/assets/card_images/buildings/`

### Implementation for User Story 2

- [X] T009 [US2] Implement `generate_building_cards()` in `card-generator/generate_cards.py`: load `config/buildings.json` via BuildingsConfig, iterate over buildings, for each card call `create_card_base()` then draw: card name, "Cost: N coins", visitor reward using `format_resources()` plus `visitor_reward_special` text if present (e.g., "Draw Quest", "Draw Intrigue"), owner bonus using `format_resources()` plus `owner_bonus_special` text if present, description text. Save as `{card.id}.png` in `client/assets/card_images/buildings/`
- [X] T010 [US2] Run script and visually verify building card output per quickstart.md scenario 3 and scenario 9

**Checkpoint**: 24 building card PNGs generated.

---

## Phase 5: User Story 3 - Generate Intrigue Card Images (Priority: P3)

**Goal**: Render all 50 intrigue cards as PNGs with name, description, effect summary, target indicator

**Independent Test**: Run script, verify 50 PNGs in `client/assets/card_images/intrigue/`

### Implementation for User Story 3

- [X] T011 [US3] Implement `generate_intrigue_cards()` in `card-generator/generate_cards.py`: load `config/intrigue.json` via IntrigueConfig, iterate over intrigue_cards, for each card call `create_card_base()` then draw: card name, "INTRIGUE" label, description text, effect summary line derived from effect_type and effect_value (reuse logic from `CardRenderer._intrigue_effect_summary()` in `client/ui/card_renderer.py` as reference), effect_target indicator (e.g., "Target: Opponent", "All Players"). Save as `{card.id}.png` in `client/assets/card_images/intrigue/`
- [X] T012 [US3] Run script and visually verify intrigue card output per quickstart.md scenarios 4 and 10

**Checkpoint**: 50 intrigue card PNGs generated.

---

## Phase 6: User Story 4 - Generate Producer Card Images (Priority: P4)

**Goal**: Render all 11 producer cards as PNGs with name, description, bonus genres, VP per contract

**Independent Test**: Run script, verify 11 PNGs in `client/assets/card_images/producers/`

### Implementation for User Story 4

- [X] T013 [US4] Implement `generate_producer_cards()` in `card-generator/generate_cards.py`: load `config/producers.json` via ProducersConfig, iterate over producers, for each card call `create_card_base()` then draw: card name, description text, bonus genres listed (e.g., "Jazz, Pop"), "+N VP per matching contract" line. Save as `{card.id}.png` in `client/assets/card_images/producers/`
- [X] T014 [US4] Run script and visually verify producer card output per quickstart.md scenario 5

**Checkpoint**: 11 producer card PNGs generated.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [X] T015 Run full script and verify total output is exactly 151 card images (66 + 24 + 50 + 11) per quickstart.md scenario 1
- [X] T016 Verify long name truncation per quickstart.md scenario 6
- [X] T017 Verify idempotent regeneration per quickstart.md scenario 7
- [X] T018 Verify script completes in under 30 seconds per quickstart.md scenario 11
- [X] T019 Run `ruff check card-generator/generate_cards.py` and fix any lint issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — create directory and add dependency
- **Foundational (Phase 2)**: Depends on Phase 1 — script scaffold and helpers
- **US1 (Phase 3)**: Depends on Phase 2 — quest card rendering
- **US2 (Phase 4)**: Depends on Phase 2 — building card rendering
- **US3 (Phase 5)**: Depends on Phase 2 — intrigue card rendering
- **US4 (Phase 6)**: Depends on Phase 2 — producer card rendering
- **Polish (Phase 7)**: Depends on all user stories

### User Story Dependencies

- **US1 (P1)**: Independent after Phase 2
- **US2 (P2)**: Independent after Phase 2, can run in parallel with US1
- **US3 (P3)**: Independent after Phase 2, can run in parallel with US1/US2
- **US4 (P4)**: Independent after Phase 2, can run in parallel with US1/US2/US3

### Parallel Opportunities

- T001, T002, T003 can run in parallel (different files)
- T005 can run in parallel with T004 (same file but different sections — constants vs scaffold)
- US1-US4 implementation tasks (T007, T009, T011, T013) can all run in parallel after Phase 2 (each adds an independent function to the same file)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Script scaffold + helpers
3. Complete Phase 3: Quest card generation
4. **STOP and VALIDATE**: Check quest card PNGs visually

### Incremental Delivery

1. Setup + Foundational → Script runs, creates directories
2. Add US1 → 66 quest cards generated → Validate
3. Add US2 → 24 building cards generated → Validate
4. Add US3 → 50 intrigue cards generated → Validate
5. Add US4 → 11 producer cards generated → Validate
6. Polish → Full count verification, lint, performance check

---

## Notes

- All 4 user stories add functions to the same file (`card-generator/generate_cards.py`) but are independent functions with no cross-dependencies
- The script reuses existing Pydantic models — no new data models created
- Reference `client/ui/card_renderer.py` for layout inspiration but render with Pillow, not Arcade
- Output directory `client/assets/card_images/` is gitignored as a generated artifact
