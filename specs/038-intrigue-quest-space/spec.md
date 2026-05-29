# Feature Specification: The Green Room — Intrigue Quest Space

**Feature Branch**: `038-intrigue-quest-space`  
**Created**: 2026-05-29  
**Status**: Draft  
**Input**: User description: "Add a new permanent board space requiring intrigue card play + quest selection, with board layout rearrangement"

## Clarifications

### Session 2026-05-29

- Q: What should the new board space be called? → A: "The Green Room" — fits the music/entertainment venue theme and thematically matches a space where performers prepare before going on stage.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play Intrigue and Select Quest at The Green Room (Priority: P1)

A player places their worker on The Green Room. They are first required to play an intrigue card from their hand (resolving its effect with the play-intrigue animation used at backstage). Then, as a second action, they must select one of the face-up quest cards (with the same quest-selection flow and animation used at Sunset Records or The Back Room). The player receives the selected quest card.

**Why this priority**: This is the core new gameplay mechanic. Without the two-step action flow working correctly, the space has no function.

**Independent Test**: Can be fully tested by placing a worker on The Green Room, playing an intrigue card, and selecting a quest card. Delivers the combined intrigue-play + quest-selection experience as a single worker placement.

**Acceptance Scenarios**:

1. **Given** a player has at least one intrigue card in hand and there are face-up quest cards available, **When** they place a worker on The Green Room, **Then** they are prompted to select and play an intrigue card, followed by selecting a face-up quest card.
2. **Given** the player plays an intrigue card, **When** the intrigue effect resolves, **Then** the play-intrigue animation is shown (same as backstage) and the intrigue effect is applied before proceeding to quest selection.
3. **Given** the intrigue card has been played, **When** the player is prompted for quest selection, **Then** the face-up quest display appears with the same selection flow and animations used at Sunset Records.
4. **Given** the player selects a quest card, **When** the selection is confirmed, **Then** the quest card is added to their hand, a replacement is drawn from the quest deck, and the turn advances.

---

### User Story 2 - Back Out When Unable to Play Intrigue (Priority: P1)

A player attempts to place a worker on The Green Room but does not have any intrigue cards in hand (or cannot play any). The system allows them to back out and choose a different action space instead.

**Why this priority**: Without the ability to back out, players could get stuck in an invalid state. This is critical for game flow integrity.

**Independent Test**: Can be tested by attempting to place a worker on The Green Room with no intrigue cards in hand and verifying the player can cancel and place elsewhere.

**Acceptance Scenarios**:

1. **Given** a player has no intrigue cards in hand, **When** they attempt to place a worker on The Green Room, **Then** they are allowed to back out and select a different space.
2. **Given** a player has intrigue cards but is partway through the placement, **When** they choose to back out before confirming the intrigue card play, **Then** their worker is returned and they can choose another space.
3. **Given** a player backs out, **When** they select a different space, **Then** gameplay continues normally as if they never attempted to use this space.

---

### User Story 3 - The Green Room Card Appearance (Priority: P2)

The card image for The Green Room visually resembles "The Back Room" card but displays "Play" followed by the intrigue card icon, making it clear that the player must play (not draw) an intrigue card, plus a quest card icon for the quest selection.

**Why this priority**: Visual clarity is important for player understanding, but the space functions correctly regardless of the card art.

**Independent Test**: Can be verified visually by inspecting the generated card image and confirming it shows "Play [intrigue icon]" and a quest icon.

**Acceptance Scenarios**:

1. **Given** the card image is generated, **When** displayed on the board, **Then** it shows text "Play" alongside the intrigue card icon, clearly distinguishing this from spaces that draw intrigue cards.
2. **Given** the card image is generated, **When** compared to "The Back Room" card, **Then** it uses a similar visual style and layout but with the "Play" label added before the intrigue icon.
3. **Given** the card is displayed, **When** a player views it, **Then** a quest card icon is also visible indicating the quest selection component.

---

### User Story 4 - Board Layout Rearrangement (Priority: P2)

The permanent resource/action spaces (including this new one) are rearranged into a grid display. Player-constructed buildings appear below the permanent spaces. If constructed buildings exceed the visible area, the player can page through them using the existing pagination mechanism.

**Why this priority**: The layout rearrangement accommodates the new space and improves overall board organization, but existing gameplay works without it.

**Independent Test**: Can be tested by loading a game and verifying all permanent spaces render in the new grid arrangement, and that constructed buildings appear below with working pagination.

**Acceptance Scenarios**:

1. **Given** the board loads, **When** the permanent spaces are rendered, **Then** all permanent resource/action spaces (including the new one) are arranged in the grid layout.
2. **Given** a player has constructed buildings, **When** the board is displayed, **Then** constructed buildings appear below the permanent spaces section.
3. **Given** more constructed buildings exist than fit on one page, **When** the player uses pagination controls, **Then** they can page through all their constructed buildings.
4. **Given** the board is displayed, **When** the player views the layout, **Then** all spaces are clearly visible and accessible for worker placement.

---

### Edge Cases

- What happens if the intrigue deck is empty but the player has intrigue cards in hand? The player can still use this space since they play from hand.
- What happens if all face-up quest slots are empty and the quest deck is exhausted? The quest selection step should handle this gracefully (same as existing quest spaces).
- What happens if an intrigue card effect changes the game state in a way that affects quest selection (e.g., a "reset quests" intrigue card)? The quest selection step should use the current face-up quests at the time of selection, after intrigue resolution.
- What happens during backstage reassignment phase? If a worker is reassigned from backstage to this space, the same two-step flow applies (play intrigue, then select quest).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a new permanent action space to the board that requires two sequential actions: playing an intrigue card, then selecting a face-up quest card.
- **FR-002**: When a player places a worker on this space, the system MUST first prompt them to select and play an intrigue card from their hand.
- **FR-003**: The intrigue card play MUST use the same play-intrigue animation as the backstage slots.
- **FR-004**: The intrigue card effect MUST resolve fully before the quest selection step begins.
- **FR-005**: After intrigue resolution, the system MUST prompt the player to select a face-up quest card, using the same selection flow and animations as Sunset Records or The Back Room.
- **FR-006**: The selected quest card MUST be added to the player's contract hand, and a replacement MUST be drawn from the quest deck.
- **FR-007**: If the player has no intrigue cards in hand, the system MUST allow the player to back out before committing their worker.
- **FR-008**: The player MUST be able to back out at any point before confirming the intrigue card play.
- **FR-009**: The card image for The Green Room MUST display "Play" alongside the intrigue card icon and include a quest card icon, using a visual style similar to "The Back Room."
- **FR-010**: The permanent resource/action spaces (all 9, including the new one) MUST be rearranged into a 3x3 grid display layout (3 columns, 3 rows).
- **FR-011**: Player-constructed buildings MUST appear below the permanent spaces in the board layout.
- **FR-012**: When constructed buildings exceed the visible area, the player MUST be able to page through them using pagination controls.
- **FR-013**: This space MUST have exactly 1 worker slot (consistent with other permanent spaces).

### Key Entities

- **The Green Room**: A permanent action space with a two-step action sequence (play intrigue, then select quest). Has a unique space ID, card image, and grid position.
- **Intrigue Card Play Action**: The first step of the space's action, reusing the existing intrigue card play mechanics from backstage.
- **Quest Selection Action**: The second step, reusing the existing quest selection mechanics from garage spaces.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can place a worker on The Green Room, play an intrigue card, and select a quest card in a single turn with no errors or stuck states.
- **SC-002**: Players with no intrigue cards can back out of The Green Room without losing their turn or worker.
- **SC-003**: The play-intrigue animation plays identically to how it plays on backstage slots.
- **SC-004**: The quest selection animation plays identically to how it plays on Sunset Records or The Back Room.
- **SC-005**: The card image clearly communicates "play an intrigue card" (not draw) to players viewing the board.
- **SC-006**: All permanent spaces render correctly in the new grid layout with no overlapping or missing spaces.
- **SC-007**: Constructed building pagination works correctly below the permanent spaces, supporting all existing buildings.

## Assumptions

- The new space uses the same intrigue card play mechanics as backstage (select from hand, resolve effect, animate), not a new intrigue mechanic.
- The quest selection reuses the existing face-up quest display and selection flow. No new quest selection UI is needed.
- The space has 1 worker slot, consistent with most permanent spaces.
- The existing pagination system for constructed buildings is sufficient and does not need redesign, only repositioning.
- The Green Room will be added to `config/board.json` alongside the other permanent spaces.
- "Play intrigue" means the player selects an intrigue card from their hand and its effect resolves (same as backstage), as opposed to drawing a new intrigue card from the deck.
