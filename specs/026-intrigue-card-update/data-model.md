# Data Model: Intrigue Card Update

## New Intrigue Cards (config/intrigue.json)

14 new entries added to the `intrigue_cards` array. All use the existing `IntrigueCard` schema from `shared/card_models.py`.

### Do-Nothing Cards (4 cards, IDs intrigue_055–intrigue_058)

| Field | Value |
|-------|-------|
| effect_type | `"no_effect"` |
| effect_target | `"self"` |
| effect_value | `{}` |

Card names and descriptions (music industry humor):
- **intrigue_055**: "Mom's Surprise Visit" — "Your mom showed up at the studio unannounced. Everyone is on their best behavior. Nothing gets done."
- **intrigue_056**: "Fire Drill" — "The building's fire alarm goes off during a recording session. Everyone stands in the parking lot for 20 minutes. Nothing happens."
- **intrigue_057**: "Wrong Studio" — "You walk into the wrong recording studio and sit through an entire meeting before realizing your mistake. A complete waste of time."
- **intrigue_058**: "Power Nap" — "You dozed off on the studio couch and dreamed you were productive. You weren't."

### Draw-1-Intrigue Cards (4 cards, IDs intrigue_059–intrigue_062)

| Field | Value |
|-------|-------|
| effect_type | `"draw_intrigue"` |
| effect_target | `"self"` |
| effect_value | `{"count": 1}` |

Card names:
- **intrigue_059**: "Water Cooler Gossip" — "Hang around the studio water cooler and pick up a juicy piece of industry intel."
- **intrigue_060**: "Overheard Phone Call" — "You accidentally overhear a phone conversation in the next booth. Interesting..."
- **intrigue_061**: "Coffee Run Tip-Off" — "The barista at the corner cafe slips you a note with a hot tip."
- **intrigue_062**: "Parking Lot Encounter" — "You bump into an old contact in the parking lot who shares some inside info."

### Reset-Quests Cards (2 cards, IDs intrigue_063–intrigue_064)

| Field | Value |
|-------|-------|
| effect_type | `"reset_quests"` |
| effect_target | `"self"` |
| effect_value | `{}` |

Card names:
- **intrigue_063**: "New Wave Movement" — "A fresh wave of musical talent shakes up the industry. All the old contracts are out — new opportunities are in."
- **intrigue_064**: "Genre Revolution" — "An underground movement explodes into the mainstream, reshuffling every deal on the table."

### Reset-Buildings Cards (2 cards, IDs intrigue_065–intrigue_066)

| Field | Value |
|-------|-------|
| effect_type | `"reset_buildings"` |
| effect_target | `"self"` |
| effect_value | `{}` |

Card names:
- **intrigue_065**: "Zoning Shakeup" — "City hall announces a major rezoning. The old properties are swept off the market and new ones take their place."
- **intrigue_066**: "Real Estate Crash" — "A sudden market downturn clears the board. Developers scramble to offer fresh properties."

### First-Player-Marker Cards (2 cards, IDs intrigue_067–intrigue_068)

| Field | Value |
|-------|-------|
| effect_type | `"first_player_marker"` |
| effect_target | `"self"` |
| effect_value | `{}` |

Card names:
- **intrigue_067**: "Early Bird Special" — "You set your alarm for 4 AM and beat everyone to the studio. First come, first served."
- **intrigue_068**: "Red-Eye Flight" — "You took the overnight flight to get here before anyone else. Exhausted but first in line."

## Model Changes

### BoardState (server/models/game.py)

**New field**:
- `building_discard: list[BuildingTile] = Field(default_factory=list)` — Discard pile for buildings removed from face-up display. Reshuffled into `building_deck` when deck is depleted.

**Existing fields used** (no changes needed):
- `quest_discard: list[ContractCard]` — Already exists
- `quest_deck: list[ContractCard]` — Already exists
- `building_deck: list[BuildingTile]` — Already exists
- `face_up_quests: list[ContractCard]` — Already exists
- `face_up_buildings: list[BuildingTile]` — Already exists
- `first_player_id: str` — Already exists

### IntrigueCard (shared/card_models.py)

No changes needed. The existing schema supports all new effect types via the `effect_type: str` field.

## State Transitions

### Quest Reset Flow
```
face_up_quests → quest_discard (discarded cards)
quest_deck → face_up_quests (new cards drawn)
If quest_deck empty: quest_discard → quest_deck (reshuffle, excluding completed)
```

### Building Reset Flow
```
face_up_buildings → building_discard (discarded cards)
building_deck → face_up_buildings (new cards drawn)
If building_deck empty: building_discard → building_deck (reshuffle)
```

### First Player Marker Flow
```
all players: has_first_player_marker = False
playing player: has_first_player_marker = True
board.first_player_id = playing player's ID
```
