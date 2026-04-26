# Feature Specification: Resource Trigger Plot Quests

**Feature Branch**: `018-resource-trigger-plots`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Look at 'specs/waterdeep-card-mapping.md'. Specify how to implement the 'Resource Trigger Plot Quests'"

## User Scenarios & Testing

### User Story 1 - Simple Resource Bonus Triggers (Priority: P1)

A player completes a plot quest that grants bonus resources whenever they gain a specific resource type through a board action. For the rest of the game, every time that player gains the trigger resource from placing a worker on an action space, they automatically receive the bonus resource(s) as well.

**Covers these cards:**
- **Rock Loyalty Program** (`on_gain_guitarist`): When you gain a Guitarist, +1 extra Guitarist
- **Fence Bootleg Recordings** (`on_gain_bass_coins`): When you gain a Bass Player, +2 Coins
- **Payola Pipeline** (`on_gain_coins_bass`): When you gain Coins, +1 Bass Player

**Why this priority**: These three cards share a straightforward pattern — gain resource X, automatically receive bonus Y. No player interaction is required. This is the simplest trigger type and establishes the core hook mechanism that all other triggers build upon.

**Independent Test**: Complete "Rock Loyalty Program", then place a worker on any space that grants at least 1 Guitarist. The player should receive their normal reward plus 1 extra Guitarist. The bonus resources appear in the player's resource bar immediately.

**Acceptance Scenarios**:

1. **Given** a player has completed "Rock Loyalty Program", **When** they place a worker on a space granting 2 Guitarists, **Then** they receive 3 Guitarists total (2 normal + 1 bonus).
2. **Given** a player has completed "Fence Bootleg Recordings", **When** they place a worker on a space granting 1 Bass Player, **Then** they receive 1 Bass Player + 2 Coins as a bonus.
3. **Given** a player has completed "Payola Pipeline", **When** they place a worker on a space granting 4 Coins, **Then** they receive 4 Coins + 1 Bass Player as a bonus.
4. **Given** a player has NOT completed any resource trigger plot quest, **When** they place a worker on any space, **Then** they receive only the normal reward with no bonus.
5. **Given** a player has completed "Rock Loyalty Program", **When** they gain a Guitarist from a quest completion reward (not a board action), **Then** no bonus is triggered. Triggers only fire from board action rewards.
6. **Given** a player has completed both "Rock Loyalty Program" and another plot quest that triggers on Guitarist gains (e.g., "Explore the Groove Archive"), **When** they gain a Guitarist from a board action, **Then** both bonuses trigger independently.

---

### User Story 2 - Intrigue Card Bonus Trigger (Priority: P2)

A player completes "Explore the Groove Archive" (`on_gain_guitarist_i`). For the rest of the game, whenever they gain a Guitarist from a board action, they also draw 1 Intrigue card from the intrigue deck.

**Why this priority**: This trigger grants a non-resource reward (an intrigue card draw), which is slightly more complex than pure resource bonuses but uses a draw mechanism that already exists in the game.

**Independent Test**: Complete "Explore the Groove Archive", then place a worker on a space granting Guitarists. The player should receive their Guitarists plus 1 Intrigue card added to their hand.

**Acceptance Scenarios**:

1. **Given** a player has completed "Explore the Groove Archive", **When** they place a worker on a space granting at least 1 Guitarist, **Then** they receive their normal reward plus 1 Intrigue card drawn from the intrigue deck.
2. **Given** the intrigue deck is empty, **When** the trigger fires, **Then** no intrigue card is drawn and the normal resource reward still applies without error.
3. **Given** a player has completed both "Rock Loyalty Program" and "Explore the Groove Archive", **When** they gain a Guitarist from a board action, **Then** they receive +1 extra Guitarist AND +1 Intrigue card.

---

### User Story 3 - Resource Swap Trigger (Priority: P3)

A player completes "Miracle at the Microphone" (`on_gain_singer_swap`). For the rest of the game, whenever they gain a Singer from a board action, they may trade any 1 owned non-Singer resource for 1 additional Singer.

**Why this priority**: This is the most complex trigger because it requires player interaction — the player must choose which resource to trade. It introduces an optional decision point that interrupts the normal flow.

**Independent Test**: Complete "Miracle at the Microphone", then place a worker on a space granting at least 1 Singer. A prompt should appear asking the player if they want to trade a resource for an extra Singer.

**Acceptance Scenarios**:

1. **Given** a player has completed "Miracle at the Microphone" and owns at least 1 non-Singer resource, **When** they place a worker on a space granting at least 1 Singer, **Then** they are prompted to optionally trade 1 owned non-Singer resource for 1 additional Singer.
2. **Given** the swap prompt appears, **When** the player selects a Guitarist to trade, **Then** they lose 1 Guitarist and gain 1 additional Singer beyond the normal reward.
3. **Given** the swap prompt appears, **When** the player declines the swap (skips/cancels), **Then** they receive only the normal reward and no resources are traded.
4. **Given** a player has completed "Miracle at the Microphone" but owns 0 non-Singer resources, **When** they gain a Singer from a board action, **Then** no swap prompt appears (the trigger is silently skipped).
5. **Given** a player gains a Singer from a quest completion reward, **When** the reward is applied, **Then** no swap prompt appears. Triggers only fire from board actions.

---

### Edge Cases

- What happens when multiple resource triggers fire from a single board action? All applicable triggers fire independently. For example, gaining Guitarists with both "Rock Loyalty Program" and "Explore the Groove Archive" completed grants +1 Guitarist AND +1 Intrigue card.
- What happens when a trigger bonus itself would trigger another trigger? Bonus resources from triggers do NOT chain — only the original board action reward is checked for triggers. For example, if "Payola Pipeline" (coins → +1 bass) fires and the player also has "Fence Bootleg Recordings" (bass → +2 coins), only the original trigger fires, not a cascade.
- What happens when a board action grants multiple resource types that each have triggers? Each trigger fires once based on the original reward. If a space grants both Guitarists and Coins, and the player has triggers for both, both fire independently.
- What happens during the reassignment phase when a worker is reassigned to a new space? The new space's reward is a board action, so triggers should fire normally.
- What if a player cancels placement on a building (returning their intrigue card)? The placement is reversed, so any trigger bonuses that were granted should also be reversed.
- What about owner bonuses from buildings — do they trigger resource triggers for the building owner? No. Owner bonuses are a separate system from the visitor reward. Only the placing player's board action reward triggers their plot quest bonuses.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST detect when a player gains resources from placing a worker on a board action space (including building spaces and reassignment).
- **FR-002**: The system MUST check the placing player's completed plot quests for any resource trigger that matches the gained resource type(s).
- **FR-003**: For simple bonus triggers (`on_gain_guitarist`, `on_gain_bass_coins`, `on_gain_coins_bass`), the system MUST automatically grant the bonus resources without player interaction.
- **FR-004**: For the intrigue draw trigger (`on_gain_guitarist_i`), the system MUST automatically draw 1 intrigue card and add it to the player's hand.
- **FR-005**: For the swap trigger (`on_gain_singer_swap`), the system MUST prompt the player with a choice to trade 1 non-Singer resource for 1 Singer, or skip.
- **FR-006**: Bonus resources from triggers MUST NOT cause further trigger cascading. Only the original board action reward is evaluated for triggers.
- **FR-007**: Triggers MUST only fire from board action rewards (worker placement and reassignment), NOT from quest completion rewards, intrigue card effects, or other non-board-action sources.
- **FR-008**: If multiple triggers match a single board action, all matching triggers MUST fire independently.
- **FR-009**: When a placement is cancelled (e.g., backstage intrigue cancel), any trigger bonuses already granted MUST be reversed.
- **FR-010**: The game log MUST record when a resource trigger fires, including the trigger source quest name, the bonus granted, and the player.
- **FR-011**: All connected players MUST see the trigger bonus reflected in the triggering player's resource counts in real time.
- **FR-012**: Each of the 5 resource trigger cards MUST have its trigger type and bonus configured in the card data, not hard-coded in game logic.

### Key Entities

- **ContractCard**: Gains new fields to define trigger type, trigger resource, and bonus outcome. Each resource trigger plot quest card carries its own trigger configuration.
- **Resource Trigger Event**: When a board action awards resources, triggers are evaluated. The event produces zero or more bonus grants based on the player's completed plot quests.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 5 resource trigger plot quest cards function correctly — completing them and then gaining the trigger resource produces the specified bonus every time.
- **SC-002**: Resource bonuses appear in the player's resource bar within the same turn feedback as the board action that triggered them, with no additional clicks required (except for the swap trigger, which requires one choice).
- **SC-003**: The swap trigger prompt responds within 1 action — player sees the choice, picks a resource or skips, and the game continues immediately.
- **SC-004**: No cascading occurs — placing a worker that fires a trigger never causes a second trigger to fire from the bonus, regardless of which triggers the player has completed.
- **SC-005**: Cancelling a placement fully reverses all trigger bonuses, leaving the player's resources exactly as they were before the cancelled placement.
- **SC-006**: All existing game functionality (worker placement, quest completion, intrigue play, building purchase) continues to work without regression.

## Assumptions

- Triggers only fire from "board actions" — defined as placing or reassigning a worker to an action space. Quest completion rewards, intrigue card effects, round-start bonuses, and building owner bonuses are NOT board actions for trigger purposes.
- The existing resource choice prompt system (used for building visitor rewards and intrigue effects) can be reused for the Singer swap trigger prompt.
- Trigger bonuses are granted immediately alongside the board action reward, before any subsequent prompts (e.g., quest completion prompt). The swap trigger prompt, if applicable, happens after the automatic triggers but before the quest completion prompt.
- A trigger fires if the board action reward includes at least 1 of the trigger resource, regardless of quantity. The bonus is always a fixed amount (not scaled by quantity gained).
- Building owner bonuses received by the building owner when another player visits do not trigger plot quest bonuses for the owner.
