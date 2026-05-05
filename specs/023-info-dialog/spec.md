# Feature Specification: Informational Dialog System

**Feature Branch**: `023-info-dialog`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a routine where we can have an informational dialog in the middle of the screen. The dialog will be centered and it will auto-dismiss. When we switch rounds, the dialog will pop in the middle of the screen saying 'ROUND 2' and go away 1.5 seconds. When we are waiting on another player to make a choice during our round (like, if the other player is selecting a resource. This would happen with some buildings where owner gets a choice. Or intrigue cards) the window stays open until the user is done. If Player A plays an intrigue card that steals from Player B, then have a 1.5 second dialog pop up that says 'Player A stole 2 drummers'"

## Clarifications

### Session 2026-05-05

- Q: Should round transition dialog play a sound effect? → A: Yes, play `client/assets/sounds/sound2.mp3` when the round transition dialog appears
- Q: Which waiting states trigger the "Waiting on [Player]" dialog? → A: All waiting states — owner bonus choices, intrigue target selection, round-start resource choices, and any other deferred player choice

## User Scenarios & Testing

### User Story 1 - Round Transition Dialog (Priority: P1)

When a round ends and a new round begins, a large centered dialog appears on screen displaying the new round number (e.g., "ROUND 2"). The dialog automatically dismisses after 1.5 seconds without requiring any player interaction.

**Why this priority**: Round transitions are the most frequent and visible game event. Every player sees them every round, making this the highest-impact use of the dialog system. It also establishes the core dialog infrastructure that other stories build upon.

**Independent Test**: Start a game, complete all worker placements in round 1, verify the "ROUND 2" dialog appears centered on screen and auto-dismisses after 1.5 seconds, then gameplay resumes normally.

**Acceptance Scenarios**:

1. **Given** all players have placed their workers and the round ends, **When** the new round begins, **Then** a centered dialog displays "ROUND [N]" (where N is the new round number), plays `sound2.mp3`, and automatically dismisses after 1.5 seconds
2. **Given** the round transition dialog is displayed, **When** 1.5 seconds elapse, **Then** the dialog disappears and the game continues with the first player's turn
3. **Given** the game is in round 7 and the round ends, **When** round 8 (final round) begins, **Then** the dialog displays "ROUND 8" following the same pattern

---

### User Story 2 - Waiting on Another Player Dialog (Priority: P1)

When a player must wait for another player to make a choice, a centered dialog appears informing the waiting player who they are waiting on. This applies to all waiting states: building owner bonus choices, intrigue target selection, round-start resource choices (trigger swap plots), and any other deferred player choice. The dialog stays open until the other player completes their action.

**Why this priority**: Equally critical to round transitions — without this, players see a frozen screen with no explanation when another player is making a choice. This replaces the current status-text-only approach with a prominent centered dialog.

**Independent Test**: Have Player A place a worker on a building owned by Player B that grants the owner a resource choice. Verify Player A sees a "Waiting on Player B" dialog that remains visible until Player B makes their choice, then the dialog dismisses.

**Acceptance Scenarios**:

1. **Given** Player A places a worker on a building owned by Player B that triggers an owner bonus choice, **When** Player B's choice prompt is sent, **Then** Player A sees a centered dialog saying "Waiting on [Player B's name]" that persists until Player B responds
2. **Given** Player A plays an intrigue card that requires choosing a target player, **When** the intrigue target prompt is sent, **Then** other players see a centered dialog saying "Waiting on [Player A's name]" until the target selection completes
3. **Given** a waiting dialog is displayed, **When** the other player completes their choice, **Then** the dialog dismisses and gameplay continues

---

### User Story 3 - Intrigue Steal Notification Dialog (Priority: P2)

When a player plays an intrigue card that steals resources from another player, all players see a centered dialog that briefly describes the theft (e.g., "Alice stole 2 drummers from Bob"). The dialog auto-dismisses after 1.5 seconds.

**Why this priority**: Important for game awareness — players need to know when resources are being stolen. However, the game already broadcasts this information via the game log and the intrigue effect resolution message, so this is an enhancement over existing functionality rather than filling a gap.

**Independent Test**: Have Player A play a "steal resources" intrigue card targeting Player B. Verify all players see a dialog such as "Alice stole 2 drummers from Bob" that auto-dismisses after 1.5 seconds.

**Acceptance Scenarios**:

1. **Given** Player A plays an intrigue card that steals 2 drummers from Player B, **When** the intrigue effect resolves, **Then** all players see a centered dialog reading "[Player A name] stole 2 drummers from [Player B name]" that auto-dismisses after 1.5 seconds
2. **Given** Player A plays an intrigue card that steals multiple resource types (e.g., 1 guitarist and 1 singer), **When** the effect resolves, **Then** the dialog lists all stolen resources (e.g., "Alice stole 1 guitarist, 1 singer from Bob")
3. **Given** a steal notification dialog is displayed, **When** 1.5 seconds elapse, **Then** the dialog disappears without player interaction

---

### Edge Cases

- What happens if a round transition dialog and a steal notification need to display at the same time? Assumption: they queue — the first dialog displays, then the second appears after the first dismisses.
- What happens if the game ends (final round completes)? The dialog system should not interfere with the final score screen transition.
- What happens if a waiting dialog is displayed and the waited-on player disconnects? The dialog should dismiss when the server resolves the disconnection (timeout or reconnection).

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a reusable centered dialog component that can display text messages over the game view
- **FR-002**: System MUST support auto-dismiss dialogs with a configurable duration (default 1.5 seconds)
- **FR-003**: System MUST support persistent dialogs that remain visible until explicitly dismissed by a game event
- **FR-004**: System MUST display a "ROUND [N]" dialog when a new round begins, play `sound2.mp3`, and auto-dismiss after 1.5 seconds
- **FR-005**: System MUST display a "Waiting on [Player Name]" dialog whenever any player is waiting for another player to make a choice, including owner bonus choices, intrigue target selection, round-start resource choices, and any other deferred player choice
- **FR-006**: System MUST dismiss the waiting dialog when the other player's action resolves
- **FR-007**: System MUST display a steal notification dialog (e.g., "[Player] stole [amount] [resource] from [Target]") when an intrigue card steal effect resolves, auto-dismissing after 1.5 seconds
- **FR-008**: System MUST queue multiple dialogs if they overlap, displaying them sequentially
- **FR-009**: The dialog MUST be visually centered on the game screen
- **FR-010**: The dialog MUST NOT block server communication or game state updates while displayed

### Key Entities

- **InfoDialog**: A transient UI element displayed centered on screen. Has a message (text), a duration (seconds or None for persistent), and a dismiss callback.
- **DialogQueue**: Manages ordering when multiple dialogs are triggered in quick succession.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Round transition dialog appears within 0.5 seconds of receiving the round-end message and dismisses after 1.5 seconds
- **SC-002**: Waiting dialog appears immediately when another player's choice prompt is received and dismisses within 0.5 seconds of the choice resolving
- **SC-003**: Steal notification dialog appears immediately when an intrigue steal effect resolves and dismisses after 1.5 seconds
- **SC-004**: Dialog is visually centered on screen at all supported window sizes
- **SC-005**: Multiple rapid dialog triggers (e.g., round end + immediate steal) display sequentially without lost messages

## Assumptions

- The dialog is a client-side-only UI component; no new server messages are required (existing messages already carry all needed data)
- The dialog renders on top of all other game UI elements (board, panels, etc.)
- The dialog has a semi-transparent background overlay to draw attention
- The dialog text uses a large, readable font size appropriate for the game's visual style
- The auto-dismiss duration of 1.5 seconds is consistent across all timed dialogs
- The Arcade library's scheduling/timer system will be used for auto-dismiss timing
