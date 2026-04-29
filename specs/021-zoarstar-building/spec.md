# Feature Specification: Zoarstar Building (Shadow Studio)

**Feature Branch**: `021-zoarstar-building`
**Created**: 2026-04-29
**Status**: Draft
**Input**: User description: "Add a building equivalent to Waterdeep's 'The Zoarstar'. When landing on it, a player selects a location that has another player's token (not their own, not empty) and uses that space's action as if they had a worker there."

## User Scenarios & Testing

### User Story 1 - Copy an Opponent's Occupied Space (Priority: P1)

A player places a worker on the Shadow Studio building. They are then presented with all action spaces currently occupied by other players (not by the visiting player themselves, and not empty spaces). The player selects one of those spaces and receives the rewards of that space as if they had placed a worker there. The player does not actually place a second worker — they only receive the space's action/reward.

**Why this priority**: This is the core mechanic of the building. Without it, the building has no purpose.

**Independent Test**: Can be fully tested by purchasing the building, having another player occupy a space, then visiting the Shadow Studio and selecting the occupied space. The visitor receives the copied space's rewards.

**Acceptance Scenarios**:

1. **Given** Shadow Studio is constructed and another player occupies "Motown" (2 bass players), **When** the visiting player places on Shadow Studio and selects "Motown", **Then** the visitor receives 2 bass players from the supply (the same reward as placing directly on Motown).
2. **Given** Shadow Studio is constructed and no other player occupies any space, **When** the visiting player places on Shadow Studio, **Then** the visitor receives only the building's base reward (if any) and is not prompted to select a space (there are no valid targets).
3. **Given** Shadow Studio is constructed, **When** the visiting player has a worker on "Guitar Center" and an opponent has a worker on "Motown", **Then** only "Motown" is shown as a selectable target (not the player's own occupied space).

---

### User Story 2 - Owner Bonus (Priority: P2)

When another player visits the Shadow Studio, the building's owner receives 2 victory points as their owner bonus.

**Why this priority**: Owner bonuses are standard for all buildings and must work correctly, but are secondary to the core copy mechanic.

**Independent Test**: Have a non-owner visit the Shadow Studio and verify the owner receives 2 VP.

**Acceptance Scenarios**:

1. **Given** Player A owns Shadow Studio and Player B visits it, **When** Player B completes their action, **Then** Player A gains 2 VP.
2. **Given** Player A owns Shadow Studio and Player A visits it, **Then** Player A does not receive the owner bonus (owners visiting their own building never trigger owner bonus).

---

### User Story 3 - Copying Special Spaces (Priority: P2)

The copy mechanic must correctly handle special action spaces beyond simple resource grants — including buildings with resource choices, buildings with accumulated stock, garage spaces (quest selection + coins/intrigue), and permanent spaces.

**Why this priority**: Tied with owner bonus. If copying only works for simple resource spaces, the building is severely limited.

**Independent Test**: Have an opponent occupy a building with a resource choice (e.g., "The Fillmore"), then visit Shadow Studio and select it. Verify the resource choice prompt appears for the visitor.

**Acceptance Scenarios**:

1. **Given** an opponent occupies a building with a resource choice reward, **When** the visitor copies that space via Shadow Studio, **Then** the visitor receives the resource choice prompt and resolves it normally.
2. **Given** an opponent occupies a building with accumulated stock (e.g., "Red Rocks"), **When** the visitor copies that space, **Then** the visitor collects the accumulated stock from that building (draining it as normal).
3. **Given** an opponent occupies a garage space (quest selection), **When** the visitor copies that garage space, **Then** the visitor goes through the quest selection flow as if they had placed directly on that garage space.
4. **Given** an opponent occupies the castle space (first player marker + intrigue), **When** the visitor copies it, **Then** the visitor gains the first player marker and draws an intrigue card.

---

### User Story 4 - Quest Completion After Copy (Priority: P3)

After resolving the copied space's action, the visitor should be prompted to complete a quest (if they can afford one), following the standard post-placement flow.

**Why this priority**: Standard post-action behavior, not specific to this building but must be verified.

**Independent Test**: Copy a space that grants resources sufficient to complete a quest. Verify the quest completion prompt appears.

**Acceptance Scenarios**:

1. **Given** the visitor copies a space and now has enough resources to complete a quest, **When** the copy resolves, **Then** the quest completion prompt appears.

---

### Edge Cases

- What happens if the only occupied spaces are occupied by the visiting player? The visitor is not prompted (no valid targets), and receives only the base building reward.
- What happens if the copied space is a building owned by someone? The copied building's owner receives their owner bonus from the copy action (the visitor is effectively "using" their building).
- What happens if the copied space triggers a resource trigger plot quest (e.g., the visitor has "Payola Pipeline" and the copied space grants coins)? Resource triggers should fire normally on the gained resources.
- What happens if the visitor cancels the space selection? The placement is unwound — the worker returns, and the Shadow Studio is freed, following the standard cancel/unwind pattern.
- Can the visitor copy the Realtor space to purchase a building? Yes — the visitor goes through the building purchase flow as if they had placed on the Realtor.
- Can the visitor copy a backstage slot? No — backstage slots require playing an intrigue card as part of placement, which is a fundamentally different action. Only regular action spaces (permanent, building, garage, castle, realtor) are valid copy targets.

## Requirements

### Functional Requirements

- **FR-001**: The building MUST cost 8 coins to purchase (matching its Waterdeep equivalent as the most expensive building).
- **FR-002**: When a player visits the Shadow Studio, the system MUST present a list of all action spaces currently occupied by other players' workers.
- **FR-003**: The list MUST exclude spaces occupied by the visiting player's own workers.
- **FR-004**: The list MUST exclude empty (unoccupied) spaces.
- **FR-005**: The list MUST exclude backstage slots.
- **FR-006**: When the player selects a target space, the system MUST grant the same rewards as if the player had placed a worker on that space directly — including resource rewards, special rewards, accumulated stock, resource choices, and quest/contract draws.
- **FR-007**: The visiting player MUST NOT actually place a second worker on the copied space. The original occupant's worker remains undisturbed.
- **FR-008**: If the copied space is a building owned by another player, that building's owner MUST receive their owner bonus (the copy counts as a visit).
- **FR-009**: The Shadow Studio's owner MUST receive 2 VP when another player visits.
- **FR-010**: If no valid target spaces exist (no opponents have workers placed), the visitor MUST receive only the base building reward and the turn proceeds normally.
- **FR-011**: The player MUST be able to cancel the space selection, unwinding the placement using the standard cancel pattern.
- **FR-012**: After the copied space's action resolves, the standard post-action flow MUST apply (quest completion check, turn advance).

### Key Entities

- **Shadow Studio Building Tile**: A new building tile (id: building_023) with cost 8, a special visitor reward ("copy_occupied_space"), and owner bonus of 2 VP.
- **Occupied Space Selection**: A player-facing prompt listing all valid target spaces, similar to existing space-selection prompts in the game.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can purchase the Shadow Studio for 8 coins via the Realtor, and it appears on the board as a constructed building.
- **SC-002**: Visitors to Shadow Studio see a list of all opponent-occupied spaces and can select one to copy its action within 2 clicks.
- **SC-003**: 100% of existing action space types (permanent, building, garage, castle, realtor) can be copied without errors when occupied by an opponent.
- **SC-004**: The building owner receives 2 VP every time another player visits, visible in the game log and player score.
- **SC-005**: Cancelling the space selection cleanly unwinds the placement with no lingering state.

## Assumptions

- The building will be named "Shadow Studio" as a music-industry-themed equivalent of "The Zoarstar" (a shadowy, versatile studio that mirrors any other studio's capabilities).
- The building uses `visitor_reward_special: "copy_occupied_space"` as the config-driven mechanic identifier, following the existing pattern for special building actions.
- Backstage slots are excluded from valid copy targets because they require intrigue card play as part of placement — a fundamentally different interaction that cannot be "copied."
- The building does not grant any base resource reward — its entire value is the copy mechanic.
- When copying a space that triggers an interactive prompt (resource choice, quest selection, building purchase), the visitor goes through that prompt flow exactly as if they had placed directly on the space.
