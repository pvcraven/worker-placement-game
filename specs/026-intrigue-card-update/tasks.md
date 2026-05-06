# Tasks: Intrigue Card Update

**Input**: Design documents from `specs/026-intrigue-card-update/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted. Existing test suite validates via `pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Add all 14 new intrigue card entries to configuration

- [ ] T001 Add 14 new intrigue card entries to config/intrigue.json (IDs intrigue_055 through intrigue_068). Use exact names, descriptions, effect_types, and effect_values from data-model.md: 4 no_effect cards (intrigue_055–058), 4 draw_intrigue cards with count:1 (intrigue_059–062), 2 reset_quests cards (intrigue_063–064), 2 reset_buildings cards (intrigue_065–066), 2 first_player_marker cards (intrigue_067–068). All have effect_target "self".

---

## Phase 2: Foundational

**Purpose**: Add building discard pile infrastructure and completed-quest safety filter. These are global mechanics that all user stories (and existing code) depend on.

- [ ] T002 Add `building_discard: list[BuildingTile] = Field(default_factory=list)` field to BoardState in server/models/game.py (~line 121, near quest_discard)

- [ ] T003 Add `_draw_from_building_deck(state)` helper function in server/game_engine.py (~line 82, after existing `_draw_from_quest_deck()`). Mirror the quest helper pattern: if building_deck is empty but building_discard has cards, move discard to deck, clear discard, shuffle with `random.shuffle()`, then pop(0) from deck. Return the drawn BuildingTile or None.

- [ ] T004 Add completed-quest exclusion filter to `_draw_from_quest_deck()` in server/game_engine.py (~line 75). Before reshuffling quest_discard into quest_deck, collect all completed quest IDs from all players' `completed_contracts` lists, then filter quest_discard to exclude any card whose id is in that set. Pass `state` (not just `state.board`) to the function so it can access players.

- [ ] T005 Update existing building purchase/refill logic in server/game_engine.py to use `_draw_from_building_deck()` and `building_discard`. At ~line 3116 where buildings are removed from face_up after purchase: when a face-up building slot needs refilling, call `_draw_from_building_deck(state)` instead of directly popping from `state.board.building_deck`. Do NOT add discarding here (purchased buildings go to the player, not to discard).

**Checkpoint**: Building discard infrastructure is ready. Quest reshuffle excludes completed quests. All existing building/quest draws support reshuffle from discard piles.

---

## Phase 3: User Story 1 - Play "Do Nothing" Intrigue Cards (Priority: P1) MVP

**Goal**: When a player plays a no-effect intrigue card, it is consumed with no game state changes.

**Independent Test**: Play a no-effect card from hand. Verify card is removed, game log shows it was played, no other changes occur.

### Implementation for User Story 1

- [ ] T006 [US1] Add "no_effect" elif branch in `_resolve_intrigue_effect()` in server/game_engine.py (~line 2466, before the final else). Return `{"type": "no_effect", "details": "No effect"}`. No state changes needed.

- [ ] T007 [P] [US1] Add "no_effect" handling in `_intrigue_effect_summary()` in card-generator/generate_cards.py (~line 1180). Return "No Effect" as the summary text. Add "no_effect" case in `_draw_intrigue_effect_icons()` (~line 1314) — draw a simple "—" or shrug text centered in the icon area.

**Checkpoint**: No-effect cards can be played. Card images show "No Effect" text.

---

## Phase 4: User Story 2 - Play "Draw 1 Intrigue" Cards (Priority: P2)

**Goal**: When a player plays a draw-1-intrigue card, they draw 1 intrigue card from the deck.

**Independent Test**: Play a draw-1-intrigue card. Verify hand size stays the same (1 consumed + 1 drawn), game log shows the draw.

### Implementation for User Story 2

No server implementation tasks needed — the existing `draw_intrigue` handler at game_engine.py:2403 already handles `effect_value: {"count": 1}`. The card image generator already renders draw_intrigue effects with count-based icon display.

**Checkpoint**: Draw-1-intrigue cards work out of the box from config entries alone. Verify during manual testing.

---

## Phase 5: User Story 3 - Play "Reset Quests" Cards (Priority: P3)

**Goal**: When a player plays a reset-quests card, all face-up quests are discarded and new ones drawn from the deck.

**Independent Test**: Play a reset-quests card. Verify face-up quests are all replaced, game log shows "quests refreshed".

### Implementation for User Story 3

- [ ] T008 [US3] Add "reset_quests" elif branch in `_resolve_intrigue_effect()` in server/game_engine.py (~line 2466). Logic: extend `state.board.quest_discard` with `state.board.face_up_quests`, clear `state.board.face_up_quests`, loop `FACE_UP_QUEST_COUNT` times calling `_draw_from_quest_deck(state)` and append non-None results to `state.board.face_up_quests`. Return `{"type": "reset_quests", "details": "Quests refreshed", "face_up_quests": [q.model_dump() for q in state.board.face_up_quests]}`.

- [ ] T009 [US3] Add broadcast of `FaceUpQuestsUpdatedResponse` in `handle_place_worker_backstage()` in server/game_engine.py (~line 2278). After the effect is resolved and the main `WorkerPlacedBackstageResponse` is broadcast, check if `effect_details.get("type") == "reset_quests"` and if so, broadcast `FaceUpQuestsUpdatedResponse(action="face_up_quests_updated", face_up_quests=[q.model_dump() for q in state.board.face_up_quests])` to all players.

- [ ] T010 [P] [US3] Add "reset_quests" handling in `_intrigue_effect_summary()` in card-generator/generate_cards.py (~line 1180). Return "Refresh Quests" as summary. Add "reset_quests" case in `_draw_intrigue_effect_icons()` (~line 1314) — draw a quest card icon with a circular refresh arrow overlay.

**Checkpoint**: Reset-quests cards discard face-up quests and draw new ones. All clients see the update.

---

## Phase 6: User Story 4 - Play "Reset Buildings" Cards (Priority: P4)

**Goal**: When a player plays a reset-buildings card, all face-up buildings are discarded and new ones drawn from the deck.

**Independent Test**: Play a reset-buildings card. Verify face-up buildings are all replaced, game log shows "buildings refreshed".

### Implementation for User Story 4

- [ ] T011 [US4] Add "reset_buildings" elif branch in `_resolve_intrigue_effect()` in server/game_engine.py (~line 2466). Logic: extend `state.board.building_discard` with `state.board.face_up_buildings`, clear `state.board.face_up_buildings`, loop `FACE_UP_BUILDING_COUNT` times calling `_draw_from_building_deck(state)` and append non-None results to `state.board.face_up_buildings`. Return `{"type": "reset_buildings", "details": "Buildings refreshed"}`.

- [ ] T012 [US4] Add broadcast of `BuildingMarketUpdateResponse` in `handle_place_worker_backstage()` in server/game_engine.py (~line 2278, near the T009 reset_quests broadcast). Check if `effect_details.get("type") == "reset_buildings"` and if so, call `_broadcast_building_market(state, server)` to send the updated building display to all players.

- [ ] T013 [P] [US4] Add "reset_buildings" handling in `_intrigue_effect_summary()` in card-generator/generate_cards.py (~line 1180). Return "Refresh Buildings" as summary. Add "reset_buildings" case in `_draw_intrigue_effect_icons()` (~line 1314) — draw a building icon with a circular refresh arrow overlay.

**Checkpoint**: Reset-buildings cards discard face-up buildings and draw new ones. All clients see the update.

---

## Phase 7: User Story 5 - Play "First Player Marker" Cards (Priority: P5)

**Goal**: When a player plays a first-player-marker card, they get the first-player marker for next round.

**Independent Test**: Play a first-player-marker card. Verify the player goes first next round.

### Implementation for User Story 5

- [ ] T014 [US5] Add "first_player_marker" elif branch in `_resolve_intrigue_effect()` in server/game_engine.py (~line 2466). Logic: loop all players setting `p.has_first_player_marker = False`, then set `player.has_first_player_marker = True` and `state.board.first_player_id = player.player_id`. Return `{"type": "first_player_marker", "details": f"{player.name} will go first next round"}`.

- [ ] T015 [P] [US5] Add "first_player_marker" handling in `_intrigue_effect_summary()` in card-generator/generate_cards.py (~line 1180). Return "Go First" as summary. Add "first_player_marker" case in `_draw_intrigue_effect_icons()` (~line 1314) — draw a "1st" badge or star icon.

**Checkpoint**: First-player-marker cards set turn order for next round.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T016 Regenerate intrigue card images by running `cd card-generator && python generate_cards.py`. Verify all 14 new card PNGs are created in client/assets/card_images/intrigue/ with appropriate effect icons.
- [ ] T017 Run existing test suite: `cd src && pytest` to verify no regressions
- [ ] T018 Run linting: `cd src && ruff check .` to verify code quality
- [ ] T019 Manual test: start a 2-player game, draw intrigue cards, play each of the 5 new card types, verify effects and game log per quickstart.md
- [ ] T020 Manual test: verify deck reshuffle — play reset-quests when quest deck is low, verify discard pile reshuffles (excluding completed quests)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 (config must exist for tests); T002-T005 are sequential (same file)
- **US1 (Phase 3)**: Depends on T001 (config). T006 depends on Phase 2 (same file). T007 is independent (different file).
- **US2 (Phase 4)**: Depends on T001 only — no implementation tasks
- **US3 (Phase 5)**: Depends on Phase 2 (needs _draw_from_quest_deck fix). T008-T009 sequential (same file). T010 parallel (different file).
- **US4 (Phase 6)**: Depends on Phase 2 (needs _draw_from_building_deck). T011-T012 sequential (same file). T013 parallel (different file).
- **US5 (Phase 7)**: Depends on T001. T014 sequential with other game_engine tasks. T015 parallel (different file).
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 only. Independent of other stories.
- **US2 (P2)**: Depends on Phase 1 only. Fully independent — zero implementation tasks.
- **US3 (P3)**: Depends on Phase 2 (quest reshuffle). Independent of other stories.
- **US4 (P4)**: Depends on Phase 2 (building discard infrastructure). Independent of other stories.
- **US5 (P5)**: Depends on Phase 1 only. Independent of other stories.

### Within game_engine.py (sequential constraint)

All tasks modifying server/game_engine.py must be sequential:
T003 → T004 → T005 → T006 → T008 → T009 → T011 → T012 → T014

### Parallel Opportunities

- Card image tasks (T007, T010, T013, T015) can all run in parallel with each other AND with game_engine tasks since they modify card-generator/generate_cards.py (different file)
- T002 (models/game.py) can run in parallel with T001 (config/intrigue.json)

---

## Parallel Example: Card Images + Server Logic

```text
# After T001 (config) and T002 (model) are complete:

# Stream A (server logic — sequential, same file):
T003 → T004 → T005 → T006 → T008 → T009 → T011 → T012 → T014

# Stream B (card images — parallel with Stream A, different file):
T007 + T010 + T013 + T015 (all modify generate_cards.py — sequential within stream)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Add config entries (T001)
2. Complete Phase 2: Building discard + quest filter (T002-T005)
3. Complete Phase 3: No-effect handler (T006-T007)
4. **STOP and VALIDATE**: Play a no-effect card, verify it works
5. Building is fully functional at this point

### Incremental Delivery

1. T001 → Config entries → All 14 cards appear in deck (but new effect types unhandled)
2. T002-T005 → Foundational → Building discard and quest filter ready
3. T006-T007 → US1 → No-effect cards playable (MVP!)
4. (US2 already works from T001)
5. T008-T010 → US3 → Reset-quests cards work
6. T011-T013 → US4 → Reset-buildings cards work
7. T014-T015 → US5 → First-player-marker cards work
8. T016-T020 → Polish → Card images regenerated, tests pass

---

## Notes

- US2 (draw-1-intrigue) requires zero implementation — the existing `draw_intrigue` handler with `count: 1` already works
- All 9 game_engine.py tasks are sequential since they modify the same file
- The 4 card image tasks are independent of server logic and can run as a parallel stream
- Total: 20 tasks (1 config, 4 foundational, 1 US1 server + 1 US1 image, 0 US2, 2 US3 server + 1 US3 image, 2 US4 server + 1 US4 image, 1 US5 server + 1 US5 image, 5 polish)
