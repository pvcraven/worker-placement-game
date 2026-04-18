# Quickstart Test Scenarios: Quest Reward Expansion

## Prerequisites

- Start a game with at least 1 player
- Ensure the quest deck includes new quests with expanded rewards

## Scenario 1: Quest with VP + Bonus Resources (Existing Behavior)

1. Complete a quest that costs resources and rewards VP + bonus resources
2. **Verify**: Resources deducted, VP awarded, bonus resources added
3. **Verify**: Resource bar updates immediately
4. **Verify**: Game log shows completion message

## Scenario 2: Quest with Intrigue Card Draw Reward

1. Complete a quest that rewards VP + "draw 1 intrigue card"
2. **Verify**: VP and any bonus resources awarded
3. **Verify**: 1 intrigue card drawn from intrigue deck
4. **Verify**: Card appears in player's intrigue hand (visible in My Intrigue panel)
5. **Verify**: Game log shows "drew 1 intrigue card" in addition to other rewards

## Scenario 3: Quest with Random Quest Card Draw Reward

1. Complete a quest that rewards VP + "draw 1 quest card (random)"
2. **Verify**: VP and any bonus resources awarded
3. **Verify**: 1 quest card drawn from quest deck
4. **Verify**: Card appears in player's quest hand
5. **Verify**: Game log shows the draw

## Scenario 4: Quest with "Choose Quest from Face-Up" Reward

1. Complete a quest that rewards VP + "choose 1 quest from face-up"
2. **Verify**: VP and bonus resources awarded immediately
3. **Verify**: Player is shown the face-up quests and prompted to choose one
4. **Verify**: Chosen quest is added to player's hand
5. **Verify**: Face-up quest slot refills from deck
6. **Verify**: Turn advances after choice is made

## Scenario 5: Quest with Market Choice Building Reward

1. Complete a quest that rewards VP + "choose 1 building from Builder's Hall"
2. **Verify**: VP and bonus resources awarded immediately
3. **Verify**: Player is shown available face-up buildings and prompted to choose
4. **Verify**: Chosen building is assigned to the player at no coin cost
5. **Verify**: Building appears as a constructed building with an action space
6. **Verify**: Building market refills from deck
7. **Verify**: Turn advances after choice

## Scenario 6: Quest with Random Draw Building Reward

1. Complete a quest that rewards VP + "draw 1 building from stack"
2. **Verify**: VP and bonus resources awarded
3. **Verify**: Building drawn from building deck and auto-assigned to player
4. **Verify**: Building appears as constructed with action space
5. **Verify**: Game log shows which building was received
6. **Verify**: Turn advances normally (no player interaction needed)

## Scenario 7: Combined Rewards

1. Complete a quest that rewards VP + 1 guitarist + draw 1 intrigue card
2. **Verify**: All three reward components applied
3. **Verify**: Resource bar shows updated guitarist count
4. **Verify**: Intrigue hand shows new card
5. **Verify**: Game log shows all rewards

## Scenario 8: Empty Deck Handling

1. Set up a game where the intrigue deck is empty
2. Complete a quest that rewards "draw 1 intrigue card"
3. **Verify**: Draw is skipped (no crash, no error dialog)
4. **Verify**: All other rewards (VP, resources) still granted
5. **Verify**: Game log notes the deck was empty

## Scenario 9: Empty Building Market/Deck

1. Set up a game where the building market is empty
2. Complete a quest with a "market choice" building reward
3. **Verify**: Building reward skipped
4. **Verify**: All other rewards granted
5. **Verify**: Game log notes no buildings available

## Scenario 10: Quest Card Display

1. View a quest card with expanded rewards in hand or face-up
2. **Verify**: Card shows all reward components (VP, resources, card draws, building)
3. **Verify**: Reward description is clear and readable

## Scenario 11: Player Overview Accuracy

1. Complete a quest with card draw rewards
2. Open Player Overview panel
3. **Verify**: Intrigue and Quest hand counts reflect newly drawn cards
4. **Verify**: Resource counts reflect spent and gained resources
