# Feature Specification: Quest Reward Expansion

**Feature Branch**: `008-quest-reward-expansion`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "We want quests to have 'costs' and 'rewards'. Right now the 'reward' section is just victory points. A quest can also give resources. Such as, it might take 3 guitarists and a singer, and then the reward would be a guitarist, a singer, and 4 victory points. Or a quest might give you victory points and an intrigue card. Or you might be able to draw another quest card. (randomly, or choose one.) The code should be set up, as intrigue cards should be able to do something similar with rewards giving quest/intrigue cards as well. Another possibility of a reward for a quest would be a building. This would be rare. So we need to support this functionality, and create some quests that utilize it."

## User Scenarios & Testing

### User Story 1 - Quest Rewards Give Resources and Cards (Priority: P1)

A player completes a quest and receives not just victory points but also additional rewards — resources (guitarists, bass players, drummers, singers, coins), drawn intrigue cards, drawn quest cards, or any combination. The reward is applied immediately upon quest completion.

**Why this priority**: This is the core feature. Quests currently only grant victory points and a static `bonus_resources` field. Expanding rewards to include card draws makes quests more strategic and varied, directly increasing gameplay depth.

**Independent Test**: Complete a quest that rewards 4 VP + 1 guitarist + 1 drawn intrigue card. Verify the player receives the VP, the guitarist appears in their resource bar, and the intrigue card appears in their hand.

**Acceptance Scenarios**:

1. **Given** a player has the resources to complete a quest that rewards VP + resources, **When** they complete the quest, **Then** the resources are deducted, VP is awarded, and bonus resources are added to their totals immediately.
2. **Given** a player completes a quest that rewards "draw 1 intrigue card", **When** the quest is completed, **Then** 1 intrigue card is drawn from the intrigue deck and added to the player's hand.
3. **Given** a player completes a quest that rewards "draw 1 quest card (random)", **When** the quest is completed, **Then** 1 quest card is drawn from the top of the quest deck and added to the player's hand.
6. **Given** a player completes a quest that rewards "choose 1 quest card", **When** the quest is completed, **Then** the player is shown the face-up quests and may select one to add to their hand. The face-up quest slot refills as normal.
4. **Given** a player completes a quest that rewards a combination (e.g., 4 VP + 1 singer + draw 1 intrigue card), **When** the quest is completed, **Then** all reward components are applied together.
5. **Given** the intrigue deck is empty when a quest rewards "draw intrigue card", **When** the quest is completed, **Then** the card draw portion is skipped and all other rewards are still granted. The game log notes that the deck was empty.

---

### User Story 2 - Quest Rewards Include a Building (Priority: P2)

Rarely, a quest reward includes a free building. The quest card specifies **which acquisition mode** to use:

- **Market choice**: "Put 1 building from Builder's Hall into play under your control at no cost." The player selects from the face-up buildings currently available in the market.
- **Random draw**: "Draw 1 building from the stack and put into play under your control at no cost." A building is drawn from the top of the building deck and automatically assigned to the player.

**Why this priority**: This is a rare but exciting reward type that adds variety. It depends on the same reward framework as US1 but involves the building market, making it a natural extension.

**Independent Test**: Complete a quest that rewards a free building (market choice mode). Verify the player is prompted to choose a building from the available market, and the chosen building is assigned to them at no coin cost. Then test a random-draw building quest and verify a building is drawn from the deck and assigned automatically.

**Acceptance Scenarios**:

1. **Given** a player completes a quest with a "market choice" building reward, **When** the quest is completed, **Then** the player is shown the available face-up buildings in Builder's Hall and may choose one to acquire for free.
2. **Given** a player completes a quest with a "random draw" building reward, **When** the quest is completed, **Then** 1 building is drawn from the top of the building deck and assigned to the player automatically. The game log shows which building was received.
3. **Given** a player completes a quest with a building reward but the relevant source is empty (no face-up buildings for market choice, or empty building deck for random draw), **When** the quest is completed, **Then** the building reward is skipped and all other rewards are granted. The game log notes that no buildings were available.
4. **Given** a player selects a building from the market as a reward, **When** the building is acquired, **Then** it is removed from the market, assigned to the player, and the market refills from the building deck as normal.

---

### User Story 3 - Intrigue Cards Can Reward Quest and Intrigue Cards (Priority: P3)

Intrigue card effects can grant quest card draws and intrigue card draws as part of their resolution. The existing draw_intrigue and draw_contracts effect types already exist but this story ensures the reward framework is unified so both quests and intrigue cards use the same mechanism for granting card draws.

**Why this priority**: The intrigue card draw system already partially works (draw_intrigue and draw_contracts effect types exist). This story ensures consistency with the quest reward system and adds any missing combinations.

**Independent Test**: Play an intrigue card that grants "draw 2 quest cards". Verify 2 quest cards are drawn and added to the player's hand.

**Acceptance Scenarios**:

1. **Given** a player plays an intrigue card with effect "draw 1 quest card and draw 1 intrigue card", **When** the effect resolves, **Then** the player receives 1 quest card and 1 intrigue card in their respective hands.
2. **Given** a player plays an intrigue card with a combined effect (resources + card draws), **When** the effect resolves, **Then** all components are applied together.

---

### User Story 4 - New Quest Content Utilizing Expanded Rewards (Priority: P4)

Create new quest cards in the game configuration that utilize the expanded reward types — quests that reward card draws, resource bonuses, and (rarely) buildings, in addition to victory points.

**Why this priority**: Content creation depends on the reward framework being implemented first. These quests showcase the new functionality and add gameplay variety.

**Independent Test**: Start a new game and verify the new quest cards appear in the deck with correct reward descriptions. Complete one and verify the expanded rewards are granted.

**Acceptance Scenarios**:

1. **Given** the game starts, **When** quest cards are dealt, **Then** the new quests with expanded rewards are part of the deck and display their full reward descriptions.
2. **Given** a quest card shows "Reward: 3 VP, draw 1 intrigue card", **When** viewing the quest details, **Then** all reward components are clearly listed.

---

### Edge Cases

- What happens when a quest rewards "draw 2 intrigue cards" but only 1 remains in the deck? The player draws the 1 available card; the second draw is skipped.
- What happens when a quest rewards a building but the player already owns the maximum number of buildings (if a limit exists)? Assume no building ownership limit; the player simply receives another building.
- What happens when a quest rewards "draw 1 quest card" but the quest deck and discard pile are both empty? The draw is skipped and the game log notes it.
- What happens when multiple reward types fail (empty decks, no buildings)? Each reward component is resolved independently; failures in one do not affect others.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST support quest rewards that include any combination of: victory points, resources (guitarists, bass players, drummers, singers, coins), intrigue card draws, quest card draws, and free buildings.
- **FR-002**: The system MUST apply all reward components upon quest completion, deducting costs first and then granting all rewards.
- **FR-003**: When a quest rewards quest card draws, the system MUST use the acquisition mode specified on the card: "random draw" draws from the quest deck; "choose" lets the player select from the face-up quests. Intrigue card draws are always random from the intrigue deck.
- **FR-004**: When a quest rewards a free building, the system MUST use the acquisition mode specified on the card: "market choice" presents the player with face-up buildings to choose from; "random draw" automatically draws from the building deck.
- **FR-005**: The system MUST gracefully handle empty decks or empty building markets by skipping that reward component and notifying the player via the game log.
- **FR-006**: Quest cards MUST display all reward components clearly — not just victory points.
- **FR-007**: The intrigue card effect system MUST support the same card-draw reward mechanisms as quests, ensuring a unified approach.
- **FR-008**: The game configuration MUST include new quest cards that utilize the expanded reward types, covering at least: VP + resources, VP + intrigue card draw, VP + quest card draw, and VP + free building.
- **FR-009**: The system MUST update the player's resource display and hand counts immediately when rewards are granted.

### Key Entities

- **Quest Reward**: A structured reward associated with a quest card. Contains victory points, bonus resources, number of intrigue cards to draw, number of quest cards to draw (with acquisition mode: random draw or choose from face-up), and an optional building grant (with acquisition mode: market choice or random draw).
- **Quest Card**: Extended to carry a full reward definition beyond just victory points and bonus resources.
- **Intrigue Card**: Already supports multiple effect types; may be extended to support combined effects using the same reward structure.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can complete quests and receive all expanded reward types (resources, cards, buildings) within the same turn, with no additional clicks beyond the existing quest completion flow (except building selection when applicable).
- **SC-002**: 100% of reward components are applied correctly — no reward is silently dropped unless the source deck/market is empty.
- **SC-003**: At least 6 new quest cards utilizing expanded rewards are included in the game configuration.
- **SC-004**: The game log accurately describes all rewards received upon quest completion, showing each component.
- **SC-005**: Players can identify what rewards a quest offers before choosing to complete it, by viewing the quest card details.

## Clarifications

### Session 2026-04-18

- Q: How does a building reward work — does the player always choose from the market? → A: Each quest card specifies the acquisition mode: either "market choice" (pick from face-up buildings in Builder's Hall) or "random draw" (draw from the building deck). Both modes grant the building at no coin cost.
- Q: Are quest card draw rewards always random, or can the player choose? → A: Each quest card specifies its mode: either "random draw" from the quest deck, or "choose" from face-up quests. The player follows what the card says.

## Assumptions

- The existing `bonus_resources` field on quest cards already supports granting resources; this feature extends the reward model to also include card draws and building grants.
- Quest card draw rewards use the acquisition mode specified on the quest card: "random draw" pulls from the quest deck; "choose" lets the player pick from face-up quests. Intrigue card draws are always random from the intrigue deck.
- Free building rewards use the acquisition mode specified on the quest card: "market choice" lets the player pick from face-up buildings in Builder's Hall; "random draw" pulls from the building deck automatically.
- There is no limit on how many buildings a player can own.
- Intrigue card effects that draw cards already work (draw_intrigue, draw_contracts); this feature ensures the same patterns are available as quest rewards.
- The reward framework should be general enough to add new reward types in the future without major restructuring.
