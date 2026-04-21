# Quickstart: Tabbed Side Panel

## Setup

No additional setup required. This is a client-side UI change using existing dependencies.

## Manual Testing Scenarios

### Scenario 1: Basic Tab Switching

1. Start the server and client
2. Create a game, join with 2+ players, start the game
3. The right panel should show "Game Log" tab as active with log entries below
4. Click each tab: "My Quests", "My Intrigue", "Completed Quests", "Producer"
5. Verify: title changes, content changes, active tab is visually highlighted

### Scenario 2: Card Two-Column Layout

1. During gameplay, draw some quest cards (place workers on Garage spots)
2. Click the "My Quests" tab
3. Verify cards appear in a 2-column grid within the panel
4. Verify cards don't overflow the panel width

### Scenario 3: Tab Switching During Dialogs

1. During gameplay, place a worker on a Backstage slot (triggers intrigue card selection)
2. While the intrigue selection dialog is visible, click the "My Quests" tab
3. Verify: the panel switches to quests view, and the dialog remains open
4. Click back to the dialog and complete the selection
5. Verify: the action completes normally

### Scenario 4: Window Resize

1. While viewing any tab, resize the window
2. Verify: tab bar, title, and content scale proportionally
3. Card views maintain 2-column layout at the new size

### Scenario 5: Empty States

1. At game start (before drawing any quests), click "Completed Quests"
2. Verify: panel shows "No completed quests" message
3. Click "My Quests" with no quests drawn
4. Verify: panel shows "No quests" message

## Verification Checklist

- [ ] All 5 tabs are clickable and switch content
- [ ] Active tab is visually distinct from inactive tabs
- [ ] Game log scroll still works in its tab
- [ ] Cards display in 2 columns in all card tabs
- [ ] Producer card image displays in Producer tab
- [ ] Empty state messages show when no data
- [ ] Tabs work while dialogs are open
- [ ] Window resize preserves layout
- [ ] Old dialog buttons are removed
- [ ] "Player Overview" button still works separately
