# Research: Intrigue Card Animation

**Date**: 2026-05-16

## R1: Face-Down Image Generation Pattern

**Decision**: Generate a full-size (400×500 px) face-down intrigue card image using the same visual pattern as the existing small icon (84×114 px) — dark gray (60,60,60) background, black/white border, centered "I" letter in parchment color. Scale up proportionally.

**Rationale**: The existing `generate_card_icon_pngs()` function in `generate_cards.py` already creates small intrigue icons at 2× the inline icon size. A full-size back follows the same 3-layer rectangle (black border → white border → colored fill) pattern, scaled to 400×500. The card dimensions match `INT_CARD_WIDTH` × `INT_CARD_HEIGHT`.

**Alternatives considered**:
- Custom artwork/pattern for the card back — rejected as overengineered; the "I" motif is the established visual identity
- Reusing the small icon and just scaling it up — rejected because bitmap scaling produces blurry results; generating at native resolution is better

## R2: Draw Animation Entry Point (Quest Rewards)

**Decision**: Hook into `_on_quest_completed()` in `game_view.py` to queue intrigue draw animation events. The server already sends `drawn_intrigue: list[dict]` in `QuestCompletedResponse` with full card data to all clients. The client already distinguishes local vs opponent players to decide which data to store. Use the same distinction to choose face-up vs face-down sprite.

**Rationale**: The `QuestCompletedResponse` broadcast already includes card IDs and details for drawn intrigue cards. No server changes needed for the draw flow.

**Alternatives considered**:
- Adding a separate server message for intrigue draws — rejected; existing message already contains the data

## R3: Draw Animation Entry Point (Backstage)

**Decision**: Hook into the backstage handler on the client side. `WorkerPlacedBackstageResponse` already includes `intrigue_card` with full card details. Queue a draw animation event before processing the intrigue effect.

**Rationale**: Backstage draws include card data in the existing broadcast. The animation can display face-up for the drawer and face-down for opponents using the same `player_id == local_id` check.

## R4: Play Animation — Server Message Gap

**Decision**: Add `intrigue_card_id: str = ""` and `intrigue_card_name: str = ""` fields to `IntrigueEffectResolvedResponse`. For non-targeting intrigue plays (which currently have no broadcast), add a broadcast of effect resolution so all clients can animate the play.

**Rationale**: For play animations, all players must see the card face-up. Currently:
- Backstage plays: Card data is in `WorkerPlacedBackstageResponse` (sufficient)
- Quest reward plays with targeting: `IntrigueEffectResolvedResponse` is broadcast but lacks card ID
- Quest reward plays without targeting: No broadcast at all

Adding card fields to the existing response and ensuring it's always broadcast is the simplest change that covers all play paths.

**Alternatives considered**:
- New `IntrigueCardPlayedResponse` message — rejected per Simplicity First principle; extending the existing message type is sufficient
- Client-side tracking of "which card was just played" — rejected; the client removes the card from hand immediately, and opponents never had the data

## R5: Animation Coordinates and Timing

**Decision**: Follow the quest card animation pattern exactly:
- **Draw entry**: Start at lower-right `(window.width - 100, 100)` → center `(window.width/2, window.height/2)`, 0.5s, Easing.SINE, scale 1→2
- **Pause**: Hold at center, 2.0s, Easing.LINEAR
- **Draw exit**: Center → player marker position from `_player_marker_positions[pid]`, 0.75s, Easing.QUAD_IN, scale 2→1
- **Play entry**: Start at player marker position → center, 0.5s, Easing.SINE, scale 1→2
- **Play pause**: Hold at center, 2.0s, Easing.LINEAR
- **Play exit**: Center → lower-right `(window.width - 100, 100)`, 0.75s, Easing.QUAD_IN, scale 2→1

**Rationale**: Matching quest card timing (0.5s + 2.0s + 0.75s = 3.25s total) provides visual consistency. The lower-right and upper-left anchors match the spec's directional requirements.

## R6: Sound Integration

**Decision**: Reuse `self._card_sound` (already loaded from `card1.mp3`) as the sound parameter on the entry-phase animation. This is the same approach as the quest card pick animation.

**Rationale**: The sound is already loaded. The AnimationManager's `animate()` method already supports a `sound` parameter that plays via `arcade.play_sound()` at animation start.

## R7: Event Queue Integration

**Decision**: Wrap each intrigue animation in an `AnimationEvent` and enqueue it via `self.event_queue.enqueue()`. For multiple draws, create one `AnimationEvent` per card and enqueue them sequentially — the event queue's FIFO processing ensures they play one at a time.

**Rationale**: This is the established pattern used by quest card animations. The event queue blocks subsequent game events until the animation completes (FR-012, FR-013).

## R8: Intrigue Card Sprite Loading

**Decision**: Load intrigue card sprites from `client/assets/card_images/intrigue/{card_id}.png` for face-up display. Load from `client/assets/card_images/intrigue/intrigue_back.png` for face-down display. Use `arcade.Sprite()` with the appropriate path.

**Rationale**: Face-up intrigue card PNGs already exist at this path, generated by `generate_intrigue_cards()`. The face-down back will be generated to the same directory as `intrigue_back.png`.
