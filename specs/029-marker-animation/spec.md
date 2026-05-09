# Feature Specification: Marker Placement Animation

**Feature Branch**: `029-marker-animation`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add marker/pawn animation with sine easing for worker placement, replace player circles with marker sprites, and animate markers flying from player name area to board spots."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Player Indicator Shows Marker Sprite (Priority: P1)

As a player, I see each player's actual worker marker sprite next to their name in the top-left player list, instead of a plain colored circle. This gives me an immediate visual connection between the markers on the board and the players they belong to.

**Why this priority**: This is a foundational visual change that must exist before animations can reference the player name area as a source position. It also improves visual consistency across the game.

**Independent Test**: Can be fully tested by starting a game and verifying each player's name in the top-left is accompanied by their worker marker sprite (the same image used when markers appear on board spots) rather than a colored circle.

**Acceptance Scenarios**:

1. **Given** a game with 1-5 players, **When** the game view loads, **Then** each player's entry in the top-left player list shows their worker marker sprite (matching their player color) instead of a colored circle.
2. **Given** a game in progress, **When** viewing the player list, **Then** the marker sprite is visually consistent with the markers placed on board spots (same image, appropriately scaled for the player list area).
3. **Given** the window is resized, **When** the player list re-renders, **Then** the marker sprites scale proportionally and remain properly aligned with player names.

---

### User Story 2 - Animated Worker Placement for Current Player (Priority: P1)

As the current player, when I place a worker on a board spot, I see my worker marker sprite animate smoothly from my name area in the top-left to the target spot on the board. The animation uses a sine easing curve for a natural, satisfying motion.

**Why this priority**: This is the core feature — animating worker placement is the primary goal and provides the most impactful visual feedback for the player's own actions.

**Independent Test**: Can be fully tested by placing a worker on any available board spot and observing a smooth sine-eased animation of the marker sprite traveling from the player's name in the top-left to the target spot.

**Acceptance Scenarios**:

1. **Given** it is my turn and I click on an available board spot, **When** the server confirms the placement, **Then** a worker marker sprite appears at my name position in the player list and animates smoothly to the target spot using sine easing, accompanied by a tick sound effect.
2. **Given** a placement animation is in progress, **When** the animation completes, **Then** the marker sprite settles into its final position on the board spot (identical to the current static placement).
3. **Given** I place a worker, **When** the animation plays, **Then** the game remains responsive — I can still view information and the board does not freeze during animation.

---

### User Story 3 - Animated Worker Placement for Other Players (Priority: P1)

As a player in a multiplayer game, when another player places a worker, I see their worker marker sprite animate from that player's name area in the top-left to the target board spot. This makes it easy to notice and follow other players' moves.

**Why this priority**: Equally critical for multiplayer experience — seeing other players' moves animate from their name is essential for game awareness and the core value proposition of this feature.

**Independent Test**: Can be fully tested in a multiplayer game by having a second player place a worker and observing the animation fly from that player's name area to the board spot.

**Acceptance Scenarios**:

1. **Given** a multiplayer game where another player places a worker, **When** the placement notification arrives, **Then** a marker sprite in that player's color animates from their name position in the player list to the target board spot using sine easing.
2. **Given** multiple players take turns in quick succession, **When** each placement notification arrives, **Then** each animation originates from the correct player's name position and travels to the correct target spot.
3. **Given** a multiplayer game, **When** I observe another player's placement animation, **Then** it is visually clear which player made the move (the animation starts at the correct player's name area).

---

### User Story 4 - Reusable Animation System (Priority: P2)

As a developer, the animation system is abstracted so that future animations (such as card animations) can reuse the same infrastructure. The system supports animating any sprite from one position to another with configurable easing.

**Why this priority**: While not user-facing, this architectural decision directly impacts the maintainability and extensibility of the game. It enables future animation features without refactoring.

**Independent Test**: Can be verified by confirming the animation system accepts arbitrary sprites, start/end positions, duration, and easing function — and that the worker animation is built on top of this general system rather than being hard-coded.

**Acceptance Scenarios**:

1. **Given** the animation system exists, **When** a developer creates a new animation for a different sprite type, **Then** they can reuse the same animation infrastructure without duplicating animation logic.
2. **Given** an animation is queued, **When** it runs, **Then** it supports configurable parameters: start position, end position, duration, and easing function.
3. **Given** multiple animations are active simultaneously, **When** the game renders, **Then** all active animations update independently and correctly without visual artifacts.

---

### User Story 5 - Animated Worker Recall (Priority: P2)

As a player, when the round ends and workers are recalled from the board, I see each worker marker animate from its board spot back to the owning player's name area in the top-left. This provides a satisfying visual closure to each round and reinforces which workers belonged to which player.

**Why this priority**: Adds visual polish and completes the animation lifecycle (placement + recall), but the game is fully playable without it. Depends on the core animation system from Stories 2-4.

**Independent Test**: Can be fully tested by completing a round and observing that all placed workers animate back from their board spots to the respective players' name areas, accompanied by the tick sound effect.

**Acceptance Scenarios**:

1. **Given** a round ends and workers are being recalled, **When** the recall phase begins, **Then** each placed worker animates from its board spot back to the owning player's name position using sine easing, accompanied by the tick sound effect.
2. **Given** multiple players have workers on the board, **When** recall occurs, **Then** each worker flies back to the correct player's name area (not all to the same player).
3. **Given** workers are recalled, **When** all recall animations complete, **Then** the board shows no remaining worker markers and the game proceeds to the next round.

---

### User Story 6 - Animated Worker Reassignment (Priority: P2)

As a player, during the reassignment phase when a worker moves from a Backstage holding slot to its final action space, I see the worker marker animate from the Backstage slot position on the board to the target space. This visually communicates the strategic second-placement move and makes it clear where the reassigned worker ends up.

**Why this priority**: Reassignment is an important game mechanic but occurs less frequently than regular placement. The animation reuses the same core system, so implementation cost is low once the foundation exists.

**Independent Test**: Can be fully tested by placing a worker on a Backstage slot, completing the placement phase, then reassigning the worker to an action space and observing the marker animate from the Backstage slot to the target space, accompanied by the tick sound effect.

**Acceptance Scenarios**:

1. **Given** the reassignment phase has started and a worker occupies a Backstage slot, **When** the worker is reassigned to a target action space, **Then** the marker sprite animates from the Backstage slot's position on the board to the target space using sine easing, accompanied by the tick sound effect.
2. **Given** a multiplayer game during reassignment, **When** another player's worker is reassigned, **Then** the animation shows the marker moving from that player's Backstage slot to the target space (not from the player's name area).
3. **Given** multiple Backstage slots are occupied (processed in order 1→2→3), **When** each is reassigned in sequence, **Then** each reassignment animates independently from the correct Backstage slot position.

---

### Edge Cases

- What happens if the game window is resized during an active animation? The animation should adapt to the new coordinate space or complete at the original target position without visual glitches.
- What happens if a placement is cancelled (via the cancel/undo mechanism) while an animation is in progress? The animation should be interrupted and the marker should either disappear or return to its origin.
- What happens if a player disconnects or reconnects during an animation? The game state should still be correct — animations are purely visual and do not affect game logic.
- What happens if multiple placements happen very rapidly (e.g., backstage placements in sequence)? Each animation should play correctly, potentially overlapping, without blocking game flow.

## Clarifications

### Session 2026-05-09

- Q: Should a sound effect play during worker placement animation? → A: Yes, play `tick_001.ogg` whenever a worker animation/movement occurs.
- Q: Should workers animate when recalled at end of round? → A: Yes, animate in reverse — workers fly back from board spots to the player's name area.
- Q: How should worker reassignment animate? → A: Animate from the Backstage holding slot position to the final target action space (not from the player's name area).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display each player's worker marker sprite (the same image used on board spots) next to their name in the top-left player list, replacing the current colored circles.
- **FR-002**: System MUST animate worker marker placement by creating a sprite at the placing player's name position in the player list and easing it to the target board spot position.
- **FR-003**: System MUST use sine easing (specifically the SINE easing curve from the animation library) for all worker placement animations.
- **FR-004**: System MUST show placement animations for all players — both the current player's own placements and other players' placements in multiplayer games.
- **FR-005**: System MUST ensure the animation originates from the correct player's name position in the player list, making it visually clear which player is placing the worker.
- **FR-006**: System MUST keep the game responsive during animations — animations are non-blocking and do not prevent user interaction.
- **FR-007**: System MUST provide a reusable animation abstraction that supports animating any sprite from one position to another with configurable easing function and duration.
- **FR-008**: System MUST correctly handle the final state after animation completes — the marker sprite at the target position must match the current static worker display.
- **FR-009**: System MUST handle animations gracefully when the game window is resized or when placements are cancelled mid-animation.
- **FR-010**: System MUST support multiple simultaneous animations without visual artifacts (e.g., two placements happening in rapid succession).
- **FR-011**: System MUST play the `tick_001.ogg` sound effect when a worker placement animation begins, for both the current player's own placements and other players' placements.
- **FR-012**: System MUST animate worker recall at the end of each round by flying each worker marker from its board spot back to the owning player's name position in the player list, using sine easing.
- **FR-013**: System MUST play the `tick_001.ogg` sound effect for each worker recall animation.
- **FR-014**: System MUST animate worker reassignment by moving the marker sprite from the Backstage holding slot's board position to the target action space, using sine easing (not from the player's name area).
- **FR-015**: System MUST play the `tick_001.ogg` sound effect for each worker reassignment animation.

### Key Entities

- **Animation**: Represents a single sprite movement from a start position to an end position over a duration using an easing function. Key attributes: sprite being animated, start position, end position, start time, duration, easing function, completion status, optional sound effect.
- **Animation Manager**: Orchestrates active animations, updating them each frame and cleaning up completed animations. Designed for reuse across different animation types (workers, cards, etc.).
- **Worker Marker Sprite**: The visual representation of a player's worker, identified by player color. Used both in the player list display and in placement animations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When any player places a worker, a visible animation plays showing the marker moving from the player's name area to the board spot — no placement appears instantly without animation. When workers are recalled, they animate back to the player's name area.
- **SC-002**: Players in multiplayer games can identify which opponent made a move by observing which player name the animation originates from, without needing to read the game log.
- **SC-003**: The player list displays marker sprites instead of circles, and each marker visually matches the markers shown on board spots.
- **SC-004**: Animations complete within a reasonable duration (between 0.5 and 2 seconds) — fast enough to not slow gameplay, slow enough to be noticeable.
- **SC-005**: The game remains interactive during animations — players can scroll, view information, and prepare for their turn while animations play.
- **SC-006**: The animation system can be extended to support new animation types (e.g., cards) without modifying the core animation logic.

## Assumptions

- The existing worker marker sprite images (`worker_{color}.png`) are suitable for use in both the player list and animations without modification.
- Animation duration will be set to a reasonable default (approximately 1 second) that can be adjusted through configuration if needed.
- Animations are purely cosmetic — game state is updated immediately upon server confirmation, and the animation is a visual overlay that plays afterward.
- The sine easing curve provides the desired visual feel; no custom easing curves are needed for this iteration.
- Backstage placements (intrigue card slots) will also animate from the placing player's name area to the backstage slot position.
- The animation system does not need to support pausing, rewinding, or speed control for this iteration — these can be added later if needed.
