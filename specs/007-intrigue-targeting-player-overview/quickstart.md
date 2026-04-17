# Quickstart: Intrigue Targeting & Player Overview Testing

## Prerequisites

- Server running: `python -m server`
- Client running: `python -m client`
- Min players set to 1 (already configured in game_rules.json)

## Test Scenario 1: Steal Resources — 2-Player Game

1. Create a 2-player game and start it
2. Both players place workers until one player has a steal_resources intrigue card (e.g., "Poach the Vocalist")
3. Place a worker on a backstage slot and select the steal card
4. **Verify**: A target selection dialog appears showing the opponent with their relevant resource counts
5. Select the opponent
6. **Verify**: The resource is transferred — your resource count increases, opponent's decreases
7. **Verify**: Game log shows "Player X stole 1 singer from Player Y" or similar

## Test Scenario 2: Steal Resources — No Valid Targets

1. Create a solo game (1 player)
2. Place a worker on a backstage slot and select a steal_resources intrigue card
3. **Verify**: A message appears saying no valid targets exist
4. **Verify**: The backstage placement is unwound — worker returns, card returns to hand

## Test Scenario 3: Steal Resources — Cancel

1. Create a 2-player game
2. Place a worker on backstage, select a steal card
3. When the target selection dialog appears, click "Cancel"
4. **Verify**: Dialog closes, backstage placement is unwound, worker and card are restored

## Test Scenario 4: Opponent Loses Resources

1. Create a 2-player game
2. Play an "opponent_loses" intrigue card (e.g., "Sabotaged Soundcheck")
3. Select the opponent as target
4. **Verify**: The opponent loses the specified resources
5. **Verify**: The active player does NOT gain those resources (unlike steal)

## Test Scenario 5: Partial Steal (Opponent Has Less Than Card Specifies)

1. In a 2-player game, ensure the opponent has exactly 0 of a targeted resource (e.g., 0 singers)
2. Play a steal card targeting singers
3. **Verify**: The dialog shows the opponent but after targeting, 0 singers are stolen (no change)
4. **Verify**: No errors, game continues normally

## Test Scenario 6: Player Overview Panel — Basic Display

1. Start a game with 2+ players
2. Click the "Player Overview" button
3. **Verify**: A panel appears with a table showing all players
4. **Verify**: Each row shows: name, workers, guitarists, bass players, drummers, singers, coins, intrigue count, quest hand count, quests completed, VP
5. **Verify**: Your own row is visually highlighted

## Test Scenario 7: Player Overview Panel — Data Currency

1. Start a game, open the Player Overview panel, note the values
2. Close the panel, place a worker on a resource-granting space
3. Reopen the Player Overview panel
4. **Verify**: Your resource counts have updated to reflect the new state

## Test Scenario 8: Player Overview Panel — Toggle Behavior

1. Open the Player Overview panel
2. Click the "Player Overview" button again
3. **Verify**: Panel closes
4. Open the Player Overview panel, then click "My Quests"
5. **Verify**: Player Overview closes and My Quests opens (mutually exclusive)
