# Feature Specification: Resource Distribution Buildings

**Feature Branch**: `040-resource-distribution-buildings`  
**Created**: 2026-06-11  
**Status**: Draft  
**Input**: User description: "Implement Phase 1 Undermountain buildings (UN-1 through UN-5) that use the 'place resources on action card' mechanic. Visual representation of placed resources on buildings below worker token area."

## Clarifications

### Session 2026-06-11

- Q: When placed resources land on a building that also accumulates stock, does the visitor receive both? → A: Separate pools — visitor collects both accumulated stock AND placed resources independently. They are tracked as distinct pools.
- Q: Can the owner place resources back on the building being visited? → A: No — the building being visited is excluded as a target. Owner must choose other action spaces.
- Q: How should the "place resources on spaces" reward be shown on building card images? → A: Text line with resource icons (e.g., "Place: [icon]x2 spaces"), consistent with existing card reward formatting.
- Q: Can multiple distributed resources go on the same space in a single placement? → A: No — each resource must go on a different space. All target spaces must be distinct within a single placement phase.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visit a Resource Distribution Building (Priority: P1)

A player places their worker on a resource distribution building (e.g., a guitarist-focused venue). They immediately receive their visitor reward of resources. Then the building owner is prompted to choose action spaces on the board where additional resources from the supply will be placed. Those resources sit visibly on the chosen action spaces until a future visitor collects them.

**Why this priority**: This is the core mechanic — without it, none of the five buildings function. It establishes the "place resources on action spaces" pattern that all five buildings share.

**Independent Test**: Can be fully tested by visiting one resource distribution building, verifying the visitor receives their resources, the owner selects target spaces, and the placed resources appear on those spaces.

**Acceptance Scenarios**:

1. **Given** a constructed resource distribution building with no current visitor, **When** a player places their worker on it, **Then** the visitor receives the building's stated resource reward (e.g., 4 guitarists for UN-1).
2. **Given** a player has just visited a resource distribution building, **When** the building owner is prompted to choose target action spaces, **Then** the owner can select the required number of distinct action spaces from the board.
3. **Given** the owner has selected target action spaces, **When** the selection is confirmed, **Then** the specified resources are placed from the supply onto those action spaces and are visible to all players.
4. **Given** a player visits a resource distribution building they own, **When** the visit completes, **Then** they receive both the visitor reward and the owner bonus, and they also choose where to place the distributed resources.

---

### User Story 2 - Collect Placed Resources from an Action Space (Priority: P1)

A player places their worker on an action space that has resources sitting on it (placed there by a previous resource distribution building visit). The player collects all placed resources on that space in addition to the space's normal reward.

**Why this priority**: Equally critical to US1 — placed resources must be collectible or the mechanic has no purpose. This completes the resource distribution cycle.

**Independent Test**: Can be tested by pre-placing resources on a space and then having a player visit that space.

**Acceptance Scenarios**:

1. **Given** an action space has 1 guitarist resource placed on it, **When** a player places their worker on that space, **Then** the player receives the guitarist in addition to the space's normal reward.
2. **Given** an action space has multiple placed resources (e.g., 2 coins from UN-2), **When** a player visits it, **Then** the player receives all placed resources and the space is cleared of placed resources.
3. **Given** an action space has placed resources from multiple building visits (e.g., 1 guitarist + 2 coins), **When** a player visits it, **Then** the player receives all placed resources of all types.
4. **Given** a round ends and action spaces still have uncollected placed resources, **When** the next round begins, **Then** the placed resources remain on those spaces (they persist across rounds until collected).

---

### User Story 3 - Visual Display of Placed Resources on Action Spaces (Priority: P1)

When resources are placed on an action space, small resource icons appear on the space's card so all players can see what's available. This gives players strategic information about which spaces are more valuable to visit.

**Why this priority**: Players must be able to see placed resources to make informed decisions. Without visual feedback, the mechanic is invisible and confusing.

**Independent Test**: Can be tested by placing resources on a space and visually confirming the icons appear below the worker token area.

**Acceptance Scenarios**:

1. **Given** resources have been placed on an action space, **When** any player views the board, **Then** resource icons appear on that space's card below the worker token area.
2. **Given** multiple resource types are placed on a single space, **When** viewing the board, **Then** each resource type is shown with its icon and count.
3. **Given** a player collects all placed resources from a space, **When** the collection completes, **Then** the resource icons are removed from that space.
4. **Given** resources are placed on a constructed building (which is itself an action space), **When** viewing the board, **Then** the placed resource icons appear below the worker token area on that building card.

---

### User Story 4 - Owner Selects Target Spaces for Resource Placement (Priority: P2)

When the building owner must choose which action spaces receive the distributed resources, they are presented with a selection interface showing eligible spaces. The owner picks the required number of distinct spaces.

**Why this priority**: The selection mechanic is important for gameplay depth but builds on the core mechanics from US1. Without it, resources could be auto-placed, but owner choice is what makes the mechanic strategic.

**Independent Test**: Can be tested by having the owner interact with the space selection UI after a visitor activates a distribution building.

**Acceptance Scenarios**:

1. **Given** a visitor has activated a distribution building that places resources on 2 different action spaces, **When** the owner is prompted, **Then** the owner sees a list of all available action spaces and can select exactly 2 distinct spaces.
2. **Given** the owner is selecting target spaces, **When** they try to select the same space twice, **Then** the system prevents duplicate selection.
3. **Given** the owner is selecting target spaces, **When** they try to select the building being visited, **Then** the system prevents this selection — the visited building is excluded from valid targets.
4. **Given** a non-owner visits a distribution building, **When** the building has no owner (unclaimed building lot), **Then** the visitor themselves selects the target spaces for resource placement.

---

### User Story 5 - Five Themed Resource Distribution Buildings (Priority: P2)

The game includes five distinct resource distribution buildings, each themed to the music world and mapped from the Undermountain expansion. Each distributes a different resource type with varying quantities.

**Why this priority**: The specific building content depends on the core mechanic (US1-US4) working first. These are the concrete instances.

**Independent Test**: Can be tested by purchasing and using each of the five buildings independently.

**Acceptance Scenarios**:

1. **Given** the building market, **When** the game populates available buildings, **Then** the five resource distribution buildings can appear in the building market with correct costs (7 coins each).

The five buildings (mapped from Undermountain to music theme):

| ID | Name | Cost | Visitor Reward | Place on Spaces | Owner Bonus |
|--------|--------|------|----------------|-----------------|-------------|
| UN-1 | TBD (Guitarist venue) | 7 coins | 4 Guitarists | 1 Guitarist on each of 2 spaces | 2 Guitarists |
| UN-2 | TBD (Coin venue) | 7 coins | 8 Coins | 2 Coins on each of 2 spaces | 4 Coins |
| UN-3 | TBD (Singer venue) | 7 coins | 2 Singers | 1 Singer on 1 space | 1 Singer |
| UN-4 | TBD (Bass Player venue) | 7 coins | 4 Bass Players | 1 Bass Player on each of 2 spaces | 2 Bass Players |
| UN-5 | TBD (Drummer venue) | 7 coins | 2 Drummers | 1 Drummer on 1 space | 1 Drummer |

---

### Edge Cases

- What happens if there are no eligible action spaces to place resources on? (e.g., only 1 space exists but building requires 2) — Resources that cannot be placed are forfeited.
- What happens if the building owner disconnects during target space selection? — Auto-select random eligible spaces after a timeout.
- Can resources be placed on an action space that already has placed resources from a previous visit? — Yes, resources from separate placement phases stack. However, within a single placement phase, each resource must go on a different space.
- Can resources be placed on the resource distribution building itself? — No, the building being visited is excluded as a valid target. All other action spaces on the board are valid.
- What happens to placed resources when a building is removed from the board? — Placed resources remain on whatever spaces they were placed on; they are independent of the building that created them.
- Can the owner place resources on spaces already occupied by another player's worker this round? — Yes, the resources stay there for future rounds when the space becomes available again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support a new building type "resource distribution" where visiting the building triggers both a visitor reward AND a resource placement phase where resources from the supply are placed onto other action spaces.
- **FR-002**: System MUST allow the building owner to choose which action spaces receive the distributed resources, selecting the number of distinct spaces specified by the building definition.
- **FR-003**: System MUST track placed resources per action space as a separate pool from any existing accumulation stock, supporting multiple resource types and quantities stacking on a single space.
- **FR-004**: System MUST automatically grant placed resources to any player who visits an action space that has placed resources, in addition to the space's normal reward and any accumulated stock (these are independent pools).
- **FR-005**: System MUST clear placed resources from an action space when they are collected by a visiting player.
- **FR-006**: Placed resources MUST persist across rounds until collected — they are not cleared at round end.
- **FR-007**: System MUST display resource icons on action spaces that have placed resources, positioned below the worker token area on the card.
- **FR-013**: Building card images for resource distribution buildings MUST show the "place resources on spaces" reward as a text line with resource icons (e.g., "Place: [icon]x2 spaces"), consistent with existing card reward formatting.
- **FR-008**: System MUST support five specific resource distribution buildings with the costs, rewards, placement rules, and owner bonuses defined in the building table above.
- **FR-009**: System MUST handle the case where the visitor is also the building owner — they receive both rewards and also choose target spaces.
- **FR-010**: System MUST prevent the owner from selecting the same action space more than once during a single placement phase — each distributed resource must go on a different space (all target spaces must be distinct).
- **FR-012**: System MUST exclude the building being visited from the list of valid target spaces for resource placement.
- **FR-011**: When a building has no owner (unowned building lot scenario), the visitor MUST select the target spaces themselves.

### Key Entities

- **Resource Distribution Building**: A building that, when visited, rewards the visitor with resources and triggers a placement phase where additional resources are placed onto other action spaces. Defined by: resource type to distribute, quantity per space, number of target spaces.
- **Placed Resources**: A collection of resources sitting on an action space, waiting to be collected. Tracks: resource type(s), quantity per type, which space they are on. Independent of the building that placed them.
- **Target Space Selection**: A player interaction where the building owner (or visitor if unowned) chooses which action spaces receive distributed resources. Constrained by: number of spaces required, distinctness rule.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can visit any of the five resource distribution buildings and receive the correct visitor reward within the normal turn flow.
- **SC-002**: After a resource distribution building visit, the building owner can select the correct number of distinct target action spaces within 15 seconds.
- **SC-003**: Placed resource icons are visible on action spaces to all players immediately after placement.
- **SC-004**: Players who visit an action space with placed resources receive all placed resources plus the space's normal reward in a single visit.
- **SC-005**: Placed resources persist across rounds until collected — no resources are lost to round transitions.
- **SC-006**: All five resource distribution buildings function correctly with their specific resource types, quantities, and owner bonuses.

## Assumptions

- Building names (music-themed) for UN-1 through UN-5 will be chosen during implementation or in a follow-up task. Placeholder names are acceptable for initial development.
- The "place resources on action spaces" mechanic applies only to buildings, not to permanent board spaces or other game elements, for this feature.
- Resource icons will reuse the existing resource icon assets already used elsewhere in the game (guitarist, bass player, drummer, singer, coin icons).
- The building cost of 7 coins each is higher than any existing building (max was 8 coins), making these premium purchases — this is intentional per the source material.
- UN-11 (Hall of Three Lords) is explicitly out of scope for this feature due to its additional complexity (spend resources + distribute + earn VP). It will be a separate feature.
- Owner choice of target spaces is the primary interaction model. Auto-placement or AI-driven placement for non-human players is out of scope.
- All existing action spaces (permanent board spaces and constructed buildings) are valid targets for resource placement.
