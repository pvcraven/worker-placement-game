# Implementation Plan: Resource Choice Rewards

**Branch**: `012-resource-choice-rewards` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/012-resource-choice-rewards/spec.md`

## Summary

Extend the reward system so buildings and intrigue cards can require players to choose resources instead of always granting fixed amounts. Adds a shared `ResourceChoiceReward` config model, a prompt/response message pair, a server-side choice resolver, and a client-side dialog. Covers five interaction patterns: pick N from a set, predefined bundles, constrained combo allocation, two-phase exchange, and multi-player sequential picks.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2
**Storage**: In-memory game state (server); JSON configuration files (game content)
**Testing**: pytest + ruff
**Target Platform**: Windows desktop (also Mac/Linux)
**Project Type**: Desktop game (client-server over WebSocket)
**Performance Goals**: Resource choice dialog appears instantly; selection resolves in under 1 frame
**Constraints**: All game logic server-authoritative; client only sends selections
**Scale/Scope**: 2-5 players, single game session, ~10 new config entries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Dialog uses `arcade.gui` (UIManager widgets), same as existing dialogs. No primitive draw calls. |
| II. Pydantic Data Modeling | PASS | New models (`ResourceChoiceReward`, `ResourceBundle`) in `shared/card_models.py`. New messages in `shared/messages.py`. All Pydantic. |
| III. Client-Server Separation | PASS | Choice validation and resource granting in `server/game_engine.py`. Client sends `resource_choice` message, renders prompts from server responses. |
| IV. Test-Driven Game Logic | PASS | pytest tests for choice resolution, validation, edge cases. No Arcade dependency in tests. |
| V. Simplicity First | PASS | Extends existing pending-state + prompt/response pattern (`pending_intrigue_target`, `pending_quest_reward`). Single dialog class with mode switching. No unnecessary abstractions. |

All gates pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/012-resource-choice-rewards/
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # New/modified entities
├── quickstart.md        # Integration test scenarios
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
shared/
├── card_models.py       # MODIFY: Add ResourceBundle, ResourceChoiceReward models
├── messages.py          # MODIFY: Add ResourceChoicePromptResponse, ResourceChoiceRequest, ResourceChoiceResolvedResponse
└── constants.py         # (unchanged)

server/
├── models/
│   └── game.py          # MODIFY: Add pending_resource_choice field to GameState
└── game_engine.py       # MODIFY: Add _resolve_resource_choice(), _send_resource_choice_prompt(), handle_resource_choice()

client/
├── ui/
│   └── dialogs.py       # MODIFY: Add ResourceChoiceDialog class
└── views/
    └── game_view.py     # MODIFY: Add handlers for resource_choice_prompt, resource_choice_resolved

config/
├── buildings.json       # MODIFY: Add 4 new buildings with choice rewards
└── intrigue.json        # MODIFY: Add 2 new intrigue cards with choice rewards

tests/
└── test_resource_choice.py  # NEW: pytest tests for choice resolution
```

**Structure Decision**: No new directories needed. All changes extend existing files following established patterns. One new test file.

## Key Design Decisions

### 1. Single ResourceChoiceReward model for all 5 scenarios

A single config model with a `choice_type` discriminator handles all patterns:
- `"pick"` — select N individual resources from allowed types
- `"bundle"` — select one predefined resource bundle
- `"combo"` — allocate a total across allowed types
- `"exchange"` — two-phase: spend prompt then gain prompt

This keeps config simple and the server resolver is a single function with mode branching.

### 2. Extend existing models rather than replacing them

`BuildingTile` gets an optional `visitor_reward_choice: ResourceChoiceReward | None` field. When present, the server sends a choice prompt after granting any fixed `visitor_reward`. Same pattern for `IntrigueCard` with a `choice_reward` field.

### 3. Reuse the pending-state + prompt/response pattern

The server already uses `pending_intrigue_target` and `pending_quest_reward` to pause the game for player input. Adding `pending_resource_choice` follows the same pattern — no architectural change needed.

### 4. Multi-player choices use a queue

For US5 (multi-player pick), the server maintains a `resource_choice_queue` in the pending state. After the main player resolves, it sends prompts to each other player in turn order. The game doesn't advance until all players have resolved.

### 5. Client dialog modes

One `ResourceChoiceDialog` class with three rendering modes:
- **Pick mode**: Buttons for each resource type; player clicks to add to selection, confirm when count reached
- **Bundle mode**: One button per predefined bundle; single click selects
- **Combo mode**: +/- stepper controls per type with running total; confirm when total reached
