# Feature Specification: Intrigue Card Update

**Feature Branch**: `026-intrigue-card-update`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Add 14 new intrigue cards across 5 categories: 4 do-nothing cards, 4 draw-1-intrigue cards, 2 reset-quests cards, 2 reset-buildings cards, and 2 first-player-marker cards."

## Clarifications

### Session 2026-05-06

- Q: When quest or building decks are depleted, what should happen? → A: Reshuffle the discard pile back into the deck and draw from that. For quests, exclude any quests completed by any player from the reshuffle. This applies globally to all quest/building draws (not just reset cards).
- Q: Does the reshuffle mechanic apply only to reset card effects, or any time quests/buildings need to be drawn? → A: Globally — any time a draw is needed and the deck is empty (end-of-round refill, reset cards, etc.). This may already be implemented; verify and fix if not.

## User Scenarios & Testing

### User Story 1 - Play "Do Nothing" Intrigue Cards (Priority: P1)

A player plays one of four humorous intrigue cards that have no game effect. The card is consumed from the player's hand, the game log shows it was played, but no resources, cards, or state changes occur. These cards add humor and variety to the intrigue deck while diluting the average power level.

**Why this priority**: Simplest to implement — requires only a new effect type that does nothing, establishing the pattern for future no-op cards.

**Independent Test**: Play a do-nothing intrigue card from hand. Verify it is removed from the intrigue hand, the game log shows the card name, and no resources or state changes occur.

**Acceptance Scenarios**:

1. **Given** a player has a do-nothing intrigue card in hand, **When** they play it, **Then** the card is removed from their hand and the game log shows "[Player] played [Card Name]" with no additional effects.
2. **Given** a player plays a do-nothing card, **When** the action resolves, **Then** no resources, coins, VP, or other game state changes occur for any player.
3. **Given** a player has only do-nothing intrigue cards, **When** they view their intrigue hand, **Then** the cards are displayed normally with their humorous descriptions.

---

### User Story 2 - Play "Draw 1 Intrigue" Cards (Priority: P2)

A player plays one of four intrigue cards whose only effect is to draw one intrigue card from the deck. This is a simple exchange — spend one card to get a different one — adding deck cycling and mild strategic value.

**Why this priority**: The `draw_intrigue` effect type already exists in the game engine for buildings, but needs to work as an intrigue card effect. This reuses proven infrastructure.

**Independent Test**: Play a draw-1-intrigue card. Verify the played card is removed from hand, one new intrigue card is drawn from the deck, and the game log reflects the action.

**Acceptance Scenarios**:

1. **Given** a player has a draw-1-intrigue card in hand and the intrigue deck is not empty, **When** they play it, **Then** the played card is removed and one new intrigue card is added to their hand.
2. **Given** a player plays a draw-1-intrigue card, **When** the intrigue deck is empty, **Then** the played card is removed but no new card is drawn (no error).
3. **Given** a player plays a draw-1-intrigue card, **When** the action resolves, **Then** the game log shows "[Player] played [Card Name] (+1 intrigue card)".

---

### User Story 3 - Play "Reset Quests" Cards (Priority: P3)

A player plays one of two intrigue cards that resets the face-up quest display. All currently visible face-up quests are discarded and replaced with new quests drawn from the quest deck. This allows players to refresh a stale quest board when no available quests match their strategy.

**Why this priority**: Introduces a new effect type that modifies shared board state (the quest display), which is more complex than personal resource changes but uses existing quest deck mechanics.

**Independent Test**: Play a reset-quests card. Verify all face-up quests are replaced with new ones from the quest deck and the game log reflects the action.

**Acceptance Scenarios**:

1. **Given** a player has a reset-quests intrigue card, **When** they play it, **Then** all face-up quests are discarded and new quests are drawn from the quest deck to fill the display.
2. **Given** the quest deck is empty, **When** a player plays the reset card, **Then** the discard pile (excluding quests completed by any player) is shuffled to form a new quest deck and quests are drawn from it.
3. **Given** both the quest deck and discard pile are empty (all quests are either face-up or completed), **When** a player plays the reset card, **Then** the face-up quests are discarded, reshuffled into a new deck, and new quests are drawn from it.
4. **Given** a player plays a reset-quests card, **When** the action resolves, **Then** all players see the updated quest display and the game log shows "[Player] played [Card Name] — quests refreshed".

---

### User Story 4 - Play "Reset Buildings" Cards (Priority: P4)

A player plays one of two intrigue cards that resets the face-up purchasable buildings display. All currently visible buildings are discarded and replaced with new buildings drawn from the building deck. This lets players refresh the building market when no available buildings suit their strategy.

**Why this priority**: Mirrors the reset-quests mechanic but targets the building display. Slightly lower priority since buildings are purchased less frequently than quests are taken.

**Independent Test**: Play a reset-buildings card. Verify all face-up buildings are replaced with new ones from the building deck and the game log reflects the action.

**Acceptance Scenarios**:

1. **Given** a player has a reset-buildings intrigue card, **When** they play it, **Then** all face-up purchasable buildings are discarded and new buildings are drawn from the building deck to fill the display.
2. **Given** the building deck is empty, **When** a player plays the reset card, **Then** the discard pile is shuffled to form a new building deck and buildings are drawn from it.
3. **Given** both the building deck and discard pile are empty (all buildings are either face-up or purchased), **When** a player plays the reset card, **Then** the face-up buildings are discarded, reshuffled into a new deck, and new buildings are drawn from it.
4. **Given** a player plays a reset-buildings card, **When** the action resolves, **Then** all players see the updated building display and the game log shows "[Player] played [Card Name] — buildings refreshed".

---

### User Story 5 - Play "First Player Marker" Cards (Priority: P5)

A player plays one of two intrigue cards that grants them the first-player marker for the next round. This works like the Fastpass permanent space but without the bonus intrigue card draw — the player simply moves to first in turn order for the upcoming round.

**Why this priority**: Reuses existing first-player-marker logic from the Fastpass space but as a card effect. Lower priority since it's the most strategically niche of the five card types.

**Independent Test**: Play a first-player-marker card. Verify the player is set to go first in the next round and the game log reflects the action.

**Acceptance Scenarios**:

1. **Given** a player has a first-player-marker intrigue card, **When** they play it, **Then** the player is designated as first player for the next round.
2. **Given** a player plays the first-player card, **When** the next round begins, **Then** that player takes the first turn.
3. **Given** two players both play first-player cards in the same round, **When** the next round begins, **Then** the last player to have played the card goes first (last-in-wins, consistent with Fastpass behavior).
4. **Given** a player plays a first-player card, **When** the action resolves, **Then** the game log shows "[Player] played [Card Name] — will go first next round".

---

### Edge Cases

- What happens when a player plays a reset-quests card but the quest deck is empty? The discard pile (excluding completed quests) is reshuffled into a new deck and quests are drawn from it. If no discardable quests exist, the face-up quests are discarded, reshuffled, and redrawn.
- What happens when a player plays a reset-buildings card but the building deck is empty? The discard pile is reshuffled into a new building deck and buildings are drawn from it. If no discardable buildings exist, the face-up buildings are discarded, reshuffled, and redrawn.
- What happens when a player plays a draw-1-intrigue card but the intrigue deck is empty? The played card is still consumed but no new card is drawn.
- What happens when two players both play first-player cards in the same round? The last one played takes effect (last-in-wins).
- What happens when a player plays a first-player card and also visits Fastpass? The last action taken determines first player.

## Requirements

### Functional Requirements

- **FR-001**: System MUST add four new intrigue cards with a "no effect" type that can be played but produce no game state changes.
- **FR-002**: System MUST add four new intrigue cards with an effect that draws one intrigue card from the deck when played.
- **FR-003**: System MUST add two new intrigue cards with an effect that discards all face-up quests and draws new quests from the quest deck to refill the display.
- **FR-004**: System MUST add two new intrigue cards with an effect that discards all face-up purchasable buildings and draws new buildings from the building deck to refill the display.
- **FR-005**: System MUST add two new intrigue cards with an effect that grants the playing player the first-player marker for the next round (without drawing an intrigue card).
- **FR-006**: All 14 new cards MUST have thematic names and humorous or flavorful descriptions consistent with the game's music industry theme.
- **FR-007**: The game engine MUST handle each new effect type when an intrigue card is played, updating game state appropriately.
- **FR-008**: The game log MUST display an appropriate message when each new card type is played.
- **FR-009**: All new intrigue cards MUST generate card images via the card image generator with appropriate visual icons.
- **FR-010**: When a reset-quests or reset-buildings card is played, all connected clients MUST see the updated display immediately.
- **FR-011**: If the quest or building deck is depleted when a draw is needed (from reset cards, end-of-round refill, or any other source), the system MUST reshuffle the discard pile into a new deck and draw from it. For quests, completed quests (held by any player) MUST be excluded from the reshuffle. This is a global mechanic applying to all quest/building draws.
- **FR-012**: The system MUST verify that the existing quest/building draw logic already supports discard-pile reshuffling, and add it if not present.

### Key Entities

- **Intrigue Card**: Existing entity — new cards added to `config/intrigue.json` with new `effect_type` values.
- **Quest Display**: Existing entity — the face-up quests on the board, refreshed by reset-quests cards.
- **Building Display**: Existing entity — the face-up purchasable buildings, refreshed by reset-buildings cards.
- **First Player Marker**: Existing game concept — determines turn order for the next round.
- **Quest Discard Pile**: Discard pile for quests removed from display — reshuffled into deck when deck is depleted (excluding completed quests).
- **Building Discard Pile**: Discard pile for buildings removed from display — reshuffled into deck when deck is depleted.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 14 new intrigue cards appear in the intrigue deck and can be drawn during gameplay.
- **SC-002**: Playing each card type produces the correct effect (or no effect for do-nothing cards) within normal turn resolution time.
- **SC-003**: All new card images are generated with appropriate icons that visually communicate each card's effect.
- **SC-004**: Reset cards immediately update the shared display for all connected players.
- **SC-005**: All existing game tests continue to pass after the new cards are added.
- **SC-006**: The intrigue deck size increases by 14 (from 54 to 68 cards).

## Assumptions

- The four do-nothing cards each have a unique humorous name and description related to real-world interruptions in the music industry (e.g., mom showing up, equipment malfunction that fixes itself, etc.).
- The four draw-1-intrigue cards use a new effect type `draw_intrigue` (same name as the existing building effect, repurposed for intrigue card effects) or a card-specific variant.
- The reset-quests cards use a new effect type (e.g., `reset_quests`) that the game engine must handle.
- The reset-buildings cards use a new effect type (e.g., `reset_buildings`) that the game engine must handle.
- The first-player-marker cards use a new effect type (e.g., `first_player_marker`) that reuses existing first-player logic from the Fastpass space handler.
- Card IDs continue the existing sequence: intrigue_055 through intrigue_068.
- All new cards target "self" (the playing player) for effect_target.
- No changes to intrigue hand limits are needed (there is no hand limit).
- Card images use existing icon primitives where possible (intrigue card icon for draw-1, quest/building icons for reset cards, star/arrow icon for first-player).
