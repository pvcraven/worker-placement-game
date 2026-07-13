# Research: Resource Distribution Buildings

**Date**: 2026-06-11

## Decision 1: How to Model the Distribution Mechanic on BuildingTile

**Decision**: Add three new fields to BuildingTile in `shared/card_models.py`:
- `distribute_resource_type: str | None` — which resource type to place (e.g., "guitarists", "coins")
- `distribute_per_space: int` — quantity per target space (e.g., 1 or 2)
- `distribute_space_count: int` — how many distinct target spaces to select (e.g., 1 or 2)

**Rationale**: Follows Constitution VII (Config-Driven) — the mechanic is expressed as new fields on the existing model, not new code branches per building ID. The three fields fully parameterize all five UN buildings:
- UN-1: type=guitarists, per_space=1, count=2
- UN-2: type=coins, per_space=2, count=2
- UN-3: type=singers, per_space=1, count=1
- UN-4: type=bass_players, per_space=1, count=2
- UN-5: type=drummers, per_space=1, count=1

**Alternatives considered**:
- Using `visitor_reward_special` with a string value: Rejected — the mechanic needs parameterization (type, count, spaces) that a simple string can't express.
- Creating a new `DistributionConfig` nested model: Rejected — three flat fields are simpler (Constitution V) and sufficient.

## Decision 2: How to Track Placed Resources on Action Spaces

**Decision**: Add a `placed_resources` field to ActionSpace in `server/models/game.py`:
- `placed_resources: dict[str, int] = {}` — maps resource type to quantity (e.g., `{"guitarists": 1, "coins": 2}`)

**Rationale**: This is a separate pool from `accumulated_stock` (which is a single int for a single type). Placed resources can be multi-type and come from multiple sources. A dict naturally supports stacking from separate placement phases.

**Alternatives considered**:
- Reusing `accumulated_stock`: Rejected — accumulation is a single-type int that resets differently. Placed resources are multi-type and cleared on visit, not replenished each round.
- List of placement events: Rejected — overkill; we only need to know what's on the space, not the history.

## Decision 3: Pending State for Distribution Selection

**Decision**: Add `pending_resource_distribution: dict | None` to GameState, following the existing pending pattern (Constitution VIII).

Fields: `player_id` (who is selecting), `building_space_id` (the building being visited, excluded from targets), `resource_type`, `per_space`, `remaining_selections` (how many spaces still need to be chosen), `selected_spaces` (list of space_ids already chosen).

**Rationale**: The owner needs to make 1-2 sequential selections. Storing selections in progress allows the server to validate each pick, enforce distinctness, and know when the phase is complete.

**Alternatives considered**:
- Single batch selection (client sends all at once): Rejected — harder to validate on client, inconsistent with existing one-at-a-time interaction patterns.

## Decision 4: Collection of Placed Resources

**Decision**: Check for `placed_resources` in the existing `handle_place_worker()` flow, right after accumulated stock collection. Grant all placed resources to the visitor and clear the dict.

**Rationale**: Minimal change to existing flow. Placed resources are collected at the same point as accumulated stock — during worker placement resolution.

## Decision 5: Visual Display of Placed Resources

**Decision**: Render placed resource icons dynamically in `board_renderer.py` below the worker token area. Use the same programmatic colored squares (36px) used in card generation, with count text beside each.

**Rationale**: No individual resource icon PNGs exist — the system uses programmatically drawn colored squares for all resource representations. Follow the same visual language. Display as dynamic overlay (not baked into card PNGs) since placed resources change during gameplay.

## Decision 6: Card Image Text for Distribution

**Decision**: Add a "Place:" line in the building card image (generated PNG) using the existing `_draw_reward_line()` pattern, with resource symbols and space count text.

**Rationale**: Consistent with existing card text layout. The static card shows what the building does; the dynamic board renderer shows current state.
