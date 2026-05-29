# Research: The Green Room — Intrigue Quest Space

## R1: How to handle the two-step flow (play intrigue then select quest)

**Decision**: Reuse the existing `pending_play_intrigue` state and `handle_play_intrigue_from_quest` handler pattern for the intrigue play step, then chain into the existing garage-style quest selection flow via `pending_placement`.

**Rationale**: The `pending_play_intrigue` pattern already exists (spec 019) and wraps `_resolve_intrigue_effect()` cleanly. The quest selection flow is already implemented for garage spaces via `handle_select_quest_card()`. The Green Room chains these two existing flows: first the intrigue play prompt, then the quest selection prompt. The `pending_play_intrigue` dict can carry a `"source": "green_room"` field to distinguish from quest-completion play, so the post-resolution handler knows to transition to quest selection rather than advancing the turn.

**Alternatives considered**:
- Combining into a single new handler — rejected because it would duplicate intrigue resolution logic already in `_resolve_intrigue_effect()` and quest selection logic in `handle_select_quest_card()`.
- Using the backstage placement flow — rejected because backstage requires the intrigue card ID in the initial placement request, whereas The Green Room should place the worker first, then prompt for intrigue card selection separately.

## R2: What space_type and reward_special should The Green Room use?

**Decision**: Use `space_type: "permanent"` with `reward_special: "play_intrigue_and_quest"`. This follows the existing pattern where `reward_special` drives the space's special behavior (e.g., `"quest_and_coins"`, `"quest_and_intrigue"`, `"draw_intrigue_2"`).

**Rationale**: Constitution Principle VII (Config-Driven Game Content) requires new abilities to be expressed as model field values, not hard-coded IDs. The `reward_special` field already serves as the branching mechanism for special space behaviors. Adding a new value follows the established pattern.

**Alternatives considered**:
- New space_type (e.g., `"green_room"`) — rejected because it would require routing changes in `handle_place_worker()` and doesn't match how other permanent spaces differentiate behavior.
- Using `space_type: "garage"` — rejected because The Green Room's primary action is playing an intrigue card, not just selecting a quest.

## R3: How to handle cancel/back-out

**Decision**: Allow cancel before intrigue card play only. Once the intrigue card is played and its effect resolves, the player is committed and must select a quest. Cancel at the intrigue-selection stage uses `_unwind_placement()` to reverse the worker placement.

**Rationale**: This matches backstage behavior — once you play an intrigue card, its effect is applied and cannot be reversed (resources gained/stolen, cards drawn, etc.). The clean cancel point is before committing the intrigue card. The existing `_unwind_placement()` function handles all the reversal logic.

**Alternatives considered**:
- Allow cancel after intrigue play but before quest selection — rejected because intrigue effects (steal resources, draw cards, etc.) have already mutated game state for other players and cannot be cleanly reversed.

## R4: Board layout rearrangement (3x3 grid for permanent spaces)

**Decision**: Rearrange the 9 permanent spaces (8 existing + The Green Room) into a 3x3 grid occupying columns 0-2, rows 0-2 in the board grid. Constructed buildings move to columns 0-2, rows 3+ with existing pagination. All other spaces (garage, backstage, realtor) keep their current relative positions but may shift to accommodate.

**Rationale**: The current layout has 8 permanent spaces stacked vertically in column 0 (rows 0-7) and constructed buildings in columns 1-2. With 9 spaces, a 3x3 grid is more compact and leaves room for buildings below. The grid system already supports integer column/row coordinates.

**Alternatives considered**:
- Keeping column 0 layout and adding the 9th space elsewhere — rejected because the user specifically requested rearranging into a 3x3 grid.

## R5: Card image generation for The Green Room

**Decision**: Add a new case in `generate_space_cards()` for `reward_special == "play_intrigue_and_quest"`. Display "Play" text followed by the intrigue card icon, plus a quest card icon. Use the same blue band color and layout style as "The Back Room."

**Rationale**: The card generator already handles each `reward_special` value with specific icon layouts. "The Back Room" displays quest + intrigue icons; The Green Room will display "Play" + intrigue icon + quest icon to visually distinguish playing vs. drawing.

**Alternatives considered**:
- Reusing "The Back Room" image — rejected because it doesn't communicate the "play" requirement.
