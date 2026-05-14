# Feature Specification: Card Pick Animation

**Feature Branch**: `030-card-pick-animation`  
**Created**: 2026-05-14  
**Status**: Draft  
**Input**: User description: "Add a card animation when user selects a face-up quest/contract card. Card animates to center screen, pauses, then animates off-screen toward the player list."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Card Animates to Center on Selection (Priority: P1)

When a player selects a face-up quest/contract card, the card visually lifts from its board position and glides to the center of the screen using a smooth SINE easing curve over 0.75 seconds. The original card position appears empty during the animation (the card is moved, not copied). This animation plays on every connected client, not just the selecting player's screen — all players see the card pick happen.

**Why this priority**: This is the core visual effect. Without it, no other animation steps matter.

**Independent Test**: Can be fully tested by selecting any face-up quest card during a game round and observing the card sprite move smoothly from its board position to the screen center on all connected clients. The card's original board slot should appear empty during the animation.

**Acceptance Scenarios**:

1. **Given** a player selects a face-up quest card, **When** the selection is made, **Then** the card sprite animates from its board position to the center of the screen using SINE easing over 0.75 seconds on every connected client.
2. **Given** a card animation is in progress from board to center, **When** the animation plays, **Then** the card's original board slot appears empty (no duplicate card remains at the original position).
3. **Given** a card animation is in progress, **When** the animation plays, **Then** no other player input is processed until the full animation sequence completes.

---

### User Story 2 - Card Pauses at Center Then Exits Toward Player List (Priority: P2)

After arriving at the center of the screen, the card holds its position for one second so all players can see it clearly. Then the card animates off-screen toward the specific row of the player who picked it up in the player list (upper-left area) using Quad-In easing over 0.75 seconds, giving the visual impression that the card is being added to that player's collection.

**Why this priority**: Completes the full animation arc. The pause makes the card readable; the exit direction toward the specific player reinforces who received it.

**Independent Test**: Can be tested by observing the full animation sequence after card selection — the card should visibly pause at center, then accelerate off toward the selecting player's row in the upper-left player list.

**Acceptance Scenarios**:

1. **Given** the card has arrived at the center of the screen, **When** one second elapses, **Then** the card begins animating off-screen toward the selecting player's row in the player list, using Quad-In easing over 0.75 seconds.
2. **Given** the card exit animation is playing, **When** the card moves fully off-screen, **Then** the animation sequence is considered complete.

---

### User Story 3 - Board Updates After Animation Completes (Priority: P3)

Once the card has fully exited the screen, the board refreshes to show the updated face-up quest cards. Only the slot where the selected card was should change — the remaining cards stay in their current positions, and the replacement card (drawn from the deck) fills the vacated slot.

**Why this priority**: Ensures visual continuity. Cards that weren't selected should not visually jump or reposition, which would be disorienting.

**Independent Test**: Can be tested by noting the positions of the non-selected cards before and after the animation completes — they should remain in the same slots. The replacement card should appear only in the slot of the selected card.

**Acceptance Scenarios**:

1. **Given** the card exit animation has completed, **When** the board refreshes with the updated face-up quest list, **Then** the replacement card appears in the slot previously occupied by the selected card.
2. **Given** four face-up quest cards are displayed and one is selected, **When** the animation completes and the board updates, **Then** the three non-selected cards remain in their original positions and only the selected card's slot shows a new card.

---

### Edge Cases

- What happens if the game advances to the next phase (e.g., another player's turn starts) before the animation finishes? The animation should complete before processing further state updates.
- What happens if the quest deck is empty and no replacement card is drawn? The slot should remain empty after animation completes, consistent with current behavior.
- What happens if the player resizes the window during the animation? The animation target positions (center, exit direction) should be based on the screen dimensions at animation start and not change mid-animation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST animate the selected quest card from its board position to the center of the screen using SINE easing over 0.75 seconds when a player picks a face-up quest card.
- **FR-002**: System MUST remove the card sprite from its original board position at the start of the animation so no duplicate is visible.
- **FR-003**: System MUST hold the card at the center of the screen for one second after the arrival animation completes.
- **FR-004**: System MUST animate the card from the center of the screen toward the selecting player's row in the player list using Quad-In easing over 0.75 seconds after the one-second pause.
- **FR-005**: System MUST defer the board refresh (showing the replacement card) until the full animation sequence (move to center, pause, move off-screen) has completed.
- **FR-006**: System MUST keep non-selected face-up quest cards in their current board positions when the board refreshes after animation. Only the vacated slot should change.
- **FR-007**: System MUST block player input during the card animation sequence to prevent conflicting actions.
- **FR-008**: System MUST play the card pick animation on all connected clients when any player selects a quest card, not only on the selecting player's client.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full card animation sequence (0.75s entry + 1.0s pause + 0.75s exit = 2.5s total) completes predictably, maintaining a responsive feel.
- **SC-002**: Non-selected face-up quest cards remain visually stationary during and after the animation — no position jumping or flickering.
- **SC-003**: The animation plays smoothly at the application's target frame rate with no visible stuttering or frame drops.
- **SC-004**: Players can visually identify which card was selected during the one-second center-screen pause.

## Clarifications

### Session 2026-05-14

- Q: Does the animation play only on the selecting player's client? → A: No, the animation plays on all connected clients whenever any player selects a quest card.
- Q: Does the exit animation target the player list generically or a specific player? → A: The card exits toward the specific row of the player who picked it up in the player list.
- Q: What are the entry and exit animation durations? → A: 0.75 seconds each (entry and exit), with a 1-second center pause, totaling 2.5 seconds.

## Assumptions

- The animation applies only to face-up quest/contract card selection (not building purchases, intrigue cards, or other card types).
- The animation uses the same card sprite/image that is already rendered on the board — no new artwork or alternate card view is needed.
- The exit animation targets the selecting player's specific row in the player list (upper-left status bar area).
- Animation timing (0.75s SINE entry, 1.0s hold, 0.75s Quad-In exit) is applied consistently regardless of the distance the card needs to travel.
- The server-side game state update proceeds immediately as it does today; only the client-side visual refresh is deferred until animation completion.
