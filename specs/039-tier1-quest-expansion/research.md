# Research: Tier 1 Quest Card Expansion

**Date**: 2026-06-02

## Summary

No technical unknowns. All 15 new cards use existing `ContractCard` Pydantic model fields (id, name, description, genre, cost, victory_points, bonus_resources, is_plot_quest). No new code paths, server handlers, or message types needed.

## Decisions

### Card Data Structure
- **Decision**: Use existing ContractCard fields only — no new Pydantic fields.
- **Rationale**: All 15 cards are simple cost→VP+bonus, which is fully supported by the current model.
- **Alternatives considered**: Adding a "mega_quest" boolean field — rejected because nothing in the game logic needs to distinguish mega quests from normal quests. They're just high-cost, high-VP cards.

### "Defend the Lanceboard Room" Deferral
- **Decision**: Defer this card (would be "Grand Jazz Caper") to a future feature.
- **Rationale**: It rewards 8 resources of the player's choice ("any" resource), which requires a one-time resource-choice reward mechanic not yet implemented. The existing `reward_choose_resource_per_round` is a different ongoing mechanic.
- **Alternatives considered**: Simplifying the reward to specific resources (4 bass + 4 coins) — rejected by the user in favor of implementing the original mechanic properly later.

### Unequal Genre Distribution
- **Decision**: Accept uneven card counts (Pop 16, Rock 15, Soul 15, Funk 14, Jazz 15) and update the equality test.
- **Rationale**: The original source material has uneven distribution across quest types in expansion content. Forcing equal counts would mean inventing cards not in the reference or deferring cards unnecessarily.
- **Alternatives considered**: Adding filler cards to equalize — rejected as it introduces untested balance and doesn't match the reference material.
