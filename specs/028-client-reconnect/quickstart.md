# Quickstart: Client Disconnect & Reconnect

**Date**: 2026-05-08 | **Feature**: 028-client-reconnect

## Overview

Enable graceful client disconnect/reconnect for the worker placement game. When a player's connection drops (network issue or client close), they can rejoin with the same name and game code. Disconnected players appear as red text in the player list; reconnected players return to white.

## What Already Works

- Server detects disconnect, sets `player.is_connected = False`, broadcasts `PlayerDisconnectedResponse`
- Server has `reconnect()` handler matching by name + slot_index + game_code
- Server sends `StateSyncResponse` with full filtered state on reconnect
- Server broadcasts `PlayerReconnectedResponse` to other players
- Client WebSocket auto-reconnects on network loss (2s retry)

## What Needs to Change

### 1. Client auto-sends ReconnectRequest (network_client.py)
Store reconnect credentials (game_code, player_name, slot_index) on NetworkClient. After WebSocket reconnects, if credentials exist, automatically send ReconnectRequest.

### 2. Store slot_index on window (menu_view.py, game_view.py)
Extract and store `slot_index` from game state when player enters a game, so it's available for reconnect.

### 3. Red text for disconnected players (game_view.py)
In `_draw_player_list()`, check `p.get("is_connected", True)` and use `arcade.color.RED` when disconnected.

### 4. Join-as-reconnect for restarted clients (server/lobby.py)
When `join_game` arrives for a game past LOBBY phase, treat it as a reconnect attempt if player name matches a disconnected player.

## Files to Modify

| File | Change |
|------|--------|
| `client/network_client.py` | Add reconnect credential storage and auto-reconnect logic |
| `client/views/game_view.py` | Red text in `_draw_player_list()`, handle reconnect state |
| `client/views/menu_view.py` | Store slot_index on window from join/create response |
| `server/lobby.py` | Handle join-during-active-game as reconnect |

## Testing

- `cd src && pytest && ruff check .`
- Manual: Start server + two clients, disconnect one, verify red text, reconnect, verify white text and state restore
