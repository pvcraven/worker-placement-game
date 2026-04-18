# Feature Specification: Card Image Generator

**Feature Branch**: `010-card-image-generator`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Create a top-level folder called card-generator. In that folder, create a script that reads all the card JSON items, and generates an image for each card using pillow. Put the cards in client/assets/card_images and do a subfolder for each type of card (intrigue, quest, etc.)"

## User Scenarios & Testing

### User Story 1 - Generate Quest Card Images (Priority: P1)

A developer runs the card generator script. The script reads all 66 quest contracts from `config/contracts.json`, renders each one as a PNG image matching the in-game visual style, and saves them to `client/assets/card_images/quests/`.

**Why this priority**: Quest cards are the most numerous card type (66 cards) and the most visually complex, with genre-colored header bands, cost, VP, bonus rewards, and description text.

**Independent Test**: Run the script and verify that 66 PNG files appear in `client/assets/card_images/quests/`, each showing the card's name, genre, cost, VP, bonuses, and description in a readable layout.

**Acceptance Scenarios**:

1. **Given** the script is run, **When** `config/contracts.json` contains 66 contracts, **Then** 66 PNG files are generated in `client/assets/card_images/quests/`
2. **Given** a quest card has genre "jazz", **When** the image is generated, **Then** the card displays a colored genre header band matching the in-game jazz color
3. **Given** a quest card has bonus rewards (e.g., "+1B", "Choose Free Building"), **When** the image is generated, **Then** the bonus line appears on the card

---

### User Story 2 - Generate Building Card Images (Priority: P2)

The script reads all 24 buildings from `config/buildings.json` and renders each one as a PNG showing name, coin cost, visitor reward, owner bonus, and description.

**Why this priority**: Building cards are the second most important card type and are always visible on the game board.

**Independent Test**: Run the script and verify 24 PNG files appear in `client/assets/card_images/buildings/`.

**Acceptance Scenarios**:

1. **Given** the script is run, **When** `config/buildings.json` contains 24 buildings, **Then** 24 PNG files are generated in `client/assets/card_images/buildings/`
2. **Given** a building costs 7 coins, **When** the image is generated, **Then** the card displays "Cost: 7 coins"

---

### User Story 3 - Generate Intrigue Card Images (Priority: P3)

The script reads all 50 intrigue cards from `config/intrigue.json` and renders each one as a PNG showing name, description, and effect summary.

**Why this priority**: Intrigue cards are used frequently but are only seen in hand panels and backstage dialogs.

**Independent Test**: Run the script and verify 50 PNG files appear in `client/assets/card_images/intrigue/`.

**Acceptance Scenarios**:

1. **Given** the script is run, **When** `config/intrigue.json` contains 50 intrigue cards, **Then** 50 PNG files are generated in `client/assets/card_images/intrigue/`
2. **Given** an intrigue card has effect type "steal_resources", **When** the image is generated, **Then** the card displays the effect summary

---

### User Story 4 - Generate Producer Card Images (Priority: P4)

The script reads all 11 producer cards from `config/producers.json` and renders each one as a PNG showing name, description, bonus genres, and VP-per-contract value.

**Why this priority**: Producer cards are secret end-game scoring cards, less frequently viewed.

**Independent Test**: Run the script and verify 11 PNG files appear in `client/assets/card_images/producers/`.

**Acceptance Scenarios**:

1. **Given** the script is run, **When** `config/producers.json` contains 11 producers, **Then** 11 PNG files are generated in `client/assets/card_images/producers/`

---

### Edge Cases

- What happens when a card name is very long (20+ characters)? It should be truncated with ".." to fit the card width.
- What happens when a card has no description? The description area should be left blank.
- What happens when a card has no bonus rewards? The bonus line should be omitted and the description should fill the space.
- What happens when the output directory does not exist? The script should create it automatically.

## Requirements

### Functional Requirements

- **FR-001**: The script MUST reside in a top-level `card-generator/` directory
- **FR-002**: The script MUST read card data from the existing JSON config files (`config/contracts.json`, `config/buildings.json`, `config/intrigue.json`, `config/producers.json`)
- **FR-003**: The script MUST generate one PNG image per card
- **FR-004**: The script MUST organize output images into subdirectories by card type: `client/assets/card_images/quests/`, `client/assets/card_images/buildings/`, `client/assets/card_images/intrigue/`, `client/assets/card_images/producers/`
- **FR-005**: The script MUST create output directories if they do not exist
- **FR-006**: Each generated card image MUST display all relevant card data (name, costs, rewards, description, etc.)
- **FR-007**: Quest card images MUST use a genre-colored header band matching the in-game colors (jazz=blue, pop=magenta, soul=purple, funk=amber, rock=crimson)
- **FR-008**: Card images MUST use a transparent PNG background with a parchment-colored rounded rectangle as the card shape, and dark text for readability
- **FR-009**: The script MUST name output files using the card's ID (e.g., `contract_001.png`, `building_004.png`)
- **FR-010**: The script MUST be runnable as a standalone command from the project root

### Key Entities

- **Quest Card (Contract)**: name, genre, cost (resources), victory_points, bonus_resources, reward_draw_intrigue, reward_draw_quests, reward_building, description, is_plot_quest, ongoing_benefit_description
- **Building Card**: name, description, cost_coins, visitor_reward, visitor_reward_special, owner_bonus, owner_bonus_special
- **Intrigue Card**: name, description, effect_type, effect_target, effect_value
- **Producer Card**: name, description, bonus_genres, bonus_vp_per_contract

## Success Criteria

### Measurable Outcomes

- **SC-001**: Running the script produces exactly 151 card images (66 quests + 24 buildings + 50 intrigue + 11 producers)
- **SC-002**: Every generated image is readable at 100% zoom — text is not clipped, overlapping, or illegible
- **SC-003**: The script completes generation of all cards in under 30 seconds
- **SC-004**: Each card type is visually distinguishable by its color scheme and layout

## Clarifications

### Session 2026-04-18

- Q: What background style should card images use? → A: Card images start with a transparent background, then draw the card as a parchment-colored rectangle with rounded corners. Dark text for readability.
- Q: What size should the generated card images be? → A: 190x230 pixels (1:1 with in-game size)
- Q: How should genre be indicated on quest cards with parchment background? → A: Keep colored genre band at top of card (over parchment)
- Q: Should card images display all JSON fields or only the Key Entities subset? → A: Display all JSON fields (specials, targets, plot quest markers, etc.)

## Assumptions

- The system running the script has Pillow installed (or it will be added as a project dependency)
- The existing JSON config files are the authoritative source for card data
- Card image dimensions will be 190x230 pixels (1:1 with in-game size)
- A standard system font (e.g., Arial, Tahoma) will be used; no custom font files are required
- The `client/assets/card_images/` directory and its contents will be added to `.gitignore` as generated artifacts
- Text on parchment background will be dark (brown/black) for readability
