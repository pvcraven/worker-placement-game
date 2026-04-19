# Quickstart: Sprite Card Rendering

**Feature**: Sprite Card Rendering
**Date**: 2026-04-18

## Prerequisites

- Python 3.12+
- Card images generated (auto-generated on client startup via `ensure_card_images()`)
- Game server running

## Run the Game

```bash
python client/main.py
```

## Verification Scenarios

### Scenario 1: Board Quest Cards Display as Sprites

1. Start the server and connect a client
2. Start a game so face-up quest cards appear on the board
3. Verify: quest cards display as parchment-colored PNG images with genre bands, text, and VP circles
4. Verify: cards are NOT rendered as plain colored rectangles with text overlays

### Scenario 2: Board Building Cards Display as Sprites

1. With a game in progress, observe the building card row on the board
2. Verify: building cards display as parchment-colored PNG images
3. Verify: cards show name, cost, visitor/owner rewards as rendered in the PNG

### Scenario 3: Quest Card Highlighting

1. Enter highlight mode (e.g., quest completion prompt)
2. Verify: highlighted quest cards have a visible colored outline around the sprite
3. Verify: non-highlighted cards display normally without outline

### Scenario 4: Building Card Highlighting

1. Enter building purchase mode
2. Verify: highlighted building cards have a visible colored outline
3. Verify: clicking a highlighted building card triggers the purchase action

### Scenario 5: Quest Card Click Detection

1. With face-up quest cards on the board
2. Click on a quest card
3. Verify: click is detected correctly, triggering the appropriate action
4. Verify: clicking between cards does NOT trigger a card action

### Scenario 6: Hand Panel Quest Cards

1. Press the key to open the quest hand panel
2. Verify: quest cards in hand display as PNG sprites
3. Verify: up to 6 cards display correctly with proper spacing

### Scenario 7: Hand Panel Intrigue Cards

1. Press the key to open the intrigue hand panel
2. Verify: intrigue cards in hand display as PNG sprites
3. Verify: cards show intrigue card images (green-tinted with effect text)

### Scenario 8: Quest Completion Dialog

1. Complete a turn that triggers the quest completion dialog
2. Verify: quest cards in the dialog display as PNG sprites
3. Verify: clicking a card or "Skip" still works correctly

### Scenario 9: Card Data Changes

1. During gameplay, observe when face-up quest cards change (card taken, new card drawn)
2. Verify: the board updates to show the new card's sprite image
3. Verify: removed cards no longer appear

### Scenario 10: Empty Hand Panel

1. Open the hand panel when the player has no cards
2. Verify: "No cards" message displays (no sprites needed)

### Scenario 11: CardRenderer Removed

1. Verify `card_renderer.py` no longer exists or is unused
2. Verify no imports of `CardRenderer` remain in the codebase
