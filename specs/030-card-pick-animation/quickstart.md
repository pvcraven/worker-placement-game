# Quickstart: Card Pick Animation

## What This Feature Does

When a player selects a face-up quest card, instead of the card instantly disappearing and being replaced, it animates: glides to the center of the screen (0.75s, SINE easing), pauses for 1 second, then flies off toward the selecting player's name in the player list (0.75s, Quad-In easing). After the animation, the board refreshes with the replacement card in the vacated slot. This plays on all connected clients.

## Key Files

| File | Role |
|------|------|
| `client/views/game_view.py` | Message handlers, animation orchestration, input blocking |
| `client/ui/animation_manager.py` | Existing eased sprite animation engine |
| `client/ui/board_renderer.py` | Quest card positions and sprite creation |

## How to Test

1. Start server: `python -m server`
2. Start 2+ clients: `python -m client`
3. Join a game, advance to a turn where quest card selection is available
4. Select a quest card — observe the 3-phase animation on all clients
5. Verify non-selected cards don't move when the board refreshes

## Architecture

No server changes. The existing `AnimationManager.animate()` with `on_complete` callbacks chains three phases:
1. **Entry** (board → center): SINE easing, 0.75s
2. **Pause** (center → center): zero-distance animation, 1.0s
3. **Exit** (center → player list row): QUAD_IN easing, 0.75s

The `face_up_quests_updated` server message is buffered during animation and applied in the exit callback.
