# Feature Specification: Tabbed Side Panel

**Feature Branch**: `014-tabbed-side-panel`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: User description: "Convert the right-side panel from a fixed game log into a tabbed interface with selectable views for Game Log, My Quests, My Intrigue, Completed Quests, and Producer."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tab Navigation Between Panel Views (Priority: P1)

During gameplay, the player wants to quickly switch between different information views (game log, quest cards, intrigue cards, completed quests, producer card) without losing context. Currently, the game log occupies the entire right panel, and the other views are accessed via pop-up dialogs that obscure the board. The player clicks tab buttons at the top of the right panel to switch what content is displayed below.

**Why this priority**: This is the core interaction — without tab switching, none of the other content views can be accessed in the new panel layout. It replaces five separate dialog buttons with a unified tabbed interface.

**Independent Test**: Can be fully tested by clicking each tab button and verifying the panel title changes and the correct content type appears. Delivers immediate value by consolidating scattered dialogs into one consistent panel.

**Acceptance Scenarios**:

1. **Given** the game is in progress and the right panel is visible, **When** the player clicks the "Game Log" tab, **Then** the panel title reads "Game Log" and the scrollable log entries are displayed below.
2. **Given** the game is in progress, **When** the player clicks the "My Quests" tab, **Then** the panel title reads "My Quests" and the player's current quest cards are displayed.
3. **Given** the game is in progress, **When** the player clicks any tab, **Then** the previously active tab is deselected and the newly clicked tab becomes visually active (highlighted or differentiated).
4. **Given** the panel is showing "My Intrigue", **When** the player clicks "Game Log", **Then** the panel switches back to the game log without any dialog pop-up appearing.
5. **Given** a dialog box is displayed (e.g., "Select an intrigue card to play"), **When** the player clicks a different tab such as "My Quests", **Then** the panel content switches to the quests view while the dialog remains open and functional.
6. **Given** a dialog box is displayed and the player has switched tabs to review information, **When** the player returns to the original tab or interacts with the dialog, **Then** the dialog is still active and the player can complete the prompted action.

---

### User Story 2 - Card Display in Two-Column Layout (Priority: P2)

When the player views card-based tabs (My Quests, My Intrigue, Completed Quests), the cards are displayed in a two-column grid within the panel so that more cards are visible at once without scrolling, and the cards fit within the panel width.

**Why this priority**: The panel has limited width. Displaying cards in two columns maximizes information density and makes the tabbed views practical for card content. Without this, cards may not fit or only one card would show per row, wasting space.

**Independent Test**: Can be tested by switching to any card tab and verifying cards are arranged in two columns that fit within the panel boundaries, with no horizontal overflow or overlap.

**Acceptance Scenarios**:

1. **Given** the player has 4 quest cards and clicks "My Quests", **When** the panel renders, **Then** the cards are arranged in a 2-column grid (2 rows of 2 cards).
2. **Given** the player has 1 quest card, **When** the panel renders, **Then** the single card is displayed in the first column position without layout issues.
3. **Given** the player has more cards than can fit in the visible panel area, **When** the panel renders, **Then** the cards are laid out in two columns and the lower cards extend downward (scrollable or clipped gracefully).

---

### User Story 3 - Producer Card Display in Panel (Priority: P3)

When the player clicks the "Producer" tab, their producer card is displayed within the right-side panel instead of a pop-up dialog.

**Why this priority**: The producer card is a single-card view, simpler than the multi-card tabs. It completes the set of views that previously used dialogs, ensuring the full migration from dialogs to the tabbed panel.

**Independent Test**: Can be tested by clicking the "Producer" tab and confirming the producer card image (or fallback text) appears within the panel with a "Producer" title.

**Acceptance Scenarios**:

1. **Given** the player has a producer card assigned, **When** the player clicks the "Producer" tab, **Then** the panel title reads "Producer" and the producer card image is displayed.
2. **Given** the player has no producer card, **When** the player clicks the "Producer" tab, **Then** the panel displays a message such as "No producer card".

---

### Edge Cases

- What happens when the player has zero cards in a card tab (e.g., no intrigue cards)? The panel displays an empty state message (e.g., "No intrigue cards").
- What happens when the window is resized? The tab bar and panel content scale proportionally with the window, maintaining the two-column card layout.
- What happens if a card is gained or lost while viewing that tab? The panel content refreshes to reflect the current card state.
- What happens during phases where the player cannot interact (e.g., opponent's turn)? Tabs remain fully functional — they are read-only informational views, not actions.
- What happens when a dialog is displayed and the player clicks a tab? The tab switches normally; the dialog remains open and interactive. Tab switching never dismisses or interferes with active dialogs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The right-side panel MUST have a row of tab buttons at its top, above the content area.
- **FR-002**: The tab buttons MUST include: "Game Log", "My Quests", "My Intrigue", "Completed Quests", and "Producer".
- **FR-003**: Clicking a tab button MUST switch the panel content to the corresponding view.
- **FR-004**: The currently active tab MUST be visually distinguished from inactive tabs (e.g., different background color, bold text, or underline).
- **FR-005**: The panel MUST display a title matching the active tab name, positioned below the tab bar and above the content.
- **FR-006**: Card-based views (My Quests, My Intrigue, Completed Quests) MUST display cards in a two-column grid layout that fits within the panel width.
- **FR-007**: The Producer view MUST display the player's producer card image, or a "No producer card" message if none is assigned.
- **FR-008**: The Game Log view MUST display the same scrollable log entries currently shown in the panel.
- **FR-009**: The existing dialog-based buttons for "My Quests", "My Intrigue", "Completed Quests", and "Producer" MUST be removed, as their functionality is replaced by the tabs.
- **FR-010**: The default active tab when the game starts MUST be "Game Log".
- **FR-011**: Card views MUST update their content when the underlying data changes (e.g., a quest is completed, an intrigue card is played).
- **FR-012**: Tab switching MUST remain functional even when a dialog box is displayed (e.g., card selection prompts, quest completion prompts). Switching tabs MUST NOT dismiss or interfere with active dialogs.

### Key Entities

- **Tab**: Represents a selectable view option with a label, active/inactive state, and associated content type.
- **Panel Content**: The rendered view area below the tab bar, whose content varies based on the active tab selection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can switch between all 5 panel views with a single click, with the view changing within the same frame (no perceptible delay).
- **SC-002**: Card views display cards in exactly 2 columns that fit within the panel boundaries without horizontal overflow.
- **SC-003**: 100% of previously dialog-based views (quests, intrigue, completed quests, producer) are accessible via the tabbed panel.
- **SC-004**: The active tab is visually identifiable at a glance — a new user can determine which tab is selected without clicking.
- **SC-005**: The game log retains full functionality (scrolling, entry display) when viewed via its tab.
- **SC-006**: Players can switch tabs while a dialog is open, review information in another tab, and return to complete the dialog action without losing dialog state.

## Assumptions

- The right-side panel width remains unchanged; cards will be scaled down to fit two per row within the existing panel dimensions.
- The tab bar occupies a small fixed height at the top of the panel, reducing the content area height slightly compared to the current full-panel game log.
- The "Game Log" tab is the default view because it is the most frequently referenced information during active gameplay.
- Tab state is purely local to the client — switching tabs does not send any network messages or affect game state.
- The "Player Overview" button is not included in the tabs, as the user's description did not mention it. It remains as a separate button or is removed based on future decisions.
