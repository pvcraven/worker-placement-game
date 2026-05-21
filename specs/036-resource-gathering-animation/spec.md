# Feature Specification: Resource Gathering Animation

**Feature Branch**: `036-resource-gathering-animation`  
**Created**: 2026-05-21  
**Status**: Draft  
**Input**: User description: "Animate resource gathering. When a worker lands on a permanent resource spot/building or a constructed one, animate the resources flying from the building to the player name in the top left. Match timing and scale of existing quest completion resource animation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resource Animation on Permanent Spot (Priority: P1)

A player places a worker on a permanent resource spot (e.g., Merch Store, Motown). After the worker marker lands on the spot, the resources earned fly as individual icons from the building's position on the board to the player's name area in the top-left corner, giving satisfying visual feedback that resources were collected.

**Why this priority**: Permanent resource spots are the most frequently used spaces in the game. Animating their rewards covers the majority of resource-gathering interactions and delivers the highest visual impact.

**Independent Test**: Place a worker on any permanent resource spot that grants resources. Observe resource icons flying from the spot to the player's name area in the top-left corner.

**Acceptance Scenarios**:

1. **Given** it is a player's turn, **When** the player places a worker on a permanent resource spot that grants resources, **Then** individual resource icons animate from the spot's position to the player's name area in the top-left corner
2. **Given** a permanent spot grants multiple resource types (e.g., 2 coins and 1 guitarist), **When** the worker is placed, **Then** each individual resource icon animates separately with a staggered delay between them
3. **Given** a permanent spot grants zero resources (only special actions like quest selection), **When** the worker is placed, **Then** no resource animation plays

---

### User Story 2 - Resource Animation on Constructed Building (Priority: P1)

A player places a worker on a constructed building. After the worker marker lands, the resources earned fly from the building's position to the player's name area, just like with permanent spots.

**Why this priority**: Constructed buildings are equally common as permanent spots for resource gathering. The animation must work identically for both space types to maintain visual consistency.

**Independent Test**: Place a worker on a constructed building that grants resources. Observe the same flying icon animation as with permanent spots.

**Acceptance Scenarios**:

1. **Given** a constructed building exists on the board, **When** a player places a worker on it and earns resources, **Then** resource icons animate from the building's board position to the player's name area
2. **Given** the visiting player earns a visitor reward and the building owner earns an owner bonus, **When** the worker is placed, **Then** both the visitor's reward icons fly to the visitor's name area and the owner's bonus icons fly to the owner's name area

---

### User Story 3 - Resource Trigger Bonus Animation (Priority: P2)

When placing a worker triggers bonus resources from completed plot quests, those bonus resources also animate from the building to the player's name area, sequenced after the primary reward animation.

**Why this priority**: Trigger bonuses are a secondary reward mechanism. Animating them reinforces the value of completed plot quests and helps players notice when triggers fire, but they occur less frequently than base rewards.

**Independent Test**: Complete a plot quest that provides a resource trigger, then place a worker on a matching resource spot. Observe that both the base reward and the trigger bonus resources animate sequentially.

**Acceptance Scenarios**:

1. **Given** a player has completed a plot quest with a resource trigger, **When** they place a worker on a spot that activates the trigger, **Then** the base reward icons animate first, followed by the trigger bonus icons
2. **Given** multiple triggers fire for a single placement, **When** the worker is placed, **Then** all trigger bonus icons animate in sequence after the base reward

---

### Edge Cases

- What happens when a spot grants only victory points and no visible resources? No animation plays for victory points since they have no physical icon on the resource bar.
- What happens when a spot grants a special reward (quest selection, building purchase, intrigue draw) in addition to resources? The resource animation plays first for any granted resources, then the special interaction begins.
- What happens when resources are granted but the player's name area is obscured or off-screen? The animation targets the fixed player name position in the top-left corner regardless of scroll or panel state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST animate individual resource icons (guitarists, bass players, drummers, singers, coins) flying from the building/spot position to the current player's name area when a worker is placed and resources are granted
- **FR-002**: System MUST use the same icon scale (0.5), animation duration (1.0 second per icon), stagger delay (0.25 seconds between icons), and easing (SINE) as the existing quest completion resource animation
- **FR-003**: System MUST play the resource animation after the worker marker placement animation completes and before any special interaction (quest selection, building purchase) begins
- **FR-004**: System MUST animate owner bonus resources flying to the building owner's name area when a visiting player places a worker on an owned building
- **FR-005**: System MUST animate trigger bonus resources after base reward resources when plot quest triggers activate
- **FR-006**: System MUST skip the resource animation when a placement grants no animatable resources (e.g., only victory points or only special actions)
- **FR-007**: System MUST use the existing resource icon image files for the animated sprites

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every worker placement that grants visible resources displays the flying icon animation from building to player name area
- **SC-002**: The animation timing and icon scale are visually indistinguishable from the existing quest completion resource animation
- **SC-003**: Owner bonus resources animate to the correct owner's name area, not the visitor's
- **SC-004**: The resource animation completes before any special interaction mode (quest selection, building purchase) activates
- **SC-005**: No animation plays when a placement grants zero visible resources

## Assumptions

- The existing resource icon images (guitarist.png, bass_player.png, drummer.png, singer.png, coin.png) are reused for this animation
- The existing AnimationManager and EventQueue infrastructure handles the new animations without modification
- The player name area position in the top-left corner is already tracked and accessible (via `_player_marker_positions`)
- Victory points do not produce a flying icon animation since they have no dedicated icon in the resource bar
- The animation origin is the center of the building/spot card on the board
- Sound effects for the resource animation match the existing quest completion resource animation behavior
