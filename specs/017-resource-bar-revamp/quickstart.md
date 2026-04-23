# Quickstart: Resource Bar Revamp

## How to Generate Icons

```bash
cd card-generator
python generate_cards.py --icons-only
```

This generates resource and card icon PNGs in `client/assets/card_images/icons/`.

To regenerate all cards including icons:
```bash
python generate_cards.py
```

## How to Test Visually

1. Start the server: `cd src && python -m server`
2. Start the client: `cd src && python -m client`
3. Join a game and observe the bottom resource panel
4. Verify:
   - Parchment-colored background (tan, not dark)
   - Resource icons are colored sprites (orange/black/purple/white squares, gold circles)
   - Quest counts show miniature "Q" card icon
   - Intrigue count shows miniature "I" card icon
   - Worker marker (colored circle) appears next to "Workers left"
   - Text is dark brown, Tahoma font

## How to Test Scaling

1. Resize the game window to various sizes
2. Verify icons and text scale proportionally without overlapping
3. Verify no visual glitches when rapidly resizing

## How to Test Fallback

1. Temporarily rename/delete a resource icon PNG from `icons/`
2. Launch the game
3. Verify the panel still renders without crashing (graceful fallback)

## Key Files

| File | Purpose |
|------|---------|
| `card-generator/generate_cards.py` | Generates resource icon and card icon PNGs |
| `client/ui/resource_bar.py` | Renders the bottom panel with sprites |
| `client/views/game_view.py` | Passes player data to resource bar |
| `client/assets/card_images/icons/` | Generated icon PNGs |
| `client/assets/card_images/markers/` | Existing worker marker PNGs |
