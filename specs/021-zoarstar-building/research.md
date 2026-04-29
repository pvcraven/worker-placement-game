# Research: Shadow Studio + Bootleg Recording

**Date**: 2026-04-29

## R1: Reward-Granting Code Reuse Strategy

**Decision**: Extract a shared `_resolve_copied_space_rewards()` function that mirrors the reward-granting logic from `handle_reassign_worker` (lines 2997-3112) rather than calling `handle_place_worker` or `handle_reassign_worker` directly.

**Rationale**: Both `handle_place_worker` and `handle_reassign_worker` contain reward-granting logic interleaved with placement-specific concerns (worker movement, slot validation, phase checks). A focused helper that takes a target space and grants its rewards to a player is cleaner and avoids coupling to either function's lifecycle.

**Alternatives considered**:
- Calling `handle_reassign_worker` with a fake reassignment message — rejected because reassignment has phase guards and queue validation that don't apply here.
- Refactoring `handle_place_worker` to extract reward granting into a shared helper — too invasive for this feature; the existing function works correctly and changing it risks regressions across all placement paths.

## R2: Intrigue Card Coin Cost Validation Timing

**Decision**: Validate coin affordability inside `_resolve_intrigue_effect()` and return a flag (`insufficient_coins: True`) so `handle_place_worker_backstage` can unwind before any state is committed.

**Rationale**: The current `_resolve_intrigue_effect` function always succeeds — effects are applied inline. The Bootleg Recording card introduces a prerequisite (2 coins). Checking in the effect resolver keeps the validation close to the card definition, and the caller handles the unwind if the check fails.

**Alternatives considered**:
- Pre-validating in `handle_place_worker_backstage` before calling `_resolve_intrigue_effect` — rejected because the cost is defined in the card's `effect_value`, which is the resolver's responsibility to interpret.
- Deducting coins optimistically and reversing on failure — rejected as unnecessarily complex.

## R3: Pending State Structure for Copy Selection

**Decision**: Add `pending_copy_source: dict | None` to GameState alongside the existing `pending_placement`. The copy source dict stores `player_id`, `source_space_id`, `source_type` ("building" or "intrigue"), `cost_deducted` (intrigue path only), and `eligible_spaces`.

**Rationale**: The copy mechanic needs its own pending field because the selection is a distinct interaction step. `pending_placement` tracks the physical placement (Shadow Studio or backstage slot) for cancel/unwind, while `pending_copy_source` tracks the copy-specific selection state.

**Alternatives considered**:
- Overloading `pending_intrigue_target` — rejected because that field expects `target_player_id` (a player) not `target_space_id` (a space), and the handler logic is different.
- Using only `pending_placement` with extra fields — rejected because it conflates placement state with selection state and complicates the cancel handlers.

## R4: Owner Bonus Cascading for Copied Buildings

**Decision**: When a player copies a building space via Shadow Studio or Bootleg Recording, the copied building's owner receives their owner bonus (if the copying player is not the owner). This is implemented inside `_resolve_copied_space_rewards()` using the same owner bonus logic as `handle_place_worker` lines 1252-1286.

**Rationale**: Per the spec (FR-008, FR-019), the copy counts as a "visit" to the copied building. There is no per-round cap on owner bonuses — an owner can receive multiple bonuses from different sources.

**Alternatives considered**: None — the spec is explicit about this behavior.

## R5: Nested Copy (Copying Shadow Studio via Bootleg Recording)

**Decision**: If a player uses Bootleg Recording to copy Shadow Studio (which is occupied by an opponent), the player enters the Shadow Studio's copy flow — selecting a second target space. This is handled naturally because `_resolve_copied_space_rewards()` processes the target space's `visitor_reward_special`, and `copy_occupied_space` triggers the same selection prompt.

**Rationale**: The spec edge case confirms this is valid. The implementation is recursive in the UI sense (two sequential selection prompts) but not in the code sense — each selection is a separate pending state cycle.

**Alternatives considered**: Blocking nested copies — rejected because the spec explicitly allows it and it adds strategic depth.
