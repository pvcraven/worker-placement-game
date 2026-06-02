# Tasks: Tier 1 Quest Card Expansion

**Input**: Design documents from `specs/039-tier1-quest-expansion/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: Existing test suite covers card validation. One test update needed (`test_equal_cards_per_genre`). No new test files.

**Organization**: Tasks grouped by user story. US1 and US2 are both P1 but US2 (mega quests) is part of the same JSON edit, so they share a phase. US3 (card images) follows.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No project setup needed — all infrastructure exists. This phase handles the test update that unblocks adding uneven card counts.

- [x] T001 Update `test_equal_cards_per_genre` in `src/tests/test_cards.py` to allow uneven genre counts (currently asserts all genres have exactly 12 cards; change to assert each genre has at least 12 cards)

**Checkpoint**: Test suite passes with current 60 cards and will accept unequal genre counts.

---

## Phase 2: User Stories 1 & 2 - Quest Cards + Mega Quests (Priority: P1) MVP

**Goal**: Add 15 new quest cards to the game (10 standard + 5 mega quests), expanding the pool from 60 to 75 cards.

**Independent Test**: Start a game, verify new cards appear in the quest market, complete one and confirm correct VP and bonus resources are awarded. Verify a mega quest shows 40 VP with high cost.

### Implementation

- [x] T002 [US1] Add 4 new Pop contracts to `src/config/contracts.json`: Platinum Record Heist (contract_pop_013), Street Team Recruitment (contract_pop_014), International Pop Tour (contract_pop_015), Global Pop Domination (contract_pop_016, mega quest 40VP)
- [x] T003 [US1] Add 3 new Rock contracts to `src/config/contracts.json`: Wake the Sleeping Legends (contract_rock_013), Demolish the Rival Arena (contract_rock_014), Rock Legends World Tour (contract_rock_015, mega quest 40VP)
- [x] T004 [US1] Add 3 new Soul contracts to `src/config/contracts.json`: Rescue the Gospel Choir (contract_soul_013), Soul Heritage Foundation (contract_soul_014), Soul Music Magnum Opus (contract_soul_015, mega quest 40VP)
- [x] T005 [US1] Add 2 new Funk contracts to `src/config/contracts.json`: Resurrect the Funk Pioneers (contract_funk_013), Funkadelic Magnum Opus (contract_funk_014, mega quest 40VP)
- [x] T006 [US1] Add 3 new Jazz contracts to `src/config/contracts.json`: Survive the Genre Crossover (contract_jazz_013), Underground Jazz Blitz (contract_jazz_014), Jazz Empire Conspiracy (contract_jazz_015, mega quest 40VP)
- [x] T007 [US1] Run `cd src && pytest && ruff check .` to verify all card balance tests pass with the new 75-card pool (benefit ratios, genre specialization, minimum benefit)

**Checkpoint**: 75 cards in pool, all tests pass, new cards playable in-game.

---

## Phase 3: User Story 3 - Card Images (Priority: P2)

**Goal**: Generate card images for all 15 new quest cards so they display correctly in the game UI.

**Independent Test**: Run the card image generator and verify 15 new PNG files appear in `src/client/assets/card_images/quests/`. Start the game client and confirm new cards render with correct genre color, name, cost icons, and VP.

### Implementation

- [x] T008 [US3] Run the card image generator (`src/card-generator/generate_cards.py`) to produce PNG card images for the 15 new contracts in `src/client/assets/card_images/quests/`
- [x] T009 [US3] Visually verify a sample of generated card images show correct genre band color, card name, resource cost symbols, VP value, and bonus resource symbols

**Checkpoint**: All 15 new cards have generated images and display correctly in the game UI.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Update documentation to track implementation progress.

- [x] T010 Update `specs/card_reference/quest_implementation_analysis.md`: move the 15 implemented cards from the "Tier 1" unimplemented list to a new "Implemented in 039" section, and add a TBD note for "Defend the Lanceboard Room" (deferred until "choose any resource" reward mechanic exists)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — update test assertion first
- **Phase 2 (Quest Cards)**: Depends on Phase 1 — test must accept uneven counts before adding cards
- **Phase 3 (Card Images)**: Depends on Phase 2 — cards must exist in JSON before generating images
- **Phase 4 (Polish)**: Depends on Phase 2 — can run in parallel with Phase 3

### Within Phase 2

Tasks T002–T006 all edit the same file (`contracts.json`) so they must be done sequentially, but they are independent logical units that can be committed individually. T007 (test run) must follow all card additions.

### Parallel Opportunities

- T010 (doc update) can run in parallel with T008–T009 (card image generation)
- Within Phase 2, card additions are sequential (same file) but could be batched into a single edit

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2)

1. Update test assertion (T001)
2. Add all 15 cards to contracts.json (T002–T006)
3. Run tests (T007) — **STOP and VALIDATE**
4. Cards are playable immediately even without generated images

### Full Delivery

5. Generate card images (T008–T009)
6. Update analysis doc (T010)
7. All done — 75-card pool with images and documentation

---

## Notes

- All 15 cards use only existing `ContractCard` fields — no Pydantic model changes needed
- Card costs and VP values are from `specs/039-tier1-quest-expansion/data-model.md`
- The `contracts.json` file is under `src/config/` (the `src/` prefix matters for test paths)
- Card image generation uses Pillow, not Arcade — it runs independently of the game client
