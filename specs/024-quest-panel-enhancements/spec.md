# Feature Specification: Quest Panel Enhancements

**Feature Branch**: `024-quest-panel-enhancements`
**Created**: 2026-05-06
**Status**: Draft
**Input**: User description: "Update the quest display on the right-side panel and other places. Scrollable quest list, sub-tabs for other players' quests, and genre-match star indicator."

## Clarifications

### Session 2026-05-06

- Q: What should the star indicator look like? → A: Yellow star PNG graphic, rendered as a sprite in a sprite list.
- Q: Should opponents' uncompleted quest hands be visible? → A: Yes, show everything — full quest card details for all opponents.

## User Scenarios & Testing

### User Story 1 - Scrollable Quest Card Grid (Priority: P1)

When a player has more quest cards than fit in the visible area of the Quests tab (currently limited to ~6 cards), the player can scroll through all their quest cards using the mouse wheel.

**Why this priority**: Players currently cannot see all their quest cards if they have more than 6, which directly impacts gameplay decisions. This is the most critical usability gap.

**Independent Test**: Acquire 7+ quest cards in a game. Open the Quests tab. Verify all cards are accessible by scrolling down with the mouse wheel. Scroll back up to see the first cards again.

**Acceptance Scenarios**:

1. **Given** a player has 8 quest cards and the Quests tab is open, **When** the player scrolls down with the mouse wheel, **Then** the card grid scrolls to reveal the hidden cards below the visible area.
2. **Given** a player has scrolled down in the Quests tab, **When** the player scrolls up with the mouse wheel, **Then** the card grid scrolls back to show the earlier cards.
3. **Given** a player has 4 quest cards (all visible without scrolling), **When** the player scrolls with the mouse wheel, **Then** nothing happens (no over-scroll).
4. **Given** a player has scrolled to the bottom of their quest list, **When** the player scrolls down further, **Then** the view does not scroll past the last card.

---

### User Story 2 - Sub-Tabs for Other Players' Quests (Priority: P2)

The Quests tab gains sub-tabs allowing a player to view their own quests, as well as the completed and uncompleted quests of each other player in the game.

**Why this priority**: Knowing what quests opponents are pursuing or have completed is strategically important. Currently players have no visibility into opponent quest hands.

**Independent Test**: In a 3-player game, open the Quests tab. Verify sub-tabs appear for "My Quests", "Player B", and "Player C". Click on another player's sub-tab and verify their completed and uncompleted quests are displayed.

**Acceptance Scenarios**:

1. **Given** a 3-player game, **When** the player opens the Quests tab, **Then** sub-tabs appear: one for the player's own quests (selected by default) and one for each opponent.
2. **Given** the player clicks an opponent's sub-tab, **When** that opponent has 2 completed and 3 uncompleted quests, **Then** both completed and uncompleted quests are shown, with a visual distinction between completed and uncompleted quests.
3. **Given** the player is viewing an opponent's quests, **When** the player clicks back to their own sub-tab, **Then** their own quest cards are displayed as before.
4. **Given** the player is viewing an opponent's quests, **When** the opponent completes a quest during play, **Then** the display updates to reflect the new state when the tab is refreshed.

---

### User Story 3 - Genre Match Star Indicator (Priority: P3)

When viewing the player's own quest cards or face-up quest cards on the board, a yellow star appears in the upper-left corner of any quest card whose genre matches one of the player's producer card bonus genres. The star is a generated PNG graphic rendered as a sprite. This indicator does not appear when viewing other players' quests.

**Why this priority**: Helps players quickly identify which quests will earn them bonus VP from their producer card, reducing mental overhead during quest selection. Lower priority because it is a convenience enhancement rather than a missing capability.

**Independent Test**: With a producer card that gives bonuses for "rock" and "funk" genres, verify that rock and funk quest cards display a star in the upper-left corner in the player's hand and on the board face-up quests. Verify no stars appear when viewing an opponent's quests.

**Acceptance Scenarios**:

1. **Given** the player's producer card grants bonuses for "rock" genre, **When** the player views their own Quests tab, **Then** all rock-genre quest cards display a star in the upper-left corner.
2. **Given** the player's producer card grants bonuses for "rock" and "funk" genres, **When** the player looks at face-up quest cards on the board (near the Garage), **Then** rock and funk quest cards display a star in the upper-left corner.
3. **Given** the player is viewing an opponent's quests via the sub-tab, **When** the opponent has quest cards matching the player's producer genre, **Then** no star indicators appear (to avoid revealing the player's producer card strategy).
4. **Given** the player's producer card grants no bonus for "jazz" genre, **When** a jazz quest card is in the player's hand, **Then** no star appears on that card.

---

### Edge Cases

- What happens when the player has zero quest cards? The Quests tab shows an empty state message, no scroll is needed, no sub-tabs affected.
- What happens when an opponent has zero quests (completed and uncompleted)? Their sub-tab shows an empty state message.
- What happens with scrolling and the Intrigue/Completed tabs? Scrolling should also work on the Intrigue and Completed tabs if they overflow, using the same mechanism.
- What happens when a player's producer card covers all 5 genres (e.g., Brian Eno)? All quest cards in the player's hand and on the board show the star.

## Requirements

### Functional Requirements

- **FR-001**: The quest card grid in the side panel MUST be scrollable via mouse wheel when cards overflow the visible area.
- **FR-002**: Scrolling MUST be bounded — the player cannot scroll past the first card or past the last card.
- **FR-003**: Scrolling MUST also work on the Intrigue and Completed tabs when their cards overflow the visible area.
- **FR-004**: The Quests tab MUST display sub-tabs: one for the player's own quests (default) and one for each opponent in the game.
- **FR-005**: Opponent sub-tabs MUST display both completed and uncompleted quest cards for that opponent, with full card details visible and a clear visual distinction between completed and uncompleted.
- **FR-006**: Sub-tab labels MUST show the opponent's player name.
- **FR-007**: A yellow star indicator MUST appear in the upper-left corner of quest cards whose genre matches the player's producer card bonus genres. The star MUST be a generated PNG graphic rendered as a sprite in a sprite list.
- **FR-008**: The star indicator MUST appear on the player's own quest cards in the Quests tab and on face-up quest cards on the board.
- **FR-009**: The star indicator MUST NOT appear when viewing opponent quests via sub-tabs.
- **FR-010**: The scroll position MUST reset to the top when switching between sub-tabs or main tabs.

### Key Entities

- **Producer Card**: Secret card assigning 1+ bonus genres and a VP-per-contract value. Only visible to the owning player during gameplay.
- **Quest Card (ContractCard)**: Has a `genre` field (jazz, pop, soul, funk, rock) that determines producer card bonus eligibility.
- **Sub-Tab State**: Tracks which player's quests are currently displayed in the Quests tab.
- **Scroll Offset**: Tracks the vertical scroll position within a card grid, measured in pixels or rows.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can view all quest cards in their hand regardless of quantity (no hidden cards).
- **SC-002**: Players can view any opponent's completed and uncompleted quests within 2 clicks (tab + sub-tab).
- **SC-003**: Genre-matching quest cards are visually identifiable within 1 second of viewing the panel or board, without requiring the player to recall their producer card's genres.
- **SC-004**: Scrolling through quest cards feels responsive with no perceptible delay.

## Assumptions

- The existing tabbed side panel layout and tab structure (Log, Quests, Intrigue, Completed, Producer) remain unchanged; sub-tabs are added within the Quests tab only.
- Opponent quest card data (completed and uncompleted) must be fully visible to all clients. The server currently hides opponent uncompleted quest hands — this filter must be removed so full card details are sent to all players.
- The star indicator is a yellow star PNG graphic rendered as a sprite in a sprite list, drawn on top of the card sprite — it does not modify the card image files.
- Mouse wheel scrolling is the only scroll mechanism needed (no click-drag scrolling or scroll bar).
- The producer card information is already available to the client for the owning player.
