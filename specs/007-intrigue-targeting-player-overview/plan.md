# Implementation Plan: Intrigue Targeting & Player Overview

**Branch**: `007-intrigue-targeting-player-overview` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-intrigue-targeting-player-overview/spec.md`

## Summary

Fix non-functional "choose_opponent" intrigue cards (steal_resources, opponent_loses) by implementing the deferred targeting flow: server pauses after backstage placement, client shows a target selection dialog, server resolves the effect on confirmation. Add a player overview panel showing all players' resources in a table.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration (game content)
**Testing**: Manual play-testing via quickstart scenarios
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Client-server multiplayer game
**Performance Goals**: Real-time UI updates, sub-second message round-trips
**Constraints**: Server is authoritative; client updates local state from messages
**Scale/Scope**: 2-5 players per game session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a template with no project-specific rules defined. No gates to evaluate. PASS.

## Project Structure

### Documentation (this feature)

```text
specs/007-intrigue-targeting-player-overview/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── websocket-messages.md
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
client/
├── views/
│   └── game_view.py        # Add target dialog trigger, player overview toggle, handlers
├── ui/
│   ├── dialogs.py           # Add PlayerTargetDialog
│   └── board_renderer.py    # No changes expected
server/
├── game_engine.py           # Implement handle_choose_intrigue_target, cancel flow
├── network.py               # Route already wired (choose_intrigue_target)
├── models/
│   └── game.py              # Add pending_intrigue_target state field
shared/
├── messages.py              # Add IntrigueTargetPromptResponse, IntrigueEffectResolvedResponse
├── constants.py             # No changes expected
└── card_models.py           # No changes expected
```

**Structure Decision**: Extends existing client-server structure. No new directories needed. The route for `choose_intrigue_target` already exists in network.py. The stub handler in game_engine.py will be replaced with the real implementation.

## Key Implementation Details

### Server Flow for Targeted Intrigue Cards

1. Player places on backstage slot, selects intrigue card
2. `handle_place_worker_backstage()` calls `_resolve_intrigue_effect()`
3. `_resolve_intrigue_effect()` detects `effect_target == "choose_opponent"` → returns without resolving
4. **NEW**: Server saves pending intrigue state on the game state (`pending_intrigue_target` with card info and player_id)
5. **NEW**: Server broadcasts `IntrigueTargetPromptResponse` to the active player with eligible opponents list
6. Client shows `PlayerTargetDialog` listing eligible opponents
7. Player selects target → client sends `ChooseIntrigueTargetRequest` (already exists)
8. Server's `handle_choose_intrigue_target()` resolves: transfers/removes resources, clears pending state
9. Server broadcasts `IntrigueEffectResolvedResponse` → all clients update
10. Normal flow resumes (`_check_quest_completion`)

### Cancel Flow for Targeted Intrigue

- Player clicks Cancel in target dialog → client sends a cancel message
- Server unwinds: removes worker from backstage slot, returns intrigue card to hand, restores available_workers, clears pending state
- Broadcasts `PlacementCancelledResponse` (reuse existing)

### No Valid Targets Flow

- Server detects no eligible opponents before sending prompt
- Server sends error/notification to player
- Server auto-unwinds the backstage placement (same as cancel)

### Player Overview Panel

- New button "Player Overview" in the existing button row
- Toggle pattern identical to "My Quests" / "My Intrigue" panels
- Renders a table from `self.game_state["players"]` data
- Shows: name, workers, guitarists, bass_players, drummers, singers, coins, intrigue_hand_count, contract_hand_count, completed_quests count, victory_points
- Current player's row highlighted with distinct background color
