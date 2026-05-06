# Feature Specification: Intrigue Draw Building

**Feature Branch**: `025-intrigue-draw-building`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Let's add a building that lets you draw two intrigue cards. Come up with a good building name/description. In the building image itself, put two intrigue card icons. Player lands there, gets two intrigue cards."

## User Scenarios & Testing

### User Story 1 - Draw Two Intrigue Cards from Building (Priority: P1)

A player purchases or visits a building that grants two intrigue cards as its visitor reward. When a worker is placed on this building, the visiting player draws two intrigue cards from the intrigue deck, both of which are added to their intrigue hand.

**Why this priority**: This is the core mechanic — without the two-card draw, the building has no purpose.

**Independent Test**: Can be fully tested by placing a worker on the building in a game and verifying two intrigue cards appear in the player's intrigue hand tab.

**Acceptance Scenarios**:

1. **Given** a game with the intrigue draw building on the board, **When** a player places a worker on it, **Then** two intrigue cards are drawn from the intrigue deck and added to the visiting player's hand.
2. **Given** a player visits the intrigue draw building, **When** the action resolves, **Then** the game log displays a message indicating the player drew two intrigue cards (e.g., "Player A placed worker on [Building Name] (+2 intrigue cards)").
3. **Given** the intrigue deck has only one card remaining, **When** a player visits the building, **Then** the player draws one card (partial draw) and the system handles the depleted deck gracefully.
4. **Given** the intrigue deck is empty, **When** a player visits the building, **Then** zero cards are drawn and the player is not penalized.

---

### User Story 2 - Building Card Image with Two Intrigue Icons (Priority: P2)

The building's generated card image visually shows two intrigue card icons, making it immediately clear to players what reward the building provides.

**Why this priority**: Visual clarity helps players make strategic decisions, but the game functions without it (the text description suffices).

**Independent Test**: Can be tested by generating the card image and visually confirming two intrigue card icons appear on the building card.

**Acceptance Scenarios**:

1. **Given** the card image generator runs, **When** the intrigue draw building card is generated, **Then** the resulting PNG image contains two intrigue card icons in the reward area.
2. **Given** a player views the building card on the board or in a purchase dialog, **When** they look at the card, **Then** the two intrigue icons are clearly visible and distinguishable.

---

### User Story 3 - Building Owner Receives Bonus (Priority: P3)

When another player visits the building, the building owner receives a bonus reward as compensation for owning the property.

**Why this priority**: Owner bonuses are standard for all purchasable buildings and important for game balance, but the building works for the visitor without this.

**Independent Test**: Can be tested by having a non-owner player visit the building and verifying the owner receives the configured bonus.

**Acceptance Scenarios**:

1. **Given** Player A owns the intrigue draw building, **When** Player B places a worker on it, **Then** Player A receives the owner bonus (e.g., 2 coins or 2 VP).
2. **Given** a player visits their own building, **When** the action resolves, **Then** only the visitor reward is granted (no owner bonus for visiting your own building, per existing game rules).

---

### Edge Cases

- What happens when the intrigue deck runs out mid-draw (only 1 card left when 2 are needed)? Player draws as many as available.
- What happens when the intrigue deck is completely empty? Player draws zero cards; no error or penalty.
- What happens when intrigue hand is already at maximum capacity? Assumption: there is no hand limit for intrigue cards (consistent with existing game behavior).

## Requirements

### Functional Requirements

- **FR-001**: System MUST add a new purchasable building to the building configuration that grants two intrigue cards as its visitor reward.
- **FR-002**: When a player places a worker on this building, the system MUST draw two intrigue cards from the intrigue deck and add them to the visiting player's intrigue hand.
- **FR-003**: The game log MUST display an appropriate message when a player uses this building (e.g., "Player A placed worker on [Building Name] (+2 intrigue cards)").
- **FR-004**: The building card image MUST display two intrigue card icons in its reward area, visually communicating the building's effect.
- **FR-005**: The building MUST have a thematic name and description consistent with the game's music industry theme.
- **FR-006**: The building MUST have a purchase cost in coins, consistent with existing building pricing (3-8 coins).
- **FR-007**: The building MUST provide an owner bonus when a non-owner visits, consistent with existing building patterns.
- **FR-008**: If fewer than two intrigue cards remain in the deck, the system MUST draw as many as available without error.

### Key Entities

- **Building Tile**: A new entry in the buildings configuration with visitor_reward_special set to draw two intrigue cards, a cost, and an owner bonus.
- **Intrigue Card**: Existing entity — cards drawn from the intrigue deck into a player's hand.
- **Intrigue Deck**: Existing entity — the shared deck from which intrigue cards are drawn.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A player visiting the building receives exactly two intrigue cards (or fewer if the deck is depleted) within the normal turn resolution time.
- **SC-002**: The building card image clearly shows two intrigue card icons that are recognizable at the standard card display size.
- **SC-003**: The building integrates seamlessly with existing game flow — purchasing, visiting, owner bonuses, and game log all work identically to other buildings.
- **SC-004**: All existing game tests continue to pass after the new building is added.

## Assumptions

- The building's name and description follow the music industry / recording studio theme used by all other buildings in the game.
- The building uses the existing `visitor_reward_special` mechanism (a new special type for drawing two intrigue cards, or reuse of `draw_intrigue` with a count parameter).
- The building cost is set at 4 coins (mid-range, comparable to Chess Records Studio which draws 1 intrigue + 1 drummer).
- The owner bonus is 2 VP (valuable but not overpowered, since the visitor reward of 2 intrigue cards is already strong).
- There is no intrigue hand size limit.
- The building's thematic name is "Whisper Room" — a secretive back-channel venue where industry insiders exchange confidential intel (intrigue cards).
