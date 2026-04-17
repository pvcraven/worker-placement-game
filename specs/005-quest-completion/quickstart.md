# Quickstart: Quest Completion Testing

## Prerequisites

- Server running: `python -m server`
- Client running: `python -m client`
- Min players set to 1 (already configured in game_rules.json)

## Test Scenario 1: Quest Completion Dialog Appears

1. Create and start a solo game
2. Place a worker on a resource space to gain resources
3. Place a worker on "The Garage" and select a quest card with affordable cost
4. Continue placing workers and gaining resources until you meet a quest's cost
5. Place another worker — after placement resolves, the quest completion dialog should appear
6. **Verify**: Dialog shows the quest card(s) you can afford, arranged horizontally, with a "Skip" button

## Test Scenario 2: Complete a Quest

1. Follow Scenario 1 until the dialog appears
2. Click on a quest card in the dialog
3. **Verify**: Quest is removed from your hand, VP increases by the quest's value, resources are deducted, turn advances

## Test Scenario 3: Skip Quest Completion

1. Follow Scenario 1 until the dialog appears
2. Click "Skip"
3. **Verify**: Dialog closes, no resources are deducted, no VP change, turn advances normally

## Test Scenario 4: No Eligible Quests

1. Start a game with no quests in hand (or insufficient resources for all held quests)
2. Place a worker
3. **Verify**: No dialog appears, turn advances immediately

## Test Scenario 5: Status Line Display

1. Start a game and observe the bottom of the screen
2. **Verify**: A status line shows "Workers left: [N]  VP: [M]" above the resource bar
3. Place a worker
4. **Verify**: Workers left count decreases by 1
5. Complete a quest
6. **Verify**: VP count increases accordingly
