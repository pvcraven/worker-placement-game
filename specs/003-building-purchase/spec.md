# Feature Specification: Building Purchase System

**Feature Branch**: `003-building-purchase`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Building purchase system with layout rearrangement, buy/sell mechanics, owner benefits, and JSON-driven building specs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rearrange Permanent Spaces to Single Column (Priority: P1)

When the game starts, all permanent action spaces (The Merch Store, Motown, Guitar Center, Talent Show, The Rhythm Pit, Fastpass, Builder's Hall) are displayed in a single column on the left side of the board, spaced more tightly together than the current two-column layout. This frees up a second column area for purchased buildings.

**Why this priority**: This is foundational — the visual layout must be correct before purchased buildings can appear in the freed column space. Without this change, there is no room for purchased buildings.

**Independent Test**: Can be fully tested by launching a new game and verifying that all permanent spaces appear in one column on the left, tightly packed, with the second column area visibly empty and available.

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** the board renders, **Then** all permanent action spaces are arranged in a single column on the left side of the board
2. **Given** a new game starts, **When** the board renders, **Then** the spaces are visually closer together (less vertical spacing) than the previous two-column layout
3. **Given** a new game starts, **When** the board renders, **Then** the second column area (previously occupied by some permanent spaces) is empty and reserved for purchased buildings

---

### User Story 2 - Place Worker on Builder's Hall and Purchase a Building (Priority: P1)

A player places their worker on the Builder's Hall space. They are presented with the 3 face-up buildings from the building market, each showing its name, coin cost, accumulated VP, visitor reward, and owner bonus. The player selects a building they can afford, confirms the purchase, the cost is deducted from their coins, the accumulated VP is awarded to the buyer, and the building appears in the second column on the board. A replacement building is drawn from the deck to refill the market (if the deck is not empty). Newly drawn buildings start at 1 VP.

**Why this priority**: This is the core purchase mechanic — without it, no buildings can be acquired and the rest of the feature has no meaning.

**Independent Test**: Can be fully tested by starting a game, placing a worker on Builder's Hall, selecting an available building, confirming purchase, and verifying the building appears on the board and coins are deducted.

**Acceptance Scenarios**:

1. **Given** a player has a worker available and Builder's Hall is unoccupied, **When** the player places a worker on Builder's Hall, **Then** a building purchase dialog appears showing the face-up buildings (up to 3)
2. **Given** the purchase dialog is shown, **When** the player selects a building they can afford, **Then** the building is highlighted and a confirm/cancel option appears
3. **Given** the player confirms the purchase, **When** the transaction completes, **Then** the building's coin cost is deducted from the player's resources
4. **Given** the player confirms the purchase, **When** the transaction completes, **Then** the purchased building appears in the second column area on the board, owned by that player
5. **Given** the player confirms the purchase, **When** the transaction completes, **Then** the buyer receives the VP that had accumulated on that building
6. **Given** the player selects a building they cannot afford, **When** they attempt to confirm, **Then** an error message is displayed indicating insufficient coins and the purchase does not proceed
7. **Given** the purchase dialog is shown, **When** the player clicks cancel, **Then** the dialog closes and no purchase is made (the worker remains on Builder's Hall and the player still receives placement benefits, if any)
8. **Given** a building is purchased from the face-up market, **When** the deck still has buildings remaining, **Then** a new building is drawn and placed face-up with 1 VP

---

### User Story 3 - Land on a Purchased Building as a Visitor (Priority: P2)

A player (who is not the building's owner) places a worker on a purchased building. The visiting player receives the building's visitor reward (resources as defined in the building spec). The building's owner simultaneously receives the owner bonus (a smaller reward, also defined in the building spec).

**Why this priority**: This delivers the gameplay value of purchased buildings — they become new action spaces that benefit both the visitor and the owner.

**Independent Test**: Can be fully tested by having Player A purchase a building, then Player B places a worker on that building. Verify Player B receives the visitor reward and Player A receives the owner bonus.

**Acceptance Scenarios**:

1. **Given** a purchased building exists on the board and is unoccupied, **When** a non-owner player places a worker on it, **Then** the visiting player receives the visitor reward defined for that building
2. **Given** a purchased building exists on the board, **When** a non-owner player places a worker on it, **Then** the building's owner receives the owner bonus defined for that building
3. **Given** a purchased building exists on the board, **When** the building's owner places a worker on their own building, **Then** the owner receives the visitor reward but does NOT receive the owner bonus

---

### User Story 4 - Building Specs Driven by JSON Configuration (Priority: P2)

All purchasable buildings are defined in a JSON configuration file. Each building entry specifies its name (music-related famous place), cost, visitor reward (what the landing player gets), and owner bonus (what the owner gets when a different player lands on it). The owner bonus is smaller than the visitor reward.

**Why this priority**: JSON-driven configuration allows game balancing and content updates without code changes. The building data already follows this pattern and needs to be validated.

**Independent Test**: Can be tested by modifying the JSON file to add or change a building, restarting the game, and verifying the new building appears with correct stats in the purchase dialog and functions correctly when placed and visited.

**Acceptance Scenarios**:

1. **Given** the buildings JSON file defines a building with specific visitor rewards and owner bonuses, **When** that building is purchased and placed, **Then** landing on it grants the exact rewards specified in the JSON
2. **Given** the buildings JSON file is updated with a new building entry, **When** the game loads, **Then** the new building appears in the available pool
3. **Given** a building's JSON entry, **When** comparing visitor reward to owner bonus, **Then** the owner bonus is smaller in total value than the visitor reward

---

### Edge Cases

- What happens when a player tries to purchase a building but all building lots are occupied? The purchase dialog should indicate no lots are available, or the option to purchase should be disabled.
- What happens when the building deck is exhausted and fewer than 3 buildings are face-up? The remaining face-up buildings are still purchasable. When no face-up buildings remain, the Builder's Hall space should still be landable but the purchase dialog should inform the player there are no buildings to buy.
- What happens if a player has exactly enough coins for a building? The purchase should succeed normally.
- What happens if multiple buildings have been purchased and the second column fills up? Additional buildings should flow into subsequent columns following the existing layout algorithm.
- What happens to VP on a newly drawn replacement building? It starts at 1 VP regardless of the current round number.
- What happens if no buildings are face-up (deck and market both empty) and a player lands on Builder's Hall? The player is informed no buildings are available; no purchase occurs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render all permanent action spaces in a single column on the left side of the board with reduced vertical spacing
- **FR-002**: System MUST reserve a second column area for purchased buildings
- **FR-003**: System MUST allow a player to place a worker on Builder's Hall, triggering a building purchase interaction
- **FR-004**: System MUST display a purchase dialog showing the face-up buildings (up to 3) with their name, coin cost, accumulated VP, visitor reward, and owner bonus
- **FR-005**: System MUST validate that the purchasing player has sufficient coins before completing a purchase
- **FR-006**: System MUST display an error message if the player cannot afford the selected building
- **FR-007**: System MUST allow the player to cancel the purchase without penalty
- **FR-008**: System MUST deduct the building's coin cost from the player upon confirmed purchase
- **FR-009**: System MUST place the purchased building in the next available lot in the second column area
- **FR-010**: System MUST track building ownership (which player purchased each building)
- **FR-011**: System MUST allow any player to place a worker on a purchased building as an action space
- **FR-012**: System MUST grant the visiting player the building's visitor reward when they land on a purchased building
- **FR-013**: System MUST grant the building owner the owner bonus when a different player lands on their building
- **FR-014**: System MUST NOT grant the owner bonus when the owner lands on their own building
- **FR-015**: System MUST load all building definitions (name, cost, visitor reward, owner bonus) from a JSON configuration file
- **FR-016**: All purchasable buildings MUST have names referencing famous music-related places
- **FR-017**: System MUST maintain a face-up display of 3 buildings available for purchase at any time
- **FR-018**: System MUST draw a replacement building from the deck when a face-up building is purchased, if the deck is not empty
- **FR-019**: When the building deck is exhausted, no replacement is drawn and fewer than 3 buildings may be face-up
- **FR-020**: Each face-up building MUST start with 1 VP when it enters the market
- **FR-021**: At the end of each round, each face-up building in the market MUST gain +1 VP
- **FR-022**: When a building is purchased, the buyer MUST receive the VP accumulated on that building
- **FR-023**: The purchase dialog MUST display the current accumulated VP on each face-up building
- **FR-024**: The "Builder's Hall" space MUST be renamed to "Real Estate Listings" across all display names, configuration, and code references

### Key Entities

- **Building Tile**: A purchasable game piece with a name, coin cost (3-8 coins, no resource cost), accumulated VP, visitor reward (resources granted to any player landing on it), and owner bonus (resources granted to the owner when someone else lands on it). Cost scales with reward value — buildings granting more resources cost more coins. VP starts at 1 when the building enters the face-up market and increases by 1 each round it remains unpurchased. Defined in JSON configuration.
- **Building Lot**: An empty slot on the board where a purchased building can be placed. Located in the second column area freed by rearranging permanent spaces.
- **Action Space**: A location on the board where a player can place a worker. Includes both permanent spaces and constructed buildings.
- **Builder's Hall**: A permanent action space that enables the building purchase interaction when a worker is placed on it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All permanent action spaces display in a single column layout when the game starts
- **SC-002**: A player can complete the full building purchase flow (select, confirm, see building placed) within 15 seconds
- **SC-003**: 100% of building purchases correctly deduct the exact coin cost from the buyer
- **SC-004**: When a non-owner visits a purchased building, both the visitor reward and owner bonus are granted correctly every time
- **SC-005**: When an owner visits their own building, they receive the visitor reward but never the owner bonus
- **SC-006**: All building data (names, costs, rewards) matches the JSON configuration file with zero discrepancies
- **SC-007**: Players can cancel a building purchase at any point before confirmation without losing resources
- **SC-008**: Face-up buildings that remain unpurchased for N rounds display exactly N+1 VP (1 base + N accumulated)
- **SC-009**: When a building is purchased, the buyer's VP total increases by the exact amount shown on the building

## Clarifications

### Session 2026-04-14

- Q: What do buildings cost? → A: Buildings cost coins only (3-8 coin range), never resources. Higher-reward buildings cost more coins.
- Q: How many buildings are face-up at any time? → A: 3 buildings are face-up. When one is purchased, the next is drawn from the deck. If the deck is empty, no replacement is drawn.
- Q: Do buildings provide victory points? → A: Yes. Each face-up building starts at 1 VP and gains +1 VP per round it remains unpurchased. The buyer receives the accumulated VP at time of purchase.
- Q: What should Builder's Hall be renamed to? → A: "Real Estate Listings" — rename applies to display name, space ID, and all references in code and config.

## Assumptions

- The existing buildings JSON file already contains appropriate music-themed building names and balanced reward/bonus values
- The existing server-side purchase validation and owner bonus mechanics are functional and can be relied upon
- The game shuffles all buildings into a deck at game start, reveals 3 face-up as the building market, and replenishes from the deck after each purchase
- Building lots are filled left-to-right, top-to-bottom in the second column area
- Garage spaces (bottom row) and backstage slots are not affected by the column rearrangement
- The number of available building lots (currently 10) is sufficient for a typical game
