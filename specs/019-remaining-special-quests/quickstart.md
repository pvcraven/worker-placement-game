# Quickstart: Remaining Special Quest Mechanics

## Verification Scenarios

### Scenario 1: Play Intrigue on Quest Completion
1. Start a 2-player game
2. Give player 1 the "Jailhouse Jazz Session" quest and at least 1 intrigue card
3. Give player 1 enough resources to complete the quest (4 bass, 2 drums, 2 coins)
4. Complete the quest
5. **Verify**: Player is prompted to select an intrigue card from their hand
6. Select and play the intrigue card
7. **Verify**: Intrigue effect resolves normally, turn advances

### Scenario 2: Play Intrigue — No Cards in Hand
1. Same setup as Scenario 1 but player has 0 intrigue cards
2. Complete the quest
3. **Verify**: No intrigue prompt appears, turn advances normally

### Scenario 3: Opponent Gains Coins (2-player)
1. Start a 2-player game
2. Give player 1 "Charity Gala Showcase" and enough resources (1G, 1B, 1S, 4 coins)
3. Complete the quest
4. **Verify**: Opponent automatically receives 4 coins (no choice prompt)

### Scenario 4: Opponent Gains Coins (3+ player)
1. Start a 3-player game
2. Complete "Charity Gala Showcase"
3. **Verify**: Player is prompted to choose which opponent receives 4 coins
4. Choose an opponent
5. **Verify**: Chosen opponent's coin count increases by 4

### Scenario 5: Extra Worker
1. Complete "Hire a Tour Manager" (5G, 1B, 1D, 1S)
2. **Verify**: Player's total worker count increases by 1
3. **Verify**: The extra worker is NOT available this round
4. Advance to next round
5. **Verify**: Extra worker is now available

### Scenario 6: Round-Start Resource Choice
1. Complete "Soul Music Residency" (1G, 1B, 1D, 2S)
2. Advance to next round
3. **Verify**: Player is prompted to choose a non-coin resource (Guitarist, Bass Player, Drummer, or Singer)
4. Choose a resource
5. **Verify**: Chosen resource is added to player's pool, logged in game log
6. **Verify**: First turn of the round begins after choice is made

### Scenario 7: Worker Recall on Completion
1. Place a worker on a board space earlier in the round
2. Complete "Time Warp Remix" (2D, 4 coins)
3. **Verify**: Message appears at top of screen prompting to click a space to recall from
4. Click on the space where your worker is placed
5. **Verify**: Worker returns to pool, space is freed
6. **Verify**: Turn advances normally

### Scenario 7b: Worker Recall — No Workers Placed
1. Complete "Time Warp Remix" with no workers currently on the board
2. **Verify**: Recall step is skipped, turn advances normally

### Scenario 8: Use Occupied Building
1. Complete "Recover the Master Tapes" (3B, 2D)
2. Have another player place a worker on a building
3. On your turn, place a worker on that same occupied building
4. **Verify**: Placement succeeds, you get visitor reward, owner gets owner bonus
5. **Verify**: Both workers visible on the building
6. **Verify**: Cannot use ability again this round
7. **Verify**: Ability resets next round

### Scenario 9: Use Occupied — Own Building Blocked
1. With "Recover the Master Tapes" completed, place your own worker on a building
2. Try to place a second worker on that same building
3. **Verify**: Placement is rejected (ability only works for buildings occupied by OTHER players)

### Scenario 10: Backward Compatibility
1. Complete a normal quest (no special mechanics)
2. **Verify**: Standard rewards granted, no special prompts
3. Place workers normally on unoccupied spaces
4. **Verify**: No changes to standard placement flow
