# Research: Backstage & Intrigue Mechanics

## Decision 1: How to route backstage placement clicks

**Decision**: The client detects backstage clicks by checking if the `space_id` starts with `"backstage_slot_"`. Instead of sending `place_worker`, the client shows an intrigue card selection dialog first, then sends `place_worker_backstage` with the chosen `intrigue_card_id` and `slot_number`.

**Rationale**: The `PlaceWorkerBackstageRequest` message type already exists in `shared/messages.py` with `slot_number` and `intrigue_card_id` fields. The server's `handle_place_worker()` correctly rejects backstage space_ids (they're not in `action_spaces` dict), so using a separate message type is the existing design. Client-side card selection before server placement allows cancel/unwind without server round-trips.

**Alternatives considered**:
- Server-side intrigue selection prompt (like quest completion): Rejected because the backstage placement requires a card to be selected *during* placement, not after. Sending the card with the placement message is simpler.
- Adding backstage slots to action_spaces dict: Rejected because BackstageSlot is a separate model with different semantics (sequential filling, intrigue card attachment, reassignment queue).

## Decision 2: Where to add starting resource initialization

**Decision**: Add starting coins and intrigue card dealing in `server/lobby.py` during game initialization, right after player creation and before the game phase is set to PLACEMENT.

**Rationale**: The lobby already handles player initialization (worker assignment, producer card dealing). Adding starting coins and intrigue cards here keeps all initialization in one place. Starting coins follow the formula `4 + (slot_index * 2)` where slot_index is 0-based. Intrigue cards are drawn from the shuffled intrigue deck (already loaded by config_loader).

**Alternatives considered**:
- Constants in shared/constants.py: Could add STARTING_INTRIGUE_CARDS = 2 and STARTING_COINS_BASE = 4, STARTING_COINS_INCREMENT = 2. Decided to use constants for clarity.

## Decision 3: Backstage sequential filling validation

**Decision**: Validate on the server in `handle_place_worker_backstage()` by checking that all lower-numbered slots are occupied before allowing placement on slot N.

**Rationale**: Server-side validation is authoritative. The client can also grey out unavailable slots for UX, but the server must enforce the rule. The check is simple: for slot N, verify slots 1 through N-1 all have `occupied_by` set.

**Alternatives considered**:
- Client-only validation: Rejected because server must be authoritative.

## Decision 4: Intrigue card selection cancel/unwind flow

**Decision**: The cancel happens entirely on the client side. Since the client shows the intrigue card selection dialog *before* sending the placement message, cancelling simply closes the dialog without sending anything. No server-side unwind needed.

**Rationale**: This is simpler than the alternative of placing the worker first and then unwinding. The worker is only placed on the server after the client sends `place_worker_backstage` with a valid card selection.

**Alternatives considered**:
- Place worker first, then select card, unwind on cancel: Rejected because it requires server-side unwind logic and extra messages. Client-side selection before placement is cleaner.

## Decision 5: Reassignment phase — preventing backstage re-placement

**Decision**: The existing `handle_reassign_worker()` handler validates the target space against `action_spaces` dict. Since backstage slots are not in `action_spaces`, they are naturally excluded. Add an explicit check for backstage space_ids as a safety net.

**Rationale**: The existing architecture already prevents this by design. An explicit check adds defense-in-depth and a clear error message.

**Alternatives considered**:
- Relying solely on the existing dict lookup: Would work but fails silently. An explicit check gives a better error message.

## Decision 6: Existing infrastructure inventory

**Decision**: Leverage existing infrastructure rather than building new:
- `BackstageSlot` model: already exists in `server/models/game.py`
- `IntrigueCard` model: already exists in `shared/card_models.py`
- `_resolve_intrigue_effect()`: already exists in `server/game_engine.py`
- `PlaceWorkerBackstageRequest/Response`: already exist in `shared/messages.py`
- `ReassignmentPhaseStartResponse`: already exists
- `handle_reassign_worker()`: already exists
- `_end_placement_phase()`: already transitions to REASSIGNMENT phase
- `CardSelectionDialog`: reusable for intrigue card selection
- `intrigue.json`: 50 cards already defined with effects

**What's missing**:
- Starting resource initialization (coins + intrigue cards)
- Client-side backstage click routing and intrigue card dialog
- Server-side backstage placement validation (sequential filling, player has card)
- Server-side handler for `place_worker_backstage` messages (routing in network.py)
