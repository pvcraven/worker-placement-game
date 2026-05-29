# Implementation Plan: The Green Room — Intrigue Quest Space

**Branch**: `038-intrigue-quest-space` | **Date**: 2026-05-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/038-intrigue-quest-space/spec.md`

## Summary

Add "The Green Room" — a new permanent board space requiring a two-step action: play an intrigue card from hand (resolving its effect with animations), then select a face-up quest card. Rearrange the 9 permanent spaces into a 3x3 grid with constructed buildings paginated below. Reuses existing `pending_play_intrigue` state, `_resolve_intrigue_effect()`, and `handle_select_quest_card()` — no new message types needed.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2, Pillow (card generation)
**Storage**: In-memory game state; JSON config files in `config/`
**Testing**: pytest + ruff (`cd src && pytest && ruff check .`)
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Client-server game (Arcade UI + WebSocket server)
**Performance Goals**: 60 fps client rendering, instant server response
**Constraints**: Server-authoritative, all state mutations server-side
**Scale/Scope**: 2-4 players per game, ~20 board spaces total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Card images are sprites; no primitive draw calls. Board renderer uses sprite lists and cached Text objects. |
| II. Pydantic Data Modeling | PASS | ActionSpace is Pydantic model, space defined in board.json validated through existing models. No new models needed. |
| III. Client-Server Separation | PASS | Game logic in server/game_engine.py; client renders state. No client-side state mutation. |
| IV. Test-Driven Game Logic | PASS | Server logic tested with pytest; no Arcade dependency in tests. |
| V. Simplicity First | PASS | Reuses existing pending_play_intrigue, _resolve_intrigue_effect(), and handle_select_quest_card(). No new abstractions. |
| VI. Server-Authoritative Message Protocol | PASS | Reuses existing Request/Response pairs. No new message types needed. |
| VII. Config-Driven Game Content | PASS | New space added as JSON entry in board.json with reward_special="play_intrigue_and_quest". Server branches on field value, not hard-coded ID. |
| VIII. Pending State for Deferred Actions | PASS | Reuses existing pending_play_intrigue and pending_placement fields. Source field ("green_room") distinguishes from quest-completion source. |
| IX. Cancel/Unwind Reversibility | PASS | Uses existing _unwind_placement() for cancel before intrigue play. After intrigue play, player is committed (effect already resolved). |
| X. Post-Action Turn Flow | PASS | After quest selection: _check_quest_completion() → _advance_turn(). Standard post-action sequence. |

## Project Structure

### Documentation (this feature)

```text
specs/038-intrigue-quest-space/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research decisions
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 quickstart guide
├── contracts/           # Phase 1 protocol contracts
│   └── server-client-protocol.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
config/
  board.json               # ADD: The Green Room entry to permanent_spaces

server/
  game_engine.py           # MODIFY: handle_place_worker() routing for play_intrigue_and_quest
                           # MODIFY: handle_play_intrigue_from_quest() to chain to quest selection
                           # MODIFY: handle_select_quest_card() for spot_number=3
                           # MODIFY: _advance_after_quest_rewards() for green_room source

shared/
  messages.py              # NO CHANGES (reuses existing message types)

client/
  ui/board_renderer.py     # MODIFY: _GRID_PLACEMENT for 3x3 layout
                           # MODIFY: _rebuild_shapes() for new layout
                           # MODIFY: constructed building positioning
  ui/board_grid.py         # POSSIBLY MODIFY: grid dimensions if needed
  assets/card_images/
    spaces/
      the_green_room.png   # ADD: generated card image

card-generator/
  generate_cards.py        # MODIFY: add play_intrigue_and_quest case

tests/
  test_green_room.py       # ADD: server-side tests
```

**Structure Decision**: Single project structure. All changes fit within existing directory organization. No new directories needed except the generated card image.

## Design: Server-Side Game Logic

### 1. Board Configuration (config/board.json)

Add new entry to `permanent_spaces`:
```json
{
    "space_id": "the_green_room",
    "name": "The Green Room",
    "space_type": "permanent",
    "reward": {},
    "reward_special": "play_intrigue_and_quest",
    "slots": 1
}
```

### 2. Worker Placement Handler (server/game_engine.py)

In `handle_place_worker()` (~line 1740), add a new branch for `play_intrigue_and_quest` **before** the garage check:

```python
# Handle The Green Room (play intrigue + quest selection)
if space.reward_special == "play_intrigue_and_quest":
    # Validate player has intrigue cards
    if not player.intrigue_hand:
        await conn.send_error("INVALID_ACTION",
            "You need at least one intrigue card to use The Green Room.")
        return
    state.pending_placement = _pending
    state.pending_play_intrigue = {
        "player_id": player.player_id,
        "source": "green_room",
    }
    _log_event(state, action="place_worker",
        details=f"{player.display_name} placed worker on {space.name} — awaiting intrigue play",
        player_id=player.player_id)
    await server.broadcast_to_game(state.game_code,
        WorkerPlacedResponse(player_id=player.player_id, space_id=msg.space_id,
            reward_granted={}, next_player_id=None))
    await server.send_to_player(player.player_id,
        IntriguePlayPromptResponse(
            intrigue_hand=[c.model_dump() for c in player.intrigue_hand]))
    return
```

### 3. Intrigue Play Handler Modification (server/game_engine.py)

Modify `handle_play_intrigue_from_quest()` (~line 4620):

After intrigue effect resolves and `pending_play_intrigue` is cleared (line 4678):
- Check if `source == "green_room"`
- If yes: instead of calling `_advance_after_quest_rewards()`, transition to quest selection by keeping `pending_placement` active (it's already set) and letting the client show quest selection UI
- The client will detect the pending placement on a `play_intrigue_and_quest` space and show the quest card selection dialog

For the non-pending (immediate) intrigue effect path:
```python
source = state.pending_play_intrigue.get("source")
state.pending_play_intrigue = None

if effect_details.get("pending"):
    # ... existing target selection logic ...
    # Add "source": "green_room" to pending_intrigue_target
    state.pending_intrigue_target["source"] = source or "quest_completion"
    return

# Broadcast intrigue resolution
await server.broadcast_to_game(...)

if source == "green_room":
    # Don't advance turn — wait for quest selection
    return
else:
    await _advance_after_quest_rewards(server, state, player)
```

Similarly, in `handle_choose_intrigue_target()` (~line 4228), after target is resolved:
- Check if `pending_intrigue_target["source"] == "green_room"`
- If yes: don't advance turn, wait for quest selection
- If no: continue with existing `_check_quest_completion()` or `_advance_after_quest_rewards()` logic

### 4. Quest Selection Handler Update (server/game_engine.py)

In `handle_select_quest_card()` (~line 2146):

Update the spot determination logic (~line 2170) to handle The Green Room:
```python
spot_special = space.reward_special if space else None
if is_building_draw:
    spot_num = 0
elif spot_special == "quest_and_coins":
    spot_num = 1
elif spot_special in ("quest_and_intrigue", "reset_quests"):
    spot_num = 2
elif spot_special == "play_intrigue_and_quest":
    spot_num = 3
```

The Green Room gives **no bonus reward** (the intrigue effect was the "bonus"):
```python
elif spot_special == "play_intrigue_and_quest":
    bonus_reward = {}  # No additional bonus
```

### 5. Cancel Handler

The existing `CancelPlacementRequest` flow should work. When `pending_play_intrigue` has `source == "green_room"`:
- `_unwind_placement()` reverses worker placement
- Clear `pending_play_intrigue`
- Broadcast `PlacementCancelledResponse`

Need to verify the cancel handler checks for `pending_play_intrigue` and handles it. If not, add a check.

### 6. Reconnection Support (server/lobby.py)

The existing reconnection logic (~line 590) already handles `pending_play_intrigue` by re-sending `IntriguePlayPromptResponse`. No changes needed — the source field is informational and doesn't affect the prompt.

## Design: Card Image Generation

### generate_cards.py

In `generate_space_cards()`, add a case for `reward_special == "play_intrigue_and_quest"` (~line 1706 area):

```python
elif special == "play_intrigue_and_quest":
    # "Play" text + intrigue icon + quest icon
    play_text_x = center_x - 60
    text_y = band_bottom - 40
    draw.text((play_text_x, text_y), "Play", fill="white", font=body_font)
    _draw_intrigue_card_icon(draw, play_text_x + 50, text_y - 10)
    quest_y = text_y + 70
    _draw_quest_card_icon(draw, center_x, quest_y)
```

Uses the same `_draw_quest_card_icon()` and `_draw_intrigue_card_icon()` helper functions. Same blue band color (50, 70, 100) as "The Back Room".

## Design: Board Layout Rearrangement

### Updated _GRID_PLACEMENT (client/ui/board_renderer.py)

```python
_GRID_PLACEMENT = {
    # 3x3 permanent space grid (columns 0-2, rows 0-2)
    "merch_store": (0, 0, 1, 1),
    "motown": (1, 0, 1, 1),
    "guitar_center": (2, 0, 1, 1),
    "talent_show": (0, 1, 1, 1),
    "rhythm_pit": (1, 1, 1, 1),
    "jam_session": (2, 1, 1, 1),
    "whisper_room": (0, 2, 1, 1),
    "vip_entrance": (1, 2, 1, 1),
    "the_green_room": (2, 2, 1, 1),

    # Garage spaces (top area, right of permanent grid)
    "sunset_records": (3.5, 0, 1, 1),
    "the_back_room": (4.5, 0, 1, 1),
    "the_garage": (5.5, 0, 1, 1),

    # Backstage slots
    "backstage_slot_1": (3, 4, 1, 1),
    "backstage_slot_2": (3, 5, 1, 1),
    "backstage_slot_3": (3, 6, 1, 1),

    # Realtor
    "realtor": (5, 4, 1, 1),
}
```

### Constructed Buildings Repositioning

Currently: columns 1-2, rows 0-7 (8 per page)
New: columns 0-2, rows 3+ (below the 3x3 grid)

Update the building rendering loop:
```python
for j, space_id in enumerate(page_buildings):
    col = j % 3        # Columns 0, 1, 2
    row = 3 + (j // 3) * 2  # Rows 3, 5, 7 (2 rows each)
```

Buildings per page may need adjustment based on available vertical space. With 3 columns and rows 3-7, that's ~3 rows × 3 columns = 9 buildings per page (up from 8).

### Worker Position Updates

The `_update_workers()` method needs updates to position markers correctly on the new 3x3 grid positions. The existing logic reads from `_GRID_PLACEMENT`, so updating the dict should handle most cases.

## Complexity Tracking

No violations to justify. All design decisions follow existing patterns and reuse existing infrastructure.
