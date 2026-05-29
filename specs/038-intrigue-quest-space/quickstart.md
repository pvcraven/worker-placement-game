# Quickstart: The Green Room — Intrigue Quest Space

## What This Feature Does

Adds "The Green Room" — a new permanent board space where players must play an intrigue card from their hand (resolving its effect), then select a face-up quest card. The board's permanent spaces are rearranged into a 3x3 grid with constructed buildings below.

## Key Files to Modify

### Server (game logic)
- `config/board.json` — Add The Green Room space definition
- `server/game_engine.py` — Add handler for `play_intrigue_and_quest` special in `handle_place_worker()`, modify `handle_play_intrigue_from_quest()` to chain to quest selection when source is "green_room", update `handle_select_quest_card()` for new spot_number
- `server/models/game.py` — No changes needed (reuses existing pending fields)

### Shared (messages)
- `shared/messages.py` — No new message types needed; reuses existing ones

### Client (rendering & UI)
- `client/ui/board_renderer.py` — Update `_GRID_PLACEMENT` dict for 3x3 layout, reposition constructed buildings, update rendering methods
- `client/ui/board_grid.py` — Possibly adjust grid dimensions if needed
- `card-generator/generate_cards.py` — Add card image generation for `play_intrigue_and_quest` special

### Config
- `config/board.json` — New permanent space entry

## Architecture Notes

- Reuses existing `pending_play_intrigue` state (from spec 019) with `"source": "green_room"` to chain intrigue play → quest selection
- Reuses existing `handle_select_quest_card()` for the quest selection step
- Reuses existing `_resolve_intrigue_effect()` for intrigue card resolution
- Cancel/unwind uses existing `_unwind_placement()` pattern
- Constitution: follows Principles VI (message protocol), VII (config-driven), VIII (pending state), IX (cancel/unwind), X (post-action turn flow)

## Testing Approach

- Server-side pytest tests for:
  - Placement validation (with/without intrigue cards)
  - Intrigue play → quest selection chaining
  - Cancel/unwind at intrigue selection stage
  - Edge cases (empty quest display, targeted intrigue effects)
- Visual testing for card image and 3x3 layout
