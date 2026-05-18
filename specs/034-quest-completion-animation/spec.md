# Feature Specification: Quest Completion Animation

**Feature Branch**: `034-quest-completion-animation`  
**Created**: 2026-05-18  
**Status**: Draft  
**Input**: User description: "Create an animation sequence for when a player finishes a quest. The quest card animates from the upper left to center while scaling up. Resource requirements stream from the player area to the card. Rewards animate from the card back to the player area. The card then exits to the lower right."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quest Card Entrance Animation (Priority: P1)

When a player completes a quest, the quest card appears at normal size in the upper-left area of the screen and smoothly animates to the center of the screen while scaling up to twice its normal size. This draws attention to the completed quest and sets the stage for the rest of the animation sequence.

**Why this priority**: The card entrance is the foundation of the entire animation sequence. Without it, no other animations have a visual anchor point.

**Independent Test**: Can be tested by completing any quest and observing the card animate from upper-left to screen center at 2x scale. Delivers immediate visual feedback that something important happened.

**Acceptance Scenarios**:

1. **Given** a player has just completed a quest, **When** the quest completion event fires, **Then** the quest card sprite appears at normal scale near the upper-left of the screen and smoothly animates to the center while scaling to twice its normal size.
2. **Given** the card entrance animation is playing, **When** the animation completes, **Then** the card is stationary at the center of the screen at 2x scale, ready for the next phase.

---

### User Story 2 - Resource Requirements Stream Animation (Priority: P1)

After the card reaches the center, the resources required to complete the quest animate one at a time from the player's character position (upper-left area) toward the center of the card, disappearing on arrival. Resources are staggered so each one starts approximately a quarter second after the previous one, creating a streaming effect.

**Why this priority**: Showing the cost being "paid" is core to the quest completion feedback loop. Players need to see what they spent.

**Independent Test**: Can be tested by completing a quest that requires multiple resources (e.g., 4 guitarists) and verifying each resource icon animates sequentially from the player area to the card center, with approximately 0.25-second stagger between each.

**Acceptance Scenarios**:

1. **Given** the quest card is centered at 2x scale, **When** the requirements phase begins, **Then** resource icons matching the quest's cost appear one at a time at the player's character position and animate toward the center of the card.
2. **Given** a quest requires 4 guitarists, **When** the requirements stream plays, **Then** 4 guitarist icons animate sequentially with approximately 0.25 seconds between each start, and each icon disappears upon reaching the card center.
3. **Given** a quest requires multiple resource types (e.g., 2 guitarists and 1 singer), **When** the requirements stream plays, **Then** all required resources animate in sequence regardless of type, each staggered by approximately 0.25 seconds.

---

### User Story 3 - Reward Distribution Animation (Priority: P2)

After all requirement resource animations have completed, if the quest grants resource rewards, those reward icons appear at the center of the card and animate outward to the player's character position in the upper-left area. This visually communicates what the player gained.

**Why this priority**: Reward feedback is important but secondary to the cost animation. Some quests have no resource rewards, so this phase is conditional.

**Independent Test**: Can be tested by completing a quest that has bonus resources as rewards and verifying resource icons fly from the card center to the player area after the requirements phase finishes.

**Acceptance Scenarios**:

1. **Given** all requirement animations have finished and the quest has bonus resource rewards, **When** the reward phase begins, **Then** reward resource icons appear at the card center and animate to the player's character position, staggered similarly to the requirements stream.
2. **Given** all requirement animations have finished and the quest has no resource rewards, **When** the reward phase would begin, **Then** the animation skips directly to the card exit phase.

---

### User Story 4 - Card Exit Animation (Priority: P2)

After all reward animations (or requirements animations if no rewards) complete, the quest card animates from the center of the screen toward the lower-right corner, exiting the visible area. This signals the end of the quest completion sequence and returns focus to normal gameplay.

**Why this priority**: A clean exit is needed to conclude the animation and unblock gameplay, but it is simpler than the streaming resource animations.

**Independent Test**: Can be tested by completing any quest and verifying the card moves from center toward the lower-right and disappears after all prior animation phases finish.

**Acceptance Scenarios**:

1. **Given** all reward animations have completed (or the reward phase was skipped), **When** the exit phase begins, **Then** the quest card animates from the center toward the lower-right corner of the screen and disappears.
2. **Given** the card exit animation completes, **When** the animation is fully done, **Then** normal gameplay interaction resumes and no animation sprites remain on screen.

---

### Edge Cases

- What happens when a quest has zero resource cost (free quest)? The requirements stream phase is skipped, proceeding directly to rewards or card exit.
- What happens when a quest has only non-resource rewards (e.g., victory points, draw cards, gain a building)? Only resource-type rewards are animated; non-resource rewards are not visualized in this animation.
- What happens if the player's turn advances or another event fires while the animation is playing? The animation sequence should complete fully before processing the next event, using the existing event queue to enforce ordering.
- What happens if the quest completion animation overlaps with another animation already in progress? The event queue ensures animations are sequenced; the quest completion animation waits for any prior animation to finish.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display the completed quest card starting at normal scale near the upper-left of the screen and animate it to the screen center while scaling to 2x normal size.
- **FR-002**: System MUST animate resource requirement icons one at a time from the player's character position toward the center of the quest card, with approximately 0.25 seconds between each resource's start.
- **FR-003**: Each resource requirement icon MUST disappear (be removed) when it reaches the center of the quest card.
- **FR-004**: System MUST wait for all requirement resource animations to complete before starting reward animations.
- **FR-005**: If the quest has bonus resource rewards, system MUST animate reward icons from the center of the quest card to the player's character position, staggered similarly to the requirements stream.
- **FR-006**: If the quest has no bonus resource rewards, system MUST skip the reward phase and proceed directly to the card exit.
- **FR-007**: After all reward animations complete (or are skipped), system MUST animate the quest card from screen center toward the lower-right corner of the screen until it exits the visible area.
- **FR-008**: System MUST use the existing event queue to sequence the quest completion animation, preventing overlap with other animations or events.
- **FR-009**: System MUST use the existing animation manager and easing functions for all movement and scaling transitions.
- **FR-010**: Normal gameplay interaction MUST resume only after the entire animation sequence completes.

### Key Entities

- **Quest Card**: The completed quest, displayed as a sprite with its card image. Has resource cost (requirements) and bonus resource rewards.
- **Resource Icon**: A small sprite representing a single unit of a resource type (guitarist, bass player, drummer, singer, coin). Used for both the requirements stream and the rewards stream.
- **Player Character Position**: The location in the upper-left area of the screen associated with the current player, serving as the origin for requirement resources and destination for reward resources.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players see a complete, uninterrupted animation sequence when completing a quest, from card entrance through card exit, within 5 seconds for a typical quest (2-4 resource requirements, 0-2 resource rewards).
- **SC-002**: Each resource in the requirements stream is visually distinct and individually identifiable as it animates toward the card.
- **SC-003**: The animation sequence correctly reflects the specific quest's requirements and rewards — the number and type of resource icons match the quest data.
- **SC-004**: No visual artifacts (stale sprites, flickering, mispositioned elements) remain on screen after the animation sequence completes.
- **SC-005**: Gameplay is not blocked for more than 8 seconds by the animation, even for quests with the maximum number of resources.

## Assumptions

- The player's character position in the upper-left of the screen is a known, fixed coordinate that can be referenced for animation start/end points.
- Resource icons (guitarist, bass player, drummer, singer, coin) are available as loadable image assets or can be created from existing resource bar or card imagery.
- Only resource-type rewards (bonus_resources from the quest data) are animated. Other reward types (victory points, intrigue draws, building rewards, etc.) are handled through existing UI updates and are not part of this animation.
- The existing animation manager supports concurrent animations (multiple resource icons in flight at the same time due to the staggered start).
- The existing event queue is used to prevent this animation from overlapping with other queued events (marker movement, intrigue card draws, etc.).
- The animation uses smooth easing for a polished feel, consistent with existing animation conventions in the project.
