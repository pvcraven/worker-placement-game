# Implementation Plan: Quest Reward Expansion

**Branch**: `008-quest-reward-expansion` | **Date**: 2026-04-18 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-quest-reward-expansion/spec.md`

## Summary

Expand quest completion rewards beyond victory points and bonus resources to include intrigue card draws, quest card draws (random or player-chosen), and free buildings (market choice or random draw). Unify the reward framework so intrigue cards and quests use the same mechanisms. Add new quest content utilizing expanded rewards.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration files (game content)
**Testing**: pytest, ruff (linting)
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Client-server multiplayer desktop game
**Performance Goals**: 60 fps rendering, sub-second network responses
**Constraints**: All game logic server-authoritative; client updates local state from messages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a blank template — no gates defined. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/008-quest-reward-expansion/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── websocket-messages.md
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
shared/
├── card_models.py       # ContractCard, IntrigueCard, ResourceCost models
├── messages.py          # WebSocket message types (Pydantic)
└── constants.py         # Enums, game constants

server/
├── game_engine.py       # Core game logic: quest completion, intrigue effects
├── network.py           # WebSocket routing/dispatch
├── lobby.py             # State filtering for players
└── models/
    └── game.py          # GameState, Board, Player models

client/
├── views/
│   └── game_view.py     # Main game view: message handlers, UI rendering
├── ui/
│   ├── dialogs.py       # Modal dialogs (quest completion, target selection)
│   ├── card_renderer.py # Quest/intrigue card rendering
│   ├── resource_bar.py  # Resource display bar
│   └── game_log.py      # Game log panel
└── game_window.py       # Window management

config/
├── contracts.json       # Quest card definitions
├── intrigue.json        # Intrigue card definitions
└── buildings.json       # Building tile definitions
```

**Structure Decision**: Existing project structure. No new directories needed. Changes span shared models, server engine, client view, client dialogs, and config JSON files.

## Architecture Decisions

### 1. Reward Model Extension

**Current state**: `ContractCard` has `victory_points: int` and `bonus_resources: ResourceCost`. These are the only reward types.

**Approach**: Add new optional fields to `ContractCard` for card draws and building grants:
- `reward_draw_intrigue: int = 0` — number of intrigue cards to draw
- `reward_draw_quests: int = 0` — number of quest cards to draw
- `reward_quest_draw_mode: str = "random"` — "random" or "choose"
- `reward_building: str | None = None` — "market_choice", "random_draw", or None

This keeps the existing `bonus_resources` and `victory_points` fields unchanged, maintaining full backward compatibility with existing quest data.

### 2. Server-Side Reward Resolution

**Current state**: `handle_complete_quest` does: deduct cost → add VP → add bonus_resources → remove card → broadcast.

**Approach**: After the existing reward application, add steps for:
1. Draw intrigue cards (if `reward_draw_intrigue > 0`)
2. Draw quest cards randomly (if `reward_draw_quests > 0` and mode is "random")
3. If mode is "choose" or building reward is "market_choice", set pending state and prompt the player (similar to `pending_intrigue_target` pattern)
4. If building reward is "random_draw", draw from building deck and auto-assign

For interactive rewards (choose quest from face-up, choose building from market), the quest completion flow pauses — using the same pending-state pattern as intrigue targeting. The server saves `pending_quest_reward` on GameState, sends a prompt to the client, and waits for the player's choice.

### 3. Message Flow for Interactive Rewards

**Non-interactive rewards** (VP, resources, random card draws, random building): Applied immediately in `handle_complete_quest`. Included in `QuestCompletedResponse`.

**Interactive rewards** (choose quest from face-up, choose building from market): After non-interactive rewards are applied, server sends a `QuestRewardChoicePrompt` to the player. Player responds with their selection. Server resolves and broadcasts `QuestRewardChoiceResolved`.

### 4. Client-Side Handling

`_on_quest_completed` already processes VP, resources_spent, and bonus_resources. Extend it to also handle:
- `drawn_intrigue`: list of card dicts drawn (add to local intrigue_hand)
- `drawn_quests`: list of card dicts drawn (add to local contract_hand)
- `building_granted`: building dict if random-draw building was assigned

For interactive rewards, add handlers for `QuestRewardChoicePrompt` — show a selection dialog (reuse existing patterns from quest selection and building purchase), send choice back to server.

### 5. Intrigue Card Unification

Intrigue cards already support `draw_intrigue` and `draw_contracts` as separate effect types. The existing system works. For US3, ensure the same underlying draw functions (`_draw_from_quest_deck`, intrigue deck pop) are used by both intrigue effects and quest rewards — extract into shared helpers if not already.

### 6. Quest Card Display

Quest cards need to display all reward components. The card renderer (`card_renderer.py`) needs to show reward lines beyond just VP — e.g., "+2 VP, +1 Guitarist, Draw 1 Intrigue Card".

### 7. Config Data Changes

Add new fields to quest entries in `contracts.json`. Existing quests are unchanged (new fields default to 0/None). Add at least 6 new quest cards utilizing expanded rewards.
