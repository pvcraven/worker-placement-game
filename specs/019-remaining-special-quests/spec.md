# Feature Specification: Remaining Special Quest Mechanics

**Feature Branch**: `019-remaining-special-quests`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: Implement the last 6 unimplemented special quest mechanics from the Waterdeep card mapping.

## Clarifications

### Session 2026-04-26

- Q: Is the Soul Music Residency round-start resource random or player-chosen? → A: Player chooses a non-coin resource (not random).
- Q: Is Time Warp Remix worker recall persistent (once per round) or one-time? → A: One-time on quest completion. Player selects which placed worker to recall. If no workers placed, skip. UI shows message at top of screen; player clicks the space to recall from.

## Overview

Six quest cards have special mechanics defined in the card data but no game logic to support them. Three are one-time completion rewards and three are persistent plot quest abilities. This specification covers all six so the full card set is playable.

### Cards Covered

**One-Time Completion Rewards:**
1. **Jailhouse Jazz Session** (`contract_jazz_010`) — On completion, player immediately plays one intrigue card from their hand.
2. **Charity Gala Showcase** (`contract_pop_008`) — On completion, one opponent receives 4 coins.
3. **Time Warp Remix** (`contract_funk_001`) — On completion, recall one already-placed worker back to your pool (or skip if none placed).

**Persistent Plot Quest Abilities:**
4. **Hire a Tour Manager** (`contract_rock_009`) — Gain 1 extra permanent worker.
5. **Soul Music Residency** (`contract_soul_007`) — Choose 1 non-coin resource to gain at the start of each round.
6. **Recover the Master Tapes** (`contract_funk_005`) — Once per round, use a building action space that is already occupied by another player's worker.

## User Scenarios & Testing

### User Story 1 - One-Time Completion Rewards (Priority: P1)

A player completes a quest that has a one-time special reward beyond normal resources and VP. The reward triggers immediately as part of the quest completion flow.

**Why this priority**: These are the simplest mechanics — they fire once and require no ongoing state tracking. They complete the set of one-time rewards.

**Independent Test**: Complete "Jailhouse Jazz Session" or "Charity Gala Showcase" and verify the special reward triggers immediately.

**Acceptance Scenarios**:

1. **Given** a player has "Jailhouse Jazz Session" in hand and at least one intrigue card, **When** they complete the quest, **Then** they receive the normal rewards (2 Guitarists, 14 VP) and are prompted to play one intrigue card from their hand.
2. **Given** a player completes "Jailhouse Jazz Session" but has zero intrigue cards, **When** the quest completes, **Then** the play-intrigue step is skipped and the turn proceeds normally.
3. **Given** a player completes "Charity Gala Showcase" in a 2-player game, **When** the quest completes, **Then** the single opponent receives 4 coins automatically (no choice needed).
4. **Given** a player completes "Charity Gala Showcase" in a 3+ player game, **When** the quest completes, **Then** the completing player is prompted to choose which opponent receives the 4 coins.

---

### User Story 2 - Extra Permanent Worker (Priority: P2)

A player completes the "Hire a Tour Manager" plot quest and permanently gains one additional worker for the rest of the game.

**Why this priority**: This is a high-impact, straightforward mechanic — increase the player's worker count by 1. No per-round tracking needed.

**Independent Test**: Complete "Hire a Tour Manager" and verify the player's available worker count increases by 1 on subsequent rounds.

**Acceptance Scenarios**:

1. **Given** a player has 4 workers (the standard count), **When** they complete "Hire a Tour Manager", **Then** their total worker count becomes 5 and the extra worker is available starting the next round.
2. **Given** a player already received the round-5 bonus worker (5 workers), **When** they complete "Hire a Tour Manager", **Then** their total worker count becomes 6.
3. **Given** a player completes "Hire a Tour Manager" mid-round, **Then** the extra worker is NOT available this round — it becomes available at the start of the next round (same as the round-5 bonus worker).

---

### User Story 3 - Round-Start Resource Gain (Priority: P3)

A player who has completed "Soul Music Residency" is prompted to choose 1 non-coin resource (Guitarist, Bass Player, Drummer, or Singer) at the start of each subsequent round.

**Why this priority**: Requires hooking into the round-start flow and a resource choice prompt before the first turn of the round.

**Independent Test**: Complete "Soul Music Residency", advance to the next round, and verify the player is prompted to choose a non-coin resource.

**Acceptance Scenarios**:

1. **Given** a player has completed "Soul Music Residency", **When** a new round begins, **Then** the player is prompted to choose 1 non-coin resource (Guitarist, Bass Player, Drummer, or Singer) and the chosen resource is added to their pool.
2. **Given** a player has completed "Soul Music Residency", **When** the resource choice is made, **Then** the game log shows what was gained and play proceeds to the first turn.
3. **Given** a player completes "Soul Music Residency" during round 3, **Then** the benefit first triggers at the start of round 4.

---

### User Story 4 - Worker Recall on Completion (Priority: P4)

A player who completes "Time Warp Remix" immediately recalls one of their already-placed workers from an action space back to their available pool, freeing that space. This is a one-time effect at quest completion, not a recurring ability.

**Why this priority**: Requires interactive spatial selection (player clicks a board space to recall from) as part of the quest completion flow.

**Independent Test**: Complete "Time Warp Remix" while having at least one worker placed on the board. Verify the player is prompted to select a space, the worker is recalled, and the space is freed.

**Acceptance Scenarios**:

1. **Given** a player completes "Time Warp Remix" and has at least one placed worker on the board, **When** the quest completes, **Then** a message appears at the top of the screen prompting the player to click on a space to recall a worker from.
2. **Given** the player clicks on a space occupied by their own worker, **Then** the space becomes unoccupied, the worker returns to their available pool, and the turn advances.
3. **Given** a player completes "Time Warp Remix" but has no workers currently placed on the board, **Then** the recall step is skipped automatically and the turn proceeds normally.
4. **Given** a player recalls a worker from a building owned by another player, **Then** only the worker is removed — no resources are returned or reversed.

---

### User Story 5 - Use Occupied Building (Priority: P5)

A player who has completed "Recover the Master Tapes" can once per round place a worker on a building action space that is already occupied by another player's worker.

**Why this priority**: This is the most complex mechanic — it overrides the normal "space is occupied" validation for buildings only, requires once-per-round tracking, and only applies to buildings (not standard board spaces).

**Independent Test**: Complete "Recover the Master Tapes", then place a worker on an already-occupied building and verify the reward is granted.

**Acceptance Scenarios**:

1. **Given** a player has completed "Recover the Master Tapes" and a building is occupied by another player's worker, **When** it is their turn, **Then** that building appears as a valid placement option.
2. **Given** a player places a worker on an occupied building using this ability, **Then** both workers now occupy the space, the placing player receives the building's visitor reward, and the building owner receives the owner bonus.
3. **Given** a player has already used this ability this round, **Then** occupied buildings are NOT valid placement options for the rest of the round.
4. **Given** a building is occupied by the player's own worker, **Then** this ability does NOT allow placing a second worker on it — it only works for buildings occupied by other players.
5. **Given** a non-building space (e.g., a standard board action space) is occupied, **Then** this ability does NOT apply — it only works on building spaces.
6. **Given** a new round starts, **Then** the ability resets and becomes available again.

---

### Edge Cases

- What happens if a player completes "Jailhouse Jazz Session" and plays a targeted intrigue card that requires choosing a target? The normal intrigue target selection flow applies — the quest completion pauses until the intrigue card is fully resolved.
- What happens if "Soul Music Residency" is completed and there are no more rounds left (completed during the last round)? The benefit never triggers since there is no subsequent round start.
- What happens if multiple players have completed "Soul Music Residency"? Each player is prompted in turn order. All choices must resolve before the first worker placement turn.
- What happens if a player completes "Time Warp Remix" with no workers on the board? The recall step is skipped automatically.
- What happens if a player recalls a worker from a building that accumulates VP/resources? The accumulated stock is NOT affected — it was already granted when the worker was originally placed.
- What happens if a player completes "Time Warp Remix" and recalls a worker from a backstage slot? The recall only applies to board action spaces occupied by the player's worker, not backstage slots.
- What happens if both players in a 2-player game each have "Recover the Master Tapes" and both want to use the same building? Each use creates a separate placement; a building could theoretically have 3 workers (original + 2 uses).
- What happens if a player with "Recover the Master Tapes" tries to use it on a building they own that is occupied by another player? This is allowed — the ability works on any building occupied by another player, regardless of who owns the building.

## Requirements

### Functional Requirements

**One-Time Completion Rewards:**

- **FR-001**: When a player completes a quest with a "play intrigue" reward, the system MUST prompt the player to select and play one intrigue card from their hand before the turn advances.
- **FR-002**: If the player has no intrigue cards when the "play intrigue" reward triggers, the step MUST be skipped automatically.
- **FR-003**: When a player completes a quest with an "opponent gains coins" reward in a 2-player game, the system MUST automatically grant the coins to the single opponent.
- **FR-004**: When a player completes a quest with an "opponent gains coins" reward in a 3+ player game, the system MUST prompt the completing player to choose which opponent receives the coins.

**Extra Worker:**

- **FR-005**: When a player completes "Hire a Tour Manager", the system MUST permanently increase their total worker count by 1.
- **FR-006**: The extra worker MUST become available at the start of the next round, not during the current round.

**Round-Start Resource:**

- **FR-007**: At the start of each round, the system MUST prompt each player who has completed "Soul Music Residency" to choose 1 non-coin resource (Guitarist, Bass Player, Drummer, or Singer).
- **FR-008**: The chosen resource MUST be granted, logged in the game log, and broadcast to all players. The round's first turn MUST NOT begin until all round-start resource choices are resolved.

**Worker Recall (One-Time on Completion):**

- **FR-009**: When a player completes "Time Warp Remix" and has at least one worker placed on the board, the system MUST prompt the player to select a space to recall a worker from.
- **FR-010**: Recalling a worker MUST free the action space (set it to unoccupied) and increment the player's available worker count.
- **FR-011**: If the player has no workers on the board when completing "Time Warp Remix", the recall step MUST be skipped automatically.
- **FR-012**: The recall prompt MUST display a message at the top of the screen and allow the player to click on a board space occupied by their own worker.

**Use Occupied Building:**

- **FR-013**: Once per round, a player who has completed "Recover the Master Tapes" MUST be able to place a worker on a building action space that is occupied by another player's worker.
- **FR-014**: The occupied building placement MUST grant the normal visitor reward and trigger the owner bonus.
- **FR-015**: This ability MUST only apply to building spaces, not standard board spaces.
- **FR-016**: This ability MUST NOT allow placing on a building occupied by the player's own worker.
- **FR-017**: The ability MUST reset at the start of each new round.

### Key Entities

- **Quest Card**: Existing entity with new fields for `reward_play_intrigue` and `reward_opponent_gains_coins`.
- **Player**: Existing entity; needs tracking for `use_occupied_used_this_round` flag, plus `total_workers` or `bonus_workers` count.
- **Round Start Phase**: Existing game phase where "Soul Music Residency" resource grants are applied.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 6 special quest mechanics function correctly in gameplay — completing each quest triggers its unique effect.
- **SC-002**: All 60 quest cards in the game are now fully playable with no placeholder or unimplemented mechanics.
- **SC-003**: The per-round ability (use-occupied) correctly resets each round and cannot be used more than once per round.
- **SC-004**: All special mechanics are visible in the game log so all players can see what happened.
- **SC-005**: Existing quest completion, intrigue play, and worker placement flows continue to work identically for cards without special mechanics.

## Assumptions

- The "play intrigue" reward from Jailhouse Jazz Session uses the existing intrigue card play flow (same as placing a worker on The Garage backstage), not a new simplified flow.
- The worker recall from "Time Warp Remix" does not reverse any rewards or effects that were granted when the worker was originally placed.
- The "use occupied building" ability allows dual occupation — both workers remain on the space until the round ends and workers are collected.
- The round-start resource choice from "Soul Music Residency" happens before any player takes their first turn of the round. All pending choices must be resolved before play begins.
- The extra worker from "Hire a Tour Manager" follows the same pattern as the existing round-5 bonus worker mechanic.
- The "opponent gains coins" reward value (4 coins) is read from card data, not hard-coded.
