# Tasks: Resource Bar Revamp

**Input**: Design documents from `specs/017-resource-bar-revamp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the output directory for icon assets

- [ ] T001 Create `client/assets/card_images/icons/` directory for resource and card icon PNGs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks needed — all prerequisites (card generator, resource bar, marker PNGs) already exist in the codebase.

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Generate Resource Icon PNGs (Priority: P1) MVP

**Goal**: Card generator produces 5 resource icon PNGs (guitarist, bass_player, drummer, singer, coin) and 2 card icon PNGs (quest_icon, intrigue_icon) in `client/assets/card_images/icons/`.

**Independent Test**: Run `python generate_cards.py --icons-only` and verify 7 PNG files appear in the icons directory with correct colors and shapes.

### Implementation for User Story 1

- [ ] T002 [US1] Add `generate_resource_icons()` function to `card-generator/generate_cards.py` that creates 72x72 transparent PNGs for each resource type (guitarist=orange square, bass_player=black square, drummer=purple square, singer=white square, coin=gold circle) with black outlines, saving to `client/assets/card_images/icons/`
- [ ] T003 [US1] Add `generate_card_icon_pngs()` function to `card-generator/generate_cards.py` that creates standalone quest_icon.png (84x114, dark red back, "Q") and intrigue_icon.png (84x114, dark gray back, "I") with transparent backgrounds, reusing the existing `_draw_card_icon()` helper, saving to `client/assets/card_images/icons/`
- [ ] T004 [US1] Add `--icons-only` CLI flag to `card-generator/generate_cards.py` that runs only `generate_resource_icons()` and `generate_card_icon_pngs()`, and wire both functions into the default full generation flow
- [ ] T005 [US1] Run the generator and verify all 7 PNGs are created with correct visuals in `client/assets/card_images/icons/`

**Checkpoint**: 7 icon PNGs exist and look correct. Resource bar changes can proceed.

---

## Phase 4: User Story 2 - Restyle Bottom Panel Background and Text (Priority: P2)

**Goal**: Change the resource bar background from dark (25, 25, 35) to parchment (235, 220, 185) and switch text from white/Tahoma to dark brown (60, 40, 20)/Tahoma.

**Independent Test**: Launch the game and verify the bottom panel has a warm parchment background with dark brown text.

### Implementation for User Story 2

- [ ] T006 [US2] Update the background color in `client/ui/resource_bar.py` `draw()` method from `(25, 25, 35)` to `(235, 220, 185)` (parchment)
- [ ] T007 [US2] Update all text color references in `client/ui/resource_bar.py` from `arcade.color.WHITE` to `(60, 40, 20)` (card text brown)
- [ ] T008 [US2] Visually verify the restyled panel in-game — parchment background, dark brown text, readable at various window sizes

**Checkpoint**: Bottom panel has card-consistent visual style.

---

## Phase 5: User Story 3 - Display Resource Sprites Instead of Drawn Squares (Priority: P3)

**Goal**: Replace drawn colored rectangles in the bottom row with sprite images from the generated PNGs, using a cached SpriteList.

**Independent Test**: Launch the game and verify colored resource icon sprites appear instead of plain rectangles, with no flicker on resize.

### Implementation for User Story 3

- [ ] T009 [US3] Add a `_resource_sprite_list: arcade.SpriteList | None` field and dirty-flag tracking to `ResourceBar.__init__()` in `client/ui/resource_bar.py`
- [ ] T010 [US3] Add a `_build_resource_sprites()` method to `ResourceBar` in `client/ui/resource_bar.py` that loads resource icon PNGs from `client/assets/card_images/icons/`, positions them where the colored swatches were, and scales them to fit the bar height. Include fallback to `arcade.draw_rect_filled` if a PNG is missing.
- [ ] T011 [US3] Update `ResourceBar.draw()` in `client/ui/resource_bar.py` to call `_build_resource_sprites()` only when data or geometry changes (dirty flag), then draw the SpriteList instead of the per-resource `arcade.draw_rect_filled` calls
- [ ] T012 [US3] Visually verify resource sprites render correctly, scale with window resize, and don't flicker

**Checkpoint**: Resource icons are sprites from PNGs with cached SpriteList.

---

## Phase 6: User Story 4 - Use Card Icons for Quest and Intrigue Counts (Priority: P4)

**Goal**: Show quest card icon (Q) next to quest open/done counts and intrigue card icon (I) next to intrigue count in the top row.

**Independent Test**: Launch the game and verify miniature Q and I card icons appear beside their respective counts.

### Implementation for User Story 4

- [ ] T013 [US4] Extend `_build_resource_sprites()` (or add a separate sprite-building step) in `client/ui/resource_bar.py` to load `quest_icon.png` and `intrigue_icon.png` from `client/assets/card_images/icons/` and position them in the top row next to the quest and intrigue count text
- [ ] T014 [US4] Update the top row rendering in `ResourceBar.draw()` in `client/ui/resource_bar.py` to replace the "Intrigue:", "Quests Open:", and "Quests Done:" text prefixes with the card icon sprites followed by count text
- [ ] T015 [US4] Visually verify card icons appear correctly sized and positioned next to their counts

**Checkpoint**: Quest and intrigue counts show card icons.

---

## Phase 7: User Story 5 - Show Player Marker Next to Workers Left (Priority: P5)

**Goal**: Display the player's colored worker marker sprite next to the "Workers left" count.

**Independent Test**: Launch the game and verify a colored worker marker matching the player's color appears beside the workers-left number.

### Implementation for User Story 5

- [ ] T016 [US5] Add `player_color: str` parameter to `ResourceBar.draw()` in `client/ui/resource_bar.py` (or pass via `update_resources()`)
- [ ] T017 [US5] Load the player's worker marker PNG from `client/assets/card_images/markers/worker_{color}.png` and add it to the SpriteList, positioned next to the workers-left count text in `client/ui/resource_bar.py`
- [ ] T018 [US5] Update `client/views/game_view.py` to pass the player's color name to the resource bar's draw or update method
- [ ] T019 [US5] Visually verify the worker marker appears correctly colored and positioned

**Checkpoint**: Worker marker shows player identity in the resource bar.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T020 Run `black --target-version py312` on all modified files
- [ ] T021 Run `cd src && ruff check .` and fix any issues
- [ ] T022 Full visual playtest: verify all 5 user stories work together — parchment background, resource sprites, card icons, worker marker, proper scaling across window sizes
- [ ] T023 Run quickstart.md validation steps (fallback test with missing PNG)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — create directory immediately
- **User Story 1 (Phase 3)**: Depends on Phase 1 — generates PNGs into the new directory
- **User Story 2 (Phase 4)**: No dependency on US1 — can run in parallel with Phase 3
- **User Story 3 (Phase 5)**: Depends on US1 (needs PNGs) and US2 (background should be parchment first)
- **User Story 4 (Phase 6)**: Depends on US1 (needs card icon PNGs) and US3 (extends the SpriteList pattern)
- **User Story 5 (Phase 7)**: Depends on US3 (extends the SpriteList pattern)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Independent — card generator changes only
- **US2 (P2)**: Independent — resource_bar.py color/font changes only
- **US3 (P3)**: Depends on US1 (PNGs must exist) + US2 (background context)
- **US4 (P4)**: Depends on US1 (card icon PNGs) + US3 (SpriteList infrastructure)
- **US5 (P5)**: Depends on US3 (SpriteList infrastructure)

### Within Each User Story

- Implementation tasks are sequential within each story
- Visual verification is the final task in each story

### Parallel Opportunities

- US1 and US2 can run in parallel (different files: generate_cards.py vs resource_bar.py)
- T002 and T003 within US1 can run in parallel (independent functions in the same file)

---

## Parallel Example: US1 + US2

```bash
# These can run in parallel since they modify different files:
Task T002-T005: Generate icon PNGs (card-generator/generate_cards.py)
Task T006-T008: Restyle background and text (client/ui/resource_bar.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Create icons directory
2. Complete US1: Generate all icon PNGs
3. Complete US2: Restyle panel background and text
4. **STOP and VALIDATE**: Panel looks like parchment, icons exist

### Incremental Delivery

1. US1 + US2 → Parchment panel with dark text (visual foundation)
2. US3 → Resource sprites replace drawn squares (core upgrade)
3. US4 → Card icons for quest/intrigue counts (polish)
4. US5 → Worker marker for player identity (polish)
5. Each story adds visual polish without breaking previous work

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All icon PNGs use 2x resolution and are scaled 0.5x in the client
- Parchment color: (235, 220, 185), Text color: (60, 40, 20)
- Commit after each completed user story
