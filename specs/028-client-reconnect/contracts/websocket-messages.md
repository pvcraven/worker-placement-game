# WebSocket Message Contracts: Disconnect & Reconnect

**Date**: 2026-05-08 | **Feature**: 028-client-reconnect

All messages are JSON-encoded over WebSocket. The `action` field discriminates message type.

## Existing Contracts (No Changes)

### Client → Server: ReconnectRequest
```json
{
  "action": "reconnect",
  "game_code": "ABC",
  "player_name": "Alice",
  "slot_index": 0
}
```
Sent when client reconnects to a game it was previously part of.

### Server → Client: StateSyncResponse
```json
{
  "action": "state_sync",
  "game_state": { /* filtered game state dict */ }
}
```
Sent to the reconnecting player with their full visible game state. Opponent hands are hidden (counts only).

### Server → All Clients: PlayerDisconnectedResponse
```json
{
  "action": "player_disconnected",
  "player_id": "uuid-string",
  "player_name": "Alice"
}
```
Broadcast to all connected players when a player disconnects.

### Server → All Clients: PlayerReconnectedResponse
```json
{
  "action": "player_reconnected",
  "player_id": "uuid-string",
  "player_name": "Alice"
}
```
Broadcast to all connected players when a disconnected player reconnects.

### Server → Client: ErrorResponse (reconnect failure)
```json
{
  "action": "error",
  "error_code": "GAME_NOT_FOUND",
  "message": "No game with that code."
}
```
or
```json
{
  "action": "error",
  "error_code": "INVALID_ACTION",
  "message": "No matching player found."
}
```

## Modified Contract: JoinGameRequest (in-progress game)

### Client → Server: JoinGameRequest (existing message, new behavior)
```json
{
  "action": "join_game",
  "game_code": "ABC",
  "player_name": "Alice"
}
```
**New behavior**: When the game is past LOBBY phase, the server treats this as a reconnect attempt. If `player_name` matches a disconnected player in the game, reconnect succeeds (same flow as explicit ReconnectRequest). If no match, returns error.

## Player State in Game State Sync

Each player object in `game_state.players` includes:
```json
{
  "player_id": "uuid",
  "display_name": "Alice",
  "slot_index": 0,
  "is_connected": true,
  "victory_points": 5,
  ...
}
```
The `is_connected` field is used by the client to determine player name color (white=connected, red=disconnected).
