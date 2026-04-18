# Quickstart: Board Layout Optimization

## Test Scenarios

### Scenario 1: Board Renders with New Layout
1. Start a game with 2 players
2. Verify quest cards are visible on the board (upper-center area)
3. Verify face-up buildings are visible on the board (lower-center area) — no popup needed
4. Verify backstage slots are in the left column
5. Verify Realtor space is near the building display
6. Verify no "Real Estate Listings" button exists

### Scenario 2: Inline Quest Selection
1. Start a game, it's Player 1's turn
2. Click on "The Garage 1" space to place a worker
3. Verify the 4 face-up quest cards gain yellow highlight borders
4. Verify a red cancel button appears in the lower-left corner
5. Click on one of the highlighted quest cards
6. Verify the quest is selected (appears in hand), highlights disappear, cancel button disappears

### Scenario 3: Quest Selection Cancel
1. Place a worker on a Garage space
2. Verify highlights appear on quest cards
3. Click the red cancel button
4. Verify highlights disappear, cancel button disappears, worker placement is cancelled

### Scenario 4: Inline Building Purchase
1. Ensure the current player has enough coins to afford at least one building
2. Place a worker on the Realtor space
3. Verify affordable buildings gain yellow highlight borders
4. Verify unaffordable buildings do NOT have highlights
5. Verify cancel button appears
6. Click on a highlighted (affordable) building
7. Verify the building is purchased, appears in constructed buildings, highlights disappear

### Scenario 5: Building Purchase - Can't Afford Any
1. Ensure the current player has 0 coins
2. Place a worker on the Realtor space
3. Verify an error message appears (e.g., "You can't afford any buildings")
4. Verify no buildings are highlighted

### Scenario 6: Building Purchase Cancel
1. Place a worker on the Realtor space (with enough coins)
2. Verify building highlights appear
3. Click the red cancel button
4. Verify highlights disappear, purchase is cancelled

### Scenario 7: Click Unaffordable Building
1. Place a worker on the Realtor space
2. Click on a building that is NOT highlighted (unaffordable)
3. Verify an error message appears
4. Verify highlight state remains active (not dismissed)

### Scenario 8: Building Market Updates
1. Player purchases a building
2. Verify the purchased building disappears from the on-board display
3. Verify a replacement building is drawn from the deck (if available)

### Scenario 9: Quest Reward - Choose Free Building
1. Complete a quest that rewards "Choose Free Building"
2. Verify all face-up buildings become highlighted (cost=0 for reward)
3. Click a building to claim it
4. Verify building moves to constructed buildings

### Scenario 10: Window Resize During Highlight
1. Enter highlight mode (place worker on garage)
2. Resize the window
3. Verify highlights reposition correctly with the cards

### Scenario 11: All Existing Features Still Work
1. Play a full round: place workers, complete quests, use intrigue, backstage reassignment
2. Verify nothing is broken by the layout changes
