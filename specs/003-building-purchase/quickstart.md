# Quickstart: Building Purchase System

**Branch**: `003-building-purchase`

## Prerequisites

- Python 3.12+
- Dependencies installed: `pip install -e .` from repo root

## Running the Game

```bash
# Terminal 1: Start server
cd src && python -m server.main

# Terminal 2: Start client
cd src && python -m client.main
```

## Testing the Building Purchase Feature

### Manual Test Flow

1. **Start a game** with 2+ players (open multiple client windows)
2. **Verify layout**: All permanent spaces should appear in a single left column
3. **Verify market**: 3 face-up buildings should be visible with VP=1 each
4. **Place a worker on "Real Estate Listings"** (formerly Builder's Hall)
5. **Purchase dialog** should appear showing the 3 face-up buildings
6. **Select a building** you can afford → confirm → building appears in second column
7. **Next round**: Check that remaining face-up buildings show VP=2
8. **Have another player land on the purchased building** → verify visitor gets reward, owner gets bonus
9. **Have the owner land on their own building** → verify visitor reward granted, NO owner bonus

### Running Automated Tests

```bash
cd src && pytest tests/test_building_purchase.py -v
cd src && pytest tests/test_board_layout.py -v
cd src && pytest tests/test_owner_bonus.py -v
```

## Key Files to Modify

| File | What Changes |
|------|-------------|
| `config/board.json` | Rename builders_hall → real_estate_listings |
| `shared/card_models.py` | Add `accumulated_vp` field to BuildingTile |
| `shared/messages.py` | Add BuildingMarketUpdate, simplify PurchaseBuildingRequest |
| `server/models/game.py` | BoardState: replace building_supply with building_deck + face_up_buildings |
| `server/lobby.py` | Initialize deck + 3 face-up market with VP=1 |
| `server/game_engine.py` | Update purchase flow, add VP increment in _end_round |
| `client/ui/board_renderer.py` | Single-column layout, render market and purchased buildings |
| `client/ui/dialogs.py` | Add BuildingPurchaseDialog |
| `client/views/game_view.py` | Handle purchase dialog trigger, market updates |
