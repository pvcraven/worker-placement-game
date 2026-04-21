# Quickstart: Final Score Screen

**Feature**: 015-final-score-screen
**Date**: 2026-04-21

## Test Scenarios

### Scenario 1: Manual Toggle During Gameplay

1. Start a game with 2+ players
2. Play a few rounds (complete some quests, accumulate resources)
3. Click "Final Screen" button (to the right of "Player Overview")
4. **Verify**: Dialog appears as overlay on game board
5. **Verify**: Each player has a column with producer card, name, and VP rows
6. **Verify**: Own player shows all VP categories (game VP, genre bonus, resource VP, total)
7. **Verify**: Opponent columns show game VP, resource VP; genre bonus shows "?" (producer hidden)
8. **Verify**: Player with highest visible total has "WINNER" above their card
9. Click "Final Screen" button again → dialog closes
10. Click "Final Screen" → dialog opens → click "Close" button → dialog closes
11. **Verify**: Game continues normally after closing

### Scenario 2: Game-Over Automatic Display

1. Play a game to completion (all rounds finished)
2. **Verify**: Final score dialog appears automatically (no button click needed)
3. **Verify**: All players now show complete VP breakdown including genre bonus (producer cards revealed)
4. **Verify**: Winner(s) highlighted with "WINNER" above their card
5. **Verify**: "Final Screen" toggle button does NOT close the dialog
6. Click "Close" button
7. **Verify**: Player is navigated to the lobby screen

### Scenario 3: Edge Cases

1. **No completed quests**: Start a new game, immediately click "Final Screen"
   - All VP categories should show 0
   - All players tied at 0 → all show "WINNER"

2. **No producer card**: If a player has no producer assigned
   - Producer card area shows "No Producer" placeholder
   - Genre bonus shows 0

3. **Tied scores**: Two players with identical total VP
   - Both show "WINNER" above their cards

4. **Resource VP calculation**: Player has 3 guitarists, 2 singers, 5 coins
   - Resource VP = 3 + 2 + floor(5/2) = 5 + 2 = 7

5. **Single player**: Game with 1 player
   - That player is the winner

### Scenario 4: Visual Consistency

1. Open "Player Overview" — note the dialog style (background, border, positioning)
2. Close it, open "Final Screen"
3. **Verify**: Similar visual style (dark background, white border, centered overlay)
4. **Verify**: Dialog does not interfere with other UI elements
5. Resize window → dialog adjusts appropriately

### Scenario 5: Button Placement

1. Look at the bottom-left button area
2. **Verify**: "Player Overview" button is present
3. **Verify**: "Final Screen" button is to its right
4. **Verify**: Buttons do not overlap at various window sizes
