# Data Model: Garage Quest Display Rework

**Date**: 2026-04-13 | **Feature**: 002-garage-quest-display

## Entity Changes

### Modified: BoardState

Add quest deck management fields to the existing `BoardState` model in `server/models/game.py`:

| Field | Type | Description |
|-------|------|-------------|
| `face_up_quests` | `list[ContractCard]` | Four face-up quest cards visible to all players. Max length 4. |
| `quest_deck` | `list[ContractCard]` | Shuffled draw pile. Cards drawn from the front. |
| `quest_discard` | `list[ContractCard]` | Discard pile for Spot 3 resets. Reshuffled into deck when deck is empty. |
| `backstage_slots` | `list[BackstageSlot]` | Renamed from `garage_slots`. 3 numbered slots for intrigue play + reassignment. |

Remove: `garage_slots` (renamed to `backstage_slots`)

### Renamed: GarageSlot → BackstageSlot

The existing `GarageSlot` class is renamed to `BackstageSlot`. No field changes:

| Field | Type | Description |
|-------|------|-------------|
| `slot_number` | `int` | 1, 2, or 3 |
| `occupied_by` | `str | None` | Player ID or None |
| `intrigue_card_played` | `dict | None` | The intrigue card played when landing on this slot |

### Modified: ActionSpace

The `space_type` field gains a new value and loses an old one:

| Old space_type | New space_type | Description |
|----------------|----------------|-------------|
| `"cliffwatch"` | `"garage"` | Quest acquisition spots (3 distinct spots) |
| `"garage"` | `"backstage"` | Intrigue play + reassignment slots |

New field on ActionSpace for garage spots:

| Field | Type | Description |
|-------|------|-------------|
| `reward_special` | `str` | New values: `"quest_and_coins"` (Spot 1), `"quest_and_intrigue"` (Spot 2), `"reset_quests"` (Spot 3) |

### Modified: GameState

No structural changes. The `completed_contracts` list on each Player already tracks completed quests (these are never returned to the deck). Player hand fields already exist:

| Field | Type | Notes |
|-------|------|-------|
| `contracts` | `list[ContractCard]` | Player's quest hand (no size limit) |
| `intrigue_cards` | `list[IntrigueCard]` | Player's intrigue hand (no size limit) |

## State Transitions

### Quest Card Lifecycle

```
[Quest Deck] → draw → [Face-Up Display] (4 slots)
                            │
                     ┌──────┼──────────┐
                     │      │          │
                  Spot 1  Spot 2    Spot 3
                  Spot 2             (reset)
                     │               │
                     ▼               ▼
              [Player Hand]    [Discard Pile]
                     │               │
                  Complete      Deck empty?
                     │          Yes: shuffle
                     ▼          back to deck
              [Completed]           │
              (permanent,           ▼
              never returns)   [Quest Deck]
```

### Deck Reshuffle Trigger

1. A card draw is requested (replacement draw or Spot 3 reset)
2. Quest deck is empty
3. Check discard pile: if non-empty, shuffle and move all cards to quest deck
4. Draw from deck (if still empty after reshuffle, slot remains empty)

## Naming Changes Summary

| Entity | Old Name | New Name |
|--------|----------|----------|
| Intrigue/reassignment slot model | `GarageSlot` | `BackstageSlot` |
| Board state field | `garage_slots` | `backstage_slots` |
| Intrigue slot constant | `GARAGE_SLOTS` | `BACKSTAGE_SLOTS` |
| Quest acquisition space type | `"cliffwatch"` | `"garage"` |
| Intrigue/reassignment space type | `"garage"` | `"backstage"` |
