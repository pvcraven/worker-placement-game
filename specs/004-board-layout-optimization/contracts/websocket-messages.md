# WebSocket Message Contracts: Board Layout Optimization

**Date**: 2026-04-16 | **Branch**: `004-board-layout-optimization`

## No New Messages

This feature introduces no new WebSocket messages. All changes are client-side rendering and a config/code rename.

## Existing Messages — Rename Impact

### PlacementCancelledResponse (server → client)

The `space_id` field value changes from `"real_estate_listings"` to `"realtor"`. No structural change.

### WorkerPlacedResponse (server → client)

The `space_id` field value changes from `"real_estate_listings"` to `"realtor"` when a worker is placed on the Realtor space. No structural change.

## Existing Messages — No Changes

- `BuildingMarketUpdate` — continues to provide face-up buildings data used by the new popup panel
- `BuildingConstructedResponse` — unchanged
- `PurchaseBuildingRequest` / `CancelPurchaseBuildingRequest` — unchanged
