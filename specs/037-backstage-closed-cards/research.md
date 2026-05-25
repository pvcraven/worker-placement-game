# Research: Backstage Closed Cards

## Decision 1: Sprite Swapping Strategy

**Decision**: Pre-build two separate SpriteLists (normal and closed) at layout time and swap which one is drawn based on the game phase.

**Rationale**: The board renderer already builds `_backstage_sprite_list` from PNG files during `_build_board_layout()`. Building a second sprite list from different PNGs is trivially parallel. Swapping which list to draw is a single boolean check — zero per-frame cost. This is simpler than modifying sprite textures at runtime or overlaying text objects.

**Alternatives considered**:
- Texture swap on existing sprites: More complex (requires texture loading and per-sprite updates), no performance benefit since sprite lists are cheap.
- Overlay text/shapes on top of existing cards: Violates Constitution Principle I (no primitive draw calls). Using pre-rendered PNGs avoids this entirely.
- Single sprite list with texture atlas: Over-engineered for 3 sprites.

## Decision 2: Closed Card Visual Design

**Decision**: Generate `backstage_slot_N_closed.png` images with the same card base and title band as normal cards, but replacing "Play Intrigue" with "CLOSED" in dark red text surrounded by a dark red rectangular box border.

**Rationale**: Matches the user's clarified specification. Using the same card base and title band maintains visual consistency with the normal backstage cards while making the closed state immediately obvious through color contrast and the box border.

**Alternatives considered**:
- Greying out the entire card: Less informative — doesn't tell the player why the slot is unavailable.
- Adding a semi-transparent overlay: More complex and harder to read.

## Decision 3: Phase Transition Hooks

**Decision**: Use existing `_on_reassignment_phase_start()` and `_on_round_end()` handlers in game_view.py to trigger the swap. For reconnect, check `game_state["phase"]` after state sync.

**Rationale**: These handlers already fire at exactly the right moments. No new messages or server changes needed — the client already tracks the phase as a string in `game_state["phase"]`.

**Alternatives considered**:
- New server message for backstage visual state: Unnecessary — the phase information already covers this. Violates Simplicity First principle.
