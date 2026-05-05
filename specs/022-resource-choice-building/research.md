# Research: Resource Choice Board Space

## Decision 1: Permanent space reward_choice support

**Decision**: Add `reward_choice` field to `ActionSpaceConfig` and `ActionSpace` models.

**Rationale**: Currently only buildings (via `building_tile.visitor_reward_choice`) support resource choices. Permanent spaces need this capability for The Jam Session. Adding a `reward_choice` field directly on the action space is the cleanest approach — it follows Constitution VII (config-driven) and avoids introducing a fake "building_tile" on a permanent space.

**Alternatives considered**:
- Using `reward_special` with a new handler: Would require hard-coding the specific bundles in server code, violating Constitution VII.
- Wrapping the permanent space in a BuildingTile: Semantically wrong — permanent spaces don't have owners, costs, or accumulated stock.

## Decision 2: Server handler placement

**Decision**: Add the `reward_choice` check in `handle_place_worker` right after the existing building `visitor_reward_choice` block (since permanent spaces won't match `space.building_tile`). Also add equivalent handling in `_resolve_copied_space_rewards` (copy flow) and `handle_reassign_worker`.

**Rationale**: The existing flow already handles resource choice prompts. Adding a parallel check for `space.reward_choice` (without building_tile) keeps the code path minimal.

## Decision 3: Board layout ordering

**Decision**: The order of entries in `board.json`'s `permanent_spaces` array determines visual layout order. Insert The Jam Session between `rhythm_pit` and `fastpass`.

**Rationale**: The board renderer iterates `permanent_spaces` in order to position them. Confirmed by reading `BoardRenderer` code.
