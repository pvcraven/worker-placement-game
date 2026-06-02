# Feature Specification: Tier 1 Quest Card Expansion

**Feature Branch**: `039-tier1-quest-expansion`  
**Created**: 2026-06-02  
**Status**: Draft  
**Input**: User description: "Create music-themed implementations for unimplemented Tier 1 cards from the quest reference analysis, using the established genre/resource mapping."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expanded Quest Variety (Priority: P1)

As a player, I want a larger pool of quest cards available during the game so that each playthrough feels different and offers more strategic variety. The 15 new quest cards use only existing mechanics (simple cost-to-VP with optional bonus resources), expanding the card pool from 60 to 75 cards.

**Why this priority**: More cards directly improves replayability — the core value of this feature. Every new card is immediately usable with no new rules to learn.

**Independent Test**: Start a game and verify that the new quest cards appear in the quest market rotation. Complete one of the new quests and confirm VP and bonus resources are awarded correctly.

**Acceptance Scenarios**:

1. **Given** a new game starts, **When** quest cards are dealt to the market, **Then** the new expansion cards can appear alongside original cards
2. **Given** a player has resources matching a new quest's cost, **When** they complete the quest, **Then** they receive the correct VP and any bonus resources listed on the card
3. **Given** the expanded card pool of 75 cards, **When** multiple games are played, **Then** the quest market shows greater variety between sessions

---

### User Story 2 - Mega Quest Strategy (Priority: P1)

As a player, I want access to high-risk, high-reward "mega quests" (40 VP each) so that I can pursue a late-game power play by hoarding resources for a massive payoff. There is one mega quest per genre.

**Why this priority**: Mega quests add an entirely new strategic dimension — the tension between steady small quests vs. saving for a 40-point swing. This is the most impactful addition in terms of gameplay depth.

**Independent Test**: Acquire a mega quest, accumulate the very large resource cost, complete it, and verify 40 VP is awarded. Verify that the high cost makes this a meaningful strategic tradeoff.

**Acceptance Scenarios**:

1. **Given** a mega quest appears in the market, **When** a player examines it, **Then** they see a very high resource cost and 40 VP reward with no bonus resources
2. **Given** a player has accumulated enough resources, **When** they complete a mega quest, **Then** they receive exactly 40 VP
3. **Given** all five genres, **When** viewing the full card pool, **Then** each genre has exactly one mega quest available

---

### User Story 3 - Card Images for New Quests (Priority: P2)

As a player, I want the new quest cards to have properly generated card images consistent with existing cards so they blend seamlessly into the game's visual presentation.

**Why this priority**: Card images are needed for the cards to display correctly in the UI, but the game is still functional with placeholder/generated images.

**Independent Test**: Run the card image generator and verify that all 15 new cards produce valid card images that display correctly in the quest market and side panel.

**Acceptance Scenarios**:

1. **Given** the new quest cards are added to configuration, **When** the card image generator runs, **Then** it produces card images for all 15 new cards
2. **Given** generated card images exist, **When** a new quest appears in the game UI, **Then** the card displays with correct name, cost, VP, genre color, and bonus resource information

---

### Edge Cases

- What happens when the quest market already contains 5 cards and a new expansion card would be drawn? (Existing market draw logic should handle this — no change needed)
- Do the new cards affect game balance by diluting the plot quest pool? (No — all 15 new cards are non-plot quests, so the ratio of plot quests to total quests decreases slightly, making plot quests somewhat rarer and more valuable)
- Can a player realistically complete a mega quest? (The costs are very high but achievable in longer games — this is intentional design tension)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST include 15 new quest cards, distributed as: 4 Pop, 3 Rock, 3 Soul, 2 Funk, 3 Jazz
- **FR-002**: Each new quest card MUST have a unique music-industry-themed name and description appropriate to its genre
- **FR-003**: All new quest cards MUST use only the simple "pay resources, receive VP and optional bonus resources" mechanic — no new game mechanics
- **FR-004**: Five of the 15 cards MUST be "mega quests" worth 40 VP each (one per genre), with no bonus resources
- **FR-005**: The remaining 10 cards MUST have VP values and resource costs consistent with the established game balance (see New Card Definitions below)
- **FR-006**: All new quest cards MUST be non-plot quests (is_plot_quest = false, no ongoing benefits)
- **FR-007**: Card images MUST be generated for all 15 new cards using the existing card image generation pipeline
- **FR-008**: New cards MUST be shuffled into the quest deck alongside existing cards with no weighting or separation
- **FR-009**: The quest implementation analysis document (`specs/card_reference/quest_implementation_analysis.md`) MUST be updated to reflect the newly implemented cards and mark "Defend the Lanceboard Room" as TBD (deferred until "choose any resource" reward mechanic is implemented)

### New Card Definitions

#### Pop (Commerce) — 4 new cards

**Platinum Record Heist**
- Genre: Pop
- Description: "Orchestrate the acquisition of a rival's entire back catalog, netting a fortune in royalty payments."
- Cost: 4 bass players, 2 drummers
- VP: 7
- Bonus: 10 coins

**Street Team Recruitment**
- Genre: Pop
- Description: "Build a grassroots street team that spreads your pop brand across every corner of the city."
- Cost: 1 singer, 1 drummer
- VP: 8
- Bonus: none

**International Pop Tour**
- Genre: Pop
- Description: "Fund a lavish international tour that spreads your pop empire to new markets worldwide."
- Cost: 1 singer, 1 guitarist, 2 bass players, 5 coins
- VP: 16
- Bonus: none

**Global Pop Domination** *(Mega Quest)*
- Genre: Pop
- Description: "Execute a worldwide pop takeover — saturating every market with your artists and merchandise in an unprecedented campaign."
- Cost: 2 singers, 3 guitarists, 4 bass players, 10 coins
- VP: 40
- Bonus: none

---

#### Rock (Warfare) — 3 new cards

**Wake the Sleeping Legends**
- Genre: Rock
- Description: "Rally six legendary retired rock guitarists out of retirement for one more explosive comeback tour."
- Cost: 3 singers, 3 bass players
- VP: 8
- Bonus: 6 guitarists

**Demolish the Rival Arena**
- Genre: Rock
- Description: "Tear down a competitor's concert venue with a hostile buyout, claiming the territory and earning massive street cred."
- Cost: 1 singer, 2 guitarists, 2 coins
- VP: 10
- Bonus: none

**Rock Legends World Tour** *(Mega Quest)*
- Genre: Rock
- Description: "Launch the most ambitious world tour ever attempted, with a massive band lineup that conquers every stage on the planet."
- Cost: 2 singers, 7 guitarists, 2 drummers, 2 coins
- VP: 40
- Bonus: none

---

#### Soul (Piety) — 3 new cards

**Rescue the Gospel Choir**
- Genre: Soul
- Description: "Free a renowned gospel choir from an exploitative contract, gaining their devoted voices for your label."
- Cost: 6 guitarists, 2 drummers
- VP: 10
- Bonus: 3 singers

**Soul Heritage Foundation**
- Genre: Soul
- Description: "Establish a prestigious foundation dedicated to preserving soul music history, earning enormous prestige and respect."
- Cost: 2 singers, 1 drummer, 5 coins
- VP: 18
- Bonus: none

**Soul Music Magnum Opus** *(Mega Quest)*
- Genre: Soul
- Description: "Assemble the greatest soul musicians alive for a legendary recording that defines the genre for generations to come."
- Cost: 5 singers, 2 guitarists, 2 bass players, 1 drummer
- VP: 40
- Bonus: none

---

#### Funk (Arcana) — 2 new cards

**Resurrect the Funk Pioneers**
- Genre: Funk
- Description: "Revive the lost recordings of funk pioneers, recruiting a new generation of drummers inspired by the masters."
- Cost: 3 singers, 5 coins
- VP: 6
- Bonus: 3 drummers

**Funkadelic Magnum Opus** *(Mega Quest)*
- Genre: Funk
- Description: "Pour your entire roster into creating the definitive funk album — a once-in-a-generation masterpiece that will echo through history."
- Cost: 2 guitarists, 3 bass players, 4 drummers, 6 coins
- VP: 40
- Bonus: none

---

#### Jazz (Skullduggery) — 3 new cards

> **Deferred — Grand Jazz Caper** (original: "Defend the Lanceboard Room"): This card rewards 8 resources of the player's choice ("any" resource). It requires a "choose any resource" reward mechanic that does not yet exist. It will be implemented in a future feature alongside that mechanic. Tracked as TBD in the analysis document.

**Survive the Genre Crossover**
- Genre: Jazz
- Description: "Navigate a risky genre crossover experiment, emerging with a massive bass section from the fusion fallout."
- Cost: 6 guitarists, 5 coins
- VP: 6
- Bonus: 6 bass players

**Underground Jazz Blitz**
- Genre: Jazz
- Description: "Launch a coordinated series of underground jazz shows across the city, using every type of musician in your roster."
- Cost: 1 singer, 1 guitarist, 1 bass player, 1 drummer
- VP: 12
- Bonus: none

**Jazz Empire Conspiracy** *(Mega Quest)*
- Genre: Jazz
- Description: "Execute the ultimate power play — a sprawling underground jazz operation that seizes control of the entire scene."
- Cost: 1 singer, 7 bass players, 2 drummers, 9 coins
- VP: 40
- Bonus: none

---

### Key Entities

- **Quest Card**: A card with a name, description, genre, resource cost, victory point value, and optional bonus resources. All 15 new cards follow the same data structure as existing quest cards.
- **Mega Quest**: A subtype of quest card characterized by extremely high resource costs and a 40 VP reward with no bonus resources. One exists per genre.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The total quest card pool increases from 60 to 75 cards
- **SC-002**: All 15 new quest cards can be completed successfully in-game, awarding the correct VP and bonus resources
- **SC-003**: All 5 mega quests (one per genre) appear in the card pool and can be completed for 40 VP each
- **SC-004**: Card images are generated for all 15 new cards and display correctly in the game UI
- **SC-005**: Existing quest cards and game mechanics continue to function identically (no regressions)
- **SC-006**: All existing tests continue to pass after the new cards are added

## Assumptions

- The existing card image generation pipeline can produce images for the new cards without modification
- The quest deck shuffle and market draw logic already supports a larger card pool without changes
- No game balance adjustments are needed — card costs and VP values are derived from the original reference game's tested balance
- The original "Defend the Lanceboard Room" card (which rewards 8 resources of the player's choice) is deferred to a future feature because it requires a "choose any resource" reward mechanic not yet implemented
- All new cards are non-plot quests, so no ongoing benefit tracking or plot quest logic is required
- The quest implementation analysis document will be updated as part of this feature to track which cards have been implemented and which remain outstanding
