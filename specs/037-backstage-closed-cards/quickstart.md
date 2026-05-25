# Quickstart: Backstage Closed Cards

## Test Scenarios

### Scenario 1: Backstage shows CLOSED during reassignment

1. Start a game with 2+ players
2. Place workers normally through the placement phase (including backstage slots)
3. When all workers are placed, the reassignment phase begins
4. **Verify**: All backstage slot cards now display "CLOSED" in dark red with a box border instead of "Play Intrigue"

### Scenario 2: Backstage reverts after reassignment

1. Continue from Scenario 1
2. Complete all reassignment actions
3. The round ends and a new round begins (placement phase)
4. **Verify**: All backstage slot cards now display "Play Intrigue" again (normal appearance)

### Scenario 3: Reconnect during reassignment

1. Start a game and reach the reassignment phase
2. Disconnect one player (close their client window)
3. Reconnect the player
4. **Verify**: The reconnected player's backstage cards show "CLOSED" since the game is in reassignment phase

### Scenario 4: First round (no reassignment yet)

1. Start a new game
2. **Verify**: Backstage cards show "Play Intrigue" (normal state) since the game starts in placement phase

## Card Image Verification

1. Run `python card-generator/generate_cards.py`
2. Check `client/assets/card_images/spaces/` for new files:
   - `backstage_slot_1_closed.png`
   - `backstage_slot_2_closed.png`
   - `backstage_slot_3_closed.png`
3. **Verify**: Each closed card has the same "Backstage N" title band as the normal card, but shows "CLOSED" in dark red text with a box border in the card body
