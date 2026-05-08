# Research: Client Disconnect & Reconnect

**Date**: 2026-05-08 | **Feature**: 028-client-reconnect

## Existing Infrastructure Audit

### Decision: Leverage existing server-side reconnect infrastructure
**Rationale**: The server already implements the full reconnect lifecycle:
- `ReconnectRequest` message type (shared/messages.py:132-136) with game_code, player_name, slot_index
- `reconnect()` handler (server/lobby.py:339-377) that matches by name+slot, restores `is_connected=True`, sends `StateSyncResponse`
- `_handle_disconnect()` (server/network.py:271-289) that sets `is_connected=False` and broadcasts `PlayerDisconnectedResponse`
- `PlayerReconnectedResponse` (shared/messages.py:421-424) broadcast to other players
- `_filter_state_for_player()` (server/lobby.py:310-336) for sending filtered state on reconnect

**Alternatives considered**: Building new reconnect protocol from scratch — rejected because existing server code is complete and working.

## Gap Analysis

### Gap 1: Client does not send ReconnectRequest after WebSocket reconnects
**Decision**: Add reconnect-aware logic to the client's connection lifecycle
**Rationale**: The client's `_connection_loop` (network_client.py:98-130) auto-reconnects the WebSocket on disconnection, but treats every reconnection as a fresh connection with no identity. The client needs to send a `ReconnectRequest` message after re-establishing the WebSocket if it was previously in a game.
**Approach**: Store reconnect credentials (game_code, player_name, slot_index) on the network client. After WebSocket connects, if credentials exist, automatically send ReconnectRequest. Expose a callback/queue mechanism so the game view can handle the state_sync response.

### Gap 2: slot_index not stored on window
**Decision**: Store slot_index on window alongside player_id, player_name, game_code
**Rationale**: The server's reconnect handler requires slot_index for matching (lobby.py:349). Currently `window.player_id` is set on game creation (menu_view.py:266) but slot_index is never persisted client-side. It's available in the game_state received on game start.
**Approach**: Extract slot_index from the player's entry in the game state when transitioning to game view, store on window.

### Gap 3: Player list renders all names in WHITE regardless of connection status
**Decision**: Check `is_connected` field and use RED for disconnected players
**Rationale**: `_draw_player_list()` (game_view.py:2846-2908) always uses `arcade.color.WHITE` for player names. The `is_connected` field IS already included in the game state dict (via `model_dump()` in `_filter_state_for_player`) but the client never reads it.
**Approach**: In `_draw_player_list()`, read `p.get("is_connected", True)` and use `arcade.color.RED` when False, `arcade.color.WHITE` when True. The `_text()` helper caches text objects, so the color must be updated on each frame for the cached text.

### Gap 4: Client view transition on reconnect
**Decision**: Handle state_sync in game_view to restore UI after reconnect
**Rationale**: When the client reconnects, it receives `StateSyncResponse` which updates `self.game_state` and calls `_sync_from_state()`. This path already exists (game_view.py:264-266). However, if the client was showing a different view (e.g., got kicked back to menu), it needs to transition back to the game view.
**Approach**: When a reconnect succeeds (state_sync received), if the client is not already on the game view, transition to it. The simplest path: if client detects disconnect while in game view, stay on game view and show a "reconnecting..." indicator. When state_sync arrives, refresh the UI.

## Reconnect Flow Design

### Automatic reconnect (network interruption, client stays open)
1. WebSocket drops → `_connection_loop` catches `ConnectionClosed`, waits 2s, reconnects
2. After WebSocket connects, if `reconnect_credentials` set → send `ReconnectRequest`
3. Server validates → sends `StateSyncResponse` to client, broadcasts `PlayerReconnectedResponse` to others
4. Client game_view receives `state_sync` → refreshes UI
5. Other clients receive `player_reconnected` → log message, player name turns white

### Manual reconnect (client closed and reopened)
1. Player opens client, enters same name, enters game code, clicks Join
2. Client sends `JoinGameRequest` → server sees game is in progress (not LOBBY phase)
3. Server attempts to match as reconnect instead of join
4. Success → same flow as automatic from step 3 above

**Decision**: The server should handle join-during-active-game as a reconnect attempt when name matches
**Rationale**: Requiring the user to know about a separate "reconnect" action creates unnecessary UX friction. If a player provides the right name and game code for an active game, the intent is clearly to rejoin.
**Alternative**: Separate reconnect button on menu — rejected for simplicity.
