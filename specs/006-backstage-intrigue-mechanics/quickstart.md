# Quickstart: Backstage & Intrigue Mechanics Testing

## Prerequisites

- Server running: `python -m server`
- Client running: `python -m client`
- Min players set to 1 (already configured in game_rules.json)

## Test Scenario 1: Starting Resources

1. Create and start a solo game
2. **Verify**: Player has 4 coins displayed in the resource bar
3. **Verify**: Player has 2 intrigue cards (check game state or add intrigue hand display)

## Test Scenario 2: Starting Resources — Multi-Player

1. Create a 3-player game and start it
2. **Verify**: Player 1 has 4 coins, Player 2 has 6 coins, Player 3 has 8 coins
3. **Verify**: All players have 2 intrigue cards each

## Test Scenario 3: Backstage Placement with Intrigue Card

1. Start a solo game (player should have 2 intrigue cards from starting resources)
2. Click on Backstage slot 1
3. **Verify**: An intrigue card selection dialog appears showing the player's intrigue cards
4. Select an intrigue card
5. **Verify**: Worker is placed on Backstage 1, intrigue effect resolves, worker count decreases

## Test Scenario 4: Backstage Sequential Filling

1. After Scenario 3, click on Backstage slot 2
2. **Verify**: Placement succeeds (slot 1 is occupied)
3. Try clicking Backstage slot 3 without filling slot 2
4. **Verify**: If slot 2 is empty, placement is rejected

## Test Scenario 5: Backstage Cancel

1. Start a game with intrigue cards in hand
2. Click on Backstage slot 1
3. When the intrigue card selection dialog appears, click "Cancel"
4. **Verify**: Dialog closes, no worker is placed on the backstage slot, worker remains available

## Test Scenario 6: No Intrigue Cards — Backstage Blocked

1. Start a game and use up all intrigue cards (play them on backstage spots)
2. Try clicking a backstage spot with no intrigue cards in hand
3. **Verify**: Placement is rejected with a message about needing intrigue cards

## Test Scenario 7: Worker Reassignment

1. Start a game, place workers on backstage slots and other action spaces until all workers are placed
2. **Verify**: Reassignment phase starts, worker from Backstage 1 is freed
3. **Verify**: Player is prompted to place the freed worker on an open action space
4. Click an open action space
5. **Verify**: Worker is placed, reward is granted, next backstage slot is processed

## Test Scenario 8: Reassignment — No Backstage Placement

1. Start a game, place all workers on regular action spaces (not backstage)
2. **Verify**: When all workers placed, reassignment phase is skipped, round ends normally
