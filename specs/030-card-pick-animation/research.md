# Research: Card Pick Animation

## Decision 1: Animation System

**Decision**: Use the existing `AnimationManager` class in `client/ui/animation_manager.py` with `on_complete` callback chaining for multi-phase sequencing.

**Rationale**: AnimationManager already supports per-sprite easing animations with configurable easing functions, duration, and `on_complete` callbacks. The three-phase animation (entry → pause → exit) can be implemented by chaining callbacks: entry's `on_complete` starts the pause timer, pause's completion starts the exit animation, exit's `on_complete` triggers the board refresh.

**Alternatives considered**:
- Building a dedicated timeline/sequencer class — rejected (YAGNI, callback chaining is sufficient for a 3-step sequence)
- Using arcade's built-in scheduling (`arcade.schedule`) for the pause — viable but callback from AnimationManager is simpler to reason about

## Decision 2: Pause Implementation

**Decision**: Use `AnimationManager.animate()` with a zero-distance animation (start == end) and `Easing.LINEAR` for the 1-second pause phase, rather than a separate timer mechanism.

**Rationale**: AnimationManager already manages elapsed time and fires `on_complete` callbacks when duration expires. A zero-distance animation effectively becomes a timed delay within the same system — no separate timer infrastructure needed.

**Alternatives considered**:
- `arcade.schedule()` / `arcade.unschedule()` — adds a parallel timing system that must be coordinated with animation state
- A boolean flag checked in `on_update()` — manual state management that AnimationManager already handles

## Decision 3: Quest Card Sprite for Animation

**Decision**: Create a new `arcade.Sprite` from the quest card's PNG image for animation, rather than extracting the sprite from `board_renderer._quest_sprite_list`.

**Rationale**: The board renderer's sprite list is rebuilt on `_rebuild_shapes()`. Extracting a sprite from it requires careful lifecycle management. Creating a fresh sprite from the same PNG path (`client/assets/card_images/quests/{card_id}.png`) with matching scale is straightforward. The board renderer immediately hides the original by removing the card from the face-up quest list and marking shapes dirty.

**Alternatives considered**:
- Extracting the sprite from `_quest_sprite_list` and removing it — couples animation tightly to board renderer internals and complicates the rebuild

## Decision 4: Deferring Board Refresh

**Decision**: Buffer the `face_up_quests_updated` message data during animation and apply it in the exit animation's `on_complete` callback.

**Rationale**: The server sends two messages: `quest_card_selected` (state update) and `face_up_quests_updated` (new card list). Currently `_on_face_up_quests_updated` immediately calls `_refresh_board()`. During animation, we need to buffer this update and apply it only after the animation completes. This preserves the existing two-message architecture without server changes.

**Alternatives considered**:
- Modifying the server to delay sending messages — violates client-server separation (Principle III) and complicates server logic
- Ignoring the update and re-requesting state — unnecessary network overhead

## Decision 5: Player List Exit Target

**Decision**: Use `_player_marker_positions[player_id]` to get the screen coordinates of the selecting player's row in the player list as the exit animation target.

**Rationale**: `_player_marker_positions` is already populated in `_draw_player_list()` with the (cx, row_top) position of each player's marker sprite. This gives the exact screen coordinates needed for the exit animation direction.

**Alternatives considered**:
- Hard-coding upper-left corner coordinates — doesn't target the specific player
- Calculating from turn_order index — duplicates existing position calculation

## Decision 6: Input Blocking During Animation

**Decision**: Add a boolean flag `_card_animation_active` on GameView, checked in `on_mouse_press()` to block clicks during the animation sequence.

**Rationale**: Simple flag that's set when animation starts and cleared in the final `on_complete` callback. The existing `on_mouse_press` handler already has early-return checks — adding one more is consistent with the pattern.

**Alternatives considered**:
- Disabling the UI manager — overkill, only need to block board clicks
- Using highlight mode — semantically wrong, highlight mode is for selecting targets

## Decision 7: Slot-Stable Card Replacement

**Decision**: When the board refreshes after animation, track which slot index was vacated and ensure only that slot gets the new card by maintaining slot-to-card mapping rather than relying on list order.

**Rationale**: The server appends the replacement card to the end of `face_up_quests`, which means the list order changes. The board renderer positions cards by list index (0-3 → grid columns 3-6). To keep non-selected cards stationary, the client must map each card to its slot by ID, detect which slot is now occupied by a different card, and only visually update that slot.

**Alternatives considered**:
- Having the server maintain slot positions — would require server-side changes (violates Principle III's spirit of minimal server changes for a client-only feature)
- Rebuilding all card positions — causes visible position jumping for non-selected cards (violates FR-006)
