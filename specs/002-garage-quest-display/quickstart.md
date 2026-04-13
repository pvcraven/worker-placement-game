# Quickstart: Garage Quest Display Rework

**Date**: 2026-04-13 | **Feature**: 002-garage-quest-display

## Scenario 1: Player Selects a Quest Card (Spot 1)

1. Game is in progress. Four face-up quest cards are displayed at The Garage.
2. Player places a worker on The Garage Spot 1 (quest + 2 coins).
3. Server validates the spot is unoccupied and places the worker.
4. Client shows a card selection dialog with the four face-up quest cards.
5. Player clicks on "Late Night Sessions" (a jazz quest).
6. Client sends `select_quest_card` with the card ID.
7. Server validates the card is in the face-up display, moves it to the player's hand, grants 2 coins, draws a replacement card from the deck.
8. Server broadcasts `quest_card_selected` to all players and `face_up_quests_updated` with the new display.
9. All clients update the face-up display. The selecting player sees the card in their hand (via toggle).

## Scenario 2: Player Resets the Quest Display (Spot 3)

1. Player places a worker on The Garage Spot 3 (reset quests).
2. Server discards all four face-up quest cards to the discard pile.
3. Server draws four new cards from the quest deck.
4. Server broadcasts `quests_reset` and `face_up_quests_updated`.
5. All clients see four new quest cards in the face-up display.

## Scenario 3: Deck Empty — Reshuffle Triggered

1. The quest deck has 1 card remaining. Face-up display has 3 cards (1 slot empty).
2. Player uses Spot 3 (reset). The 3 face-up cards are discarded.
3. Server draws 1 card from the deck (now empty).
4. Server reshuffles the discard pile (all previously discarded cards) into a new deck.
5. Server draws 3 more cards to fill the display.
6. Server broadcasts `quests_reset` (with `deck_reshuffled: true`) and `face_up_quests_updated`.

## Scenario 4: Player Toggles Hand Display

1. During the game, player clicks "My Quests" toggle button.
2. An overlay panel appears showing all quest cards in the player's hand, rendered using the existing card renderer.
3. Player clicks the toggle again — the panel hides.
4. Player clicks "My Intrigue" toggle — intrigue card panel appears.
5. Other players cannot see this player's hand at any point.

## Scenario 5: Backstage (Renamed from Garage)

1. Player places a worker on Backstage Slot 1 and plays an intrigue card. 
2. The mechanic works identically to the old "Garage" — intrigue card resolves immediately.
3. At end of round, Backstage workers are reassigned in slot order (1, 2, 3) to unoccupied action spaces.
4. Board labels show "BACKSTAGE" instead of "THE GARAGE."
5. Log messages reference "Backstage" instead of "Garage."

## Verification Checklist

- [ ] All "Cliffwatch Inn" references replaced with "The Garage" in UI, config, and logs
- [ ] All old "Garage" references replaced with "Backstage" in UI, config, and logs  
- [ ] Four face-up quest cards displayed at game start
- [ ] Spot 1: quest selection + 2 coins
- [ ] Spot 2: quest selection + 1 intrigue card
- [ ] Spot 3: discard all face-up, draw 4 new
- [ ] Deck reshuffle works when deck is empty
- [ ] Toggle buttons show/hide player's quest hand
- [ ] Toggle buttons show/hide player's intrigue hand
- [ ] Other players' hands are not visible
- [ ] Backstage intrigue/reassignment works as before (just renamed)
