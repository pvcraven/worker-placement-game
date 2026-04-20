# Feature Specification: Board Layout Scaling

**Feature Branch**: `pvcraven/013-board-layout-scaling`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "Scale the board with the window getting bigger, and re-arrange things on the screen. Cards scale with window. Fix building VP/Owner text positioning. Two-column building layout. Game log panel scales with window."

## Clarifications

### Session 2026-04-20

- Q: Which text elements should scale with the window? → A: All text everywhere scales (board text, game log, resource bar, status bar).
- Q: Should dialog boxes scale with the window? → A: Yes, dialog boxes (card selection, target selection, quest completion, etc.) must also scale with the window.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cards Scale With Window (Priority: P1)

A player resizes the game window larger or smaller. All card images on the board (resource spaces, quest display, building market, constructed buildings, backstage intrigue cards) scale proportionally with the window size rather than remaining at a fixed pixel size.

**Why this priority**: This is the core visual improvement — without card scaling, larger windows show tiny cards surrounded by empty space, making the game harder to read and less visually appealing.

**Independent Test**: Resize the window from the default size to double the size. All cards on the board should grow proportionally and remain legible. Shrink the window to half size — cards should shrink accordingly without overlapping or clipping.

**Acceptance Scenarios**:

1. **Given** the game window at default size, **When** the player drags the window to double width and height, **Then** all card images on the board scale up proportionally and maintain their relative positions within the board layout.
2. **Given** the game window at a large size, **When** the player shrinks the window, **Then** all cards scale down proportionally without overlapping or being clipped off-screen.
3. **Given** the game is running, **When** the window is resized at any time during gameplay, **Then** the board re-layouts immediately with no visual artifacts or lag.

---

### User Story 2 - Two-Column Building Layout (Priority: P2)

The board layout is reorganized so that player-constructed buildings display in two columns instead of one. The default resource spaces (permanent action spaces that exist at game start) shift to the left side with reduced margins to make room for the two building columns.

**Why this priority**: The current single-column building layout runs out of vertical space as players construct buildings. Two columns allow more buildings to be visible without scrolling or overlap.

**Independent Test**: Start a game and purchase several buildings. Verify they appear in two columns. Verify the permanent action spaces on the left remain fully visible with their labels.

**Acceptance Scenarios**:

1. **Given** a game in progress, **When** a player constructs a building, **Then** buildings fill into a two-column grid layout to the right of the permanent action spaces.
2. **Given** multiple buildings have been constructed, **When** viewing the board, **Then** buildings are arranged in two columns with consistent spacing and no overlap.
3. **Given** the default resource spaces, **When** the board is rendered, **Then** they are positioned on the left side of the board with reduced margins to accommodate the two building columns.

---

### User Story 3 - Building VP and Owner Text Positioning (Priority: P2)

The "1 VP" and "Owner" text labels displayed below constructed buildings currently do not reposition correctly when the window is resized. After this change, these labels stay anchored to their associated building card regardless of window size.

**Why this priority**: Mispositioned labels are visually confusing and can overlap with other elements, but the game remains playable.

**Independent Test**: Construct a building, then resize the window. The VP and Owner text should remain correctly positioned below the building card at all window sizes.

**Acceptance Scenarios**:

1. **Given** a constructed building is displayed on the board, **When** the window is resized, **Then** the VP text and Owner text remain positioned directly below the building card.
2. **Given** multiple buildings in two columns, **When** the window is at various sizes, **Then** all VP/Owner labels align correctly with their respective building cards.

---

### User Story 4 - Game Log Panel Scales With Window (Priority: P3)

The game log panel on the right side of the screen scales its width and height proportionally with the window size, so it remains readable and proportionate at all window sizes.

**Why this priority**: The game log is supplementary information. Fixed-size panels in a scaling layout look out of place, but the game is fully playable without this.

**Independent Test**: Resize the window and verify the game log panel grows and shrinks proportionally with the window, remaining readable at all sizes.

**Acceptance Scenarios**:

1. **Given** the game log panel is visible, **When** the window is enlarged, **Then** the game log panel grows proportionally in width and height.
2. **Given** the game log panel is visible, **When** the window is shrunk, **Then** the game log panel shrinks proportionally while remaining readable (text does not clip or overlap).

---

### User Story 5 - All Text Scales With Window (Priority: P1)

All text elements in the game — board labels, card names, VP/Owner labels, game log entries, resource bar numbers, and the status bar — scale proportionally with the window size, matching the card scaling so the overall presentation remains visually cohesive.

**Why this priority**: Text that stays small while cards grow (or vice versa) looks broken and is hard to read. Text scaling is essential to the core scaling experience.

**Independent Test**: Resize the window from default to double size. All text across the board, game log, resource bar, and status bar should grow proportionally. Shrink the window — all text shrinks proportionally while remaining legible.

**Acceptance Scenarios**:

1. **Given** the game window at default size, **When** the player doubles the window size, **Then** all text elements (board labels, game log, resource bar, status bar) scale up proportionally.
2. **Given** the game window at a large size, **When** the player shrinks it, **Then** all text elements scale down proportionally while remaining legible above a minimum font size threshold.

---

### User Story 6 - Dialog Boxes Scale With Window (Priority: P2)

All modal dialog boxes — card selection (intrigue, quest completion), player target selection, reward choice, building purchase — scale their dimensions, card images, buttons, and text proportionally with the window size.

**Why this priority**: Dialogs that remain small in a large window (or overflow in a small window) feel broken and inconsistent with the rest of the scaling behavior.

**Independent Test**: Open a card selection dialog at default window size, close it, resize the window larger, then open it again. The dialog, cards, buttons, and text should all be proportionally larger.

**Acceptance Scenarios**:

1. **Given** a dialog box is triggered at a large window size, **When** the dialog renders, **Then** the dialog dimensions, card images, buttons, and text are proportionally larger than at default size.
2. **Given** a dialog box is triggered at a small window size, **When** the dialog renders, **Then** the dialog scales down proportionally while remaining usable.

---

### Edge Cases

- What happens when the window is shrunk to a very small size? Cards and text should remain legible down to a minimum scale/font size threshold.
- What happens when the window is maximized on a 4K display? Cards should scale up but cap at a maximum scale to avoid pixelation of card images.
- What happens when exactly one building has been constructed? It should appear in the first column, first row.
- What happens when buildings fill both columns completely? Additional buildings should still be visible (overflow handling).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All card sprites on the board MUST scale proportionally when the window is resized.
- **FR-002**: Card scaling MUST have a minimum and maximum scale factor to prevent illegibility or excessive pixelation.
- **FR-003**: The permanent action spaces (resource spaces existing at game start) MUST be positioned on the left side of the board with reduced margins.
- **FR-004**: Player-constructed buildings MUST be arranged in a two-column grid layout to the right of the permanent action spaces.
- **FR-005**: The "VP" and "Owner" text labels on buildings MUST reposition dynamically to stay anchored below their associated building card at any window size.
- **FR-006**: The game log panel MUST scale its dimensions proportionally with the window size.
- **FR-007**: Board re-layout MUST occur immediately on window resize with no visible delay or flicker.
- **FR-009**: All text elements (board labels, game log entries, resource bar, status bar) MUST scale proportionally with the window size.
- **FR-010**: Text scaling MUST have a minimum font size threshold to prevent illegibility at small window sizes.
- **FR-011**: All modal dialog boxes (card selection, target selection, quest completion, reward choice, building purchase) MUST scale their dimensions, card images, buttons, and text proportionally with the window size.
- **FR-008**: The face-up quest display, face-up building market, and backstage slots MUST also scale and reposition correctly with the window.

### Key Entities

- **Board Layout**: The spatial arrangement of all action spaces, building lots, quest display, and backstage on the game board. Defined by proportional positions that scale with window size.
- **Card Sprite**: A visual representation of a game card (quest, intrigue, building, or action space) rendered as an image that scales with the board.
- **Building Lot Grid**: A two-column layout area where player-constructed buildings are placed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All card images on the board scale smoothly when the window is resized, with no fixed-size cards remaining at the old size.
- **SC-002**: Building VP and Owner text labels remain correctly positioned below their building card at every tested window size (default, 50% smaller, 100% larger, maximized).
- **SC-003**: Up to 10 constructed buildings are visible on the board in a two-column layout without overlap.
- **SC-004**: The game log panel maintains proportional sizing at all tested window sizes.
- **SC-005**: No visual artifacts, overlapping elements, or clipped text appear during or after window resize.
- **SC-006**: All text elements across the entire UI scale proportionally at every tested window size.
- **SC-007**: All dialog boxes scale proportionally with the window, including their card images, buttons, and text.

## Assumptions

- Card PNG images are high enough resolution to scale up to ~2x without unacceptable pixelation.
- The minimum supported window size is approximately 800x600 pixels.
- The resource bar at the bottom and status bar at the top remain at fixed heights (they do not scale).
- Overlay panels (hand display, player overview) are not part of this change — they are drawn on demand and already center themselves.
- The number of permanent action spaces and backstage slots does not change (layout is static for those elements).
