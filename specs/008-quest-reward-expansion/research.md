# Research: Quest Reward Expansion

## Decision 1: Reward Model Design

**Decision**: Extend `ContractCard` with new optional fields rather than creating a separate reward model.

**Rationale**: Adding fields directly to `ContractCard` keeps backward compatibility — all existing quests work unchanged since new fields default to 0/None. A separate reward model would add indirection without clear benefit for this scope.

**Alternatives considered**:
- Separate `QuestReward` model: More flexible but adds a layer of nesting. Existing `bonus_resources` and `victory_points` would need migration or duplication.
- Dict-based rewards (like IntrigueCard's `effect_value`): Too unstructured; Pydantic validation is preferred for quest data.

## Decision 2: Interactive vs Non-Interactive Rewards

**Decision**: Use a pending-state pattern (like `pending_intrigue_target`) for "choose" rewards. Non-interactive rewards resolve immediately.

**Rationale**: The codebase already has the `pending_intrigue_target` pattern for pausing game flow and prompting the player. Reusing this pattern for "choose quest from face-up" and "choose building from market" is consistent and proven.

**Alternatives considered**:
- Resolve all rewards immediately (force random for all): Simpler but removes the "choose" modes the user requested.
- Queue all rewards: Overcomplicated for rewards that don't need player input.

## Decision 3: Card Draw Data Format

**Decision**: Send full card data (`model_dump()`) in reward messages for drawn cards, not just IDs.

**Rationale**: The client needs full card data to display drawn cards in the player's hand. This is already the approach used for `draw_intrigue` and `draw_contracts` intrigue effects (fixed in a recent session).

**Alternatives considered**:
- Send IDs only, then request full state sync: Extra round trip, unnecessary.

## Decision 4: Building Grant Flow

**Decision**: Two modes per quest card — "market_choice" (player picks from face-up) and "random_draw" (auto-assign from deck). Building acquisition reuses the existing building placement logic (lot assignment, market refill).

**Rationale**: User explicitly requested both modes. The existing `handle_purchase_building` logic handles lot assignment and market refill — extract reusable parts rather than duplicating.

**Alternatives considered**:
- Always player-choice: User explicitly said random draw is a separate mode.
- Skip lot assignment for free buildings: Buildings need action spaces to function in gameplay.

## Decision 5: Quest Card Draw Modes

**Decision**: Two modes per quest card — "random" (draw from quest deck top) and "choose" (player picks from face-up quests).

**Rationale**: User explicitly requested both. Random uses existing `_draw_from_quest_deck`. Choose reuses face-up quest selection UI.

**Alternatives considered**:
- Random only: User explicitly requested choose mode.

## Decision 6: Intrigue Card Unification Scope

**Decision**: Intrigue cards already have `draw_intrigue` and `draw_contracts` effect types that work. US3 scope is limited to ensuring the underlying draw functions are shared with quest rewards, not restructuring intrigue cards.

**Rationale**: Intrigue cards use a flexible `effect_type` + `effect_value` dict pattern that already supports multiple effect types. No structural changes needed — just ensure quest rewards call the same draw functions.

**Alternatives considered**:
- Full intrigue card restructure to use the same reward model as quests: Massive scope creep with no user-facing benefit.
