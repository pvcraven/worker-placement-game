# Research: Quest Completion

## Decision 1: Where to insert the quest completion check in the turn flow

**Decision**: After worker placement resolves (reward applied) but before `_advance_turn()` is called. The server sends a `QuestCompletionPromptResponse` to the active player listing eligible quests. The turn does not advance until the player completes a quest or skips.

**Rationale**: The existing `handle_complete_quest()` handler already validates and processes quest completion. The new flow adds a server-initiated prompt that tells the client which quests are eligible, then waits for either a `complete_quest` or `skip_quest_completion` message before advancing. This keeps the server authoritative about eligibility.

**Alternatives considered**:
- Client-side eligibility check: Rejected because the client could show stale data; server must be authoritative.
- Automatic completion (no dialog): Rejected because the player should choose which quest to complete when multiple are eligible.

## Decision 2: New message types needed

**Decision**: Two new messages:
1. `QuestCompletionPromptResponse` (server → client): Contains list of completable quest card objects. Sent only to the active player.
2. `SkipQuestCompletionRequest` (client → server): Signals the player chose to skip.

The existing `CompleteQuestRequest` and `QuestCompletedResponse` are reused for the actual completion.

**Rationale**: Minimal new message surface. The prompt is player-specific (not broadcast). Skip is a new action the server needs to recognize to advance the turn.

**Alternatives considered**:
- Reusing existing message types with flags: Rejected for clarity — a distinct prompt message makes the flow explicit.

## Decision 3: Turn state management during quest completion prompt

**Decision**: No new game phase needed. The quest completion prompt happens within the current player's turn. The server simply delays calling `_advance_turn()` until the player responds. A `waiting_for_quest_completion` flag on the game state tracks this.

**Rationale**: Adding a full `GamePhase.QUEST_COMPLETION` would add complexity for a brief within-turn interaction. A boolean flag is simpler and sufficient since only the active player is prompted.

**Alternatives considered**:
- New GamePhase enum value: Rejected as over-engineered for a single-player prompt within an existing turn.

## Decision 4: Status line placement

**Decision**: Add a new text line drawn directly by the board renderer, positioned between the board area and the resource bar. The resource bar's y-position shifts down by ~25 pixels. VP is removed from the resource bar and displayed in the new status line.

**Rationale**: The board renderer already manages layout positioning. A dedicated status line keeps workers-left and VP visible without cluttering the resource bar.

**Alternatives considered**:
- Embedding workers-left into the resource bar: Rejected because the user explicitly requested a separate line with the format "Workers left: N  VP: M".
