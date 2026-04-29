# Feature Specification: Zoarstar Building (Shadow Studio)

**Feature Branch**: `021-zoarstar-building`
**Created**: 2026-04-29
**Status**: Draft
**Input**: User description: "Add a building equivalent to Waterdeep's 'The Zoarstar'. When landing on it, a player selects a location that has another player's token (not their own, not empty) and uses that space's action as if they had a worker there."

## User Scenarios & Testing

### User Story 1 - Copy an Opponent's Occupied Space (Priority: P1)

A player places a worker on the Shadow Studio building. They are then presented with all action spaces currently occupied by other players (not by the visiting player themselves, and not empty spaces). The player selects one of those spaces and receives the rewards of that space as if they had placed a worker there. The player does not actually place a second worker — they only receive the space's action/reward.

**Why this priority**: This is the core mechanic of the building. Without it, the building has no purpose.

**Independent Test**: Can be fully tested by purchasing the building, having another player occupy a space, then visiting the Shadow Studio and selecting the occupied space. The visitor receives the copied space's rewards.

**Acceptance Scenarios**:

1. **Given** Shadow Studio is constructed and another player occupies "Motown" (2 bass players), **When** the visiting player places on Shadow Studio and selects "Motown", **Then** the visitor receives 2 bass players from the supply (the same reward as placing directly on Motown).
2. **Given** Shadow Studio is constructed and no other player occupies any space, **When** the visiting player places on Shadow Studio, **Then** the visitor receives only the building's base reward (if any) and is not prompted to select a space (there are no valid targets).
3. **Given** Shadow Studio is constructed, **When** the visiting player has a worker on "Guitar Center" and an opponent has a worker on "Motown", **Then** only "Motown" is shown as a selectable target (not the player's own occupied space).

---

### User Story 2 - Owner Bonus (Priority: P2)

When another player visits the Shadow Studio, the building's owner receives 2 victory points as their owner bonus.

**Why this priority**: Owner bonuses are standard for all buildings and must work correctly, but are secondary to the core copy mechanic.

**Independent Test**: Have a non-owner visit the Shadow Studio and verify the owner receives 2 VP.

**Acceptance Scenarios**:

1. **Given** Player A owns Shadow Studio and Player B visits it, **When** Player B completes their action, **Then** Player A gains 2 VP.
2. **Given** Player A owns Shadow Studio and Player A visits it, **Then** Player A does not receive the owner bonus (owners visiting their own building never trigger owner bonus).

---

### User Story 3 - Copying Special Spaces (Priority: P2)

The copy mechanic must correctly handle special action spaces beyond simple resource grants — including buildings with resource choices, buildings with accumulated stock, garage spaces (quest selection + coins/intrigue), and permanent spaces.

**Why this priority**: Tied with owner bonus. If copying only works for simple resource spaces, the building is severely limited.

**Independent Test**: Have an opponent occupy a building with a resource choice (e.g., "The Fillmore"), then visit Shadow Studio and select it. Verify the resource choice prompt appears for the visitor.

**Acceptance Scenarios**:

1. **Given** an opponent occupies a building with a resource choice reward, **When** the visitor copies that space via Shadow Studio, **Then** the visitor receives the resource choice prompt and resolves it normally.
2. **Given** an opponent occupies a building with accumulated stock (e.g., "Red Rocks"), **When** the visitor copies that space, **Then** the visitor collects the accumulated stock from that building (draining it as normal).
3. **Given** an opponent occupies a garage space (quest selection), **When** the visitor copies that garage space, **Then** the visitor goes through the quest selection flow as if they had placed directly on that garage space.
4. **Given** an opponent occupies the castle space (first player marker + intrigue), **When** the visitor copies it, **Then** the visitor gains the first player marker and draws an intrigue card.

---

### User Story 4 - Quest Completion After Copy (Priority: P3)

After resolving the copied space's action, the visitor should be prompted to complete a quest (if they can afford one), following the standard post-placement flow.

**Why this priority**: Standard post-action behavior, not specific to this building but must be verified.

**Independent Test**: Copy a space that grants resources sufficient to complete a quest. Verify the quest completion prompt appears.

**Acceptance Scenarios**:

1. **Given** the visitor copies a space and now has enough resources to complete a quest, **When** the copy resolves, **Then** the quest completion prompt appears.

---

### User Story 5 - Copy Occupied Space via Intrigue Card (Priority: P2)

Two copies of a new intrigue card allow a player to pay 2 coins and copy an opponent's occupied space — the same mechanic as the Shadow Studio building, but triggered via an intrigue card played from a backstage slot. The player must have at least 2 coins to play the card. If they cannot afford it or there are no valid targets, the system displays an error message and unwinds the backstage placement. The player can cancel the space selection at any point, which returns the 2 coins and unwinds the backstage placement.

**Why this priority**: Expands the copy mechanic to a second delivery mechanism (intrigue card), adding strategic variety. Tied with owner bonus and special spaces since it reuses the same core copy logic.

**Independent Test**: Give a player this intrigue card and 2+ coins. Have an opponent occupy a space. Player places on backstage, plays this card, pays 2 coins, selects the opponent's space, and receives that space's rewards.

**Acceptance Scenarios**:

1. **Given** a player has this intrigue card and 3 coins, and an opponent occupies "Motown" (2 bass players), **When** the player places on backstage and plays this card, **Then** 2 coins are deducted and the player is shown a list of opponent-occupied spaces. The player selects "Motown" and receives 2 bass players.
2. **Given** a player has this intrigue card but only 1 coin, **When** the player attempts to play this card from backstage, **Then** the system displays an error message ("You need 2 coins to play this card") and the backstage placement is unwound (worker returns, card stays in hand).
3. **Given** a player has this intrigue card and 2 coins, but no opponents have workers placed, **When** the player attempts to play this card, **Then** the system displays an error message ("No valid target spaces available") and the backstage placement is unwound.
4. **Given** a player has played the intrigue card and paid 2 coins, **When** the player cancels the space selection, **Then** the 2 coins are returned, the backstage placement is unwound (worker returns, card stays in hand), and no rewards are granted.
5. **Given** a player copies an opponent's building via this intrigue card, **When** the copied building is owned by another player (not the card player), **Then** the building owner receives their owner bonus (the copy counts as a visit, same as Shadow Studio).

---

### Edge Cases

- What happens if the only occupied spaces are occupied by the visiting player? The visitor is not prompted (no valid targets), and receives only the base building reward.
- What happens if the copied space is a building owned by someone? The copied building's owner receives their owner bonus from the copy action (the visitor is effectively "using" their building). This means a building owner can receive their bonus multiple times per round — once from a direct visit and again from a Shadow Studio copy (or a "Recover the Master Tapes" placement).
- What happens if the copied space triggers a resource trigger plot quest (e.g., the visitor has "Payola Pipeline" and the copied space grants coins)? Resource triggers should fire normally on the gained resources.
- What happens if the visitor cancels the space selection? The placement is unwound — the worker returns, and the Shadow Studio is freed, following the standard cancel/unwind pattern.
- Can the visitor copy the Realtor space to purchase a building? Yes — the visitor goes through the building purchase flow as if they had placed on the Realtor.
- Can the visitor copy a backstage slot? No — backstage slots require playing an intrigue card as part of placement, which is a fundamentally different action. Only regular action spaces (permanent, building, garage, castle, realtor) are valid copy targets.
- What happens if the intrigue card player copies a space that triggers a deferred action (resource choice, quest selection)? The deferred flow runs exactly as it would for a Shadow Studio copy — the player goes through the prompt and can cancel, which unwinds everything including the 2-coin cost.
- What happens if a player has only this intrigue card in hand, places on backstage, and can't afford 2 coins? The backstage placement unwinds entirely — worker returns, card stays in hand.
- Can the intrigue card copy the Shadow Studio building itself (if occupied by an opponent)? Yes — the copy mechanic works on any valid occupied space, including Shadow Studio. The intrigue card player would then go through Shadow Studio's copy flow (selecting a second target).

## Clarifications

### Session 2026-04-29

- Q: Is there an existing intrigue card with a similar "use occupied space" mechanic to reuse? → A: No intrigue card exists. The closest existing mechanic is the "Recover the Master Tapes" quest (contract_funk_005), which grants `reward_use_occupied_building` — allowing a player to place on an opponent's occupied building. The Shadow Studio mechanic is different (one-time copy per visit, no second worker placed), but the server's reward-granting logic from `handle_reassign_worker` (which already handles all space types including specials, accumulated stock, resource choices, and owner bonuses) is the primary code reuse target for resolving the copied space's action.
- Q: Can the copied building's owner bonus trigger multiple times per round (once from a direct visit and once from a Shadow Studio copy)? → A: Yes.
- Q: What should the "copy occupied space" intrigue card be named? → A: "Bootleg Recording" — an unauthorized copy of another label's session. If Player A visits Building B normally and Player C copies Building B via Shadow Studio, the owner of Building B receives their owner bonus twice — once from each visit. There is no per-round cap on owner bonus triggers. The same applies if the "Recover the Master Tapes" quest is used to place on an occupied building — the building owner still receives their owner bonus from that visit.

## Requirements

### Functional Requirements

- **FR-001**: The building MUST cost 8 coins to purchase (matching its Waterdeep equivalent as the most expensive building).
- **FR-002**: When a player visits the Shadow Studio, the system MUST present a list of all action spaces currently occupied by other players' workers.
- **FR-003**: The list MUST exclude spaces occupied by the visiting player's own workers.
- **FR-004**: The list MUST exclude empty (unoccupied) spaces.
- **FR-005**: The list MUST exclude backstage slots.
- **FR-006**: When the player selects a target space, the system MUST grant the same rewards as if the player had placed a worker on that space directly — including resource rewards, special rewards, accumulated stock, resource choices, and quest/contract draws.
- **FR-007**: The visiting player MUST NOT actually place a second worker on the copied space. The original occupant's worker remains undisturbed.
- **FR-008**: If the copied space is a building owned by another player, that building's owner MUST receive their owner bonus (the copy counts as a visit). There is no per-round cap on owner bonus triggers — a building owner can receive their bonus multiple times in the same round from different sources (direct visits, Shadow Studio copies, and "Recover the Master Tapes" quest placements).
- **FR-009**: The Shadow Studio's owner MUST receive 2 VP when another player visits.
- **FR-010**: If no valid target spaces exist (no opponents have workers placed), the visitor MUST receive only the base building reward and the turn proceeds normally.
- **FR-011**: The player MUST be able to cancel the space selection, unwinding the placement using the standard cancel pattern.
- **FR-012**: After the copied space's action resolves, the standard post-action flow MUST apply (quest completion check, turn advance).
- **FR-013**: Two copies of a "copy occupied space" intrigue card MUST exist in the intrigue deck.
- **FR-014**: Playing the intrigue card MUST cost 2 coins, deducted when the card is played (before target selection).
- **FR-015**: If the player cannot afford 2 coins when attempting to play the card, the system MUST display an error message and unwind the backstage placement (worker returns, card stays in hand).
- **FR-016**: If no valid target spaces exist when the card is played, the system MUST display an error message and unwind the backstage placement without deducting coins.
- **FR-017**: Valid target spaces for the intrigue card MUST follow the same rules as the Shadow Studio building (FR-002 through FR-005): opponent-occupied spaces only, excluding the card player's own spaces, empty spaces, and backstage slots.
- **FR-018**: If the player cancels the space selection after coins are deducted, the 2 coins MUST be returned and the backstage placement MUST be fully unwound.
- **FR-019**: If the copied space is a building owned by another player, that building's owner MUST receive their owner bonus (same cascading rule as FR-008).

### Key Entities

- **Shadow Studio Building Tile**: A new building tile (id: building_023) with cost 8, a special visitor reward ("copy_occupied_space"), and owner bonus of 2 VP.
- **Bootleg Recording Intrigue Card**: Two copies of a new intrigue card named "Bootleg Recording" (ids: intrigue_053, intrigue_054) with `effect_type: "copy_occupied_space"`, `effect_value: {"cost_coins": 2}`, and `effect_target: "self"`.
- **Occupied Space Selection**: A player-facing prompt listing all valid target spaces, similar to existing space-selection prompts in the game. Shared by both the Shadow Studio building and the intrigue card.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Players can purchase the Shadow Studio for 8 coins via the Realtor, and it appears on the board as a constructed building.
- **SC-002**: Visitors to Shadow Studio see a list of all opponent-occupied spaces and can select one to copy its action within 2 clicks.
- **SC-003**: 100% of existing action space types (permanent, building, garage, castle, realtor) can be copied without errors when occupied by an opponent.
- **SC-004**: The building owner receives 2 VP every time another player visits, visible in the game log and player score.
- **SC-005**: Cancelling the space selection cleanly unwinds the placement with no lingering state.
- **SC-006**: Players can play the copy intrigue card from backstage, pay 2 coins, and copy an opponent-occupied space identically to the Shadow Studio building mechanic.
- **SC-007**: Attempting to play the intrigue card without 2 coins displays an error and unwinds the backstage placement cleanly.
- **SC-008**: Cancelling the intrigue card's space selection returns the 2 coins and unwinds the backstage placement with no lingering state.

## Assumptions

- The building will be named "Shadow Studio" as a music-industry-themed equivalent of "The Zoarstar" (a shadowy, versatile studio that mirrors any other studio's capabilities).
- The building uses `visitor_reward_special: "copy_occupied_space"` as the config-driven mechanic identifier, following the existing pattern for special building actions.
- Backstage slots are excluded from valid copy targets because they require intrigue card play as part of placement — a fundamentally different interaction that cannot be "copied."
- The building does not grant any base resource reward — its entire value is the copy mechanic.
- When copying a space that triggers an interactive prompt (resource choice, quest selection, building purchase), the visitor goes through that prompt flow exactly as if they had placed directly on the space.
- The reward-granting logic from `handle_reassign_worker` (which already resolves all action space types — permanent, building, garage, castle, realtor — including accumulated stock, resource choices, and owner bonuses) is the primary code reuse target for implementing the copy mechanic.
- The intrigue card is named "Bootleg Recording" — an unauthorized recording session that copies another label's work. Two copies exist in the deck (intrigue_053, intrigue_054).
- The intrigue card uses `effect_type: "copy_occupied_space"` as the config-driven mechanic identifier, following the existing pattern for intrigue card effect types.
- The intrigue card's description should be music-themed, e.g., "Slip into a rival's studio and bootleg their session. Pay 2 coins to copy any opponent's occupied space."
