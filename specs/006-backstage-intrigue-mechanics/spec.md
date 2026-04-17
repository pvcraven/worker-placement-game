# Feature Specification: Backstage & Intrigue Mechanics

**Feature Branch**: `006-backstage-intrigue-mechanics`
**Created**: 2026-04-17
**Status**: Draft
**Input**: User description: "Backstage placement, intrigue card selection, starting resources, and worker reassignment"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Starting Resources (Priority: P1)

When a game begins, each player receives 2 intrigue cards drawn from the intrigue deck. Additionally, players receive starting coins based on turn order: the first player receives 4 coins, the second player receives 6 coins, the third receives 8 coins, and so on (+2 coins per position). This compensates later players for the disadvantage of going second/third/etc.

**Why this priority**: Starting resources are the foundation of the first round. Without them, players have no intrigue cards to play on Backstage and later players have a significant turn-order disadvantage.

**Independent Test**: Create a 3-player game. After the game starts, verify Player 1 has 4 coins and 2 intrigue cards, Player 2 has 6 coins and 2 intrigue cards, Player 3 has 8 coins and 2 intrigue cards.

**Acceptance Scenarios**:

1. **Given** a new game starts with 3 players, **When** the game state is initialized, **Then** Player 1 (first in turn order) has 4 coins and 2 intrigue cards, Player 2 has 6 coins and 2 intrigue cards, Player 3 has 8 coins and 2 intrigue cards.
2. **Given** a new game starts with 1 player (solo), **When** the game state is initialized, **Then** that player has 4 coins and 2 intrigue cards.
3. **Given** a new game starts with 5 players, **When** the game state is initialized, **Then** Player 5 has 12 coins and 2 intrigue cards.

---

### User Story 2 - Backstage Placement with Intrigue Card (Priority: P1)

A player may place a worker on a Backstage spot (1, 2, or 3). Backstage spots must be filled left-to-right: spot 1 must be occupied before spot 2 can be used, and spot 2 before spot 3. To place on a Backstage spot, the player must have at least one intrigue card in hand. After placing the worker, the player selects which intrigue card to play from their hand. If the player cancels the intrigue card selection, the placement is unwound: the worker is removed from the Backstage spot and returned to the player's available pool.

**Why this priority**: Backstage is a core action space. Currently it shows "Unknown action space" — this is a blocking bug that prevents players from using a major game mechanic.

**Independent Test**: Start a game, acquire intrigue cards, attempt to place a worker on Backstage 1. Verify intrigue card selection dialog appears. Select a card and verify placement succeeds. Then verify Backstage 2 becomes available.

**Acceptance Scenarios**:

1. **Given** Backstage 1 is empty, **When** a player with intrigue cards clicks Backstage 1, **Then** the worker is placed and an intrigue card selection dialog appears showing the player's intrigue cards.
2. **Given** the intrigue card selection dialog is showing, **When** the player selects a card, **Then** the card is played, its effect resolves, and the turn proceeds.
3. **Given** the intrigue card selection dialog is showing, **When** the player clicks "Cancel", **Then** the worker is removed from the Backstage spot and returned to the player's pool.
4. **Given** Backstage 1 is empty, **When** a player tries to place on Backstage 2, **Then** the placement is rejected with a message indicating Backstage 1 must be filled first.
5. **Given** Backstage 1 is occupied but Backstage 2 is empty, **When** a player places on Backstage 2, **Then** the placement succeeds and intrigue card selection appears.
6. **Given** a player has no intrigue cards, **When** they try to place on any Backstage spot, **Then** the placement is rejected with a message indicating they need an intrigue card.
7. **Given** all 3 Backstage spots are occupied, **When** a player tries to place on any Backstage spot, **Then** the placement is rejected (spots are full).

---

### User Story 3 - Worker Reassignment Phase (Priority: P2)

When all players have placed all their workers during the round, the game enters the Backstage Reassignment phase. Starting with Backstage spot 1, the worker on that spot is removed and returned to its owner's available pool. That player then places the freed worker on any open action space on the board (following normal placement rules, excluding Backstage). This process repeats for Backstage spots 2 and 3 in order. If a Backstage spot is unoccupied, it is skipped.

**Why this priority**: Worker reassignment is the payoff for the Backstage mechanic — it gives players a strategic second placement opportunity. Without it, Backstage has no purpose beyond playing intrigue cards.

**Independent Test**: Start a game, fill all worker placements including some Backstage spots. After the last worker is placed, verify the reassignment phase begins. Verify the player from Backstage 1 is prompted to place their freed worker, then Backstage 2, then 3.

**Acceptance Scenarios**:

1. **Given** all workers are placed and Backstage 1 is occupied by Player A, **When** the reassignment phase begins, **Then** Player A is prompted to place their freed worker on any open action space.
2. **Given** Player A is prompted to reassign, **When** Player A clicks an open action space, **Then** the worker is placed there, the space reward is granted, and the next occupied Backstage spot is processed.
3. **Given** Backstage 2 is unoccupied but Backstage 3 is occupied, **When** reassignment reaches spot 2, **Then** spot 2 is skipped and spot 3 is processed.
4. **Given** all Backstage spots are empty, **When** all workers are placed, **Then** the reassignment phase is skipped and the round ends normally.
5. **Given** the reassignment phase is active, **When** the prompted player clicks an already-occupied space, **Then** the placement is rejected and the player must choose an open space.

---

### Edge Cases

- What happens if a player disconnects during intrigue card selection on Backstage? The placement is unwound (worker removed from Backstage spot) and the turn times out, advancing to the next player.
- What happens if there are fewer than 2 intrigue cards in the deck at game start? Each player receives as many intrigue cards as available (0 or 1). No error occurs.
- What happens if a player needs to reassign but all action spaces are occupied? The worker is returned to the player's pool but cannot be placed. The reassignment moves to the next Backstage spot.
- What happens if intrigue card effects modify resources during the backstage placement? The intrigue card effect resolves immediately upon selection, before the turn proceeds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deal 2 intrigue cards from the intrigue deck to each player when the game starts.
- **FR-002**: System MUST grant starting coins based on turn order: 4 coins to the first player, +2 for each subsequent player.
- **FR-003**: Backstage spots MUST be filled in sequential order — spot N+1 cannot be occupied until spot N is occupied.
- **FR-004**: A player MUST have at least one intrigue card in hand to place a worker on a Backstage spot.
- **FR-005**: After placing a worker on a Backstage spot, the system MUST present the player with a selection dialog showing their intrigue cards.
- **FR-006**: The player MUST select an intrigue card to play. Cancelling the selection MUST unwind the placement (remove worker, return to pool).
- **FR-007**: The selected intrigue card's effect MUST resolve immediately upon selection.
- **FR-008**: When all players have placed all workers, the system MUST enter a Backstage Reassignment phase.
- **FR-009**: During reassignment, the system MUST process Backstage spots in order (1, 2, 3), skipping unoccupied spots.
- **FR-010**: For each occupied Backstage spot during reassignment, the system MUST return the worker to its owner's pool and prompt that player to place it on any open action space.
- **FR-011**: During reassignment, the freed worker follows normal placement rules (space must be unoccupied) but MUST NOT be placed on a Backstage spot.
- **FR-012**: The reassignment placement MUST grant the normal reward of the chosen action space.
- **FR-013**: All connected players MUST see updated game state after each backstage placement, intrigue card play, and reassignment.

### Key Entities

- **Intrigue Card**: A card with a name, description, and gameplay effect. Players hold intrigue cards in hand and play them when placing on Backstage spots.
- **Backstage Spot**: One of three ordered spots (1, 2, 3) where workers can be placed alongside an intrigue card. During reassignment, the worker is freed for redeployment.
- **Turn Order**: The sequence in which players take turns. Determines starting coin amounts (4 + 2 per position after first).
- **Reassignment Phase**: A game phase that occurs after all workers are placed, processing Backstage spots sequentially.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of games correctly distribute starting coins and intrigue cards per turn-order rules.
- **SC-002**: Players can complete a Backstage placement (worker + intrigue card selection) in under 10 seconds.
- **SC-003**: The Backstage left-to-right ordering rule is enforced with 100% accuracy (no out-of-order placements permitted).
- **SC-004**: Cancelling intrigue card selection successfully unwinds the placement in 100% of cases (no stuck workers).
- **SC-005**: The reassignment phase processes all occupied Backstage spots within 30 seconds per spot (including player decision time).
- **SC-006**: Players with no intrigue cards are blocked from Backstage placement with a clear message in 100% of attempts.

## Assumptions

- Intrigue card effects are already defined in the game configuration and the effect resolution logic already exists.
- The intrigue card selection dialog follows the same UI pattern as existing card selection dialogs (list of cards with cancel option).
- During reassignment, the freed worker can be placed on any permanent or building action space, but not on Backstage or Garage spots.
- The game already tracks turn order and uses it for determining play sequence.
- The Backstage spots are already defined in the board configuration but are currently non-functional ("Unknown action space" error).
