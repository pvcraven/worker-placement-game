# Tasks: Resource Choice Board Space ("The Jam Session")

**Input**: Design documents from `specs/022-resource-choice-building/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not explicitly requested in feature specification — test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed — existing project with established structure.

*(No tasks — project already initialized)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add `reward_choice` support to models and config loading so permanent spaces can offer resource choices.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T001 [P] Add optional `reward_choice: ResourceChoiceReward | None = None` field to `ActionSpaceConfig` in `server/models/config.py`
- [X] T002 [P] Add optional `reward_choice: ResourceChoiceReward | None = None` field to `ActionSpace` in `server/models/game.py`
- [X] T003 Propagate `reward_choice` from `ActionSpaceConfig` to `ActionSpace` when building action spaces in `server/config_loader.py`

**Checkpoint**: Models and config loading now support `reward_choice` on permanent spaces.

---

## Phase 3: User Story 1 — Place Worker on Resource Choice Space (Priority: P1) MVP

**Goal**: A player places a worker on "The Jam Session" and is presented with a choice of 1 drummer, 1 singer, or 1 guitarist + 1 bassist. Selecting an option grants those resources.

**Independent Test**: Place a worker on The Jam Session, select each of the three options in separate tests, verify correct resources are added to the player's supply and turn advances.

### Implementation for User Story 1

- [X] T004 [US1] Add `reward_choice` handling for permanent spaces in `handle_place_worker` in `server/game_engine.py` — after the building `visitor_reward_choice` block, add check for `space.reward_choice` that sends a `ResourceChoicePromptResponse`
- [X] T005 [US1] Add `reward_choice` handling in `_resolve_copied_space_rewards` in `server/game_engine.py` for copy mechanics (Shadow Studio, copy intrigue cards)
- [X] T006 [US1] Add `reward_choice` handling in `handle_reassign_worker` in `server/game_engine.py` for backstage reassignment flow
- [X] T007 [US1] Add "The Jam Session" permanent space entry to `config/board.json` — insert between `rhythm_pit` and `fastpass` with `reward_choice` bundle config (3 options: 1 drummer, 1 singer, 1 guitarist + 1 bassist)
- [X] T008 [US1] Generate card image for "The Jam Session" using `card-generator/generate_cards.py` — show space name and resource choice icons (white=drummer, purple=singer, orange=guitarist, black=bassist)

**Checkpoint**: The Jam Session is fully functional — player can place worker, choose resources, and turn advances.

---

## Phase 4: User Story 2 — Space Occupancy Rules (Priority: P1)

**Goal**: The Jam Session follows standard board rules: one worker per round, space freed at round end.

**Independent Test**: Place a worker on the space, verify a second player cannot place on it. Verify the space is freed at round end.

### Implementation for User Story 2

*(No additional tasks — standard occupancy is inherited from existing permanent space behavior. The `slots: 1` config in board.json and existing `occupied_by` checking handle this automatically.)*

**Checkpoint**: Occupancy rules work identically to other permanent spaces.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation across all flows.

- [X] T009 Run full test suite (`cd src && pytest`) and fix any failures
- [X] T010 Run linter (`cd src && ruff check .`) and fix any issues
- [X] T011 Verify board layout — confirm The Jam Session appears between The Rhythm Pit and Fastpass in the client UI
- [X] T012 Verify copy/reassignment compatibility — test that Shadow Studio copy and backstage reassignment both trigger the resource choice dialog correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped — existing project
- **Foundational (Phase 2)**: No dependencies — can start immediately. BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 (model fields must exist before game engine can reference them)
- **User Story 2 (Phase 4)**: No additional tasks — inherited behavior
- **Polish (Phase 5)**: Depends on Phase 3 completion

### Within Phase 2 (Foundational)

- T001 and T002 can run in parallel (different files)
- T003 depends on T001 and T002 (needs both model fields to exist)

### Within Phase 3 (User Story 1)

- T004, T005, T006 are sequential within game_engine.py (same file)
- T007 can run in parallel with T004-T006 (different file: board.json)
- T008 can run in parallel with T004-T006 (different file: card generator)

### Parallel Opportunities

```bash
# Phase 2 — parallel model changes:
Task T001: "Add reward_choice to ActionSpaceConfig in server/models/config.py"
Task T002: "Add reward_choice to ActionSpace in server/models/game.py"

# Phase 3 — parallel with game engine work:
Task T007: "Add board.json entry" (parallel with T004-T006)
Task T008: "Generate card image" (parallel with T004-T006)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (model fields + config loader)
2. Complete Phase 3: User Story 1 (game engine handlers + board.json + card image)
3. **STOP and VALIDATE**: Test placing a worker on The Jam Session, select each option
4. Run tests and linter

### Incremental Delivery

1. Add model fields → Config loading works
2. Add game engine handlers → Server processes resource choices on permanent spaces
3. Add board.json entry → Space appears in game
4. Generate card image → Space has visual representation
5. Each step adds value without breaking existing functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 requires no implementation — standard permanent space occupancy rules apply automatically
- The `bundle` choice type is already implemented and tested (used by intrigue cards)
- Cancel/unwind is handled by existing `pending_placement` infrastructure
- Total: 12 tasks across 5 phases
