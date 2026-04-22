# Research: Building Revamp

## R1: Accumulation State Storage

**Decision**: Add accumulation fields to `BuildingTile` model in `shared/card_models.py`.

**Rationale**: `BuildingTile` is already stored on `ActionSpace.building_tile` for constructed buildings and in `BoardState.face_up_buildings` for the market. Adding accumulation fields here keeps state co-located with the building definition and avoids a parallel tracking structure.

**Fields to add**:
- `accumulation_type: str | None = None` — resource key ("guitarists", "bass_players", etc.) or "victory_points"
- `accumulation_per_round: int = 0` — amount added each round
- `accumulation_initial: int = 0` — starting stock on purchase
- `accumulated_stock: int = 0` — current accumulated count (runtime, not in JSON config)

**Alternatives considered**:
- Separate `AccumulationState` dict on `BoardState` keyed by space_id — rejected because it would require cross-referencing and is more complex.
- Store on `ActionSpace` instead — rejected because `BuildingTile` already carries the building data and ActionSpace just wraps it.

## R2: VP in ResourceCost vs Separate Fields

**Decision**: Add `victory_points: int = 0` to `ResourceCost`.

**Rationale**: `ResourceCost` is used for `visitor_reward`, `owner_bonus`, and `cost` fields throughout the codebase. Adding VP here means `player.resources.add(space.reward)` automatically handles VP without special-casing. The `total()` method should NOT include VP (VP is not a spendable resource), so `total()` stays unchanged.

**Impact on existing code**:
- `ResourceCost.add()` will need to handle VP: `self.victory_points += other.victory_points` → but `add()` doesn't exist as a method on ResourceCost directly. Check: resources are added via `player.resources.add()` where `player.resources` is a separate `PlayerResources` model. Need to verify.
- Actually, `player.resources` is a `ResourceCost` used as mutable state. The `add()` method exists on it. Adding `victory_points` to ResourceCost means the add method picks it up automatically if add() iterates fields.
- VP awarded via `player.victory_points` (a separate int on PlayerState), NOT via `player.resources`. So VP in ResourceCost should be handled separately: when granting a reward that includes VP, add the VP to `player.victory_points` rather than to `player.resources`.

**Revised decision**: Keep VP separate from `ResourceCost`. Add `visitor_reward_vp: int = 0` and `owner_bonus_vp: int = 0` to `BuildingTile`. Handle VP grants explicitly in game_engine.py reward code.

**Rationale for revision**: ResourceCost represents spendable/collectible resources. VP is a score, not a resource. Mixing them would require special handling everywhere ResourceCost is used for affordability checks, cost deduction, etc.

## R3: Owner Bonus Choice Flow

**Decision**: Reuse existing `ResourceChoiceReward` model and `_send_resource_choice_prompt` function for owner bonus choices.

**Rationale**: The resource choice prompt/response infrastructure already handles pick, combo, exchange, and bundle types. Owner choice is always a simple "pick 1 from 2 types" which maps to `choice_type="pick"` with `pick_count=1` and `allowed_types` listing the two options.

**Flow**:
1. Visitor places worker → visitor gets fixed reward
2. Server detects `building_tile.owner_bonus_choice` is not None
3. Server sends `ResourceChoicePrompt` to building owner (not visitor)
4. Owner selects resource type
5. Server validates and grants the chosen resource to owner
6. Game continues (advance turn / check quest completion)

**Key difference from visitor choice**: The prompt targets a different player. The existing `_send_resource_choice_prompt` sends to `player` — need to pass the owner player instead. State tracking (`pending_resource_choice`) must track that this is an owner choice so the response handler knows which player to grant resources to.

## R4: visitor_reward_special for Buildings

**Decision**: Add processing for `visitor_reward_special` in `handle_place_worker` after granting the basic reward.

**Current state**: The field exists on 6 existing buildings but is never checked in game logic. Only `reward_special == "purchase_building"` is handled (for the Realtor space).

**Implementation**:
- After granting `space.reward` to visitor, check `space.building_tile.visitor_reward_special`:
  - `"draw_contract"`: Prompt player to pick one face-up quest card (reuse garage-style quest selection, but pick 1 from face-up instead of garage mechanism)
  - `"draw_intrigue"`: Draw top intrigue card from deck and add to player's hand

**Note**: `"draw_contract"` in the spec means "pick 1 face-up quest" which is functionally the same as the garage quest pick flow but limited to 1 card.

## R5: Building Card Image Generation

**Decision**: Update `card-generator/generate_cards.py` to generate PNGs for 20 new buildings, replacing the existing 28.

**Rationale**: The card generator already handles building cards. The 20 new buildings need new names assigned from the existing building name pool where appropriate, plus new names for buildings that don't map to existing ones.

**Name assignments** (to be finalized during implementation): Map existing music venue/studio names to the 20 new buildings based on thematic fit. Some existing names will be retired (28 → 20 means 8 names dropped).
