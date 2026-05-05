# Implementation Plan: Resource Choice Board Space ("The Jam Session")

**Branch**: `022-resource-choice-building` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/022-resource-choice-building/spec.md`

## Summary

Add a new permanent board space called "The Jam Session" that offers a bundle-style resource choice: 1 drummer, 1 singer, or 1 guitarist + 1 bassist. The space is positioned between The Rhythm Pit and Fastpass. This is primarily a config change (new entry in `board.json`) with a card image generation step and a board layout adjustment.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source), websockets, Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state; JSON configuration in `config/`
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (Arcade client)
**Project Type**: Multiplayer board game (client/server)
**Performance Goals**: Choice dialog appears instantly on placement
**Constraints**: Must use existing `bundle` choice type already supported by the engine
**Scale/Scope**: Single new board space added to `board.json`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | N/A | No new rendering code; existing board renderer handles permanent spaces |
| II. Pydantic Data Modeling | PASS | Space uses existing Pydantic models (`ActionSpace`, resource choice types) |
| III. Client-Server Separation | PASS | Config-only change; server handles resource choice via existing `bundle` handler |
| IV. Test-Driven Game Logic | PASS | Will verify with existing test suite; no new game logic needed |
| V. Simplicity First | PASS | Config entry only — no new code paths, no new abstractions |
| VI. Server-Authoritative Message Protocol | PASS | Uses existing `ResourceChoicePromptResponse` / `ResourceChoiceResolvedResponse` |
| VII. Config-Driven Game Content | PASS | New space added as JSON entry in `board.json` with `reward_choice` field |
| VIII. Pending State for Deferred Actions | PASS | Existing `pending_resource_choice` handles the bundle selection lifecycle |
| IX. Cancel/Unwind Reversibility | PASS | Existing `pending_placement` + `_unwind_placement()` handles cancel |
| X. Post-Action Turn Flow | PASS | Existing flow: place worker → resource choice prompt → resolve → quest check → advance |

All gates pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/022-resource-choice-building/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 (minimal — no unknowns)
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (files to modify)

```text
config/
  board.json               # Add new permanent space entry for "The Jam Session"

client/
  ui/board_renderer.py     # Adjust layout: insert space between Rhythm Pit and Fastpass

card-generator/
  generate_cards.py        # Generate card image for The Jam Session (if needed)
```

**Structure Decision**: No new files or directories. This feature modifies existing config and adjusts board layout only.

## Implementation Approach

### How the `bundle` choice type works (existing)

The game already supports bundle-style resource choices. When a permanent space has a `reward_choice` field with `choice_type: "bundle"`, the server:
1. Grants any base `reward` resources
2. Sends a `ResourceChoicePromptResponse` with the bundles list
3. Player selects a bundle → `handle_resource_choice` grants it
4. Turn advances via `_check_quest_completion` → `_advance_turn`

The Jam Session needs a `reward_choice` with three bundles — no new server code.

### Board layout adjustment

The permanent spaces are rendered by `BoardRenderer` which positions them in a column. Adding a new space between Rhythm Pit and Fastpass requires:
1. Adding the new entry in `board.json` between `rhythm_pit` and `fastpass`
2. The board renderer already dynamically positions spaces from the config list, so ordering in the JSON determines visual order

### Card image

The card-generator creates board space card images showing the space name and reward icons. The Jam Session card should show the three bundle options using standard resource icon colors (white=drummer, purple=singer, orange=guitarist, black=bassist).

## Changes Required

### 1. `server/models/config.py` — Add `reward_choice` to `ActionSpaceConfig`

Add optional `reward_choice: ResourceChoiceReward | None = None` field to `ActionSpaceConfig` (line 86).

### 2. `server/models/game.py` — Add `reward_choice` to `ActionSpace`

Add optional `reward_choice: ResourceChoiceReward | None = None` field to `ActionSpace` (after line 100). Import `ResourceChoiceReward` from `shared.card_models`.

### 3. `server/config_loader.py` — Propagate `reward_choice` when building ActionSpaces

When constructing `ActionSpace` from `ActionSpaceConfig`, copy the `reward_choice` field through.

### 4. `server/game_engine.py` — Handle `reward_choice` on permanent spaces

In `handle_place_worker`, after the building `visitor_reward_choice` block (~line 1688), add:

```python
if space.reward_choice:
    state.pending_placement = _pending
    await _send_resource_choice_prompt(
        server, state, player, space.reward_choice,
        "permanent", space.name,
    )
    return
```

Similarly add handling in:
- `_resolve_copied_space_rewards` (copy flow)
- `handle_reassign_worker` (reassignment flow)

No cost affordability check needed (The Jam Session is free).

### 5. `config/board.json` — Add new permanent space

Insert between `rhythm_pit` and `fastpass`:

```json
{
  "space_id": "jam_session",
  "name": "The Jam Session",
  "space_type": "permanent",
  "reward": {"guitarists": 0, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
  "reward_choice": {
    "choice_type": "bundle",
    "bundles": [
      {"label": "1 Drummer", "resources": {"drummers": 1}},
      {"label": "1 Singer", "resources": {"singers": 1}},
      {"label": "1 Guitarist + 1 Bassist", "resources": {"guitarists": 1, "bass_players": 1}}
    ]
  },
  "slots": 1
}
```

### 6. Card image generation

Generate a card image for The Jam Session using the existing card generator, showing the space name and resource choice icons (white=drummer, purple=singer, orange=guitarist + black=bassist).

### 7. Board layout verification

Verify the board renderer correctly positions the new space. The renderer reads `permanent_spaces` from `board.json` in order, so placing the entry between `rhythm_pit` and `fastpass` should produce the correct visual layout.

## Risk Assessment

**Low risk**:
- The `bundle` choice type is already implemented and tested (used by intrigue cards)
- The board renderer dynamically positions permanent spaces from config order
- Cancel/unwind is handled by existing `pending_placement` infrastructure
- New model field follows Constitution VII (config-driven)

**Medium risk** area: The `_send_resource_choice_prompt` function and `handle_resource_choice` resolution path need to work with a non-building source type. Need to verify the resolution path doesn't assume building_tile exists.
