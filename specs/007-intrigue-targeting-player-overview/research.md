# Research: Intrigue Targeting & Player Overview

## Decision 1: Server-Side Pending State for Targeting

**Decision**: Add a `pending_intrigue_target` field to GameState to track when the server is waiting for a target selection.

**Rationale**: The server must remember which intrigue card was played and by whom while waiting for the `ChooseIntrigueTargetRequest`. Without this, the server has no context when the target message arrives. The backstage placement is already committed (worker placed, card removed from hand) but the effect is deferred.

**Alternatives considered**:
- Client-only tracking: Rejected — server must validate and resolve effects authoritatively.
- Re-send card info in the target request: Rejected — client shouldn't be trusted with effect resolution data.

## Decision 2: Eligible Target Filtering

**Decision**: Server computes eligible targets (opponents with at least one of the targeted resources) and sends the list to the client. Client displays only eligible opponents.

**Rationale**: Server-side filtering prevents invalid selections and simplifies the client. The client only needs to show buttons for the provided player list.

**Alternatives considered**:
- Client-side filtering: Rejected — client may have stale resource data; server is authoritative.
- Show all opponents and reject invalid: Rejected — poor UX, wastes player time.

## Decision 3: Cancel Unwind During Targeting

**Decision**: Cancel during target selection fully unwinds the backstage placement using the existing `PlacementCancelledResponse` pattern.

**Rationale**: Consistent with how quest selection cancel works (removes worker from space, returns card/worker). The pending_intrigue_target state is cleared.

**Alternatives considered**:
- Force player to pick a target (no cancel): Rejected — user explicitly requested cancel support. Also handles edge case of no valid targets gracefully.

## Decision 4: New Messages vs Reuse

**Decision**: Add `IntrigueTargetPromptResponse` (server→client, shows who can be targeted) and `IntrigueEffectResolvedResponse` (server→all, shows what happened). Reuse existing `ChooseIntrigueTargetRequest` (client→server) and `PlacementCancelledResponse` (for cancel unwind).

**Rationale**: The prompt needs to carry eligible opponent data (player_id, name, relevant resource counts). The resolution needs to broadcast the outcome to all clients. Existing request message already has the right shape.

**Alternatives considered**:
- Reuse WorkerPlacedBackstageResponse: Rejected — different semantics, would overload the message.

## Decision 5: Player Overview Data Source

**Decision**: Player overview panel reads from `self.game_state["players"]` which already contains all needed fields. Opponent intrigue/quest hand sizes use the `_count` fields already provided by the server's `_filter_state_for_player`.

**Rationale**: No new server messages needed. All data is already available in the client's local game state. The server already sends `intrigue_hand_count` and `contract_hand_count` for opponents.

**Alternatives considered**:
- Request fresh data from server: Rejected — unnecessary round-trip, local state is kept in sync by message handlers.

## Decision 6: Cancel Message for Targeting

**Decision**: Add a new `CancelIntrigueTargetRequest` message (client→server) rather than reusing `CancelQuestSelectionRequest`.

**Rationale**: The cancel logic is different — quest cancel frees a Garage space, while intrigue cancel frees a backstage slot and returns an intrigue card. Using a separate message keeps the handlers clean.
