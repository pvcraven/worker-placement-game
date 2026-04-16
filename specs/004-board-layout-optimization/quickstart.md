# Quickstart: Board Layout Optimization

**Branch**: `004-board-layout-optimization`

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

## Testing the Board Layout Changes

### Manual Test Flow

1. **Start a game** with 2+ players
2. **Verify labels removed**: No "THE BOARD", "THE GARAGE", or "BACKSTAGE" text visible
3. **Verify upward shift**: Board elements use more vertical space, no large gaps
4. **Verify backstage labels**: Slots show "Backstage 1", "Backstage 2", "Backstage 3"
5. **Verify Realtor space**: Left column shows "Realtor" (not "Real Estate Listings")
6. **Verify no inline market**: No building market text on the board surface
7. **Click "Real Estate Listings" button** (bottom-left, next to My Quests): popup should show face-up buildings with full details
8. **Click button again**: popup should close (toggle)
9. **Open My Quests, then click Real Estate Listings**: My Quests closes, Real Estate Listings opens
10. **Place worker on Realtor**: Purchase dialog should appear with title "Real Estate Listings"
11. **Verify rendering**: Board should look smooth at 60fps with no visual differences from batched rendering

## Key Files Modified

| File | What Changes |
|------|-------------|
| `config/board.json` | Rename real_estate_listings → realtor |
| `client/ui/board_renderer.py` | Remove labels, shift layout, batch shapes with ShapeElementList, remove inline market |
| `client/views/game_view.py` | Add "Real Estate Listings" toggle button, add building market popup panel, rename references |
| `client/ui/dialogs.py` | Update purchase dialog title to "Real Estate Listings" |
| `server/game_engine.py` | Rename real_estate_listings → realtor in space references |
