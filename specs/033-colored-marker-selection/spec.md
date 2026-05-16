# Feature Specification: Colored Marker Selection

**Feature Branch**: `033-colored-marker-selection`
**Created**: 2026-05-16
**Status**: Draft
**Input**: User description: "Create seven different colored markers. On startup, have a dialog pop up that lets a player select which color marker they would like to have. When selected, put the players name under the marker. If two players try to select the same marker, ignore the second player. Once the final player has picked, pause for a second so people can see the picked markers, then start the game."

## User Scenarios & Testing

### User Story 1 - Player Selects a Marker Color (Priority: P1)

When a game is starting, each player sees a dialog presenting seven differently colored markers. The player clicks on the marker color they want. Once selected, the player's name appears beneath that marker, and the marker becomes unavailable to other players. The dialog remains visible until all players in the game have selected their marker.

**Why this priority**: This is the core feature — without marker selection, the game cannot assign player colors. This must work before anything else.

**Independent Test**: Start a game with 2+ players. Verify the marker selection dialog appears for each player, each player can click a marker, their name appears under it, and selected markers become unavailable.

**Acceptance Scenarios**:

1. **Given** a game is starting with multiple players connected, **When** the game transitions to the pre-game phase, **Then** all players see a dialog displaying seven colored markers
2. **Given** the marker selection dialog is visible, **When** a player clicks an available marker, **Then** the player's name appears beneath that marker for all connected players
3. **Given** a marker has already been selected by another player, **When** a second player clicks that same marker, **Then** the selection is ignored and the marker remains assigned to the first player

---

### User Story 2 - Game Starts After All Players Pick (Priority: P1)

After the last player selects their marker, all players see the final marker assignments for a brief moment (approximately one second), giving everyone time to see who chose what. Then the game starts automatically.

**Why this priority**: This completes the selection flow — without it, the game never transitions from marker selection to gameplay.

**Independent Test**: Start a game with all players, have each select a marker, verify a brief pause occurs showing final assignments, then the game begins.

**Acceptance Scenarios**:

1. **Given** all players have selected a marker, **When** the last player makes their selection, **Then** the dialog remains visible for approximately one second showing all assignments
2. **Given** the pause period has elapsed, **When** the timer completes, **Then** the game starts normally (same behavior as current game start)

---

### User Story 3 - Seven Distinct Marker Colors (Priority: P1)

Seven visually distinct marker colors are available for selection. The colors should be easily distinguishable from one another and work well on the game board background.

**Why this priority**: The markers must exist and be visually distinct for selection to be meaningful.

**Independent Test**: Open the marker selection dialog and verify seven markers are displayed, each with a clearly different color that is easy to distinguish.

**Acceptance Scenarios**:

1. **Given** the marker selection dialog is displayed, **When** a player views the dialog, **Then** exactly seven markers are shown in green, red, purple, blue, pink, lilac, and orange
2. **Given** the markers are displayed on the game board, **When** a player looks at the board, **Then** each player's marker color is easily distinguishable from other players' markers

---

### Edge Cases

- What happens if a player disconnects during marker selection? The game should handle disconnection the same way it currently handles disconnection during gameplay — the selection dialog should update accordingly.
- What happens if two players click the same marker at nearly the same time? The server processes selections in order of receipt — the first to arrive wins, the second is silently ignored.
- What if there are fewer players than markers? Unselected markers simply remain unclaimed. The game starts once all connected players have picked.

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a marker selection dialog to all players when a game is starting
- **FR-002**: The dialog MUST present exactly seven markers in these colors: green, red, purple, blue, pink, lilac, and orange
- **FR-003**: When a player selects a marker, their name MUST appear beneath that marker for all connected players in real time
- **FR-004**: If a marker has already been claimed by another player, subsequent attempts to select it MUST be silently ignored
- **FR-005**: Once all players have selected a marker, the system MUST pause for approximately one second before starting the game
- **FR-006**: The selected marker color MUST be used as the player's color throughout the game (board markers, UI elements)
- **FR-007**: The marker selection dialog MUST update in real time as other players make their selections

### Key Entities

- **Marker**: Represents a colored game piece. Has a color, an optional owner (player), and a selected/available status.
- **Marker Selection State**: Tracks which markers are claimed by which players during the pre-game selection phase.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All players can see and interact with the marker selection dialog within 1 second of game start
- **SC-002**: Marker selections are reflected on all clients within 1 second of the selection being made
- **SC-003**: 100% of simultaneous selection conflicts are resolved correctly (first-come-first-served)
- **SC-004**: The game transitions from marker selection to gameplay within 2 seconds of the last player selecting
- **SC-005**: All seven marker colors are distinguishable by players under normal viewing conditions

## Clarifications

### Session 2026-05-16

- Q: What are the specific seven marker colors? → A: Green, red, purple, blue, pink, lilac, orange

## Assumptions

- The maximum number of players in a game is fewer than seven, so there will always be unclaimed markers remaining
- Marker colors are predetermined as green, red, purple, blue, pink, lilac, and orange (not user-customizable beyond selection from these seven)
- The existing game startup flow can accommodate a pre-game selection phase before the current game start logic
- Player markers are currently a single default color — this feature replaces that with player-chosen colors
- The one-second pause after all selections is a fixed duration, not configurable
