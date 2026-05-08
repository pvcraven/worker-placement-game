# Data Model: Client Disconnect & Reconnect

**Date**: 2026-05-08 | **Feature**: 028-client-reconnect

## Existing Entities (No Changes Required)

### Player (server/models/game.py)
Already has all required fields:
- `is_connected: bool = True` — tracks connection status
- `consecutive_timeouts: int = 0` — reset on reconnect
- `player_id: str` — unique identifier
- `display_name: str` — used for reconnect matching
- `slot_index: int` — used for reconnect matching

### GameState (server/models/game.py)
Already preserves full game state when players disconnect:
- `players: list[Player]` — players remain in list when disconnected
- `game_code: str` — used for reconnect matching
- `last_activity: float` — session cleanup timer

### Messages (shared/messages.py)
All required message types already exist:
- `ReconnectRequest` (action: "reconnect") — game_code, player_name, slot_index
- `StateSyncResponse` (action: "state_sync") — full filtered game state
- `PlayerDisconnectedResponse` (action: "player_disconnected") — player_id, player_name
- `PlayerReconnectedResponse` (action: "player_reconnected") — player_id, player_name

## New Client-Side State

### NetworkClient reconnect credentials (client/network_client.py)
New attributes to store reconnect identity:
- `reconnect_game_code: str | None` — game code for auto-reconnect
- `reconnect_player_name: str | None` — player name for auto-reconnect
- `reconnect_slot_index: int | None` — slot index for auto-reconnect

Set when player enters a game, cleared when returning to menu. Used by `_connection_loop` to automatically send `ReconnectRequest` after WebSocket re-establishes.

### Window attributes (client/main.py)
New attribute:
- `window.slot_index: int | None` — player's slot index, set from game state on game start

## State Transitions

```
CONNECTED ──(WebSocket closes)──> DISCONNECTED
    - Server: player.is_connected = False
    - Server: broadcast PlayerDisconnectedResponse
    - Client: show reconnecting indicator (if client still running)
    - Other clients: player name turns red

DISCONNECTED ──(ReconnectRequest matches)──> CONNECTED  
    - Server: player.is_connected = True
    - Server: send StateSyncResponse to reconnecting player
    - Server: broadcast PlayerReconnectedResponse
    - Client: refresh UI from state_sync
    - Other clients: player name turns white

DISCONNECTED ──(session expires)──> REMOVED
    - Server: session cleanup removes game
    - No reconnection possible
```
