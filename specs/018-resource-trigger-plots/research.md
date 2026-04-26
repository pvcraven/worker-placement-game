# Research: Resource Trigger Plot Quests

## Decision 1: Where to hook resource triggers

**Decision**: Hook after `player.resources.add(space.reward)` in `handle_place_worker()` (line 817) and `handle_reassign_worker()` (line 2281). Also after accumulating building stock grants (lines 828-833, 2293-2300).

**Rationale**: These are the only places where a player receives resources from an active board action (placing or reassigning a worker). All other resource grants (quest rewards, intrigue effects, owner bonuses) are explicitly excluded per the spec.

**Alternatives considered**:
- Wrapping `player.resources.add()` globally — rejected because it would fire on non-board-action grants too (intrigue effects, quest rewards, owner bonuses).
- Adding a flag parameter to `resources.add()` — rejected as overly invasive; the hook points are few and well-defined.

## Decision 2: Data model for triggers

**Decision**: Add four fields to `ContractCard`:
- `resource_trigger_type: str | None` — which resource type activates this trigger (e.g., "guitarists")
- `resource_trigger_bonus: ResourceCost` — automatic bonus resources granted
- `resource_trigger_draw_intrigue: int` — intrigue cards to draw as bonus
- `resource_trigger_is_swap: bool` — whether this is the interactive Singer swap

**Rationale**: Follows the existing pattern of data-driven fields on ContractCard (like `bonus_vp_per_genre_quest`). Each trigger card defines its own behavior through data, not hard-coded logic. A single helper function checks `player.completed_contracts` for any matching `resource_trigger_type`.

**Alternatives considered**:
- A separate `ResourceTrigger` model — rejected per Simplicity First principle; the fields are few and belong naturally on ContractCard.
- A generic `effect_type` + `effect_value` dict — rejected because the existing pattern uses typed fields, and dicts violate the Pydantic constitution principle.

## Decision 3: Trigger evaluation function

**Decision**: Create a helper function `_evaluate_resource_triggers(state, player, reward)` that:
1. Inspects the `reward` ResourceCost for which resource types are > 0
2. Scans `player.completed_contracts` for matching `resource_trigger_type`
3. Returns a list of trigger results (bonus resources, intrigue draws, swap prompts)
4. Applies all automatic bonuses immediately
5. Returns any pending interactive prompt (Singer swap) for deferred handling

**Rationale**: Centralizes trigger logic in one place, called from both `handle_place_worker()` and `handle_reassign_worker()`. Keeps the pattern consistent with how plot quest VP bonuses are calculated.

## Decision 4: Singer swap prompt

**Decision**: Reuse the existing `ResourceChoicePromptResponse` with `choice_type = "exchange"` and `is_spend = True`.

**Rationale**: The resource choice system already handles prompting a player to select resources, resolving the choice, and continuing the game flow. The swap is "spend 1 of any non-Singer resource to gain 1 Singer" — this maps directly to the exchange pattern. No new message types needed.

**Alternatives considered**:
- New `SingerSwapPromptResponse` — rejected because the existing system handles this case and introducing a new message type adds unnecessary complexity.

## Decision 5: No-cascade rule

**Decision**: Trigger evaluation only checks the original board action reward (`space.reward`), not any bonus resources from triggers. The helper function is called once with the original reward and never re-invoked with trigger outputs.

**Rationale**: Cascading triggers would create infinite loops (coins→bass→coins→bass...) and confusing game states. The original Waterdeep board game does not cascade triggers either.

## Decision 6: Cancellation handling

**Decision**: Store trigger bonus details in the existing pending state dicts. On cancel, reverse the bonus resources. For the Singer swap, if the player hasn't resolved it yet, simply clear the pending prompt. If already resolved, reverse the swap (return the spent resource, remove the gained Singer).

**Rationale**: Follows the established pattern used for `plot_bonus_vp` in `handle_cancel_intrigue_target()`.

## Decision 7: Message field additions

**Decision**: Add `trigger_bonuses: list[dict]` to `WorkerPlacedResponse` and `WorkerReassignedResponse`. Each entry contains: `quest_name`, `bonus_resources` dict, `intrigue_drawn` count. The client uses this to update resources and display log entries.

**Rationale**: Keeps the server-authoritative pattern — server calculates bonuses, broadcasts them, client applies.
