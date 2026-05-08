# Implementation Plan: Client Disconnect & Reconnect

**Branch**: `028-client-reconnect` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/028-client-reconnect/spec.md`

## Summary

Enable graceful client disconnect and reconnect for the multiplayer worker placement game. The server-side infrastructure (disconnect detection, reconnect handler, state sync) already exists. The primary work is on the client side: automatically sending a ReconnectRequest after WebSocket reconnects, displaying disconnected players as red text in the player list, and allowing restarted clients to rejoin via the normal join flow.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Arcade (local source at C:\Users\PaCra\Projects\arcade), websockets, Pydantic v2
**Storage**: In-memory game state (server)
**Testing**: pytest + ruff
**Target Platform**: Desktop (Windows/Mac/Linux)
**Project Type**: Multiplayer desktop game (client-server)
**Performance Goals**: Reconnect within 10 seconds, visual feedback within 3 seconds
**Constraints**: Must use existing message protocol (Pydantic-based, JSON over WebSocket)
**Scale/Scope**: 2-5 players per game, single server instance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arcade Rendering Standards | PASS | Player list uses `_text()` helper (arcade.Text cache). No draw_text calls needed. |
| II. Pydantic Data Modeling | PASS | All messages use existing Pydantic models (ReconnectRequest, StateSyncResponse, etc.). No new message types needed. |
| III. Client-Server Separation | PASS | Server handles all reconnect logic and state. Client only renders and sends messages. |
| IV. Test-Driven Game Logic | PASS | Server reconnect logic exists and should have test coverage. New join-as-reconnect path needs tests. |
| V. Simplicity First | PASS | Leveraging existing infrastructure, minimal new code. No new abstractions. |
| VI. Server-Authoritative Message Protocol | PASS | Using existing Request/Response pairs. StateSyncResponse replaces client state on reconnect. |
| VII. Config-Driven Game Content | N/A | No game content changes. |
| VIII. Pending State for Deferred Actions | PASS | Reconnect mid-pending-action: StateSyncResponse includes pending state, client resumes. |
| IX. Cancel/Unwind Reversibility | N/A | No new cancel flows. |
| X. Post-Action Turn Flow | N/A | No changes to turn flow. |

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/028-client-reconnect/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: codebase audit and gap analysis
├── data-model.md        # Phase 1: data model (mostly existing)
├── quickstart.md        # Phase 1: implementation summary
├── contracts/
│   └── websocket-messages.md  # Phase 1: message contracts
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
client/
  network_client.py        # MODIFY: add reconnect credential storage, auto-reconnect
  views/
    game_view.py           # MODIFY: red text in _draw_player_list(), reconnect UI
    menu_view.py           # MODIFY: store slot_index, handle join-as-reconnect response
server/
  lobby.py                 # MODIFY: handle join_game during active game as reconnect
shared/
  messages.py              # NO CHANGE: all message types already exist
tests/                     # ADD: reconnect tests for join-as-reconnect path
```

**Structure Decision**: No structural changes. All modifications are to existing files in the established client/server/shared architecture.

## Implementation Phases

### Phase 1: Server — Join-as-Reconnect (server/lobby.py)

Modify the `join_game` handler to detect when a join request targets a game that is past LOBBY phase. If the player name matches a disconnected player, treat it as a reconnect (delegate to existing `reconnect()` function). If no match, return an error.

**Key change**: In the join handler, after finding the game session, check `state.phase != GamePhase.LOBBY`. If so, find a disconnected player with matching `display_name`. If found, call `reconnect()` with appropriate parameters.

**Tests**: Add pytest tests for:
- Join request for active game with matching disconnected player → reconnect succeeds
- Join request for active game with non-matching name → error returned
- Join request for LOBBY phase game → normal join (existing behavior)

### Phase 2: Client — Auto-Reconnect on Network Loss (client/network_client.py)

Add reconnect credential storage to NetworkClient:
- `set_reconnect_credentials(game_code, player_name, slot_index)` — called when entering a game
- `clear_reconnect_credentials()` — called when returning to menu
- After WebSocket connects in `_connection_loop`, if credentials exist, automatically enqueue a `ReconnectRequest` message

### Phase 3: Client — Store slot_index (menu_view.py, game_view.py)

- When `game_created` response arrives, store `slot_index` on window (it's in the response)
- When `game_started` response arrives in game_view, extract own slot_index from players list and store on window
- Pass credentials to network client via `set_reconnect_credentials()` when transitioning to game

### Phase 4: Client — Red Text for Disconnected Players (game_view.py)

In `_draw_player_list()`:
- Read `p.get("is_connected", True)` for each player
- Use `arcade.color.RED` when `is_connected` is False, `arcade.color.WHITE` when True
- Update the cached text object's color property on each frame to handle transitions

On `player_disconnected` / `player_reconnected` messages:
- Update the player's `is_connected` field in the local `game_state` dict so the color change takes effect immediately without waiting for a full state sync

## Complexity Tracking

No constitution violations to justify.
