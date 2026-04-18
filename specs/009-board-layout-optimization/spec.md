# Feature Specification: Board Layout Optimization

**Feature Branch**: `009-board-layout-optimization`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Remove Real Estate Listings popup, show buildings on-board like quests. Reorganize board layout. Replace quest/building selection dialogs with inline highlight-and-click interaction using a cancel button."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inline Quest Selection via Highlight (Priority: P1)

When a player places a worker on a Garage space, instead of a popup dialog appearing, the four face-up quest cards on the board become highlighted with a yellow border. The player clicks directly on the quest card they want. A red cancel button (using `cancel.png`) appears in the lower-left corner of the window, allowing the player to cancel the selection.

**Why this priority**: This replaces the current disruptive popup dialog with a smoother, more intuitive in-board interaction. It is the most impactful UX improvement and establishes the highlight-and-click pattern reused by building selection.

**Independent Test**: Can be tested by placing a worker on any Garage space, verifying quest cards highlight, clicking a card to select, or clicking cancel to abort.

**Acceptance Scenarios**:

1. **Given** a player's turn and available workers, **When** the player places a worker on Garage 1/2/3, **Then** the four face-up quest cards gain a yellow highlight border and a red cancel button appears in the lower-left corner.
2. **Given** quest cards are highlighted, **When** the player clicks on a highlighted quest card, **Then** that quest is selected (same server message as today), highlights are removed, and the cancel button disappears.
3. **Given** quest cards are highlighted, **When** the player clicks the red cancel button, **Then** the selection is cancelled (same cancel message as today), highlights are removed, and the cancel button disappears.
4. **Given** quest cards are highlighted, **When** the player clicks elsewhere on the board (not a quest card or the cancel button), **Then** nothing happens and the highlight state persists.

---

### User Story 2 - Always-Visible Building Market on Board (Priority: P2)

The "Real Estate Listings" button and popup dialog are removed. Instead, face-up buildings for sale are rendered directly on the board, similar to how quest cards are always visible. The board layout is reorganized: quest cards move up, backstage spaces are repositioned, and buildings are placed in a dedicated area with the Realtor action space positioned near them.

**Why this priority**: Showing buildings permanently on the board eliminates the hidden-information problem where players must open a popup to see what's for sale. This is the main layout restructuring that the other stories depend on.

**Independent Test**: Can be tested by starting a game and verifying buildings are visible on the board without clicking any button, and that the Realtor space is near the building display.

**Acceptance Scenarios**:

1. **Given** a game is in progress, **When** the board is displayed, **Then** face-up buildings for sale are rendered directly on the board (not behind a popup).
2. **Given** a game is in progress, **When** the board is displayed, **Then** the quest cards are positioned higher on the board than before.
3. **Given** a game is in progress, **When** the board is displayed, **Then** backstage spaces are visible in their new position.
4. **Given** a game is in progress, **When** the board is displayed, **Then** the Realtor action space is positioned near the building display area.
5. **Given** a game is in progress, **When** a building is purchased by any player, **Then** the building display updates (purchased building removed, replacement drawn from deck if available).

---

### User Story 3 - Inline Building Purchase via Highlight (Priority: P3)

When a player places a worker on the Realtor space, the face-up buildings they can afford become highlighted with a yellow border. Buildings they cannot afford are not highlighted, and an error message is shown if they cannot afford any building. The player clicks directly on the highlighted building to purchase it. A red cancel button (using `cancel.png`) appears in the lower-left corner for cancellation.

**Why this priority**: This mirrors the quest selection UX from Story 1 but for buildings, completing the unified highlight-and-click interaction pattern.

**Independent Test**: Can be tested by placing a worker on the Realtor space, verifying affordable buildings highlight, clicking one to purchase, or cancelling.

**Acceptance Scenarios**:

1. **Given** a player's turn and available workers, **When** the player places a worker on the Realtor space, **Then** buildings the player can afford gain a yellow highlight border, unaffordable buildings do not highlight, and a red cancel button appears.
2. **Given** buildings are highlighted, **When** the player clicks on a highlighted (affordable) building, **Then** that building is purchased (same server message as today), highlights are removed, and the cancel button disappears.
3. **Given** buildings are highlighted, **When** the player clicks on a non-highlighted (unaffordable) building, **Then** an error message is shown (e.g., "You can't afford that building").
4. **Given** buildings are highlighted, **When** the player clicks the red cancel button, **Then** the purchase is cancelled, highlights are removed, and the cancel button disappears.
5. **Given** the player cannot afford any building, **When** they place a worker on the Realtor, **Then** an error message is displayed and no buildings are highlighted.

---

### Edge Cases

- What happens when there are zero buildings in the market (deck exhausted)? The building area shows empty slots or a "No buildings available" label.
- What happens when a quest reward grants a "Choose Free Building"? The building highlight flow activates with all buildings highlighted (since cost is zero).
- What happens if the player resizes the window while highlights are active? Highlights reposition correctly with the cards.
- What happens if a quest card or building is selected by another player while the current player is in highlight mode? The highlight state refreshes to reflect the updated cards.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render face-up buildings directly on the game board, visible at all times during gameplay.
- **FR-002**: System MUST remove the "Real Estate Listings" toggle button and popup dialog.
- **FR-003**: System MUST reorganize the board layout so quest cards, backstage spaces, buildings, and action spaces all fit without overlap.
- **FR-004**: System MUST position the Realtor action space near the building display area.
- **FR-005**: System MUST highlight face-up quest cards with a yellow border when a player places a worker on a Garage space.
- **FR-006**: System MUST allow the player to click a highlighted quest card to select it.
- **FR-007**: System MUST display a red cancel button (using `cancel.png`) in the lower-left corner during highlight selection mode.
- **FR-008**: System MUST highlight affordable face-up buildings with a yellow border when a player places a worker on the Realtor space.
- **FR-009**: System MUST NOT highlight buildings the player cannot afford.
- **FR-010**: System MUST show an error message if the player clicks an unaffordable building during highlight mode.
- **FR-011**: System MUST show an error message if the player cannot afford any building when landing on the Realtor.
- **FR-012**: System MUST remove all highlights and the cancel button when a selection is made or cancelled.
- **FR-013**: System MUST update the on-board building display when a building is purchased (remove purchased building, show replacement from deck).

### Key Entities

- **Board Layout**: The spatial arrangement of action spaces, quest cards, backstage slots, and building cards on the game board.
- **Highlight State**: A transient UI state indicating which cards are selectable, triggered by specific worker placements.
- **Cancel Button**: A persistent on-screen control during highlight mode that allows the player to abort their selection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can see all available buildings without opening any popup or menu.
- **SC-002**: Quest selection after landing on a Garage space completes in a single click on the board (no dialog interaction required).
- **SC-003**: Building purchase after landing on the Realtor completes in a single click on the board (no dialog interaction required).
- **SC-004**: All board elements (action spaces, quest cards, backstage slots, buildings) are visible without overlap at the default window size.
- **SC-005**: Cancel button appears within 100ms of entering highlight mode and disappears immediately on selection or cancellation.
- **SC-006**: 100% of existing game functionality (worker placement, quest completion, intrigue, backstage) continues to work after the layout change.

## Assumptions

- The `cancel.png` graphic asset exists or will be created as part of this feature.
- The board has sufficient screen real estate to display both quest cards and building cards simultaneously at the default window size.
- The server-side messaging protocol for quest selection and building purchase remains unchanged; only the client-side interaction flow changes.
- The number of face-up buildings (currently 3) and face-up quest cards (currently 4) remains the same.
- Backstage spaces can be repositioned without affecting their game mechanics.
