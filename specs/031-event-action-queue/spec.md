# Feature Specification: Event Action Queue

**Feature Branch**: `031-event-action-queue`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: User description: "The dialog for completing a quest pops up immediately, while the animation for getting a card starts at the same time the dialog pops up. So the card appears, but is blocked by the dialog. And you can't interact with the dialog that just popped up. We'd like the dialog to pop up AFTER the animation. This is an issue in several places, and we'll be adding more so we need a queue of stuff to show the user so it goes in the right order. Same with sounds."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Animations Complete Before Dialogs Appear (Priority: P1)

A player places a worker on a space that triggers a card pick animation (e.g., selecting a quest from The Garage). Currently the quest completion dialog pops up on top of the card animation, blocking both the animation view and dialog interaction. With the event queue, the card animation plays to completion first, then the dialog appears and is immediately interactive.

**Why this priority**: This is the core problem — overlapping animations and dialogs confuse the player and block interaction. Fixing this delivers the primary value.

**Independent Test**: Select a quest from a space that triggers both a card pick animation and a quest completion prompt. The card animation should play fully before the quest completion dialog appears.

**Acceptance Scenarios**:

1. **Given** a player selects a quest card from the board, **When** the card pick animation starts and a quest completion prompt is triggered, **Then** the quest completion dialog does not appear until the card animation finishes.
2. **Given** a card animation is playing, **When** the animation completes, **Then** the queued dialog appears immediately and the player can interact with it without delay.
3. **Given** multiple events are triggered in rapid succession (e.g., animation, then dialog, then another animation), **When** each event completes, **Then** the next event in the queue starts automatically in the correct order.

---

### User Story 2 - Sounds Play at the Right Time (Priority: P2)

Sounds associated with game events (card draws, round transitions, turn notifications) should play in sequence with their corresponding visual events rather than all firing at once. If a card animation plays followed by a dialog, the card sound plays with the animation and the dialog sound (if any) plays when the dialog appears.

**Why this priority**: Sound timing reinforces visual feedback. Mis-timed sounds are disorienting but less blocking than overlapping dialogs.

**Independent Test**: Trigger a sequence of events that each have associated sounds. Each sound should play when its corresponding visual event starts, not all at once.

**Acceptance Scenarios**:

1. **Given** a card pick animation with an associated sound is queued, **When** the animation begins playing, **Then** the sound plays at that moment (not before).
2. **Given** two events with sounds are queued back-to-back, **When** the first event finishes, **Then** the second event's sound plays when it starts, not overlapping with the first.

---

### User Story 3 - Queue Handles Varying Event Types (Priority: P3)

The queue must handle different types of events — animations, dialogs, and sounds — in any combination and order. New event types can be added in the future without restructuring the queue. For example, a future "toast notification" or "score tally animation" should slot into the same queue.

**Why this priority**: Extensibility ensures the queue remains useful as the game grows. Without this, each new event type would reintroduce the overlap problem.

**Independent Test**: Queue a mixed sequence of events (e.g., sound, then animation, then dialog). Each should execute in order, with the next starting only after the previous completes.

**Acceptance Scenarios**:

1. **Given** a sound event followed by an animation event are in the queue, **When** the sound finishes, **Then** the animation starts.
2. **Given** a dialog is in the queue, **When** the player dismisses the dialog (makes a choice or closes it), **Then** the next queued event starts.
3. **Given** no events are in the queue, **When** a new event is added, **Then** it starts immediately without waiting.

---

### Edge Cases

- What happens when the queue has events and the game round ends? Events should continue processing; round-end logic waits for the queue to drain.
- What happens if a queued dialog becomes irrelevant (e.g., another player's action changes game state)? The dialog should still show with current data, as the server has already committed the game state.
- What happens if events arrive faster than they can be displayed? They queue up and play in arrival order.
- What happens with events meant for spectators or non-active players? Non-interactive events (animations, sounds) play for all players. Dialogs only show for the player who needs to act.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST process queued events sequentially — the next event starts only after the current event completes.
- **FR-002**: The system MUST support at least three event types: animations (timed, complete automatically), dialogs (complete when the player interacts), and sounds (timed, complete when playback ends or after a brief duration).
- **FR-003**: When an animation is the current event, the system MUST allow it to play to completion before starting the next event.
- **FR-004**: When a dialog is the current event, the system MUST wait for the player to interact with it (make a selection, dismiss it) before starting the next event.
- **FR-005**: When a sound is the current event and has no visual component, the system MUST proceed to the next event after the sound's duration elapses or a short default delay.
- **FR-006**: The system MUST start a newly added event immediately if the queue is empty and no event is currently active.
- **FR-007**: The system MUST preserve the order of events as they were enqueued.
- **FR-008**: The system MUST be extensible to support new event types in the future without modifying the core queue logic.
- **FR-009**: Events that are not interactive (animations, sounds) MUST play for all connected players. Dialogs MUST only appear for the intended player.
- **FR-010**: The system MUST not block game state updates while the queue is processing — state updates from the server should still be applied in the background.

### Key Entities

- **Event Queue**: An ordered list of pending events to show the player. Processes one event at a time.
- **Event**: A single unit of presentation — an animation, dialog, or sound. Each event knows how to start, how to determine when it's complete, and what to do on completion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players never see a dialog overlapping a playing animation — events always present one at a time in sequence.
- **SC-002**: Players can interact with every dialog immediately when it appears — no unresponsive dialogs due to background animations.
- **SC-003**: Sounds play in sync with their corresponding visual events, not before or after.
- **SC-004**: Adding a new event type requires only defining the new event's start/complete behavior, not changing the queue itself.

## Assumptions

- The existing animation system (AnimationManager with completion callbacks) will remain the mechanism for playing animations; the queue wraps around it rather than replacing it.
- Sound durations are short enough (under 2 seconds) that a brief fixed delay is acceptable if exact duration detection is unavailable.
- The server will continue to send game state updates independently of the client's event queue — the queue is purely a client-side presentation concern.
- All current dialog types (QuestCompletionDialog, ResourceChoiceDialog, CardSelectionDialog, CardSpriteSelectionDialog, PlayerTargetDialog) will eventually be integrated into the queue, but initial implementation may start with the most impactful cases.
- The queue processes events for the local player's presentation only; it does not coordinate across players.
