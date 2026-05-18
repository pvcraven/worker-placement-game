# Feature Specification: Building Acquisition Animation

**Feature Branch**: `035-building-acquisition-animation`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "When buying or otherwise getting a face-up building, animate the building moving to its spot to the left where it can be used. If a user is drawing a building, animate it flying up from the lower right corner."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Face-Up Building Purchase Animation (Priority: P1)

A player purchases a face-up building from the building market on the right side of the board. Instead of the building instantly appearing in the player's constructed buildings area on the left, the building card visually slides from its market position across the board to its assigned lot position on the left side.

**Why this priority**: This is the most common building acquisition path and provides the core visual feedback that a building has been obtained and where it now lives.

**Independent Test**: Can be fully tested by purchasing any face-up building and observing that it animates from the market (right) to the constructed buildings area (left), landing in the correct lot position.

**Acceptance Scenarios**:

1. **Given** a player is purchasing a face-up building from the market, **When** the purchase is confirmed, **Then** the building card animates from its market position to its assigned lot position in the constructed buildings area on the left side of the board.
2. **Given** a building purchase animation is playing, **When** the animation completes, **Then** the building appears in its final lot position as a fully functional action space (same as current behavior, but now it arrives via animation).
3. **Given** a building purchase animation is playing, **When** the building card reaches its destination, **Then** the market display updates to reflect the building's removal (the slot is vacated or replaced).

---

### User Story 2 - Drawn Building Animation (Priority: P2)

A player receives a building by drawing from the building deck (e.g., as a quest reward or special ability). Since the drawn building was not visible on the board, the card flies up from the lower-right corner of the screen to its assigned lot position on the left side.

**Why this priority**: This is a less frequent acquisition path but still needs distinct visual treatment to communicate that the building came from the deck rather than the market.

**Independent Test**: Can be fully tested by triggering a building draw (via quest reward or other mechanism) and observing the card fly from the lower-right corner to its lot position.

**Acceptance Scenarios**:

1. **Given** a player receives a building drawn from the deck, **When** the draw is processed, **Then** the building card appears at the lower-right corner of the screen and animates upward to its assigned lot position on the left side.
2. **Given** a drawn building animation is playing, **When** the animation completes, **Then** the building appears in its final lot position as a fully functional action space.

---

### User Story 3 - Other Players See Building Acquisition (Priority: P3)

When any player acquires a building (purchased or drawn), all other connected players see the same animation on their screens, keeping the shared game state visually consistent.

**Why this priority**: Multiplayer visual consistency is important but secondary to the acquiring player's own experience.

**Independent Test**: Can be tested by having two clients connected, one player acquires a building, and the other player observes the animation on their board.

**Acceptance Scenarios**:

1. **Given** a remote player purchases a face-up building, **When** the purchase response is received, **Then** the observing client plays the same market-to-lot animation.
2. **Given** a remote player draws a building from the deck, **When** the draw response is received, **Then** the observing client plays the lower-right-corner-to-lot animation.

---

### Edge Cases

- What happens when a building is acquired while a previous animation is still playing? The new animation should queue and play after the current one finishes.
- What happens when the constructed buildings area is paginated and the target lot is on a different page? The animation should still target the correct position; if the lot is off-screen, the building animates to the edge of the constructed area and appears on the correct page when navigated to.
- What happens if the building deck is empty and a draw is attempted? No animation plays since no building is granted (server already handles this case).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST animate a face-up building card from its market position to its assigned lot position when purchased.
- **FR-002**: System MUST animate a drawn building card from the lower-right corner of the screen to its assigned lot position.
- **FR-003**: Animations MUST use smooth easing (not linear teleportation) consistent with existing card animations in the game.
- **FR-004**: The building card MUST display the correct building image during the animation (matching the acquired building).
- **FR-005**: The building MUST become a functional action space only after the animation completes.
- **FR-006**: All connected clients MUST see the building acquisition animation, not just the acquiring player.
- **FR-007**: Multiple building acquisitions in quick succession MUST queue animations rather than overlapping them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every face-up building purchase triggers a visible card animation from the market area to the player's building area.
- **SC-002**: Every drawn building triggers a visible card animation from the lower-right corner to the player's building area.
- **SC-003**: Animation duration feels natural and consistent with existing card animations in the game (approximately 0.5-1.0 seconds).
- **SC-004**: No building appears in the constructed area before its animation completes.
- **SC-005**: All connected players see the same animation for each building acquisition event.

## Assumptions

- The existing animation manager and easing system will be reused for these animations.
- Building card images already exist and can be used as the animated sprite.
- The server already distinguishes between purchased and drawn buildings in its response messages, providing enough context for the client to choose the correct animation origin.
- Animation timing and easing style will match the existing card-pick and quest-completion animations for visual consistency.
- The "lower-right corner" for drawn buildings refers to the lower-right area of the game board or screen, representing the deck location.
