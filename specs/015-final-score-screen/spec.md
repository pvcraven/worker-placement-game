# Feature Specification: Final Score Screen

**Feature Branch**: `015-final-score-screen`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: User description: "Add an end-screen dialog showing final scores, VP breakdown, and winner highlight for each player."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Final Score Breakdown (Priority: P1)

A player wants to see a detailed breakdown of every player's victory points at any time during the game. The player clicks a "Final Screen" button (located to the right of "Player Overview") and a dialog appears showing each player's producer card, name, VP earned during gameplay, genre bonus VP, resource VP, and total VP. The player with the highest total VP is highlighted with "WINNER" above their producer card. Clicking "Final Screen" again or clicking a "Close" button on the dialog dismisses it.

**Why this priority**: This is the core feature. Without the scoring breakdown display, the feature has no value.

**Independent Test**: Click the "Final Screen" button during a game. Verify the dialog appears with all players listed, each showing their producer card image, player name, game VP, genre bonus VP, resource VP, and total VP. Verify the highest-scoring player has "WINNER" displayed above their card. Click the button again or click "Close" to dismiss.

**Acceptance Scenarios**:

1. **Given** a game is in progress, **When** the player clicks the "Final Screen" button, **Then** a dialog appears overlaying the game board showing a scoring summary for every player.
2. **Given** the final score dialog is open, **When** the player clicks "Final Screen" again, **Then** the dialog closes.
3. **Given** the final score dialog is open, **When** the player clicks the "Close" button on the dialog, **Then** the dialog closes.
4. **Given** the dialog is displayed, **Then** each player column shows: producer card image, player name, VP earned during the game, genre bonus VP, resource VP, and total VP.
5. **Given** the dialog is displayed, **Then** the player with the highest total VP has "WINNER" displayed above their producer card.
6. **Given** two or more players are tied for highest total VP, **Then** all tied players are highlighted with "WINNER" above their cards.

---

### User Story 2 - Game-Over Final Screen (Priority: P2)

When the game ends (final round completes), the final score screen automatically appears. This version of the screen includes a "Close" button that, when clicked, returns the player to the lobby instead of simply closing the dialog. The player cannot dismiss this dialog by clicking the "Final Screen" button — they must use the "Close" button.

**Why this priority**: This is the game-ending flow. It depends on US1's scoring display but adds the automatic trigger and lobby navigation.

**Independent Test**: Complete a game (or simulate game-over). Verify the final score dialog appears automatically. Verify clicking "Close" navigates the player back to the lobby.

**Acceptance Scenarios**:

1. **Given** the final round of the game has completed, **When** all end-of-round processing finishes, **Then** the final score dialog appears automatically for all players.
2. **Given** the game-over final score dialog is displayed, **When** the player clicks the "Close" button, **Then** the player is returned to the lobby screen.
3. **Given** the game-over final score dialog is displayed, **When** the player clicks the "Final Screen" toggle button, **Then** nothing happens (the dialog stays open).

---

### Edge Cases

- What happens when a player has no completed quests? The genre bonus VP is 0, and the display shows 0 for that row.
- What happens when a player has no producer card? The producer card area shows a placeholder (e.g., "No Producer") and genre bonus VP is 0.
- What happens when a player has no resources remaining? Resource VP is 0.
- What happens when all players have 0 VP? All players are shown as "WINNER" (all tied).
- What happens when the game has only 1 player? That player is the winner.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Final Screen" button to the right of the "Player Overview" button during gameplay.
- **FR-002**: Clicking the "Final Screen" button MUST toggle a dialog overlay on and off.
- **FR-003**: The dialog MUST display one column per player, each containing:
  - Producer card image (or placeholder if none assigned)
  - Player name
  - VP earned during the game (sum of victory_points from completed quests)
  - Genre bonus VP (producer bonus_vp_per_contract for each completed quest whose genre matches one of the producer's bonus_genres)
  - Resource VP (1 point per musician resource held + 1 point per pair of coins held, rounded down)
  - Total VP (sum of game VP + genre bonus VP + resource VP)
- **FR-004**: The player with the highest total VP MUST have "WINNER" displayed prominently above their producer card.
- **FR-005**: If multiple players are tied for highest total VP, all tied players MUST be highlighted as winners.
- **FR-006**: When the game ends, the final score dialog MUST appear automatically.
- **FR-007**: When the dialog appears due to game-over, the "Close" button MUST navigate the player back to the lobby.
- **FR-008**: When the dialog appears from the "Final Screen" button, the "Close" button MUST simply close the dialog without navigating away.
- **FR-009**: The dialog MUST include a visible "Close" button.
- **FR-010**: The dialog layout MUST be visually similar in style to the Player Overview dialog (overlay on game board, semi-transparent background).

### VP Calculation Rules

- **Game VP**: Sum of `victory_points` from all contracts in the player's completed contracts list.
- **Genre Bonus VP**: For each completed contract whose `genre` matches any entry in the player's producer card's `bonus_genres` list, add the producer's `bonus_vp_per_contract` (default: 4). If the player has no producer card, genre bonus is 0.
- **Resource VP**: Count of all musician resources (guitarists + bass_players + drummers + singers) plus floor(coins / 2). Each musician resource is 1 VP. Each pair of coins is 1 VP, with any odd coin ignored.
- **Total VP**: Game VP + Genre Bonus VP + Resource VP.

### Key Entities

- **ScoreBreakdown**: Represents one player's final score: player name, game VP, genre bonus VP, resource VP, total VP, and whether they are the winner.
- **ProducerCard**: Existing entity with `bonus_genres` and `bonus_vp_per_contract` fields used for genre bonus calculation.
- **ContractCard**: Existing entity with `genre` and `victory_points` fields used for game VP and genre bonus calculation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can view the complete VP breakdown for all players within 1 click from the game screen.
- **SC-002**: The final score screen displays correctly for games with 2 to 6 players.
- **SC-003**: VP totals on the final screen are 100% consistent with the underlying game data (no calculation errors).
- **SC-004**: When the game ends, 100% of players see the final score screen automatically without any additional interaction.
- **SC-005**: Players can return to the lobby from the game-over screen within 1 click.

## Assumptions

- The existing Player Overview dialog provides the visual style reference for the final score dialog (semi-transparent overlay, centered on screen).
- Producer cards, completed quests, and player resources are already available in the game state sent to clients.
- The game currently has a defined end condition (final round completion) that can trigger the automatic dialog display.
- The "Final Screen" button is a temporary testing aid but will remain in the shipped version for players who want to check scores mid-game.
- Genre bonus VP uses the producer card's `bonus_vp_per_contract` value (currently 4) per matching quest, not a variable amount.
- The layout shows players side by side (horizontally) with their scoring column beneath their producer card.
