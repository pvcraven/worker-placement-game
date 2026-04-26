# Quickstart: Resource Trigger Plot Quests

## Test Scenarios

### Scenario 1: Simple resource bonus (on_gain_guitarist)

1. Start a game with 2 players.
2. Give Player 1 the "Rock Loyalty Program" card and enough resources to complete it.
3. Player 1 completes "Rock Loyalty Program" (it's now in completed_contracts).
4. Player 1 places a worker on a space that grants at least 1 Guitarist.
5. **Expected**: Player 1 receives the normal reward PLUS 1 extra Guitarist. The game log shows the trigger bonus.

### Scenario 2: Coins trigger (on_gain_coins_bass)

1. Player 1 has completed "Payola Pipeline".
2. Player 1 places a worker on a space that grants Coins.
3. **Expected**: Player 1 receives normal Coins PLUS 1 Bass Player.

### Scenario 3: Intrigue draw trigger (on_gain_guitarist_i)

1. Player 1 has completed "Explore the Groove Archive".
2. Player 1 places a worker on a space granting Guitarists.
3. **Expected**: Player 1 receives normal reward PLUS 1 Intrigue card added to hand.

### Scenario 4: Multiple triggers from same resource

1. Player 1 has completed both "Rock Loyalty Program" AND "Explore the Groove Archive".
2. Player 1 places a worker on a space granting Guitarists.
3. **Expected**: Player 1 receives normal reward PLUS 1 extra Guitarist PLUS 1 Intrigue card.

### Scenario 5: Singer swap trigger (on_gain_singer_swap)

1. Player 1 has completed "Miracle at the Microphone" and owns 2 Guitarists, 1 Drummer.
2. Player 1 places a worker on a space granting 1 Singer.
3. **Expected**: Player 1 receives the Singer, then sees a prompt to optionally trade 1 non-Singer resource for 1 additional Singer.
4. Player 1 selects "Guitarist" to trade.
5. **Expected**: Player 1 loses 1 Guitarist, gains 1 additional Singer (2 total from this action).

### Scenario 6: Singer swap declined

1. Same setup as Scenario 5.
2. Player 1 receives the Singer, sees the swap prompt, and clicks Skip/Cancel.
3. **Expected**: No swap happens. Player 1 keeps their original resources plus the 1 Singer from the space.

### Scenario 7: Singer swap with no tradeable resources

1. Player 1 has completed "Miracle at the Microphone" but owns 0 non-Singer resources.
2. Player 1 places a worker on a space granting Singers.
3. **Expected**: No swap prompt appears. Player 1 receives only the normal Singer reward.

### Scenario 8: No cascade

1. Player 1 has completed "Payola Pipeline" (coins→bass) AND "Fence Bootleg Recordings" (bass→coins).
2. Player 1 places a worker on a space granting 4 Coins.
3. **Expected**: Player 1 receives 4 Coins + 1 Bass Player (from Payola trigger). The bonus Bass Player does NOT trigger Fence Bootleg's coins bonus.

### Scenario 9: Trigger during reassignment

1. Player 1 has completed "Rock Loyalty Program".
2. During reassignment phase, Player 1 reassigns a backstage worker to a space granting Guitarists.
3. **Expected**: Trigger fires — Player 1 gets the normal reward plus 1 extra Guitarist.

### Scenario 10: No trigger from quest rewards

1. Player 1 has completed "Rock Loyalty Program".
2. Player 1 completes a quest whose bonus_resources include Guitarists.
3. **Expected**: No trigger fires. The bonus Guitarist from the quest is the only reward. Triggers only fire from board actions.

### Scenario 11: No trigger from intrigue effects

1. Player 1 has completed "Payola Pipeline" (coins→bass).
2. An intrigue card grants Player 1 coins.
3. **Expected**: No trigger fires. Intrigue effects are not board actions.
