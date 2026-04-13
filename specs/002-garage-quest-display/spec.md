# Feature Specification: Garage Quest Display Rework

**Feature Branch**: `002-garage-quest-display`  
**Created**: 2026-04-13  
**Status**: Draft  
**Input**: User description: "Clean up and bring functionality to 'The Garage'. Cliffwatch Inn should be called 'The Garage'. Resolve naming confusion between the quest acquisition area and the intrigue/reassignment area. The Garage has three distinct action spots and a face-up quest card display."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse and Select Quest Cards at The Garage (Priority: P1)

A player places a worker on one of three action spots at The Garage. The Garage prominently displays four face-up quest cards drawn from a shuffled quest deck. Depending on which spot the player chooses, they receive a different combination of rewards alongside selecting a quest card. This is the primary way players acquire new quests throughout the game.

**Why this priority**: Quest acquisition is essential to gameplay — without it, players are limited to their starting hand and the game stagnates. The Garage is the central location for obtaining new quests, making it the most critical piece of this feature.

**Independent Test**: Can be tested by placing a worker on each of the three Garage spots, verifying the correct reward is granted, and confirming the selected quest card moves to the player's hand.

**Acceptance Scenarios**:

1. **Given** a player places a worker on Garage Spot 1, **When** the action resolves, **Then** the player selects one of the four face-up quest cards, adds it to their hand, receives 2 Coins, and the taken card is replaced from the quest deck.
2. **Given** a player places a worker on Garage Spot 2, **When** the action resolves, **Then** the player selects one of the four face-up quest cards, adds it to their hand, draws one intrigue card from the intrigue deck, and the taken quest card is replaced from the quest deck.
3. **Given** a player places a worker on Garage Spot 3, **When** the action resolves, **Then** all four face-up quest cards are discarded and four new quest cards are drawn from the quest deck to replace them. The player does not select a quest card.
4. **Given** a Garage spot is already occupied by another player's worker, **When** a player attempts to place a worker there, **Then** they are prevented from doing so (standard worker placement rules apply — each spot holds one worker).
5. **Given** the quest deck is empty, **When** a face-up quest card slot needs to be refilled, **Then** the discard pile is shuffled to form a new deck and a card is drawn. If the discard pile is also empty, the slot remains empty.

---

### User Story 2 - Rename Cliffwatch Inn to The Garage Across the System (Priority: P1)

All references to "Cliffwatch Inn" throughout the game — in configuration files, server logic, client UI rendering, board display, and game log messages — are renamed to "The Garage." The three Cliffwatch Inn action spots become the three Garage spots with their new distinct rewards. The old "Garage" concept (intrigue card play + worker reassignment) is renamed to "Backstage" to eliminate the naming conflict.

**Why this priority**: The naming confusion between "Cliffwatch Inn" and "The Garage" creates ambiguity in the codebase and for players. This cleanup must happen alongside the functional changes to avoid inconsistent naming.

**Independent Test**: Can be verified by searching the entire codebase and configuration for any remaining references to "Cliffwatch Inn" and confirming all board labels, log messages, and config entries use the new names.

**Acceptance Scenarios**:

1. **Given** the game board is displayed, **When** the player views the quest acquisition area, **Then** it is labeled "The Garage" (not "Cliffwatch Inn").
2. **Given** a player places a worker on a Garage spot, **When** the game log records the action, **Then** the log message references "The Garage" (not "Cliffwatch Inn").
3. **Given** the board configuration file is loaded, **When** the server reads the quest acquisition spaces, **Then** the space IDs and names reference "The Garage."
4. **Given** the intrigue/reassignment area exists on the board, **When** the player views it, **Then** it is labeled with its new distinct name (not "The Garage").

---

### User Story 3 - Face-Up Quest Card Display (Priority: P1)

The Garage area on the game board includes a visible display of four face-up quest cards drawn from the shuffled quest deck at game start. All players can see these cards at any time. When a card is taken (Spots 1 or 2) or discarded (Spot 3), the display is updated accordingly. This display replaces the previous "Talent Agency" concept of 5 face-up quest cards.

**Why this priority**: The face-up display is what makes quest selection strategic rather than random. Players need to see available quests to plan their actions.

**Independent Test**: Can be tested by verifying four quest cards are drawn and displayed at game start, and that taking or discarding cards correctly updates the display.

**Acceptance Scenarios**:

1. **Given** a new game has started, **When** the game board is first displayed, **Then** four quest cards are drawn from the shuffled quest deck and displayed face-up near The Garage.
2. **Given** a player takes a face-up quest card (via Spot 1 or 2), **When** the card is added to their hand, **Then** a new quest card is drawn from the deck to fill the empty slot.
3. **Given** a player uses Spot 3 (reset), **When** the action resolves, **Then** all four face-up quest cards are discarded and four new cards are drawn from the deck.
4. **Given** the quest deck runs out of cards, **When** a face-up slot needs refilling, **Then** the discard pile is shuffled to form a new deck and cards are drawn. If the discard pile is also empty, the slot remains empty and players are visually informed.
5. **Given** any player is viewing the board (including when it is not their turn), **When** they look at The Garage area, **Then** all face-up quest cards are visible with their name, genre, cost, and VP value.

---

### Edge Cases

- What happens when the quest deck is empty and a card draw is needed?
  - All discarded quest cards are shuffled to form a new quest deck, then cards are drawn normally. Completed quest cards are never returned to the deck.
- What happens when the quest deck is empty and a player uses Spot 3 (reset)?
  - The four face-up cards are discarded. The discard pile (now including those four cards) is shuffled to form a new deck, and four new cards are drawn. If the discard pile is also empty, face-up slots remain empty.
- What happens when a player uses Spot 1 or 2 but there are no face-up quest cards remaining?
  - The player still receives the bonus reward (2 Coins or 1 intrigue card) but does not gain a quest card.
- What happens when only some of the four face-up slots have cards (partial deck depletion)?
  - The player using Spot 1 or 2 may only choose from the available face-up cards. Spot 3 discards whatever is showing, triggers a reshuffle if the deck is empty, and refills as many slots as possible.
- What happens to discarded quest cards from Spot 3?
  - Discarded quest cards are placed in a discard pile. When the quest deck is empty and a draw is needed, the discard pile is shuffled to form a new deck.

## Clarifications

### Session 2026-04-13

- Q: What should the intrigue/reassignment space (previously called "The Garage") be renamed to? → A: "Backstage" — fits the music industry theme, implies behind-the-scenes scheming for intrigue card play, and workers going backstage before reappearing elsewhere for reassignment.
- Q: How should the player's own quest and intrigue cards be displayed? → A: Toggle button to show/hide cards — hidden by default, maximizes board space.
- Q: Is there a hand size limit for quest and/or intrigue cards? → A: No limit — players can hold any number of quest and intrigue cards.
- Q: What happens when the quest deck runs out of cards? → A: All discarded quest cards are shuffled back into the deck. Completed quest cards are NOT returned — only discarded cards are recycled.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST rename all references to "Cliffwatch Inn" to "The Garage" across configuration files, server logic, client rendering, and game log messages.
- **FR-002**: The system MUST rename the existing "Garage" (intrigue card play + worker reassignment) space to a new distinct name to avoid ambiguity. "Backstage"
- **FR-003**: The Garage MUST have exactly three distinct action spots, each with different rewards:
  - Spot 1: Player selects one face-up quest card and receives 2 Coins.
  - Spot 2: Player selects one face-up quest card and draws 1 intrigue card from the intrigue deck.
  - Spot 3: All face-up quest cards are discarded and replaced with new cards drawn from the quest deck. The player does not select a quest card.
- **FR-004**: The system MUST display four face-up quest cards drawn from a shuffled quest deck, visible to all players at all times.
- **FR-005**: When a face-up quest card is taken (Spots 1 or 2), the system MUST immediately draw a replacement card from the quest deck to fill the empty slot.
- **FR-006**: When Spot 3 is used, the system MUST discard all current face-up quest cards and draw four new replacement cards from the quest deck.
- **FR-007**: Discarded quest cards (from Spot 3) MUST be placed in a discard pile. When the quest deck is empty and a card draw is needed, the entire discard pile MUST be shuffled to form a new quest deck. Completed quest cards are never returned to the deck.
- **FR-008**: Each Garage spot MUST follow standard worker placement rules — only one worker per spot per round.
- **FR-009**: If both the quest deck and discard pile are empty (all remaining quest cards are in players' hands or completed), face-up slots that cannot be refilled MUST remain visibly empty.
- **FR-010**: The face-up quest card display MUST show each card's name, genre, cost, and Victory Point value so players can make informed selections.
- **FR-011**: The client MUST render a card selection interface when a player uses Spot 1 or 2, allowing them to choose one of the available face-up quest cards.
- **FR-012**: This feature replaces the previous "Talent Agency" concept (which showed 5 face-up quest cards). The face-up count is now 4, displayed at The Garage.
- **FR-013**: The client MUST provide a toggle button that shows or hides the player's own hand of quest cards. The hand is hidden by default to maximize board space.
- **FR-014**: The client MUST provide a toggle button that shows or hides the player's own hand of intrigue cards. The hand is hidden by default to maximize board space.
- **FR-015**: Players MUST NOT be able to see other players' quest cards or intrigue cards. Only the owning player can view their own hand.
- **FR-016**: There is no hand size limit. Players may hold any number of quest cards and intrigue cards simultaneously.

### Key Entities

- **The Garage**: Renamed quest acquisition area on the game board with three distinct action spots and a display of four face-up quest cards. Replaces "Cliffwatch Inn."
- **Face-Up Quest Display**: A set of four quest cards drawn from the quest deck, visible to all players, displayed near The Garage. Cards are replaced as they are taken or discarded.
- **Quest Deck**: The shuffled deck of remaining quest (contract) cards from which face-up cards are drawn.
- **Quest Discard Pile**: Where quest cards go when discarded via Spot 3. When the quest deck is empty and a draw is needed, the discard pile is shuffled to form a new deck. Completed quest cards are never placed in the discard pile.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can identify and distinguish all three Garage spots and understand their different rewards within 30 seconds of viewing the board.
- **SC-002**: The face-up quest card display updates on all clients within 2 seconds of a card being taken or the display being reset.
- **SC-003**: No references to "Cliffwatch Inn" remain anywhere in the game UI, logs, or configuration after this change.
- **SC-004**: Players can select a specific face-up quest card in 2 or fewer clicks/interactions.
- **SC-005**: The face-up quest display correctly shows card details (name, genre, cost, VP) at all supported window sizes without truncation of critical information.

## Assumptions

- The existing quest/contract card data model and deck mechanics are already implemented and functional (from spec 001). This feature modifies how cards are displayed and acquired, not the cards themselves.
- The total number of quest cards in the game (60) does not change. Only the face-up display count changes from 5 to 4.
- The intrigue card play + worker reassignment mechanic (previously called "The Garage") remains functionally unchanged — only its name changes.
- The board configuration file format (JSON) can accommodate the new distinct spot definitions without structural changes to the schema.
- Players are already familiar with the concept of face-up card selection from the previous implementation; this feature refines and clarifies the mechanic.
