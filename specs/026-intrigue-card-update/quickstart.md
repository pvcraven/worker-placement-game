# Quickstart: Intrigue Card Update

## What This Feature Does

Adds 14 new intrigue cards across 5 categories, plus a global deck reshuffle mechanic for quests and buildings.

## How to Test

### Do-Nothing Cards (4 cards)
1. Start a game and draw intrigue cards until you get one named "Mom's Surprise Visit", "Fire Drill", "Wrong Studio", or "Power Nap"
2. Play the card at a backstage slot
3. Verify: Card is consumed, game log shows "[Player] played [Card Name]", no resources or state changes occur

### Draw-1-Intrigue Cards (4 cards)
1. Draw intrigue cards until you get "Water Cooler Gossip", "Overheard Phone Call", "Coffee Run Tip-Off", or "Parking Lot Encounter"
2. Note your intrigue hand size, then play the card
3. Verify: Hand size stays the same (1 removed, 1 drawn), game log shows the draw

### Reset-Quests Cards (2 cards)
1. Draw until you get "New Wave Movement" or "Genre Revolution"
2. Note the face-up quests at The Garage
3. Play the card
4. Verify: All face-up quests are replaced with new ones, game log shows "quests refreshed"

### Reset-Buildings Cards (2 cards)
1. Draw until you get "Zoning Shakeup" or "Real Estate Crash"
2. Note the face-up buildings at the Realtor
3. Play the card
4. Verify: All face-up buildings are replaced with new ones, game log shows "buildings refreshed"

### First-Player-Marker Cards (2 cards)
1. In a 2+ player game, draw until you get "Early Bird Special" or "Red-Eye Flight"
2. Play the card (as a non-first player)
3. Verify: Next round, you go first
4. Verify: Game log shows "will go first next round"

### Deck Reshuffle (Global)
1. Play through a game until the quest or building deck runs low
2. Play a reset card or let end-of-round refill trigger with an empty deck
3. Verify: Discard pile is reshuffled into the deck and new cards appear
4. Verify: No completed quests reappear in the reshuffled quest deck

## Edge Cases to Test

- **Empty intrigue deck**: Play a draw-1-intrigue card when deck is empty — should consume card but draw nothing
- **Two first-player cards**: Two players both play first-player cards — last one played wins
- **Building reshuffle**: Purchase most buildings, then play reset-buildings — discarded buildings should reshuffle into deck

## Files Changed

| File | What Changed |
|------|-------------|
| `config/intrigue.json` | 14 new intrigue card entries |
| `server/game_engine.py` | New effect handlers: no_effect, reset_quests, reset_buildings, first_player_marker; new `_draw_from_building_deck()` helper |
| `server/models/game.py` | New `building_discard` field on BoardState |
| `card-generator/generate_cards.py` | Icon rendering and effect summaries for new effect types |
