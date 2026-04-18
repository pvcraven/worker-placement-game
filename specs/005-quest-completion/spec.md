# Feature Specification: Quest Completion

**Feature Branch**: `005-quest-completion`
**Created**: 2026-04-17
**Status**: Draft
**Input**: User description: "Quest completion flow with status bar improvements"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - End-of-Turn Quest Completion (Priority: P1)

After a player finishes placing a worker and the placement resolves, the system checks whether that player holds any quest cards whose resource requirements are fully met. If one or more quests are completable, a dialog appears showing all eligible quest cards laid out horizontally. The player clicks one quest card to complete it, gaining the quest's victory points and discarding the spent resources. If the player does not wish to complete a quest, they click "Skip" at the bottom of the dialog. Only one quest may be completed per turn.

**Why this priority**: Quest completion is the core scoring mechanic of the game. Without it, players accumulate resources with no payoff.

**Independent Test**: Start a game, acquire a quest card, gather the required resources, place a worker. After placement resolves, the quest completion dialog should appear showing only quests the player can afford. Completing a quest deducts resources and awards victory points. Skipping dismisses the dialog and ends the turn normally.

**Acceptance Scenarios**:

1. **Given** a player has 1 completable quest and sufficient resources, **When** their worker placement resolves, **Then** a dialog appears showing that quest card with a "Skip" button below.
2. **Given** a player has 3 quests but only 2 are completable, **When** the dialog appears, **Then** only the 2 completable quests are shown.
3. **Given** the quest completion dialog is showing, **When** the player clicks a quest card, **Then** the quest is completed: resources are deducted, victory points are awarded, the quest is removed from the player's hand, and the turn ends.
4. **Given** the quest completion dialog is showing, **When** the player clicks "Skip", **Then** the dialog closes and the turn ends without completing any quest.
5. **Given** a player has no completable quests (either no quests at all or insufficient resources for all held quests), **When** their worker placement resolves, **Then** no dialog appears and the turn ends normally.

---

### User Story 2 - Workers and VP Status Display (Priority: P2)

The bottom resource bar is adjusted to make room for a new status line above it. This new line displays the player's remaining available workers and their current victory point total, formatted as: "Workers left: 2  VP: 3". The VP display is moved from its previous location to this new line.

**Why this priority**: Players need at-a-glance visibility of workers remaining and VP to make informed placement decisions. This is a minor UI adjustment that supports the core gameplay loop.

**Independent Test**: Join a game, observe the new status line showing workers left and VP. Place a worker and confirm the workers count decrements. Complete a quest and confirm the VP count increments.

**Acceptance Scenarios**:

1. **Given** a player is in an active game, **When** viewing the game board, **Then** a status line is visible showing "Workers left: [N]  VP: [M]" where N is the number of unplaced workers and M is the current victory point total.
2. **Given** a player places a worker, **When** the board updates, **Then** the "Workers left" count decreases by 1.
3. **Given** a player completes a quest worth 5 VP, **When** the board updates, **Then** the VP count increases by 5.
4. **Given** a new round begins and workers are returned, **When** the board updates, **Then** the "Workers left" count resets to the player's total worker count.

---

### Edge Cases

- What happens if a player disconnects while the quest completion dialog is open? The turn should time out and skip quest completion, advancing to the next player.
- What happens if a quest's reward itself grants resources that make another quest completable? Only one quest may be completed per turn; the newly-completable quest can be completed on a future turn.
- What happens if the player has exactly 0 workers left? The "Workers left: 0" display is shown; no further placements are possible for that round.
- What happens if a quest card is completed that was the last quest in the player's hand? The quest is removed and the player's quest hand is now empty. No special handling needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST check, after each worker placement resolves, whether the active player can complete any held quest cards based on current resources.
- **FR-002**: If one or more quests are completable, the system MUST display a dialog showing all completable quest cards arranged horizontally.
- **FR-003**: The quest completion dialog MUST include a "Skip" button at the bottom that dismisses the dialog without completing any quest.
- **FR-004**: The player MUST be able to select exactly one quest card from the dialog to complete.
- **FR-005**: Upon quest completion, the system MUST deduct the quest's resource cost from the player's resources, award the quest's victory points, and remove the quest from the player's hand.
- **FR-006**: The system MUST NOT show the quest completion dialog if the player has no completable quests.
- **FR-007**: The system MUST limit quest completion to one quest per turn.
- **FR-008**: The game board MUST display a status line showing the player's remaining workers and current victory points in the format "Workers left: [N]  VP: [M]".
- **FR-009**: The resource display area MUST be shifted down to accommodate the new status line above it.
- **FR-010**: The VP display MUST be moved from its current location to the new status line.
- **FR-011**: The workers-left count MUST update immediately when a worker is placed or returned.
- **FR-012**: The VP count MUST update immediately when victory points are awarded.
- **FR-013**: All connected players MUST see updated game state (resources, VP, quest hand changes) after a quest is completed.

### Key Entities

- **Quest Card**: Represents a quest with a resource cost, victory point reward, genre, and description. Players hold quest cards in their hand and complete them by spending the required resources.
- **Player Resources**: The set of resources a player currently holds (guitarists, bass players, drummers, singers, coins). Used to determine quest eligibility.
- **Victory Points (VP)**: Cumulative score earned primarily through quest completion. Displayed in the status line.
- **Available Workers**: The number of workers a player has left to place in the current round. Displayed in the status line.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Players can complete a quest in under 5 seconds from dialog appearance to quest resolution.
- **SC-002**: The quest completion dialog displays only eligible quests with 100% accuracy (no ineligible quests shown, no eligible quests omitted).
- **SC-003**: Workers-left and VP displays update within 1 second of the triggering action.
- **SC-004**: 100% of quest completions correctly deduct resources and award victory points with no discrepancies.
- **SC-005**: The quest completion flow adds no more than 3 seconds to the average turn duration when the player has no completable quests (i.e., the check is near-instant).

## Assumptions

- The existing quest card data model already includes resource cost and victory point values.
- The worker placement resolution flow already has a defined point where the turn would normally advance to the next player; the quest completion check inserts before that point.
- The "Skip" button follows the same visual style as existing dialog buttons (e.g., "Cancel" in building purchase dialog).
- Quest completion rewards are limited to victory points (no resource rewards from completing quests in this scope).
- The resource bar's current position and layout are flexible enough to shift down without overlapping other UI elements.
- The VP display currently exists somewhere on the board and will be relocated, not duplicated.
