# Quickstart: Intrigue Card Animation

**Date**: 2026-05-16

## What This Feature Does

Adds visual animations when intrigue cards are drawn or played, matching the existing quest card animation style. Also generates a full-size face-down intrigue card image for opponent draw animations.

## Key Files to Modify

1. **`card-generator/generate_cards.py`** — Add `generate_intrigue_back()` function to produce `intrigue_back.png`
2. **`shared/messages.py`** — Add `intrigue_card_id` and `intrigue_card_name` fields to `IntrigueEffectResolvedResponse`
3. **`server/game_engine.py`** — Include card details in intrigue effect resolution broadcasts; broadcast for non-targeting plays
4. **`client/views/game_view.py`** — Add intrigue draw/play animation functions; hook into `_on_quest_completed()`, backstage handler, and effect resolution handler

## Implementation Order

1. Generate `intrigue_back.png` (no dependencies)
2. Update server message model + handlers (independent of client)
3. Add client draw animation for quest rewards
4. Add client draw animation for backstage
5. Add client play animation
6. Test end-to-end

## How to Test

1. Run card generator: `cd card-generator && python generate_cards.py`
2. Verify `client/assets/card_images/intrigue/intrigue_back.png` exists at 400×500
3. Run tests: `cd src && pytest`
4. Manual: Start server + two clients, complete quests with intrigue rewards, observe animations
5. Manual: Place worker on backstage, observe draw animation
6. Manual: Play intrigue cards, observe play animation on both clients
