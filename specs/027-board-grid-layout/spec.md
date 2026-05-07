# Feature Specification: Board Grid Layout

**Feature Branch**: `027-board-grid-layout`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a more tightly controlled positioning system using a grid-based layout for the game board."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Grid-Based Board Layout (Priority: P1)

The game board currently uses ad-hoc fractional positioning (e.g., 8% from left, 91% from top) for every element. This makes it difficult to align elements, prevent overlaps, and adjust spacing. The board should be divided into a logical grid of cells that all elements snap to, creating a clean, predictable layout.

The board area (between the top resource bar and bottom status bar, excluding the right side panel) is divided into a 7-column by 8-row grid. The right side panel occupies 2 additional columns, making the full playing field 9 columns wide and 8 rows tall. The top resource bar and bottom status bar remain unchanged.

The grid supports half-column and half-row positioning (e.g., column 3.5, row 1.5) so elements can be placed at any integer or half-integer grid coordinate.

Each board element type occupies a defined number of grid cells:
- **Permanent action spaces** (e.g., Merch Store, Motown, Guitar Center): 1 cell wide, 1 cell tall
- **Purchased/constructed buildings**: 1 cell wide, 1.5 cells tall (allowing 6 buildings per column)
- **Quest cards**: 1 cell wide, 3 cells tall
- **Building market cards**: 1 cell wide, 1.5 cells tall
- **Backstage slots**: 1 cell wide, 1 cell tall

Each grid cell has a percentage-based margin (e.g., 2% of cell width) providing visual separation between adjacent cards. All card types scale by the same uniform factor as the window changes size — no card type scales independently. All card image PNGs are generated with the same base width; card types differ only in height (1-row, 2-row, or 3-row). Cards are centered within their grid cell(s), fitting inside the margin boundary while maintaining aspect ratio.

**Why this priority**: This is the core layout engine. All other stories depend on elements being placed on the grid.

**Independent Test**: Resize the game window. All board elements should remain aligned to their grid cells without overlapping, with consistent spacing between elements.

**Acceptance Scenarios**:

1. **Given** a game in progress with all element types visible, **When** the player views the board, **Then** all elements are aligned to grid cells with uniform spacing and no overlaps.
2. **Given** the game window is resized, **When** the board redraws, **Then** grid cells and all contained elements scale proportionally while maintaining alignment.
3. **Given** the board has the top resource bar and bottom status bar, **When** the grid is calculated, **Then** the grid occupies only the space between the bars (excluding the side panel area).

---

### User Story 2 - Element Placement on Grid (Priority: P2)

Each board element type is assigned to specific grid positions so the layout is deterministic and visually organized. A shared positioning utility converts grid coordinates (column, row, column span, row span) to pixel positions, ensuring all elements use common code for placement.

**Detailed Grid Placement Map:**

| Element | Column(s) | Row(s) | Size (cols × rows) | Notes |
|---------|-----------|--------|---------------------|-------|
| Merch Store | 0 | 0 | 1 × 1 | Permanent action space |
| Motown | 0 | 1 | 1 × 1 | Permanent action space |
| Guitar Center | 0 | 2 | 1 × 1 | Permanent action space |
| Talent Show | 0 | 3 | 1 × 1 | Permanent action space |
| Rhythm Pit | 0 | 4 | 1 × 1 | Permanent action space |
| Jam Session | 0 | 5 | 1 × 1 | Permanent action space |
| Whisper Room | 0 | 6 | 1 × 1 | Permanent action space |
| FastPass | 0 | 7 | 1 × 1 | Permanent action space |
| Purchased buildings (col 1) | 1 | 0, 1.5, 3, 4.5, 6, 7.5* | 1 × 1.5 | Up to 6 buildings |
| Purchased buildings (col 2) | 2 | 0, 1.5, 3, 4.5, 6, 7.5* | 1 × 1.5 | Up to 6 buildings |
| Backstage slot 1 | 3 | 0 | 1 × 1 | |
| Backstage slot 2 | 3 | 1 | 1 × 1 | |
| Backstage slot 3 | 3 | 2 | 1 × 1 | |
| Realtor | 3 | 4 | 1 × 1 | |
| Sunset Records | 3.5 | 0 | 1 × 1 | Top-row action space (half-col) |
| The Back Room | 4.5 | 0 | 1 × 1 | Top-row action space (half-col) |
| The Garage | 5.5 | 0 | 1 × 1 | Top-row action space (half-col) |
| Face-up quest 1 | 4 | 2 | 1 × 3 | |
| Face-up quest 2 | 5 | 2 | 1 × 3 | |
| Face-up quest 3 | 4 | 5 | 1 × 3 | |
| Face-up quest 4 | 5 | 5 | 1 × 3 | |
| Building market 1 | 4 | 5.5 | 1 × 1.5 | |
| Building market 2 | 5 | 5.5 | 1 × 1.5 | |
| Building market 3 | 6 | 5.5 | 1 × 1.5 | |

*Building row 7.5 extends 0.5 rows below the nominal 8-row grid; this is acceptable since bottom rows have available space.

**Why this priority**: Once the grid exists, elements need defined home positions. This determines the visual identity of the board.

**Independent Test**: Start a game with multiple players. Verify that permanent spaces, quests, buildings, and backstage slots all appear in their expected grid regions without manual position tweaking.

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** the board renders, **Then** all 8 permanent action spaces appear in column 0, one per row, from top to bottom.
2. **Given** a player purchases a building, **When** it appears on the board, **Then** it snaps to the next available slot in the constructed buildings area (columns 1-2), spanning 1.5 rows.
3. **Given** 4 face-up quest cards are displayed, **When** the board renders, **Then** each quest occupies 1 column width and 3 rows of height, arranged without overlap.
4. **Given** elements placed at half-column positions (e.g., Sunset Records at column 3.5), **When** the board renders, **Then** the element is centered between columns 3 and 4.

---

### User Story 3 - Side Panel Grid Integration (Priority: P3)

The right side panel (game log, quest hand, intrigue hand, completed quests tabs) occupies the rightmost 2 columns of the 9-column layout. The panel's width is derived from the grid cell size rather than a hardcoded pixel value, ensuring it scales consistently with the board.

**Why this priority**: The side panel must integrate with the grid so the overall layout is cohesive. This is lower priority because the panel already works and just needs its width tied to the grid.

**Independent Test**: Resize the window. The side panel width should change proportionally with the board grid, maintaining a 2:7 ratio with the board area.

**Acceptance Scenarios**:

1. **Given** the game window renders, **When** the layout is calculated, **Then** the side panel width equals exactly 2 grid columns.
2. **Given** the window is resized, **When** the layout recalculates, **Then** the side panel and board grid resize proportionally together.

---

### Edge Cases

- What happens when the window is very narrow (fewer than 600px wide)? Grid cells should have a minimum size to remain readable, and elements should not shrink below a legible threshold.
- What happens when many buildings are constructed (12+ buildings)? With 1.5-row buildings, each column holds 6 buildings (12 total across 2 columns). If more are needed, overflow handling should be defined.
- What happens with different player counts (2-5 players)? The grid layout remains the same regardless of player count; only the number of occupied spaces changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The board area MUST be divided into a 7-column by 8-row grid between the top resource bar and bottom status bar.
- **FR-002**: The right side panel MUST occupy 2 additional columns, making the full layout 9 columns wide by 8 rows tall.
- **FR-003**: The top resource bar and bottom status bar MUST remain unchanged in position and behavior.
- **FR-004**: Permanent action spaces MUST each occupy exactly 1 grid cell (1 column, 1 row).
- **FR-005**: Constructed/purchased building cards MUST each occupy 1 column and 1.5 rows of grid space, allowing 6 buildings per column.
- **FR-006**: Quest cards MUST each occupy 1 column and 3 rows of grid space.
- **FR-007**: All board elements MUST scale to fit their assigned grid cell(s), maintaining aspect ratio.
- **FR-008**: Grid cell sizes MUST recalculate dynamically when the window is resized.
- **FR-009**: Elements MUST NOT overlap adjacent grid cells or other elements.
- **FR-010**: Building market cards MUST each occupy 1 column and 1.5 rows of grid space.
- **FR-011**: Backstage slots MUST each occupy 1 grid cell (1 column, 1 row).
- **FR-012**: Card images MUST be centered within their grid cell(s) with uniform padding.
- **FR-013**: Each grid cell MUST have a percentage-based margin (e.g., 2% of cell width) separating it from adjacent cells. Card content renders inside the margin boundary.
- **FR-014**: All card types MUST scale by the same uniform factor as the window is resized. No card type scales independently.
- **FR-015**: All card image PNGs MUST be generated with the same base width. Card types that differ in height (spaces, buildings, quests) vary only in height, not width.
- **FR-016**: The grid MUST support half-column and half-row positioning (e.g., column 3.5, row 1.5) so elements can be placed at any integer or half-integer coordinate.
- **FR-017**: All board elements MUST be positioned through a shared positioning utility that converts grid coordinates (column, row, span) to pixel positions. No element may use ad-hoc fractional positioning.

### Key Entities

- **Grid Cell**: A single unit of the layout grid, defined by column index (0-8) and row index (0-7). Supports half-integer indices (e.g., 3.5, 1.5). Has a computed pixel position and size based on the board area dimensions.
- **Grid Span**: The number of columns and rows an element occupies. Supports half-integer spans (e.g., a building spans 1 column and 1.5 rows).
- **Board Area**: The rectangular region between the top bar and bottom bar, excluding the side panel. Contains the 7x8 grid.
- **Side Panel Area**: The rightmost 2 columns of the 9-column layout, used for the tabbed panel (game log, card hands).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All board elements align to grid cells with zero visual overlap at any supported window size.
- **SC-002**: The board renders correctly at window widths from 800px to 2560px without element clipping or misalignment.
- **SC-003**: Resizing the window results in all elements repositioning within 1 frame (no visible jitter or lag).
- **SC-004**: The layout is visually consistent across 2-player, 3-player, 4-player, and 5-player games.
- **SC-005**: Existing game functionality (clicking spaces, placing workers, purchasing buildings) continues to work correctly with the new grid positions.

## Clarifications

### Session 2026-05-06

- Q: What type of margin between grid cells? → A: Percentage-based margin (e.g., 2% of cell width)
- Q: Should different card types scale independently? → A: No, all cards scale by the same uniform factor as the window resizes
- Q: Should card image PNGs have different widths per type? → A: No, all card types are generated with the same base width; they differ only in height
- Q: Should the grid support fractional positioning? → A: Yes, half-column and half-row positions (e.g., 3.5, 1.5) are supported
- Q: How tall should purchased buildings be? → A: 1.5 rows (changed from 2), allowing 6 buildings per column
- Q: Should positioning use common code? → A: Yes, all elements use a shared positioning utility — no ad-hoc fractional positioning
- Q: Where should top-row action spaces go? → A: Sunset Records at col 3.5, The Back Room at col 4.5, The Garage at col 5.5 (all row 0)
- Q: Detailed element placement? → A: See placement map table in User Story 2

## Assumptions

- The top resource bar height (`100 * scale`) and bottom status bar height (`50 * scale`) remain unchanged.
- The number of permanent action spaces (8 left column + 3 top row = 11 total) is fixed and does not change.
- Face-up quest count (4) and face-up building count (3) remain as currently configured.
- Backstage slot count (3) remains fixed.
- The side panel continues to serve the same role (game log, card tabs) and its internal layout is unchanged.
- Card aspect ratios are preserved when scaling to fit grid cells.
- The current separate width constants (CARD_WIDTH, SPACE_CARD_HEIGHT, BUILDING_CARD_HEIGHT) will be consolidated so all card types share a single base width.
- The grid approach replaces the current fractional positioning system entirely for the board area.
- A shared grid positioning utility will be used by all board elements — no element bypasses the grid system.
- With 1.5-row buildings, each column holds up to 6 buildings (rows 0, 1.5, 3, 4.5, 6, 7.5), for a maximum of 12 buildings across 2 columns.
