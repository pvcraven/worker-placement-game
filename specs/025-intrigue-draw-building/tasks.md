# Tasks: Intrigue Draw Building ("Whisper Room")

**Input**: Design documents from `specs/025-intrigue-draw-building/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — test tasks omitted. Existing test suite validates via `pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Add building configuration entry

- [X] T001 Add "Whisper Room" building entry to config/buildings.json with id "building_024", name "Whisper Room", description "A hidden back room where label insiders trade secrets and confidential intel — two pieces of valuable information for every visitor.", cost_coins 4, visitor_reward all zeros, visitor_reward_special "draw_intrigue_2", owner_bonus all zeros, owner_bonus_vp 2, no accumulation

---

## Phase 2: Foundational

**Purpose**: No foundational tasks needed — all existing infrastructure (BuildingTile model, WorkerPlacedResponse, card generator) already supports the new building. The `visitor_reward_special` field is `str | None` and accepts any string value.

**Checkpoint**: No blocking prerequisites — user story implementation can begin immediately after Phase 1.

---

## Phase 3: User Story 1 - Draw Two Intrigue Cards from Building (Priority: P1) MVP

**Goal**: When a player places a worker on the Whisper Room, they draw 2 intrigue cards from the deck.

**Independent Test**: Place a worker on the Whisper Room in a game. Verify 2 intrigue cards appear in the Intrigue tab and the game log shows the correct message.

### Implementation for User Story 1

- [X] T002 [US1] Handle "draw_intrigue_2" visitor_reward_special in handle_place_worker() in server/game_engine.py (~line 1531). Pop up to 2 cards from state.board.intrigue_deck, append each to player.intrigue_hand. Add reward_dict["intrigue_cards_drawn"] = len(drawn_cards) and reward_dict["drawn_intrigue_cards"] = [c.model_dump() for c in drawn_cards]. Follow the pattern of the existing "draw_intrigue" case but loop for 2 cards.

- [X] T003 [US1] Handle "draw_intrigue_2" in _resolve_copied_space_rewards() in server/game_engine.py (~line 1050). Same logic as T002 — pop up to 2 intrigue cards, append to player hand, add to reward_dict. This handles Shadow Studio copying the Whisper Room.

- [X] T004 [US1] Handle "draw_intrigue_2" in the worker reassignment handler in server/game_engine.py (~line 3484). Same logic — pop up to 2 intrigue cards, append to player hand. Add reward notification to the reassignment reward dict if one exists.

- [X] T005 [US1] Handle "drawn_intrigue_cards" (plural, list) in _on_worker_placed() in client/views/game_view.py. After the existing check for reward.get("intrigue_cards_drawn"), add handling for reward.get("drawn_intrigue_cards"): if the placing player is the local player, extend p["intrigue_hand"] with the list of card dicts. Update the game log to say "Player A drew N intrigue cards" where N is the drawn count. Also update intrigue_hand_count for all players.

**Checkpoint**: At this point, the Whisper Room building should be fully functional — visiting draws 2 intrigue cards, game log shows the correct message, cards appear in the intrigue tab.

---

## Phase 4: User Story 2 - Building Card Image with Two Intrigue Icons (Priority: P2)

**Goal**: The Whisper Room card image shows two side-by-side intrigue card icons.

**Independent Test**: Run the card generator and visually confirm the Whisper Room card displays two intrigue card icons.

### Implementation for User Story 2

- [X] T006 [US2] Add "draw_intrigue_2" case to _draw_special_icon() in card-generator/generate_cards.py (~line 423). Draw two intrigue card icons side-by-side: call _draw_intrigue_card_icon() twice with horizontal offsets (e.g., cx - icon_w//2 - gap//2 and cx + icon_w//2 + gap//2 where icon_w is _CARD_ICON_W and gap is ~8px).

- [X] T007 [US2] Regenerate building card images by running the card generator: `cd card-generator && python generate_cards.py`. Verify the Whisper Room card PNG is created at client/assets/card_images/buildings/building_024.png with two intrigue icons visible.

**Checkpoint**: The Whisper Room card image is generated with two visible intrigue card icons.

---

## Phase 5: User Story 3 - Building Owner Receives Bonus (Priority: P3)

**Goal**: When a non-owner visits the Whisper Room, the owner receives 2 VP.

**Independent Test**: In a 2+ player game, have Player B visit Player A's Whisper Room. Verify Player A gets 2 VP.

### Implementation for User Story 3

No implementation tasks needed — the owner bonus is handled entirely by the existing `owner_bonus_vp: 2` field in the BuildingTile config (T001). The server's existing owner bonus handler at ~line 1598 of game_engine.py already reads `tile.owner_bonus_vp` and grants VP to the owner. This story is satisfied by the config entry alone.

**Checkpoint**: Owner bonus is already functional from the Phase 1 config entry.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T008 Run existing test suite: `cd src && pytest` to verify no regressions
- [X] T009 Run linting: `cd src && ruff check .` to verify code quality
- [ ] T010 Manual test: start a 2-player game, purchase the Whisper Room, place a worker on it, verify 2 intrigue cards drawn, verify game log message, verify owner bonus on opponent visit
- [ ] T011 Manual test edge case: test with nearly empty intrigue deck (1 card remaining), verify partial draw works without error

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 3)**: Depends on T001 (config entry must exist for server to find the building)
- **US2 (Phase 4)**: Depends on T001 (config entry must exist for card generator to read)
- **US3 (Phase 5)**: No implementation needed — satisfied by T001 config
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 1 only. No dependencies on other stories.
- **User Story 2 (P2)**: Depends on Phase 1 only. Independent of US1 (card image is separate from game logic).
- **User Story 3 (P3)**: Fully satisfied by Phase 1 config. No additional work needed.

### Within User Story 1

- T002, T003, T004 all modify server/game_engine.py — must be sequential
- T005 modifies client/views/game_view.py — can run in parallel with T003/T004 but depends on T002 for understanding the reward dict structure

### Parallel Opportunities

- T006-T007 (US2 card image) can run in parallel with T002-T005 (US1 server/client logic) since they touch completely different files

---

## Parallel Example: US1 + US2

```text
# After T001 (config) is complete, these can run in parallel:

# Stream A (US1 - game logic):
T002 → T003 → T004 → T005

# Stream B (US2 - card image):
T006 → T007
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Add config entry (T001)
2. Complete Phase 3: Server + client handling (T002-T005)
3. **STOP and VALIDATE**: Place worker on Whisper Room, verify 2 intrigue cards drawn
4. Building is fully functional at this point

### Incremental Delivery

1. T001 → Config entry → Building appears in game (but no special reward handling yet)
2. T002-T005 → Game logic → Building fully functional (MVP!)
3. T006-T007 → Card image → Visual polish complete
4. T008-T011 → Testing and validation → Release ready

---

## Notes

- US3 (owner bonus) requires zero implementation — the `owner_bonus_vp` field in config is handled by existing server code
- The `draw_intrigue_2` special value is new but follows the exact pattern of `draw_intrigue` — just loops for 2 cards
- Edge case handling (deck depletion) is built into the loop: `for _ in range(2): if deck: pop()`
- Total: 11 tasks (1 config, 4 game logic, 2 card image, 4 validation)
