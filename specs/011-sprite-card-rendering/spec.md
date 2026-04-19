# Feature Specification: Sprite Card Rendering

**Feature Branch**: `011-sprite-card-rendering`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Replace all card rendering from rects/text draws to sprite-based rendering using pre-generated card images, drawn via arcade.SpriteList for batch performance."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Board Quest Cards as Sprites (Priority: P1)

The face-up quest cards displayed on the main game board currently render via `CardRenderer.draw_contract()` using rect fills, outlines, and cached `arcade.Text` objects. Replace this rendering with sprites loaded from the pre-generated PNG images in `client/assets/card_images/quests/`. The sprites should be managed in an `arcade.SpriteList` and drawn as a batch.

**Why this priority**: Quest cards on the board are the most prominent and frequently drawn cards. Converting these first provides the highest visual impact and validates the sprite approach.

**Independent Test**: Launch the game, observe the main board. Face-up quest cards should display as the pre-generated PNG images (parchment background, genre-colored band, readable text) instead of the old rect-and-text rendering. Cards should still be clickable for quest completion.

**Acceptance Scenarios**:

1. **Given** a game in progress with face-up quest cards, **When** the board renders, **Then** each quest card appears as its corresponding PNG sprite from `client/assets/card_images/quests/{card_id}.png`
2. **Given** a highlighted quest card, **When** the board renders, **Then** the highlighted card has a visible highlight indicator (e.g., colored outline drawn over the sprite)
3. **Given** a quest card on the board, **When** the player clicks on it, **Then** click detection still works correctly using the sprite's bounding box

---

### User Story 2 - Board Building Cards as Sprites (Priority: P2)

The face-up building cards on the main board currently render via `CardRenderer.draw_building()`. Replace with sprites from `client/assets/card_images/buildings/`.

**Why this priority**: Building cards are the second most visible card type on the board. Independent from quest cards — different SpriteList or same list, different source images.

**Independent Test**: Launch the game, observe building cards on the board. They should display as pre-generated PNG images instead of rect-and-text rendering.

**Acceptance Scenarios**:

1. **Given** a game with face-up building cards, **When** the board renders, **Then** each building card appears as its corresponding PNG sprite from `client/assets/card_images/buildings/{card_id}.png`
2. **Given** a highlighted building card, **When** the board renders, **Then** the highlight indicator is visible
3. **Given** a building card, **When** the player clicks on it, **Then** click detection works correctly

---

### User Story 3 - Hand Panel Cards as Sprites (Priority: P3)

The hand panel overlay (toggled to show quest or intrigue cards) currently renders cards via `CardRenderer.draw_contract()` or `CardRenderer.draw_intrigue()`. Replace with sprites from the corresponding card image directories.

**Why this priority**: The hand panel shows up to 6 cards at a time. Converting it completes the main gameplay card rendering. It covers both quest and intrigue card types in one story.

**Independent Test**: Open the quest hand panel and the intrigue hand panel. Cards should display as PNG sprites instead of rect-and-text rendering.

**Acceptance Scenarios**:

1. **Given** a player with quest cards in hand, **When** they open the quest hand panel, **Then** each card renders as a sprite from `client/assets/card_images/quests/{card_id}.png`
2. **Given** a player with intrigue cards in hand, **When** they open the intrigue hand panel, **Then** each card renders as a sprite from `client/assets/card_images/intrigue/{card_id}.png`

---

### User Story 4 - Quest Completion Dialog Cards as Sprites (Priority: P4)

The `QuestCompletionDialog` currently renders quest cards via `CardRenderer.draw_contract()`. Replace with sprites.

**Why this priority**: This dialog only appears at specific moments (end of turn when quests can be completed). Lower frequency than board and hand rendering, but still part of the complete conversion.

**Independent Test**: Trigger the quest completion dialog. Cards displayed should be PNG sprites.

**Acceptance Scenarios**:

1. **Given** a quest completion event, **When** the dialog displays available quests, **Then** each quest card renders as a sprite from `client/assets/card_images/quests/{card_id}.png`

---

### Edge Cases

- What happens when a card image PNG does not exist for a given card ID? The system should fall back gracefully (e.g., display a placeholder or log a warning).
- What happens when the card images directory is empty or missing? The system should trigger regeneration via the existing `ensure_card_images()` mechanism before attempting to load sprites.
- What happens when the set of face-up cards changes (new card drawn, card removed)? The SpriteList must be updated to reflect the current card set.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load card PNG images as `arcade.Sprite` objects from `client/assets/card_images/{type}/{card_id}.png`
- **FR-002**: System MUST use `arcade.SpriteList` for batch rendering of card sprites — individual sprite `.draw()` calls are not permitted for card rendering
- **FR-003**: System MUST replace all 5 existing `CardRenderer.draw_contract()`, `CardRenderer.draw_building()`, and `CardRenderer.draw_intrigue()` call sites with sprite-based rendering
- **FR-004**: System MUST position card sprites at the same screen locations currently used by the rect-and-text rendering
- **FR-005**: System MUST support highlight indicators on selected/highlighted cards (e.g., drawing an outline rect over the sprite)
- **FR-006**: System MUST maintain click/hit detection for card sprites using the sprite's bounding box
- **FR-007**: System MUST update sprite lists when the set of displayed cards changes (face-up cards change, hand contents change, dialog opens with different cards)
- **FR-008**: System MUST handle missing card image files gracefully without crashing

### Key Entities

- **Card Sprite**: An `arcade.Sprite` loaded from a pre-generated card PNG, positioned at a specific board/panel/dialog location
- **Card SpriteList**: An `arcade.SpriteList` containing card sprites for batch rendering — organized per rendering context (board, hand panel, dialog) or per card type

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All card rendering on the main board uses sprite images instead of rect-and-text drawing
- **SC-002**: All card rendering in dialogs and overlays uses sprite images instead of rect-and-text drawing
- **SC-003**: Cards render using SpriteList batch drawing, not individual draw calls
- **SC-004**: Card click/selection behavior works identically to the previous implementation
- **SC-005**: No visual regression — cards display readable text, correct colors, and proper positioning
- **SC-006**: Game startup and card rendering perform at least as well as the previous implementation

## Assumptions

- Card PNG images already exist in `client/assets/card_images/` and are generated by `card-generator/generate_cards.py` with the `ensure_card_images()` startup check
- Card images are 190x230 pixels (1:1 with the current `_CARD_WIDTH` and `_CARD_HEIGHT` constants in `CardRenderer`)
- The existing `CardRenderer` class can be simplified or removed after all call sites are converted
- Arcade's `SpriteList` supports dynamic add/remove of sprites as the displayed card set changes during gameplay
