# Feature Specification: Board Layout Optimization

**Feature Branch**: `004-board-layout-optimization`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "Adjust item placement on the board and optimize screen real estate. Remove labels, rename spaces, convert building market to popup dialog, batch-render shapes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remove Redundant Labels and Reclaim Vertical Space (Priority: P1)

When the game starts, the board renders without the "THE BOARD", "THE GARAGE", and "BACKSTAGE" heading labels. All board elements shift upward to fill the freed space. Backstage slots are renamed from "Slot 1/2/3" to "Backstage 1/2/3" so they are self-describing without a section heading.

**Why this priority**: This is the simplest visual change and has no gameplay or interaction impact. It immediately reclaims vertical space and improves information density.

**Independent Test**: Launch a new game and verify no "THE BOARD", "THE GARAGE", or "BACKSTAGE" heading text appears. Verify all board elements are shifted upward with no wasted whitespace. Verify backstage slots are labeled "Backstage 1", "Backstage 2", "Backstage 3".

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** the board renders, **Then** no "THE BOARD" label appears anywhere on the board
2. **Given** a new game starts, **When** the board renders, **Then** no "THE GARAGE" label appears above the garage spaces
3. **Given** a new game starts, **When** the board renders, **Then** no "BACKSTAGE" label appears above the backstage slots
4. **Given** a new game starts, **When** the board renders, **Then** backstage slots display "Backstage 1", "Backstage 2", "Backstage 3" as their labels
5. **Given** labels are removed, **When** the board renders, **Then** all board elements shift upward to use the freed vertical space, with no large empty gaps

---

### User Story 2 - Rename Realtor and Real Estate Listings (Priority: P1)

The permanent action space currently named "Real Estate Listings" (the space where a player places a worker to trigger the building purchase flow) is renamed to "Realtor" across all display names, configuration, and code references. The building market popup (see User Story 3) is titled "Real Estate Listings" — the name moves from the board space to the market dialog.

**Why this priority**: This rename is required before the building market popup (User Story 3) can be implemented, since both changes affect the "Real Estate Listings" name.

**Independent Test**: Launch a new game and verify the permanent action space on the left column reads "Realtor" (not "Real Estate Listings"). Verify the purchase dialog title reads "Real Estate Listings".

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** the board renders, **Then** the permanent action space for building purchase displays the name "Realtor"
2. **Given** a player places a worker on the "Realtor" space, **When** the building purchase dialog opens, **Then** the dialog title reads "Real Estate Listings"
3. **Given** the rename is applied, **When** any game log entry references the space, **Then** it uses "Realtor" (not "Real Estate Listings")

---

### User Story 3 - Convert Building Market to Popup Dialog (Priority: P1)

The inline building market display (currently rendered as text labels at the bottom of the board showing face-up buildings with cost and VP) is removed from the board surface. In its place, a "Real Estate Listings" button appears in the same area as the "My Quests" and "My Intrigue" buttons (bottom-left button row). Clicking this button opens a popup overlay panel (styled like the quest/intrigue hand panels) that shows the face-up buildings with full details: name, genre, coin cost, accumulated VP, visitor reward, owner bonus, and description. The deck count is also displayed. Clicking the button again or clicking elsewhere closes the panel.

**Why this priority**: This is the largest visual change and directly optimizes screen real estate by replacing always-visible market text with an on-demand popup.

**Independent Test**: Launch a game and verify no building market text appears inline on the board. Click "Real Estate Listings" button and verify a popup panel appears with full building card details. Click again to dismiss.

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** the board renders, **Then** no inline building market text or labels appear on the board surface
2. **Given** the game is running, **When** the player looks at the bottom-left button area, **Then** a "Real Estate Listings" button is visible alongside "My Quests" and "My Intrigue"
3. **Given** the player clicks "Real Estate Listings", **When** the popup opens, **Then** it displays each face-up building with: name, genre, coin cost, accumulated VP, visitor reward summary, owner bonus summary, and description text
4. **Given** the popup is open, **When** the player clicks "Real Estate Listings" again, **Then** the popup closes
5. **Given** the popup is open, **When** the popup displays buildings, **Then** the number of buildings remaining in the deck is shown (e.g., "20 in deck")
6. **Given** a building is purchased by any player, **When** the popup is open, **Then** the popup content updates to reflect the current market state
7. **Given** the "My Quests" or "My Intrigue" panel is open, **When** the player clicks "Real Estate Listings", **Then** the other panel closes and the Real Estate Listings panel opens

---

### User Story 4 - Batch Render Board Shapes for Performance (Priority: P2)

All board rectangles, outlines, and static visual elements (action space boxes, backstage slot boxes, board background) are drawn using a batched shape list instead of individual draw calls per frame. Worker tokens and text overlays continue to use immediate-mode drawing since they change frequently. This improves rendering performance by reducing per-frame draw calls.

**Why this priority**: This is a rendering optimization with no visual or gameplay change. It can be done independently and benefits all other stories by improving frame rate.

**Independent Test**: Launch a game and verify the board looks identical to the current version. Measure or observe that frame rate is stable at 60fps with no visual differences.

**Acceptance Scenarios**:

1. **Given** the board renders, **When** comparing to the previous version, **Then** all action spaces, backstage slots, and board background appear visually identical
2. **Given** the board renders, **When** using batched shape rendering, **Then** static shapes (rectangles, outlines) are drawn in a single batch call rather than individual calls per space
3. **Given** a worker is placed or the board state changes, **When** the board re-renders, **Then** the shape batch is rebuilt to reflect the updated state (e.g., occupied space color changes)
4. **Given** the game is running with 5 players and multiple buildings, **When** observing performance, **Then** frame rate remains at 60fps

---

### Edge Cases

- What happens when all three toggle buttons (My Quests, My Intrigue, Real Estate Listings) are clicked in rapid succession? Only the most recently clicked panel should be visible; others close.
- What happens to the Real Estate Listings popup when a building is purchased while it is open? The popup should update its content to reflect the new market state.
- What happens if the building deck is empty and 0 buildings are face-up? The popup should show an informational message like "No buildings available."
- What happens if the board is resized? The batched shape list should rebuild to match the new dimensions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST NOT display a "THE BOARD" heading label on the board
- **FR-002**: System MUST NOT display a "THE GARAGE" heading label above the garage spaces
- **FR-003**: System MUST NOT display a "BACKSTAGE" heading label above the backstage slots
- **FR-004**: System MUST label backstage slots as "Backstage 1", "Backstage 2", "Backstage 3" instead of "Slot 1", "Slot 2", "Slot 3"
- **FR-005**: System MUST shift all board elements upward to fill vertical space freed by removed labels
- **FR-006**: System MUST rename the permanent action space "Real Estate Listings" to "Realtor" across all display names, configuration (space_id, space_type in board.json), and code references (server, client, shared)
- **FR-007**: System MUST remove the inline building market display from the board surface (the text labels showing face-up buildings, cost, and VP)
- **FR-008**: System MUST add a "Real Estate Listings" button to the bottom-left button row alongside "My Quests" and "My Intrigue"
- **FR-009**: System MUST display a popup overlay panel when the "Real Estate Listings" button is clicked, showing face-up buildings with full details
- **FR-010**: The popup panel MUST display each building's name, genre, coin cost, accumulated VP, visitor reward, owner bonus, and description
- **FR-011**: The popup panel MUST display the count of buildings remaining in the deck
- **FR-012**: Clicking the "Real Estate Listings" button while the popup is open MUST close the popup (toggle behavior)
- **FR-013**: Opening any panel (Quests, Intrigue, Real Estate Listings) MUST close any other currently open panel
- **FR-014**: The popup MUST update its displayed content when the building market state changes (purchase, round-end VP update)
- **FR-015**: The building purchase dialog title MUST read "Real Estate Listings" (replacing "Purchase a Building")
- **FR-016**: System MUST render all static board shapes (space rectangles, outlines, background) using a batched shape list for performance
- **FR-017**: The shape batch MUST be rebuilt when board state changes affect visual appearance (e.g., space becomes occupied)
- **FR-018**: The Game Log section MUST remain unchanged

### Key Entities

- **Board Shape Batch**: A pre-built collection of all static visual shapes (rectangles, outlines) drawn in a single render call per frame. Rebuilt when board state changes.
- **Real Estate Listings Panel**: A popup overlay (similar to quest/intrigue hand panels) showing the current building market with full building details. Toggled by a button.
- **Realtor Space**: The permanent action space (formerly "Real Estate Listings", space_id: `realtor`) where a player places a worker to initiate a building purchase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The board renders with no heading labels ("THE BOARD", "THE GARAGE", "BACKSTAGE"), freeing vertical space
- **SC-002**: Backstage slots are self-describing with "Backstage N" labels, requiring no external heading
- **SC-003**: The permanent action space displays as "Realtor" and the building market popup is titled "Real Estate Listings"
- **SC-004**: Players can view full building market details (name, genre, cost, VP, rewards, description) via the popup without inline board clutter
- **SC-005**: The popup toggle behavior matches "My Quests" and "My Intrigue" panels — only one panel open at a time
- **SC-006**: Board rendering uses fewer draw calls by batching static shapes, maintaining 60fps with no visual regression
- **SC-007**: All existing gameplay functionality (worker placement, building purchase, visitor/owner rewards) continues to work identically

## Clarifications

### Session 2026-04-16

- Q: Should the rename from "Real Estate Listings" to "Realtor" include internal identifiers (space_id, space_type, config) or only the display name? → A: Rename everything — display name, space_id, space_type, and all code references change from `real_estate_listings` to `realtor`.

## Assumptions

- The existing quest/intrigue hand panel rendering pattern (semi-transparent background, centered overlay) is the desired visual style for the building market popup
- The "Real Estate Listings" button uses the same size and style as the existing "My Quests" and "My Intrigue" buttons
- The shape batch approach follows the arcade library's `ShapeElementList` pattern for batched rendering
- Worker tokens and text labels remain as immediate-mode draws since they change every frame
- The Game Log panel is unaffected by all changes in this feature
- Building card rendering in the popup can reuse the existing `CardRenderer.draw_contract` pattern or a similar card layout
