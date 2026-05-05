# Feature Specification: Resource Choice Board Space

**Feature Branch**: `022-resource-choice-building`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Create a new pre-existing building/resource spot. This building allows the player that puts a worker on it to choose from a drummer, singer, or a combo of a guitarist plus bassist."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Place Worker on Resource Choice Space (Priority: P1)

A player places a worker on a new permanent board space. Upon landing, they are presented with a choice dialog offering three options: gain 1 drummer, gain 1 singer, or gain 1 guitarist plus 1 bassist. The player selects one option and receives those resources immediately.

**Why this priority**: This is the core and only interaction for this feature. Without it, the space has no function.

**Independent Test**: Can be fully tested by placing a worker on the space, selecting each of the three options in separate tests, and verifying the correct resources are added to the player's supply.

**Acceptance Scenarios**:

1. **Given** a player has an available worker and the space is unoccupied, **When** they place a worker on the space, **Then** a choice dialog appears with three options: "1 Drummer", "1 Singer", "1 Guitarist + 1 Bassist"
2. **Given** the choice dialog is displayed, **When** the player selects "1 Drummer", **Then** they receive 1 drummer and the dialog closes
3. **Given** the choice dialog is displayed, **When** the player selects "1 Singer", **Then** they receive 1 singer and the dialog closes
4. **Given** the choice dialog is displayed, **When** the player selects "1 Guitarist + 1 Bassist", **Then** they receive 1 guitarist and 1 bassist and the dialog closes
5. **Given** a player places a worker and receives resources, **Then** the turn advances to the next player

---

### User Story 2 - Space Occupancy Rules (Priority: P1)

The space follows standard board rules: only one worker can occupy it per round, and the space is freed at the end of the round when workers return.

**Why this priority**: Without occupancy enforcement, the space would break game balance by allowing unlimited resource gain.

**Independent Test**: Place a worker on the space, then verify a second player cannot place on it. Verify the space is freed at round end.

**Acceptance Scenarios**:

1. **Given** the space is already occupied by another player's worker, **When** a different player attempts to place on it, **Then** the space is not selectable
2. **Given** the space is occupied, **When** the round ends, **Then** the worker returns and the space becomes available again

---

### Edge Cases

- What happens if the space is copied via Shadow Studio or a copy intrigue card? The player choosing the copied space should see the same three-option choice dialog.
- What happens during the reassignment phase? If a backstage worker is reassigned to this space, the choice dialog should appear normally.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game board MUST include a new permanent space that presents a resource choice when a worker is placed on it
- **FR-002**: The choice MUST offer exactly three options: 1 drummer, 1 singer, or 1 guitarist plus 1 bassist
- **FR-003**: The player MUST select exactly one option from the three choices
- **FR-004**: The selected resources MUST be added to the player's supply immediately upon selection
- **FR-005**: The space MUST follow standard occupancy rules (one worker per round, freed at round end)
- **FR-006**: The space MUST be compatible with copy mechanics (Shadow Studio, copy intrigue cards) and reassignment
- **FR-007**: The space MUST be named "The Jam Session"
- **FR-008**: No cost is required to use this space — the resource choice is free
- **FR-009**: The board space card image MUST use the standard resource icon boxes (white for drummer, purple for singer, orange/red for guitarist, black for bassist) to visually represent the available choices

### Key Entities

- **Resource Choice Space**: A permanent board space with a bundle-style resource choice offering three predefined options
- **Resource Bundles**: Three fixed options — {1 drummer}, {1 singer}, {1 guitarist + 1 bassist} — each representing a distinct resource combination the player can gain

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can place a worker on the new space and receive resources in under 5 seconds (choice dialog appears instantly)
- **SC-002**: All three resource options produce the correct resources 100% of the time
- **SC-003**: The space appears on the game board in every game session, visible and functional from round 1
- **SC-004**: Copy and reassignment mechanics work identically to other permanent spaces that offer resource choices

## Assumptions

- This is a permanent board space (always present from the start of the game), not a purchasable building
- The space has a single slot (one worker per round), consistent with other permanent resource spaces
- There is no cost to use this space — the choice is purely a gain
- The space does not grant any owner bonus (permanent spaces have no owner)
- The space is named "The Jam Session"
- The space is positioned on the board below The Rhythm Pit and above Fastpass; Fastpass moves down to make room

## Clarifications

### Session 2026-05-03

- Q: Where should the new space be positioned on the board? → A: Below The Rhythm Pit and above Fastpass. Move Fastpass down to make room.
- Q: What should the space be named? → A: The Jam Session
- Q: How should the card image represent the resource choices? → A: Use standard resource icon boxes (white for drummer, purple for singer, orange/red for guitarist, black for bassist)
