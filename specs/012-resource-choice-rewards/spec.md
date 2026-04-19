# Feature Specification: Resource Choice Rewards

**Feature Branch**: `012-resource-choice-rewards`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "Pick a resource functionality for intrigue cards and purchased buildings with shared common code"

## User Scenarios & Testing

### User Story 1 - Simple Resource Choice (Priority: P1)

A player visits a purchased building or plays an intrigue card that grants a choice of one resource from a set. The system presents the available options and the player selects one. The chosen resource is added to the player's inventory.

This covers:
- **Scenario 2**: Building that grants 1 singer, drummer, guitarist, or bassist + 2 coins
- **Scenario 6**: Building that grants any 2 non-coin resources (player picks each one)

**Why this priority**: This is the foundational "pick N resources from a set" interaction. All other scenarios build on this core mechanic. Delivering this first validates the selection UI and reward flow.

**Independent Test**: Place a worker on a building with a "pick one resource" reward. A dialog appears showing the available resource types. Select one. The resource is added to the player's total.

**Acceptance Scenarios**:

1. **Given** a player places a worker on a building offering "pick 1 of singer/drummer/guitarist/bassist + 2 coins", **When** the resource choice dialog appears and the player selects "guitarist", **Then** the player receives 1 guitarist and 2 coins
2. **Given** a player places a worker on a building offering "pick 2 non-coin resources", **When** the dialog appears, **Then** the player makes two sequential selections (each from guitarist/bassist/drummer/singer) and receives both chosen resources
3. **Given** a resource choice dialog is open, **When** the player has not yet confirmed, **Then** the dialog remains visible and the game does not advance

---

### User Story 2 - Predefined Option Selection (Priority: P2)

A player plays an intrigue card that presents a set of predefined, mutually exclusive reward bundles. The player picks exactly one bundle. This differs from Story 1 because the options are fixed bundles (e.g., "2 guitarists" or "4 coins") rather than individual resource picks.

This covers:
- **Scenario 1**: Intrigue card offering 1 singer OR 1 drummer OR 2 guitarists OR 2 bassists OR 4 coins

**Why this priority**: Extends the choice system to handle predefined bundles rather than individual picks. Reuses the selection dialog with a different data shape.

**Independent Test**: Play an intrigue card with predefined reward options. A dialog appears listing each bundle option. Select one. The full bundle is granted.

**Acceptance Scenarios**:

1. **Given** a player plays an intrigue card offering "1 singer OR 1 drummer OR 2 guitarists OR 2 bassists OR 4 coins", **When** the choice dialog appears and the player selects "2 guitarists", **Then** the player receives 2 guitarists
2. **Given** the same intrigue card, **When** the player selects "4 coins", **Then** the player receives 4 coins
3. **Given** the choice dialog is showing predefined options, **When** the player selects one, **Then** exactly one bundle is granted (no partial or multiple selections)

---

### User Story 3 - Constrained Combo Choice (Priority: P3)

A player visits a purchased building that requires spending a cost first, then grants a constrained combo — the player distributes a point total across a limited set of resource types. This differs from Story 1 because the player allocates a budget across allowed types rather than making N independent picks from the full set.

This covers:
- **Scenario 5**: Building where you spend 2 coins, then choose any combination of 4 total from guitarists and bassists (e.g., 3G+1B, 2G+2B, 4G, etc.)

**Why this priority**: Introduces the cost-then-reward pattern and combo allocation, adding meaningful strategic depth.

**Independent Test**: Place a worker on the building. The system deducts 2 coins. A combo selection dialog appears allowing the player to allocate 4 points across guitarists and bassists. Confirm the selection. Resources are granted.

**Acceptance Scenarios**:

1. **Given** a player with at least 2 coins places a worker on the combo building, **When** the cost is deducted and the combo dialog appears, **Then** the player can allocate 4 total across guitarists and bassists
2. **Given** the combo dialog is open, **When** the player sets 3 guitarists and 1 bassist (total = 4), **Then** the confirm button is enabled
3. **Given** the combo dialog is open, **When** the player tries to exceed 4 total, **Then** the dialog prevents it
4. **Given** a player with fewer than 2 coins, **When** they attempt to use this building, **Then** the action is blocked

---

### User Story 4 - Resource Exchange (Priority: P4)

A player visits a purchased building that requires turning in resources before gaining new ones. The player first selects which resources to surrender, then selects which resources to receive.

This covers:
- **Scenario 4**: Building where you turn in any 2 non-coin resources, then gain any 3 non-coin resources

**Why this priority**: This is the most complex interaction — a two-phase choose-and-trade flow. It builds on Stories 1-3 but adds the "spend resources" selection step.

**Independent Test**: Place a worker on the exchange building. A dialog prompts the player to select 2 non-coin resources to turn in. After confirming, a second dialog prompts the player to select 3 non-coin resources to receive. Both transactions are applied.

**Acceptance Scenarios**:

1. **Given** a player with at least 2 non-coin resources places a worker on the exchange building, **When** the spend dialog appears, **Then** the player can select 2 resources from their available non-coin resources to turn in
2. **Given** the player has confirmed the resources to turn in, **When** the gain dialog appears, **Then** the player selects 3 non-coin resources to receive
3. **Given** the player selects resources to turn in, **When** the player does not have enough of a selected type, **Then** the dialog prevents that selection
4. **Given** a player with fewer than 2 non-coin resources, **When** they attempt to use this building, **Then** the action is blocked

---

### User Story 5 - Multi-Player Resource Choice (Priority: P5)

An intrigue card is played that grants the playing player a resource choice, and then each other player also receives a (smaller) resource choice. The system sequentially prompts each affected player.

This covers:
- **Scenario 7**: Intrigue card where the main player picks 2 non-coin resources, then each other player picks 1 non-coin resource

**Why this priority**: Most complex coordination — requires sequentially prompting multiple players for choices, with different pick counts per player.

**Independent Test**: Play the intrigue card. The main player sees a dialog to pick 2 non-coin resources. After the main player confirms, each other player in turn sees a dialog to pick 1 non-coin resource.

**Acceptance Scenarios**:

1. **Given** a player plays the multi-player intrigue card, **When** the card resolves, **Then** the playing player is prompted to choose 2 non-coin resources
2. **Given** the main player has made their selection, **When** the next player's turn arrives, **Then** that player is prompted to choose 1 non-coin resource
3. **Given** all players have made their selections, **When** the last player confirms, **Then** all chosen resources are granted and the game continues
4. **Given** a multiplayer game, **When** the intrigue card is played, **Then** each other player receives their prompt in turn order

---

### Edge Cases

- What happens if a player has zero non-coin resources and needs to turn in resources for Story 4? The building action should be blocked or the player should not be able to use it.
- What happens if a player disconnects during a multi-player resource choice (Story 5)? The system should timeout and auto-select a default (e.g., the first available resource) after a reasonable wait.
- What happens if the resource choice dialog is open and the game round ends? The dialog should remain until the player makes a selection, since the choice is part of resolving an action.
- For combo choices (Story 3), what happens if the player sets all sliders to 0 and tries to confirm? The confirm button should be disabled until the total equals the required amount.

## Requirements

### Functional Requirements

- **FR-001**: System MUST present a resource choice dialog when a player triggers a reward that involves selecting resources
- **FR-002**: System MUST support "pick N resources from a set" selections where N can be 1 or more and the set can be any subset of the five resource types
- **FR-003**: System MUST support predefined bundle choices where the player selects one option from a list of fixed resource bundles
- **FR-004**: System MUST support constrained combo choices where the player distributes a total across a limited set of resource types
- **FR-005**: System MUST support two-phase resource exchange where the player first selects resources to turn in, then selects resources to receive
- **FR-006**: System MUST support multi-player sequential choice where each affected player is prompted for their selection in turn order
- **FR-007**: System MUST validate that a player has sufficient resources before allowing a "turn in" or "spend" action
- **FR-008**: System MUST prevent advancing the game until all required resource choices are resolved
- **FR-009**: System MUST grant the exact resources the player selected, no more, no less
- **FR-010**: System MUST use a common, reusable resource choice interaction pattern across all scenarios to maximize shared logic

### Key Entities

- **Resource Choice Prompt**: Represents a pending resource selection — includes the allowed resource types, the number of picks required, whether it's a gain or a spend, and the target player
- **Resource Bundle Option**: A predefined set of resources offered as a single selectable choice (e.g., "2 guitarists" or "4 coins")
- **Resource Exchange**: A two-step transaction pairing a spend prompt with a subsequent gain prompt

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can complete any single-player resource choice in under 10 seconds from dialog appearance to confirmation
- **SC-002**: All 7 specified reward scenarios function correctly end-to-end in a live game session
- **SC-003**: The resource choice interaction is consistent across all scenarios — same visual style, same confirmation flow, same feedback
- **SC-004**: Multi-player resource choices resolve in correct turn order without skipping or duplicating any player
- **SC-005**: 100% of resource transactions balance correctly — resources spent are deducted, resources gained are added, with no duplication or loss

## Assumptions

- The five resource types are: guitarists, bass players, drummers, singers, and coins
- The existing intrigue card and building reward systems will be extended to trigger resource choice prompts rather than being replaced
- In multi-player scenarios (Story 5), each player's choice is independent — they do not see what other players selected
- The resource choice dialog blocks other actions for the choosing player until resolved
- Auto-selection on timeout for disconnected players uses the first resource in the allowed set as a reasonable default
- The existing building and intrigue card configuration files will define which reward type each card uses
