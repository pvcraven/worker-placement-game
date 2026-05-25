# Feature Specification: Backstage Closed Cards

**Feature Branch**: `037-backstage-closed-cards`  
**Created**: 2026-05-25  
**Status**: Draft  
**Input**: User description: "Create additional backstage cards that instead of 'Play Intrigue' have a dark red '[CLOSED]' text. When in the reassignment phase, show those closed cards instead. When reassignment phase is over, go back to the normal 'Play Intrigue' cards. This is to help give players a visual cue they can't play in the backstage during reassignment phase."

## Clarifications

### Session 2026-05-25

- Q: Should the closed label read "[CLOSED]" (with brackets) or "CLOSED" (without brackets)? → A: Display "CLOSED" without brackets, with a box drawn around the text.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Backstage Slots Show Closed During Reassignment (Priority: P1)

During the reassignment phase, players cannot place workers on backstage slots (that mechanic only applies during the placement phase). Currently, there is no visual indication that backstage is unavailable — players may attempt to click backstage slots and be confused when nothing happens. This feature replaces the normal backstage card appearance with a "CLOSED" variant so players immediately understand the backstage is not available.

**Why this priority**: This is the core feature — without it, the visual cue doesn't exist and the player confusion remains.

**Independent Test**: Start a game, complete the placement phase, and enter the reassignment phase. Verify that all backstage slot cards now display "CLOSED" in dark red text with a box around it, instead of "Play Intrigue."

**Acceptance Scenarios**:

1. **Given** the game is in the reassignment phase, **When** a player views the board, **Then** each backstage slot card displays "CLOSED" in dark red text with a box drawn around it, instead of "Play Intrigue."
2. **Given** the game is in the reassignment phase, **When** a player views the backstage area, **Then** the closed appearance is shown for all backstage slots regardless of whether they are occupied or empty.

---

### User Story 2 - Backstage Slots Revert After Reassignment (Priority: P1)

When the reassignment phase ends and the next round begins (returning to the placement phase), the backstage slot cards must revert to their normal "Play Intrigue" appearance so players know the backstage is available again.

**Why this priority**: Equally critical — if the cards stay closed after reassignment ends, players will think backstage is permanently disabled.

**Independent Test**: Complete a reassignment phase and advance to the next round. Verify that backstage cards return to showing "Play Intrigue."

**Acceptance Scenarios**:

1. **Given** the reassignment phase has just ended and a new round has begun, **When** a player views the board, **Then** each backstage slot card displays the normal "Play Intrigue" text.
2. **Given** the game transitions from reassignment to a new placement phase, **When** the board refreshes, **Then** the closed card appearance is no longer visible on any backstage slot.

---

### Edge Cases

- What happens if the game ends during the reassignment phase? The closed state is irrelevant once the game-over screen appears — no special handling needed.
- What happens if a player reconnects during the reassignment phase? The backstage cards should display the closed state based on the current game phase at the time of reconnection.
- What happens in the first round before any reassignment has occurred? Backstage cards show the normal "Play Intrigue" state since the game is in the placement phase.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate a "closed" variant of each backstage slot card image that displays "CLOSED" in dark red text with a box drawn around the text, in place of "Play Intrigue."
- **FR-002**: The system MUST display the closed backstage card variant on all backstage slots when the game phase is reassignment.
- **FR-003**: The system MUST revert backstage slot cards to the normal "Play Intrigue" variant when the game phase transitions out of reassignment (i.e., at the start of a new round).
- **FR-004**: The system MUST display the correct backstage card variant when a player reconnects mid-game, based on the current game phase.
- **FR-005**: The "CLOSED" text MUST be displayed in dark red with a box border around it to visually communicate unavailability.

### Key Entities

- **Backstage Slot Card**: The visual card displayed in each backstage slot area on the board. Has two variants: the normal "Play Intrigue" version (used during placement phase) and the "CLOSED" version with boxed dark red text (used during reassignment phase).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of backstage slot cards display the "CLOSED" variant within the same frame that the reassignment phase begins.
- **SC-002**: 100% of backstage slot cards revert to the "Play Intrigue" variant within the same frame that a new placement phase begins.
- **SC-003**: Players can visually distinguish the closed state from the normal state at a glance — the dark red boxed "CLOSED" text provides a clear contrast from the normal card appearance.
- **SC-004**: Reconnecting players see the correct backstage card variant matching the current game phase immediately upon board render.

## Assumptions

- The backstage card images are pre-generated as part of the card image generation pipeline. A new closed variant image will be generated alongside the existing normal variant.
- The closed state is purely cosmetic — no server-side changes are needed. The client determines which variant to display based on the game phase already known to the client.
- All backstage slots share the same closed appearance (the "CLOSED" text replaces "Play Intrigue" identically on each slot).
- The dark red color for "CLOSED" text is a standard dark red (e.g., a deep crimson) that is legible against the backstage card background.
- The box around "CLOSED" is a simple rectangular border drawn in the same dark red color as the text.
