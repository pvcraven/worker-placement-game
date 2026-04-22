# Feature Specification: Building Revamp

**Feature Branch**: `016-building-revamp`  
**Created**: 2026-04-22  
**Status**: Draft  
**Input**: Revamp all purchasable buildings with new balance, new mechanics (accumulating resources), and 20 new building designs across 5 categories.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accumulating Resource Buildings (Priority: P1)

A player purchases a building that uses the new accumulating-resource mechanic. When purchased, the building receives an initial stock of resources. At the start of each subsequent round, additional resources are added to the building's stock. When any player places a worker on that building, they collect all accumulated resources and the building resets to zero. The building owner receives a fixed owner bonus regardless of how many resources were accumulated.

**Why this priority**: This is the most novel mechanic being introduced. It fundamentally changes building strategy by rewarding patience (letting resources build up) and creates tension around timing (visit now or wait for more). All 6 accumulating buildings depend on this core mechanic.

**Independent Test**: Can be fully tested by purchasing an accumulating building, advancing rounds without visiting it, then visiting it and verifying the correct accumulated amount is received and the building resets.

**Acceptance Scenarios**:

1. **Given** a player purchases an accumulating guitarist building, **When** the building is placed, **Then** the building starts with 2 guitarists in stock.
2. **Given** an accumulating building has 2 guitarists and a new round begins with no one having visited, **When** the round-start resource phase runs, **Then** the building now has 4 guitarists in stock.
3. **Given** an accumulating building has 6 guitarists in stock, **When** a player places a worker on it, **Then** the player receives 6 guitarists and the building resets to 0 in stock.
4. **Given** a player visits an accumulating building owned by another player, **When** the visitor collects resources, **Then** the building owner receives their fixed owner bonus (e.g., 1 guitarist) regardless of how many resources were accumulated.
5. **Given** a player acquires a building through a non-purchase method (e.g., quest reward granting a free building), **When** the building enters play, **Then** its initial stock is 0 (not the purchase-start amount).
6. **Given** the building owner places their own worker on their accumulating building, **When** they collect resources, **Then** they receive the accumulated resources but do NOT receive the owner bonus (owner bonus is only for when other players visit).

---

### User Story 2 - Standard Reward Buildings (Priority: P2)

Players can purchase and use buildings that provide straightforward resource rewards, including combinations of musicians, coins, quest draws, and intrigue card draws. These replace or rebalance many existing buildings.

**Why this priority**: Standard buildings are the bread-and-butter of the building market. They use existing mechanics (fixed rewards, draw_contract, draw_intrigue) and are simpler to implement than choice-based buildings.

**Independent Test**: Can be tested by purchasing a standard building, placing a worker on it, and verifying the correct resources, quest draw, or intrigue draw is granted to the visitor and owner.

**Acceptance Scenarios**:

1. **Given** a player places a worker on a building that rewards "1 singer and pick 1 face-up quest," **When** the reward resolves, **Then** the player receives 1 singer and is prompted to pick a face-up quest card.
2. **Given** a player places a worker on a building that rewards "1 drummer and 1 intrigue card," **When** the reward resolves, **Then** the player receives 1 drummer and draws 1 intrigue card.
3. **Given** a player places a worker on a building that rewards "2 bassists + 2 coins," **When** the reward resolves, **Then** the player receives 2 bassists and 2 coins, and the owner receives 1 bassist.
4. **Given** a player places a worker on a building that rewards "1 guitarist, 1 bassist, 2 coins," **When** the reward resolves, **Then** the player receives all listed resources and the owner gets their choice of guitarist or bassist.

---

### User Story 3 - Resource Choice Buildings (Priority: P3)

Players can purchase and use buildings where the visitor must make choices about which resources to receive. This includes "pick X from allowed types" and "spend coins to get a choice of resources" patterns.

**Why this priority**: Choice buildings add strategic depth and reuse the existing resource choice UI. They depend on the choice/combo mechanics already implemented for buildings like Musician's Union Hall and Guitar & Bass Workshop.

**Independent Test**: Can be tested by placing a worker on a choice building, making a selection in the resource choice dialog, and verifying the correct resources are granted.

**Acceptance Scenarios**:

1. **Given** a player places a worker on a "spend 2 coins, choose 2 singers or drummers" building, **When** the reward phase begins, **Then** the player pays 2 coins and selects a combination of 2 from singers and drummers.
2. **Given** a player places a worker on a "spend 4 coins, choose 4 singers or drummers" building, **When** the reward phase begins, **Then** the player pays 4 coins and selects a combination of 4 from singers and drummers.
3. **Given** a player places a worker on a "pick 1 of G/B/S/D and get 2 coins" building, **When** the reward resolves, **Then** the player picks 1 resource type and also receives 2 coins, and the owner gets 2 VP.
4. **Given** a player places a worker on a "get 1 guitarist, pick 1 of G/B/D/S" building, **When** the reward resolves, **Then** the player receives 1 guitarist plus 1 additional resource of their choice.
5. **Given** a player places a worker on a "get any 2 combo of G/B/D/S" building, **When** the reward resolves, **Then** the player picks any 2 resources and the owner picks any 1 resource.

---

### User Story 4 - Multi-Resource Buildings with Owner Choice (Priority: P4)

Players can purchase premium buildings (cost 8 coins) that give the visitor a generous multi-resource reward while the building owner gets to choose between two resource types as their bonus.

**Why this priority**: These are high-cost, high-reward buildings that add strategic depth to the owner bonus system. They require owner choice UI support, which may extend existing mechanics.

**Independent Test**: Can be tested by having one player own the building and another visit it, verifying the visitor gets fixed resources and the owner is prompted to choose between two resource types.

**Acceptance Scenarios**:

1. **Given** Player B places a worker on Player A's "2 guitarists + 1 singer" building, **When** rewards resolve, **Then** Player B gets 2 guitarists and 1 singer, and Player A is prompted to choose between 1 guitarist or 1 singer.
2. **Given** Player B places a worker on Player A's "2 bassists + 1 drummer" building, **When** rewards resolve, **Then** Player B gets 2 bassists and 1 drummer, and Player A chooses between 1 bassist or 1 drummer.
3. **Given** Player B places a worker on Player A's "2 bassists + 1 singer" building, **When** rewards resolve, **Then** Player B gets 2 bassists and 1 singer, and Player A chooses between 1 bassist or 1 singer.
4. **Given** Player B places a worker on Player A's "2 guitarists + 1 drummer" building, **When** rewards resolve, **Then** Player B gets 2 guitarists and 1 drummer, and Player A chooses between 1 guitarist or 1 drummer.

---

### User Story 5 - Exchange Buildings (Priority: P5)

Players can use buildings that let them return resources to gain different ones (the exchange mechanic), rebalancing the existing Talent Agency pattern.

**Why this priority**: Exchange buildings already have a working mechanic (Talent Agency). This story adds a new variation and rebalances the existing one.

**Independent Test**: Can be tested by placing a worker on an exchange building, selecting resources to return, selecting resources to gain, and verifying the transaction completes correctly.

**Acceptance Scenarios**:

1. **Given** a player places a worker on a "return 2, pick 3" exchange building, **When** the exchange resolves, **Then** the player returns 2 resources of any type and receives 3 resources of any type, and the owner gets 2 coins.

---

### User Story 6 - VP-Awarding Buildings (Priority: P6)

Some buildings award victory points directly as part of their reward, either as a fixed visitor reward, owner bonus, or via the accumulating mechanic.

**Why this priority**: VP rewards are a new reward type for buildings (currently only quests and intrigue cards award VP). This requires extending the reward system to handle VP.

**Independent Test**: Can be tested by placing a worker on a VP-awarding building and verifying the player's VP total increases.

**Acceptance Scenarios**:

1. **Given** a player visits the accumulating drummer building (owner gets 2 VP), **When** the owner bonus resolves, **Then** the building owner gains 2 victory points.
2. **Given** a player visits the "pick 1 resource, get 2 coins" building (owner gets 2 VP), **When** the owner bonus resolves, **Then** the owner gains 2 victory points.
3. **Given** the accumulating VP building has 9 VP stocked, **When** a player visits, **Then** the visitor receives 9 VP and can also pick 1 face-up quest card, and the owner gets 2 VP.

---

### Edge Cases

- What happens when a player cannot afford the coin cost on a spend-to-get building (e.g., has fewer than 2 coins for a "spend 2 coins" building)? The player should not be able to place a worker there if they cannot pay.
- What happens when the building market runs out of buildings to purchase? Follow existing behavior.
- What happens when an accumulating building's owner visits their own building? They collect the accumulated resources but do NOT receive the owner bonus.
- What happens when an accumulating building has 0 resources (e.g., just visited, or acquired free and not yet had a round start)? The visitor receives 0 of the accumulated resource type.
- How are accumulated resources displayed on the board? The building space should show the current stock count so players can see how many resources have accumulated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a new "accumulating" building type where resources stock up each round until collected by a visitor.
- **FR-002**: Accumulating buildings MUST receive their initial resource stock when purchased, and start at zero when acquired through non-purchase means.
- **FR-003**: At the start of each round, the system MUST add the per-round increment to every accumulating building currently in play.
- **FR-004**: When a player visits an accumulating building, the system MUST transfer all accumulated resources to the visitor and reset the building's stock to zero.
- **FR-005**: Building owner bonuses MUST be awarded when any other player visits the building, not when the owner visits their own building.
- **FR-006**: The system MUST support VP (victory points) as a building reward type for both visitor rewards and owner bonuses.
- **FR-007**: The system MUST support owner bonus choices where the owner selects between two resource types.
- **FR-008**: The system MUST support "spend coins to receive choice resources" as a building visitor mechanic.
- **FR-009**: Buildings with a coin cost for the visitor MUST prevent worker placement if the player cannot afford the cost.
- **FR-010**: The building market MUST contain the 20 new buildings as defined, with their specified costs, visitor rewards, and owner bonuses.
- **FR-011**: Existing building names from buildings.json SHOULD be reused where thematically appropriate; new names should follow the same music-industry venue/studio theme.
- **FR-012**: The accumulating VP building MUST also allow the visitor to pick 1 face-up quest card in addition to collecting accumulated VP.
- **FR-013**: The system MUST display the current accumulated resource count on accumulating buildings so players can see the stock.
- **FR-014**: Existing tests for building balance MUST still run; test results should be reported but tests should NOT be modified.
- **FR-015**: Accumulated resources MUST have no cap; they grow indefinitely until a player visits the building.

### Key Entities

- **Building**: A purchasable game location with an ID, name, description, cost, visitor reward, owner bonus, and optional special mechanics. Extended with accumulating behavior, VP rewards, and owner choice bonuses.
- **Accumulated Stock**: A per-building counter tracking how many resources (or VP) have built up since last visited. Resets to zero on visit.
- **Building Type**: Distinguishes standard buildings from accumulating buildings, determining round-start behavior.
- **Owner Bonus Choice**: An optional owner bonus variant where the owner selects one resource type from a set of allowed types instead of receiving a fixed reward.

## The 20 New Buildings

### Category A: Accumulating Resource Buildings (6 buildings, all cost 4 coins)

| # | Accumulates | Per Round | Initial Stock | Visitor Gets | Owner Gets |
|---|-------------|-----------|---------------|-------------|------------|
| A1 | Guitarists | +2 | 2 | All accumulated guitarists | 1 guitarist |
| A2 | Bassists | +2 | 2 | All accumulated bassists | 1 bassist |
| A3 | Singers | +1 | 1 | All accumulated singers | 1 intrigue card |
| A4 | Drummers | +1 | 1 | All accumulated drummers | 2 VP |
| A5 | Coins | +4 | 4 | All accumulated coins | 2 coins |
| A6 | VP | +3 | 3 | All accumulated VP + pick 1 face-up quest | 2 VP |

### Category B: Standard Reward Buildings (6 buildings)

| # | Cost | Visitor Gets | Owner Gets |
|---|------|-------------|------------|
| B1 | 3 | 1 singer + pick 1 face-up quest | 2 coins |
| B2 | 3 | 1 drummer + 1 intrigue card | 1 intrigue card |
| B3 | 3 | 2 bassists + 2 coins | 1 bassist |
| B4 | 4 | 1 guitarist + 1 bassist + 2 coins | Owner choice: G or B |
| B5 | 3 | Pick 1 of G/B/S/D + 2 coins | 2 VP |
| B6 | 3 | 1 guitarist + pick 1 of G/B/D/S | 1 guitarist |

### Category C: Spend-to-Get Choice Buildings (2 buildings, both cost 4 coins)

| # | Cost | Visitor Spends | Visitor Gets | Owner Gets |
|---|------|---------------|-------------|------------|
| C1 | 4 | 2 coins | Choice of 2 singers or drummers | 2 coins |
| C2 | 4 | 4 coins | Choice of 4 singers or drummers | 2 coins |

### Category D: Multi-Resource with Owner Choice (4 buildings, all cost 8 coins)

| # | Cost | Visitor Gets | Owner Choice |
|---|------|-------------|-------------|
| D1 | 8 | 2 guitarists + 1 singer | Guitarist or singer |
| D2 | 8 | 2 bassists + 1 drummer | Bassist or drummer |
| D3 | 8 | 2 bassists + 1 singer | Bassist or singer |
| D4 | 8 | 2 guitarists + 1 drummer | Guitarist or drummer |

### Category E: Exchange and Free-Pick Buildings (2 buildings, both cost 4 coins)

| # | Cost | Mechanic | Owner Gets |
|---|------|---------|------------|
| E1 | 4 | Return any 2 resources, pick any 3 resources | 2 coins |
| E2 | 4 | Pick any 2 resources | Owner picks any 1 resource |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 20 new buildings are playable in a game session with correct reward resolution for every building type.
- **SC-002**: Accumulating buildings correctly stock resources at round start and reset to zero on visit, verified across multiple rounds.
- **SC-003**: Owner bonus choices prompt the correct player and restrict selection to the allowed resource types.
- **SC-004**: VP rewards correctly update the player's victory point total and are reflected in the final score screen.
- **SC-005**: Existing building-balance tests run without modification and their results are reported.
- **SC-006**: Spend-to-get buildings correctly deduct coins before granting resource choices, and block placement if the player cannot afford the cost.
- **SC-007**: Accumulated resource counts are visible on the board for accumulating buildings.
- **SC-008**: Buildings acquired through non-purchase means (e.g., quest rewards) start with zero accumulated stock.

## Assumptions

- The existing building purchase and worker placement flow does not need structural changes; new mechanics extend the reward resolution phase.
- Owner bonus choices reuse or extend the existing resource choice dialog infrastructure on the client.
- VP as a building reward is a new concept and will require extending the reward data model (adding "victory_points" to visitor_reward and owner_bonus).
- The 20 new buildings fully replace the current 28 buildings in buildings.json. Building names from the current set will be reused where thematically fitting.
- Accumulating resource display on the board is a visual indicator (e.g., small number badge) and does not require a new dialog.
- The "pick 1 face-up quest" mechanic works identically to the existing draw_contract special.

## Clarifications

### Session 2026-04-22

- Q: What are the owner bonuses for B1 and B2? → A: B1 owner gets 2 coins. B2 owner gets 1 intrigue card.
- Q: What does B3 visitor get? → A: 2 bassists + 2 coins (not just 2 bassists).
- Q: Do the 20 new buildings fully replace all 28 existing buildings? → A: Yes, full replacement. Remove all 28 old buildings, use only the 20 new ones.
- Q: Is there a max cap on accumulated resources? → A: No cap. Resources accumulate indefinitely until collected.
