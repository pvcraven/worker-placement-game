# Feature Specification: Intrigue Targeting & Player Overview

**Feature Branch**: `007-intrigue-targeting-player-overview`
**Created**: 2026-04-17
**Status**: Draft
**Input**: User description: "Fix intrigue cards with steal/opponent_loses effects that require choosing a target opponent. Add a player overview panel showing all players' resources."

## User Scenarios & Testing

### User Story 1 - Targeted Intrigue Card Resolution (Priority: P1)

When a player plays an intrigue card with a "choose_opponent" target (e.g., "Poach the Vocalist" which steals a singer), the game must prompt them to select which opponent to target. Currently the effect is silently skipped because no target selection dialog exists.

**Why this priority**: This is a bug fix. Targeted intrigue cards are non-functional — playing them has no effect, which breaks core game mechanics and wastes the player's card.

**Independent Test**: Start a 2+ player game. Play a steal_resources intrigue card on a backstage slot. Verify a target selection dialog appears showing eligible opponents, select one, and confirm the resource is transferred.

**Acceptance Scenarios**:

1. **Given** a player plays a "steal_resources" intrigue card with target "choose_opponent", **When** the card is played on a backstage slot, **Then** a target selection dialog appears showing all opponents who have the targeted resource(s).
2. **Given** the target selection dialog is shown, **When** the player selects an opponent, **Then** the specified resources are transferred from the opponent to the player and both players' resource displays update.
3. **Given** the target selection dialog is shown, **When** the player clicks "Cancel", **Then** the backstage placement is unwound — the worker is removed from the backstage slot, the intrigue card is returned to the player's hand, and the player may take a different action.
4. **Given** a player plays a "steal_resources" card in a single-player game or when no opponent has the targeted resource(s), **When** the card is played, **Then** the game shows a message indicating no valid targets exist and allows the player to cancel.
5. **Given** a player plays an "opponent_loses" intrigue card with target "choose_opponent", **When** the card is played, **Then** the same target selection flow applies — the opponent loses the specified resources (they are not transferred to the player).

---

### User Story 2 - Player Overview Panel (Priority: P2)

Players need a way to see all players' current resources, worker counts, and progress at a glance. A new "Player Overview" button (alongside existing "My Quests", "My Intrigue", "Real Estate Listings" buttons) opens a panel showing a table of all players and their stats.

**Why this priority**: Supports informed decision-making for targeted intrigue cards and general strategy. Players currently have no visibility into opponents' resources.

**Independent Test**: Start a game, click the "Player Overview" button, verify a panel appears with a table showing each player's stats. Verify the data updates as the game progresses.

**Acceptance Scenarios**:

1. **Given** a game is in progress, **When** the player clicks the "Player Overview" button, **Then** a panel appears showing a table with one row per player.
2. **Given** the player overview panel is shown, **Then** each row displays: player name, available workers, guitarists, bass players, drummers, singers, coins, intrigue card count, quests in hand count, quests completed count, and victory points.
3. **Given** the player overview panel is shown, **When** the player clicks the button again or clicks elsewhere, **Then** the panel closes (toggle behavior, consistent with existing hand panels).
4. **Given** a resource changes during the game (e.g., a worker is placed, a quest is completed), **When** the player overview panel is next opened, **Then** the updated values are displayed.
5. **Given** the player overview panel is shown, **Then** the current player's row is visually distinguished from opponents' rows.

---

### Edge Cases

- What happens when a steal targets a resource the opponent has at 0? The opponent's resource stays at 0 and the stealing player receives nothing for that resource type.
- What happens when a steal card specifies multiple resources (e.g., 1 guitarist + 1 singer) but the opponent only has one of them? Each resource is stolen independently — the player gets what the opponent has (partial steal). Resources cannot go below 0.
- What happens when the "opponent_loses" effect targets resources the opponent doesn't have? The opponent's resources are reduced to 0 at minimum (no negative values). Unlike steal, the active player does not gain anything.
- What happens if the intrigue effect targets "all" instead of "choose_opponent"? The existing "all" target handling remains unchanged — no dialog is shown, the effect applies to all players automatically.

## Requirements

### Functional Requirements

- **FR-001**: When an intrigue card with effect_target "choose_opponent" is played, the system MUST pause and prompt the player to select a target opponent before resolving the effect.
- **FR-002**: The target selection dialog MUST display only opponents who have at least one of the targeted resource(s) available to steal/lose.
- **FR-003**: If no valid targets exist (solo game or no opponent has the required resources), the system MUST display a message stating no valid targets are available and allow the player to cancel the backstage placement.
- **FR-004**: The player MUST be able to cancel the target selection, which unwinds the backstage placement — removing the worker from the backstage slot, returning the intrigue card to the player's hand, and restoring the player's available worker count.
- **FR-005**: When a valid target is selected for "steal_resources", the system MUST transfer each resource from the target to the active player. If the target has fewer of a resource than specified, only the available amount is transferred.
- **FR-006**: When a valid target is selected for "opponent_loses", the system MUST remove the specified resources from the target. The target's resources cannot go below 0. The active player does not gain these resources.
- **FR-007**: After a targeted intrigue effect resolves, the game log MUST display a message indicating who targeted whom and what resources were affected.
- **FR-008**: A "Player Overview" button MUST be added to the button row alongside existing hand toggle buttons.
- **FR-009**: The player overview panel MUST display a table with one row per player showing: player name, available workers, guitarists, bass players, drummers, singers, coins, intrigue cards (count), quests in hand (count), quests completed (count), and victory points.
- **FR-010**: The player overview panel MUST show current data from the local game state each time it is opened.
- **FR-011**: The current player's row in the overview panel MUST be visually distinguished (e.g., highlighted or bordered differently).
- **FR-012**: Opponent intrigue card and quest hand counts MUST show count only (not card contents), consistent with existing information hiding rules.

### Key Entities

- **Intrigue Target Selection**: A transient interaction where the player chooses an opponent for a "choose_opponent" effect. Involves the intrigue card's effect_type, effect_value (which resources), and the list of eligible opponents.
- **Player Overview**: A read-only summary view of all players' publicly visible stats. No new data — aggregates existing game state fields.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of "choose_opponent" intrigue cards produce a target selection prompt when played.
- **SC-002**: Players can see all opponents' resource counts within 1 click from the main game view.
- **SC-003**: Steal and opponent_loses effects correctly transfer or remove the exact resources specified, with no resource going below 0.
- **SC-004**: Cancel flow from target selection restores game state to pre-placement condition with no side effects.

## Assumptions

- The existing intrigue card data model (effect_type, effect_target, effect_value) already contains all information needed for targeting — no schema changes required.
- The server already has a `ChooseIntrigueTargetRequest` message type and `handle_choose_intrigue_target` handler that can be extended or fixed rather than built from scratch.
- Opponent resource counts are considered public information (visible in the player overview), consistent with typical worker placement board game rules.
- The "cancel" flow during target selection follows the same pattern as cancel during quest selection — the backstage placement is fully unwound.
- The player overview panel uses the same toggle pattern as existing panels (My Quests, My Intrigue, Real Estate Listings).
