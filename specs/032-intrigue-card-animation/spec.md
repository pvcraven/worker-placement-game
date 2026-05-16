# Feature Specification: Intrigue Card Animation

**Feature Branch**: `032-intrigue-card-animation`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: User description: "Improve animation around intrigue cards — create a full-size face-down intrigue card image, animate drawing (lower-right to center to upper-left), and animate playing (upper-left to center to lower-right). Face-down for opponents, face-up for the drawing player and when playing."

## Clarifications

### Session 2026-05-16

- Q: Should animations include sound? → A: Yes, play a card drag sound (card1.mp3) when the animation starts
- Q: Should animations use the event queue system? → A: Yes, use the existing event queue for sequencing animations

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Draw Intrigue Card Animation (Own Card) (Priority: P1)

As a player who draws an intrigue card, I see a face-up intrigue card fly from the lower-right corner of the screen to the center, pause at double scale so I can read it, then shrink and fly off to the upper-left where the player info area is — confirming it has been added to my hand.

**Why this priority**: This is the core visual feedback loop for drawing intrigue cards. Without it, players receive cards without any visual confirmation of what they drew. This is the most common intrigue animation scenario and delivers the most value.

**Independent Test**: Draw an intrigue card as the active player and verify the full animation plays with the correct card face visible.

**Acceptance Scenarios**:

1. **Given** a player draws an intrigue card during their turn, **When** the draw event is processed, **Then** a face-up intrigue card (showing the actual card art) appears in the lower-right area and animates to screen center while scaling up to double size, accompanied by a card drag sound
2. **Given** the card has arrived at screen center at double scale, **When** the pause completes, **Then** the card shrinks back down and flies to the upper-left player info area before disappearing
3. **Given** the animation is in progress, **When** the card is at center, **Then** no other game events process until the animation sequence completes

---

### User Story 2 - Draw Intrigue Card Animation (Opponent's Card) (Priority: P1)

As a player watching an opponent draw an intrigue card, I see a face-down intrigue card (full-size back image) fly from the lower-right to center, pause at double scale, then shrink and fly to the upper-left — so I know an opponent drew a card but cannot see what it is.

**Why this priority**: Equal priority with P1 because draw events happen for all players simultaneously. The face-down image must exist and display correctly for opponent draws, which is the majority case in multiplayer.

**Independent Test**: Have an opponent draw an intrigue card and verify the animation shows a face-down card back instead of the actual card.

**Acceptance Scenarios**:

1. **Given** an opponent draws an intrigue card, **When** the draw event is processed on my screen, **Then** a face-down intrigue card image animates from the lower-right to screen center at double scale, accompanied by a card drag sound
2. **Given** the face-down card is paused at center, **When** the pause completes, **Then** the card shrinks and flies to the upper-left player info area
3. **Given** a multiplayer game with three or more players, **When** any non-local player draws an intrigue card, **Then** all other players see the face-down version of the animation

---

### User Story 3 - Play Intrigue Card Animation (Priority: P2)

As any player in the game, when someone plays an intrigue card, I see the card (face-up for all players) fly from the upper-left player info area to the center of the screen, pause at double scale so everyone can read the card being played, then shrink and fly off toward the lower-right corner.

**Why this priority**: Playing intrigue cards is less frequent than drawing them, and the game already has a card selection dialog. This animation adds drama and ensures all players see what card was played, but the game functions without it.

**Independent Test**: Play an intrigue card and verify the face-up animation sequence goes from upper-left to center to lower-right for all connected players.

**Acceptance Scenarios**:

1. **Given** a player plays an intrigue card, **When** the play event is processed, **Then** all players (including the one who played it) see a face-up card fly from the upper-left player info area to screen center while scaling up to double size, accompanied by a card drag sound
2. **Given** the played card is paused at center at double scale, **When** the pause completes, **Then** the card shrinks and flies off toward the lower-right corner before disappearing
3. **Given** the animation is playing, **When** it completes, **Then** the intrigue effect resolution proceeds (target selection, resource changes, etc.)

---

### User Story 4 - Full-Size Face-Down Intrigue Card Image (Priority: P1)

A full-size face-down intrigue card image must be generated matching the same dimensions as face-up intrigue cards. This image is used as the card back during opponent draw animations and is consistent with the game's visual style.

**Why this priority**: The face-down image is a prerequisite for the draw animation (User Story 2). Without it, opponent draw animations cannot display a proper card back.

**Independent Test**: Run the card image generator and verify a full-size face-down intrigue card PNG is produced at the correct dimensions, visually consistent with the existing small intrigue icon style.

**Acceptance Scenarios**:

1. **Given** the card image generator runs, **When** intrigue card images are generated, **Then** a full-size face-down intrigue card image is produced at the same pixel dimensions as face-up intrigue cards
2. **Given** the face-down image is generated, **When** viewed alongside face-up intrigue cards, **Then** it is visually consistent in size, shape, and border styling but clearly distinguishable as a card back (featuring the "I" indicator or similar identifying mark)

---

### Edge Cases

- What happens when multiple intrigue cards are drawn at once (e.g., a quest reward grants 2 intrigue cards)? Each card animates sequentially through the event queue before the next one begins.
- What happens if the player info area is not visible or the window is resized during animation? The animation targets the player marker position as stored at animation start time.
- What happens if a player disconnects mid-animation? The animation completes or is cancelled gracefully without blocking the event queue.
- What happens during rapid card draws in succession? The event queue ensures each animation completes before the next starts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The card image generator MUST produce a full-size face-down intrigue card image with the same pixel dimensions as face-up intrigue cards
- **FR-002**: The face-down image MUST feature a visual indicator (such as the existing "I" motif) that identifies it as an intrigue card back
- **FR-003**: When a player draws an intrigue card, the system MUST display a draw animation showing the card flying from the lower-right screen area to the screen center while scaling up to double size
- **FR-004**: After arriving at center, the draw animation MUST pause the card at double scale for a readable duration before continuing
- **FR-005**: After the center pause, the draw animation MUST shrink the card back to normal scale and fly it off-screen toward the upper-left player info area
- **FR-006**: The draw animation MUST show the face-up card (actual card art) to the player who drew the card
- **FR-007**: The draw animation MUST show the face-down card back to all other players
- **FR-008**: When a player plays an intrigue card, the system MUST display a play animation showing the card flying from the upper-left player info area to screen center while scaling up to double size
- **FR-009**: After arriving at center, the play animation MUST pause the card at double scale for a readable duration
- **FR-010**: After the center pause, the play animation MUST shrink the card and fly it off-screen toward the lower-right corner
- **FR-011**: The play animation MUST show the card face-up to all players
- **FR-012**: Both draw and play animations MUST integrate with the event queue so that no other game events process until the animation completes
- **FR-013**: When multiple intrigue cards are drawn at once, each card MUST animate sequentially
- **FR-014**: Both draw and play animations MUST play a card drag sound effect at the start of the entry phase

### Key Entities

- **Face-Down Intrigue Card Image**: A generated PNG matching the dimensions of face-up intrigue cards, serving as the card back for draw animations when the viewer is not the drawing player
- **Draw Animation Sequence**: A three-phase animation (entry from lower-right, center pause at double scale, exit to upper-left) triggered when any player draws an intrigue card
- **Play Animation Sequence**: A three-phase animation (entry from upper-left, center pause at double scale, exit to lower-right) triggered when any player plays an intrigue card

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All players see an animation whenever an intrigue card is drawn or played, with zero silent/invisible card transactions
- **SC-002**: The drawing player can read their own drawn intrigue card during the center pause phase, while opponents cannot see the card face
- **SC-003**: All players can read a played intrigue card during the center pause phase
- **SC-004**: The animation timing feels natural and matches the existing quest card animation pacing (entry, readable pause, exit)
- **SC-005**: The face-down intrigue card image is visually recognizable as an intrigue card back at both normal and double scale
- **SC-006**: Multiple sequential intrigue card draws each animate individually without overlapping or skipping
- **SC-007**: A card drag sound plays audibly at the start of every intrigue card draw and play animation

## Assumptions

- The existing quest card animation pattern (three-phase: entry, pause, exit) is the established reference for card animation behavior and timing
- The player info area in the upper-left is the correct visual anchor for "where intrigue cards live" from the player's perspective
- The lower-right corner represents the intrigue card draw pile area conceptually, even if no visible pile is rendered there
- The existing event queue system handles animation sequencing and will be used for intrigue animations
- The card image generator already produces face-up intrigue cards; only the face-down back image is new
- The "I" motif from the existing small intrigue icon is the appropriate visual identity for the face-down card
