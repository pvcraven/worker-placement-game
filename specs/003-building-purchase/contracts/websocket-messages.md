# WebSocket Message Contracts: Building Purchase System

**Date**: 2026-04-14 | **Branch**: `003-building-purchase`

## New Messages

### BuildingMarketUpdate (server → client)

Sent when the face-up building market changes: game start, after a purchase (with replacement draw), and after round-end VP increment.

```json
{
  "action": "building_market_update",
  "face_up_buildings": [
    {
      "id": "building_003",
      "name": "Electric Lady Studios",
      "description": "Jimi Hendrix's custom-built...",
      "cost_coins": 7,
      "visitor_reward": {"guitarists": 2, "bass_players": 0, "drummers": 1, "singers": 0, "coins": 0},
      "visitor_reward_special": null,
      "owner_bonus": {"guitarists": 1, "bass_players": 0, "drummers": 0, "singers": 0, "coins": 0},
      "owner_bonus_special": null,
      "accumulated_vp": 3
    }
  ],
  "deck_remaining": 18
}
```

**Fields**:
- `face_up_buildings`: list of BuildingTile objects (0-3 items) with current `accumulated_vp`
- `deck_remaining`: int — number of buildings left in the hidden deck (for UI display, e.g., "18 buildings remaining")

## Modified Messages

### PurchaseBuildingRequest (client → server) — Modified

Remove `lot_index` field. The server assigns the next available lot automatically (per spec FR-009).

```json
{
  "action": "purchase_building",
  "building_id": "building_003"
}
```

**Fields**:
- `building_id`: str — ID of the face-up building to purchase

**Removed**:
- `lot_index` — server now auto-assigns the next available lot

### BuildingConstructedResponse (server → client) — No Change

Existing response is sufficient. The market update is sent as a separate `BuildingMarketUpdate` message immediately after.

```json
{
  "action": "building_constructed",
  "player_id": "player_abc",
  "building_id": "building_003",
  "building_name": "Electric Lady Studios",
  "lot_index": 2,
  "new_space_id": "building_building_003"
}
```

## Existing Messages — No Changes Needed

- `PlaceWorkerRequest` / `WorkerPlacedResponse` — already handles building spaces
- `GameStateSync` — will naturally include updated `face_up_buildings` and `building_deck` count via state filtering

## Message Flow Sequences

### Game Start
```
Server → all clients: GameStateSync (includes initial face_up_buildings)
Server → all clients: BuildingMarketUpdate (3 face-up buildings, each with VP=1)
```

### Building Purchase
```
Client → Server:  PurchaseBuildingRequest { building_id }
Server validates:  building in face_up_buildings, player has coins, lot available
Server → client:   error response (if validation fails)
Server → all:      BuildingConstructedResponse { player_id, building_id, ... }
Server → all:      BuildingMarketUpdate { updated face_up (with replacement if drawn) }
```

### Round End (VP increment)
```
Server: increment accumulated_vp on all face_up_buildings
Server → all: BuildingMarketUpdate { updated face_up with new VP values }
```

### Worker Placement on Building
```
Client → Server:  PlaceWorkerRequest { space_id: "building_building_003" }
Server:           grant visitor_reward to placer
Server:           if placer != owner: grant owner_bonus to owner
Server → all:     WorkerPlacedResponse (existing flow, no changes)
```
