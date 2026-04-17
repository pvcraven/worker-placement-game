# Implementation Plan: Quest Completion

**Branch**: `005-quest-completion` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-quest-completion/spec.md`

## Summary

Add end-of-turn quest completion flow: after a worker placement resolves, the server checks if the active player can complete any held quests, sends eligible quests to the client, and the client shows a horizontal card dialog with a "Skip" option. Also relocate the VP display and add a workers-left counter to a new status line above the resource bar.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (client UI), websockets (networking), Pydantic (data validation/serialization)
**Storage**: In-memory game state (server); JSON configuration files (game content)
**Testing**: pytest
**Target Platform**: Desktop (Windows/macOS/Linux)
**Project Type**: Client-server desktop game
**Performance Goals**: 60 fps client rendering, sub-second turn transitions
**Constraints**: Single quest completion per turn; dialog must not block other players
**Scale/Scope**: 1-5 players per game session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is an unfilled template — no gates defined. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/005-quest-completion/
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
│   └── game_view.py          # Message handling, quest completion dialog trigger
├── ui/
│   ├── board_renderer.py     # Board drawing, status line
│   ├── resource_bar.py       # Resource bar (VP removal, shift down)
│   ├── card_renderer.py      # Quest card rendering in dialog
│   └── dialogs.py            # QuestCompletionDialog (new dialog class)

server/
├── game_engine.py            # Quest eligibility check, turn flow modification
├── models/
│   └── game.py               # Player model (existing fields sufficient)

shared/
├── messages.py               # New message types for quest completion flow
├── card_models.py            # ContractCard (existing, no changes needed)
```

**Structure Decision**: Existing project structure is sufficient. No new directories or modules needed beyond a new dialog class in `client/ui/dialogs.py`.

## Complexity Tracking

No constitution violations to justify.
