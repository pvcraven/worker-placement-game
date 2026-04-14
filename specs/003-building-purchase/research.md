# Research: Building Purchase System

**Date**: 2026-04-14 | **Branch**: `003-building-purchase`

## R1: Building Market Model — Deck vs. Flat Supply

**Decision**: Replace the flat `building_supply` list with a `building_deck` (hidden) + `face_up_buildings` (3 visible) model.

**Rationale**: The spec requires exactly 3 face-up buildings at any time, with replacement draws from a shuffled deck. The current implementation puts all 24 buildings in `building_supply` as a flat list shown to the purchasing player. Splitting into deck + face-up matches the card-game paradigm already used for quests (`quest_deck` + `face_up_quests`).

**Alternatives considered**:
- Keep flat `building_supply` and slice first 3 in the UI — rejected because VP accumulation needs to track which specific buildings are face-up vs. in the deck
- Add an `is_face_up` boolean to BuildingTile — rejected because it conflates display state with the model and doesn't cleanly handle VP tracking

## R2: VP Accumulation Tracking

**Decision**: Add an `accumulated_vp` field to each face-up building entry tracked on the server's `BoardState`. Use a wrapper or directly add the field to `BuildingTile`.

**Rationale**: VP is a runtime property (starts at 1, increments per round) not a static config property. It should not be in buildings.json. Options:
1. Add `accumulated_vp: int = 0` to `BuildingTile` model — simple, but mixes config data with runtime state
2. Create a `FaceUpBuilding` wrapper with `tile: BuildingTile` + `accumulated_vp: int` — cleaner separation

**Decision**: Use option 1 (add field to `BuildingTile`) for simplicity. The field defaults to 0 in JSON config and gets set to 1 when the building enters the face-up market. This matches the existing pattern where `BuildingTile` is already used in runtime contexts (stored in `ActionSpace.building_tile`).

**Alternatives considered**:
- Wrapper model `FaceUpBuilding` — rejected because it would require changing every reference to building tiles in the face-up context and adds a layer of indirection for one field

## R3: Board Layout — Single Column Positioning

**Decision**: Rearrange `_SPACE_LAYOUT` to place all 7 permanent spaces + Real Estate Listings in a single column at x=0.08 with y positions from 0.88 down to 0.12, spaced at ~0.10 increments.

**Rationale**: Currently 6 permanent spaces are in 2 columns (x=0.08 and x=0.22) with 3 spaces each at y=0.3, 0.5, 0.7. Moving to a single column at x=0.08 frees the x=0.22 area for purchased buildings. With 8 spaces (7 permanent + Real Estate Listings, excluding garages and backstage which have their own layout rows), spacing of ~0.10 between centers keeps them readable within the 0.12–0.88 y range.

**Alternatives considered**:
- Two tighter columns — rejected because the spec explicitly requests one column
- Moving garages into the column — rejected because garages have their own bottom-row layout that works well visually

## R4: Purchased Building Placement — Second Column

**Decision**: Purchased buildings render in a column starting at x=0.22 (the freed second column position), with the same y-spacing as the permanent spaces column. Overflow goes to x=0.36, etc.

**Rationale**: This places purchased buildings directly adjacent to permanent spaces, making the board read left-to-right: permanent spaces → purchased buildings → garages/backstage. The current implementation starts buildings at x=0.70 which is too far right.

**Alternatives considered**:
- Keep buildings at x=0.70 — rejected because the spec says buildings go "in the second column space that was freed up"

## R5: Rename Builder's Hall → Real Estate Listings

**Decision**: Rename in all locations:
- `config/board.json`: `space_id` from `"builders_hall"` to `"real_estate_listings"`, name from `"Builder's Hall"` to `"Real Estate Listings"`, space_type from `"builders_hall"` to `"real_estate_listings"`
- `client/ui/board_renderer.py`: `_SPACE_LAYOUT` key from `"builders_hall"` to `"real_estate_listings"`
- `server/game_engine.py`: Any references to `"builders_hall"` space_id or space_type
- `shared/messages.py`: Any hardcoded references

**Rationale**: Spec FR-024 requires this rename across all display names, configuration, and code references.

**Alternatives considered**: None — direct user requirement.

## R6: Purchase Dialog Design

**Decision**: Create a `BuildingPurchaseDialog` in `client/ui/dialogs.py` following the pattern of the existing `CardSelectionDialog`. Show up to 3 building cards with name, cost, VP, visitor reward, and owner bonus. Highlight affordable buildings, gray out unaffordable ones. Include confirm and cancel buttons.

**Rationale**: The existing `CardSelectionDialog` provides a proven pattern for modal selection dialogs. The building purchase dialog needs similar functionality but with building-specific information (cost, VP, rewards) rather than contract card details.

**Alternatives considered**:
- Reuse `CardSelectionDialog` with adapted rendering — rejected because building cards need substantially different information layout (cost + VP + two reward lines vs. contract card layout)

## R7: Server Message Flow for Building Market

**Decision**: Add new message types:
- `BuildingMarketUpdate` (server→client): Sends the current face-up buildings list whenever it changes (game start, after purchase, after round-end VP increment)
- Modify `BuildingConstructedResponse` to include the replacement building (if drawn) and updated market state

**Rationale**: The client needs to know the current face-up buildings to render the market and purchase dialog. Currently `building_supply` is sent as part of the full state sync, but the new deck/market split requires explicit market updates.

**Alternatives considered**:
- Only send market state in full state sync — rejected because the client needs immediate updates after purchases and round-end VP changes without waiting for a full sync

## R8: Round-End VP Increment

**Decision**: Add VP increment logic to the existing `_end_round` method in `game_engine.py`. After returning workers and advancing the round counter, iterate over `face_up_buildings` and increment each building's `accumulated_vp` by 1.

**Rationale**: The spec requires +1 VP per round on each face-up building. The `_end_round` method already handles all round-transition logic, so this is the natural place.

**Alternatives considered**:
- Increment at round start — rejected because the spec says "after each round" and the first face-up buildings start at 1 VP (set on initialization, not after a round passes)
