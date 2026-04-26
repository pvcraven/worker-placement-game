# Building Mapping Analysis: Waterdeep → Music Theme

## Resource Mapping

| Waterdeep | Music Theme |
|-----------|-------------|
| Fighter | Guitarist |
| Rogue | Bass Player |
| Cleric | Singer |
| Wizard | Drummer |
| Gold | Coins |
| Tavern | Pool/Hand |
| VP | Victory Points |

---

## Building-by-Building Mapping

### Legend

- **Match** = Mechanics are identical (just re-themed)
- **Diff** = Mechanics differ from source material
- **Missing** = No corresponding building in our game

---

### Accumulation Buildings (place resources/coins/VP on the space each round)

| # | Waterdeep | Our Building | Cost | Match? | Notes |
|---|-----------|-------------|------|--------|-------|
| 1 | Caravan Court | building_001 The Troubadour | 4g | **Match** | Accumulates 2 Fighters/Guitarists. Owner: 1 Fighter/Guitarist. |
| 2 | Jester's Court | building_002 The Cavern Club | 4g | **Match** | Accumulates 2 Rogues/Bass Players. Owner: 1 Rogue/Bass Player. |
| 3 | Spires of the Morning | building_003 Hansa Studios | 4g | **Diff** | Accumulates 1 Cleric/Singer. **Waterdeep owner: 2 VP. Ours: draw_intrigue.** |
| 4 | Tower of Order | building_004 J&M Recording Studio | 4g | **Diff** | Accumulates 1 Wizard/Drummer. **Waterdeep owner: draw 1 Intrigue. Ours: 2 VP.** |
| 5 | The Golden Horn | building_005 The Apollo Theater | 4g | **Match** | Accumulates 4 Gold/Coins. Owner: 2 Gold/Coins. |
| 6 | The Waymoot | building_006 Red Rocks Amphitheatre | 4g | **Diff** | Accumulates 3 VP. **Waterdeep visitor: take all VP + draw 1 quest. Ours: take all VP + draw 1 contract.** This is a match on action. **Waterdeep owner: 2 VP. Ours: 2 VP.** Match. |

**Note on buildings 3 & 4**: The owner bonuses appear to be swapped between Spires of the Morning / Hansa Studios and Tower of Order / J&M Recording Studio. In Waterdeep, the Cleric accumulator (Spires) gives owner 2 VP, and the Wizard accumulator (Tower of Order) gives owner draw Intrigue. In our game, the Singer accumulator (Hansa) gives owner draw Intrigue, and the Drummer accumulator (J&M) gives owner 2 VP. The accumulator + visitor mechanics are correct — only the owner bonuses are swapped relative to the source.

---

### Standard Buildings (fixed reward, no accumulation)

| # | Waterdeep | Our Building | Cost | Match? | Notes |
|---|-----------|-------------|------|--------|-------|
| 7 | House of the Moon | building_007 FAME Studios | 3g | **Match** | Visitor: 1 Cleric/Singer + draw quest/contract. Owner: 2 Gold/Coins. |
| 8 | Dragon Tower | building_008 Chess Records Studio | 3g | **Diff** | **Waterdeep visitor: 1 Wizard + draw Intrigue. Ours: 1 Drummer + draw Intrigue.** Match on visitor. **Waterdeep owner: draw Intrigue. Ours: draw Intrigue.** Match. Overall match. |
| 9 | Helmstar Warehouse | building_009 Motown Hitsville U.S.A. | 3g | **Match** | Visitor: 2 Rogues/Bass Players + 2 Gold/Coins. Owner: 1 Rogue/Bass Player. |
| 10 | The Skulkway | building_010 Criteria Studios | 4g | **Diff** | **Waterdeep visitor: 1 Fighter + 1 Rogue + 2 Gold. Ours: 1 Guitarist + 1 Bass Player + 2 Coins.** Match on visitor. **Waterdeep owner: pick 1 Fighter or 1 Rogue. Ours: pick 1 Guitarist or 1 Bass Player.** Match. |
| 11 | Northgate | building_011 The Bluebird Cafe | 3g | **Diff** | **Waterdeep visitor: 1 any-type adventurer + 2 Gold. Ours: pick 1 any-type + 2 Coins.** The mechanic differs slightly — Waterdeep says "1 adventurer of any type" (likely just pick 1) so this is effectively equivalent. **Waterdeep owner: 2 VP. Ours: 2 VP.** Match. |
| 12 | House of Good Spirits | building_012 Sun Studio | 3g | **Match** | Visitor: 1 Fighter/Guitarist + 1 any-type. Owner: 1 Fighter/Guitarist. |
| 13 | House of Wonder | building_013 The Fillmore | 4g | **Diff** | **Waterdeep: Spend 2 Gold, take 2 Clerics or Wizards (any mix). Ours: Spend 2 Coins, take 2 Singers or Drummers (any mix).** Match — the allowed types map correctly (Cleric→Singer, Wizard→Drummer). Owner: 2 Gold/Coins. Match. |
| 14 | Smuggler's Dock | building_014 The Ryman Auditorium | 4g | **Diff** | **Waterdeep: Spend 2 Gold, take 4 Fighters or Rogues (any mix). Ours: Spend 2 Coins, take 4 Guitarists or Bass Players (any mix).** Match — types map correctly (Fighter→Guitarist, Rogue→Bass Player). Owner: 2 Gold/Coins. Match. |
| 15 | Fetlock Court | building_015 Abbey Road Studios | 8g | **Diff** | **Waterdeep visitor: 2 Fighters + 1 Wizard. Ours: 2 Guitarists + 1 Singer.** Type mismatch — Waterdeep has Wizard (→Drummer), ours has Singer. **Waterdeep owner: pick 1 Fighter or 1 Wizard. Ours: pick 1 Guitarist or 1 Singer.** Owner also uses Singer instead of Drummer. |
| 16 | New Olamn | building_016 Trident Studios | 8g | **Diff** | **Waterdeep visitor: 2 Rogues + 1 Wizard. Ours: 2 Bass Players + 1 Drummer.** Match — Rogue→Bass Player, Wizard→Drummer. **Waterdeep owner: pick 1 Rogue or 1 Wizard. Ours: pick 1 Bass Player or 1 Drummer.** Match. |
| 17 | House of Heroes | building_017 Compass Point Studios | 8g | **Diff** | **Waterdeep visitor: 1 Cleric + 2 Fighters. Ours: 2 Bass Players + 1 Singer.** Significant mismatch — Waterdeep gives Fighter-heavy + 1 Cleric, ours gives Bass Player-heavy + 1 Singer. Different resource composition. **Waterdeep owner: pick 1 Fighter or 1 Cleric. Ours: pick 1 Bass Player or 1 Singer.** |
| 18 | The Tower of Luck | building_018 Electric Lady Studios | 8g | **Diff** | **Waterdeep visitor: 1 Cleric + 2 Rogues. Ours: 2 Guitarists + 1 Drummer.** Significant mismatch — completely different resource types. **Waterdeep owner: pick 1 Cleric or 1 Rogue. Ours: pick 1 Guitarist or 1 Drummer.** |
| 19 | The Three Pearls | building_019 Talent Agency | 4g | **Match** | Exchange 2 any-type for 3 any-type. Owner: 2 Gold/Coins. |
| 20 | The Yawning Portal | building_020 Musician's Union Hall | 4g | **Match** | Visitor: pick 2 any-type. Owner: pick 1 any-type. |

---

### Implemented Buildings (formerly missing)

| # | Waterdeep Building | Our Building | Cost | Status | Notes |
|---|-------------------|-------------|------|--------|-------|
| 21 | Heroes' Garden | building_022 Audition Showcase | 4g | **DONE** | Visitor: draw 1 face-up contract, may immediately complete for +4 VP bonus. Owner: 2 VP. Uses `draw_contract_and_complete` visitor_reward_special + `pending_showcase_bonus` state. |
| 22 | The Stone House | building_021 Royalty Collection Office | 4g | **DONE** | Visitor: 1 coin per player-purchased building in play. Owner: 2 coins. Uses `coins_per_building` visitor_reward_special. |

### Still Missing Buildings (2 not in our game)

| # | Waterdeep Building | Cost | Mechanic | Complexity |
|---|-------------------|------|----------|------------|
| 23 | The Palace of Waterdeep | 4g | Take the Ambassador piece — assign it as an extra worker before anyone else next round. Owner: 2 VP. | **High** — requires new Ambassador agent, special placement timing, complex edge cases |
| 24 | The Zoarstar | 8g | Choose an opponent's occupied action space and use its action as your own. Owner: 2 VP. | **High** — requires copying another space's action, interacts with every space type |

---

## Summary

### Match Status

| Status | Count | Buildings |
|--------|-------|-----------|
| **Exact Match** | 10 | Troubadour, Cavern Club, Apollo Theater, FAME Studios, Chess Records, Motown Hitsville, Criteria Studios, Bluebird Cafe, Talent Agency, Musician's Union Hall |
| **Mechanical Match (re-themed correctly)** | 6 | Red Rocks, Sun Studio, Fillmore, Ryman Auditorium, Trident Studios, Skulkway/Criteria |
| **Owner Bonus Swapped** | 2 | Hansa Studios (building_003), J&M Recording Studio (building_004) — VP and draw_intrigue are swapped vs Waterdeep |
| **Resource Type Mismatch** | 3 | Abbey Road (building_015), Compass Point (building_017), Electric Lady (building_018) — different resource compositions than their Waterdeep counterparts |
| **Newly Implemented** | 2 | Audition Showcase (Heroes' Garden), Royalty Collection Office (The Stone House) |
| **Missing** | 2 | The Palace of Waterdeep, The Zoarstar |

### Differences That May Be Intentional

The 8-cost buildings (015-018) don't follow a strict 1:1 type mapping from their Waterdeep counterparts. Instead, they seem to have been designed to provide balanced coverage across all four resource types in our game. This may be intentional game design rather than a mapping error — the exact resource mix on 8-cost buildings matters less than ensuring each resource type has adequate supply buildings.

### Remaining Missing Building Difficulty Ranking

1. **The Palace of Waterdeep** (hard) — entirely new Ambassador agent mechanic
2. **The Zoarstar** (hardest) — copy any occupied space's action, huge interaction surface
