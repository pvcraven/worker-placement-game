# Quickstart: Intrigue Draw Building

## What This Feature Does

Adds a new purchasable building called **"Whisper Room"** to the game. When a player places a worker on it, they draw 2 intrigue cards from the deck. The building owner gets 2 VP when another player visits.

## How to Test

1. Start a multiplayer game (2+ players)
2. Purchase the "Whisper Room" building from the Realtor (costs 4 coins)
3. On a subsequent round, place a worker on the Whisper Room
4. Verify: 2 intrigue cards appear in the Intrigue tab of the side panel
5. Verify: Game log shows "Player A placed worker on Whisper Room (+2 intrigue cards)"
6. Have a second player visit the building
7. Verify: Building owner receives 2 VP

## Edge Cases to Test

- **Deck has 1 card**: Place worker on Whisper Room when deck has only 1 intrigue card remaining. Should draw 1 card without error.
- **Deck empty**: Place worker when deck is completely empty. Should draw 0 cards without error.
- **Shadow Studio copy**: Use Shadow Studio to copy the Whisper Room. Should also draw 2 intrigue cards.
- **Worker reassignment**: During reassignment phase, place on Whisper Room. Should draw 2 intrigue cards.

## Files Changed

| File | What Changed |
|------|-------------|
| `config/buildings.json` | New building entry for Whisper Room |
| `server/game_engine.py` | Handle `draw_intrigue_2` in 3 locations |
| `client/views/game_view.py` | Handle 2-card intrigue draw response |
| `card-generator/generate_cards.py` | Draw two intrigue icons for building card |
