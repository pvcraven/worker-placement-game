# Implementation Plan: Card Pick Animation

**Branch**: `030-card-pick-animation` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/030-card-pick-animation/spec.md`

## Summary

Add a 3-phase card animation when a quest card is selected: SINE ease to screen center (0.75s), 1-second pause, Quad-In ease toward the selecting player's row in the player list (0.75s). Plays on all connected clients. Board refresh is deferred until animation completes, with non-selected cards remaining stationary. Uses the existing `AnimationManager` with `on_complete` callback chaining — no server changes.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), arcade.anim (Easing, ease)
**Storage**: N/A (client-side rendering only)
**Testing**: pytest + ruff (server logic unchanged, manual visual testing for animation)
**Target Platform**: Windows desktop (Arcade window)
**Project Type**: Desktop game (client-server with WebSocket networking)
**Performance Goals**: Smooth animation at target frame rate, no stuttering
**Constraints**: Animation must not block the event loop; must use existing AnimationManager pattern
**Scale/Scope**: 3 files modified, 0 new files, ~80-120 lines added

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Uses arcade.Sprite and SpriteList via AnimationManager |
| II. Pydantic Data Modeling | PASS | No new data crosses boundaries |
| III. Client-Server Separation | PASS | Animation is client-only; server unchanged |
| IV. Test-Driven Game Logic | PASS | No server logic changes; existing tests unaffected |
| V. Simplicity First | PASS | Reuses existing AnimationManager; callback chaining is simplest approach |
| VI. Server-Authoritative Message Protocol | PASS | Message types unchanged; client buffers visual refresh |
| VII. Config-Driven Game Content | PASS | No content changes |
| VIII. Pending State | N/A | No multi-step server interactions added |
| IX. Cancel/Unwind | N/A | Animation is non-cancellable display-only |
| X. Post-Action Turn Flow | PASS | Turn advancement unchanged; only visual timing deferred |

## Project Structure

### Documentation (this feature)

```text
specs/030-card-pick-animation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research decisions
├── data-model.md        # Data model (minimal)
├── quickstart.md        # Quick reference
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code (files to modify)

```text
client/
  views/game_view.py          # Animation orchestration, message handling, input blocking
  ui/animation_manager.py     # No changes needed (existing infrastructure sufficient)
  ui/board_renderer.py        # Expose quest card scale and position data for animation
```

**Structure Decision**: No new files. All changes fit within existing architecture — game_view orchestrates the animation using the existing AnimationManager, and board_renderer exposes the data needed to create the animation sprite.

## Implementation Design

### Phase 1: Board Renderer — Expose Quest Card Data

**File**: `client/ui/board_renderer.py`

Add a public method to retrieve a quest card's screen position and scale by card ID:

```python
def get_quest_card_info(self, card_id: str) -> tuple[float, float, float] | None:
    """Return (x, y, scale) for a face-up quest card, or None."""
```

This uses the existing `_quest_positions` list and `face_up_quests` data to find the card by ID, returning its center position and the `quest_scale` value.

Also store `quest_scale` as `self._quest_scale` during `_rebuild_shapes()` so it's accessible.

### Phase 2: Game View — Animation Orchestration

**File**: `client/views/game_view.py`

#### New state fields in `__init__`:
- `self._card_animation_active: bool = False`
- `self._pending_face_up_update: dict | None = None`

#### Modified: `_on_quest_card_selected()` (lines 813-848)

After existing state updates (move card to hand, apply bonus, advance turn, log), add animation trigger:

1. Get the card's screen position from `board_renderer.get_quest_card_info(card_id)`
2. Create a new `arcade.Sprite` from `client/assets/card_images/quests/{card_id}.png` with matching scale
3. Compute screen center: `(self.window.width / 2, self.window.height / 2)`
4. Get exit target: `self._player_marker_positions.get(pid, (0, self.window.height))`
5. Set `_card_animation_active = True`
6. Remove the selected card from local `face_up_quests` and mark the board dirty so the slot appears empty
7. Start entry animation (Phase A)

#### Animation chain:

**Phase A — Entry** (board position → screen center):
```python
self.animation_manager.animate(
    sprite=card_sprite,
    start=card_position,
    end=screen_center,
    duration=0.75,
    easing=Easing.SINE,
    on_complete=start_pause,
)
```

**Phase B — Pause** (screen center → screen center, zero distance):
```python
self.animation_manager.animate(
    sprite=card_sprite,
    start=screen_center,
    end=screen_center,
    duration=1.0,
    easing=Easing.LINEAR,
    on_complete=start_exit,
)
```

**Phase C — Exit** (screen center → player list row):
```python
self.animation_manager.animate(
    sprite=card_sprite,
    start=screen_center,
    end=player_target,
    duration=0.75,
    easing=Easing.QUAD_IN,
    on_complete=on_animation_complete,
)
```

**on_animation_complete callback**:
1. Set `_card_animation_active = False`
2. If `_pending_face_up_update` is not None, apply it via `_on_face_up_quests_updated()` and clear the buffer

#### Modified: `_on_face_up_quests_updated()` (lines 862-866)

If `_card_animation_active` is True, buffer the message in `_pending_face_up_update` instead of applying immediately:

```python
def _on_face_up_quests_updated(self, msg: dict) -> None:
    if self._card_animation_active:
        self._pending_face_up_update = msg
        return
    # existing logic unchanged
```

#### Modified: `on_mouse_press()` 

Add early return if `_card_animation_active` is True:

```python
if self._card_animation_active:
    return
```

### Phase 3: Slot-Stable Refresh

When the deferred `_on_face_up_quests_updated` fires after animation, the board rebuilds all quest positions. Since the server appends the replacement card to the end of `face_up_quests`, the list order may differ from slot order. However, since the full list is rebuilt each time in `_rebuild_shapes()` and positions are determined by list index → grid column mapping, the replacement card will naturally fill the position of the removed card because the server removes the selected card and appends the replacement — the remaining cards shift up in the list.

The key insight: the spec requires non-selected cards to stay in their positions (FR-006). If the server's list order changes, the visual positions may shift. To handle this cleanly, we need to verify the server's behavior: if it removes the selected card and appends the replacement to the end, remaining cards shift left in the list and get new grid positions.

**Resolution**: The server currently removes the selected card and appends the replacement. Since the card is removed from the middle of the list, the remaining cards shift indices. To maintain slot stability, the client should track the pre-animation slot-to-card mapping and, when the deferred update arrives, reorder the new `face_up_quests` list to match the original slot assignments (keeping each card in its original slot and placing the new card in the vacated slot).

This reordering happens in `_on_face_up_quests_updated` before calling `_refresh_board`.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
