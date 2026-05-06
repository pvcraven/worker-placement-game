# Research: Intrigue Draw Building

## R1: Existing `draw_intrigue` handler pattern

**Decision**: Follow the existing pattern but draw 2 cards instead of 1, and add reward notification to the client.

**Rationale**: The `draw_intrigue` handler appears in 3 server locations (handle_place_worker ~line 1531, _resolve_copied_space_rewards ~line 1050, worker reassignment ~line 3484). Each pops 1 card from `state.board.intrigue_deck` and appends to `player.intrigue_hand`. The new `draw_intrigue_2` handler will do the same but in a loop of 2, respecting deck depletion. Unlike the current building `draw_intrigue` which silently adds the card, the new handler will include drawn cards in the reward dict (matching the castle pattern) so the client can update the local hand.

**Alternatives considered**:
- Reusing `draw_intrigue` with a count modifier: would require schema changes to BuildingTile
- Adding a generic `draw_intrigue_n` with parsing: over-engineering for a single building

## R2: Card image generation for two icons

**Decision**: Add a `draw_intrigue_2` case to `_draw_special_icon()` that draws two side-by-side intrigue card icons.

**Rationale**: The existing `_draw_special_icon()` function dispatches on the special string value. For `draw_intrigue`, it calls `_draw_intrigue_card_icon(draw, card_width // 2, cy)` to draw a single centered icon. For `draw_intrigue_2`, we draw two icons offset horizontally: one at `card_width // 2 - offset` and one at `card_width // 2 + offset`, where offset is roughly half the icon width + small gap.

**Alternatives considered**:
- Drawing one icon with a "x2" label: less visually clear
- Stacking icons vertically: takes too much vertical space

## R3: Client-side handling for multiple intrigue cards

**Decision**: Extend the existing `intrigue_cards_drawn` check in `_on_worker_placed()` to also handle `drawn_intrigue_cards` (plural, a list) for multi-card draws.

**Rationale**: The client already handles `reward.get("intrigue_cards_drawn")` and `reward.get("drawn_intrigue_card")` (singular) for castle draws. For the 2-card building, the server will send `drawn_intrigue_cards` (plural) as a list. The client handler extends both the count and hand, then logs "Player A drew 2 intrigue cards".

**Alternatives considered**:
- Sending two separate `drawn_intrigue_card` messages: not how the protocol works
- Reusing the singular field with just one card: loses the second card on the client
