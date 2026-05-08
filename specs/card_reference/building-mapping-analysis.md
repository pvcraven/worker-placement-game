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
| 23 | The Zoarstar | building_023 Shadow Studio | 8g | **DONE** | Visitor: copy an opponent's occupied action space and receive its rewards. Owner: 2 VP. Uses `copy_occupied_space` visitor_reward_special + Bootleg Recording intrigue cards (intrigue_053, intrigue_054). |

### Still Missing Buildings (1 not in our game)

| # | Waterdeep Building | Cost | Mechanic | Complexity |
|---|-------------------|------|----------|------------|
| 23 | The Palace of Waterdeep | 4g | Take the Ambassador piece — assign it as an extra worker before anyone else next round. Owner: 2 VP. | **High** — requires new Ambassador agent, special placement timing, complex edge cases |

---

## Summary

### Match Status

| Status | Count | Buildings |
|--------|-------|-----------|
| **Exact Match** | 10 | Troubadour, Cavern Club, Apollo Theater, FAME Studios, Chess Records, Motown Hitsville, Criteria Studios, Bluebird Cafe, Talent Agency, Musician's Union Hall |
| **Mechanical Match (re-themed correctly)** | 6 | Red Rocks, Sun Studio, Fillmore, Ryman Auditorium, Trident Studios, Skulkway/Criteria |
| **Owner Bonus Swapped** | 2 | Hansa Studios (building_003), J&M Recording Studio (building_004) — VP and draw_intrigue are swapped vs Waterdeep |
| **Resource Type Mismatch** | 3 | Abbey Road (building_015), Compass Point (building_017), Electric Lady (building_018) — different resource compositions than their Waterdeep counterparts |
| **Newly Implemented** | 3 | Audition Showcase (Heroes' Garden), Royalty Collection Office (The Stone House), Shadow Studio (The Zoarstar) |
| **Missing** | 1 | The Palace of Waterdeep |

### Differences That May Be Intentional

The 8-cost buildings (015-018) don't follow a strict 1:1 type mapping from their Waterdeep counterparts. Instead, they seem to have been designed to provide balanced coverage across all four resource types in our game. This may be intentional game design rather than a mapping error — the exact resource mix on 8-cost buildings matters less than ensuring each resource type has adequate supply buildings.

### Remaining Missing Building Difficulty Ranking

1. **The Palace of Waterdeep** (hard) — entirely new Ambassador agent mechanic

---

## Expansion Buildings

Both expansions add 12 purchasable buildings each. The plan is to implement **Undermountain first**, then possibly Skullport (which requires the complex Corruption mechanic).

### Resource Reference

| Abbreviation | Waterdeep | Music Theme |
|---|---|---|
| oj (orange) | Fighter | Guitarist |
| bl (black) | Rogue | Bass Player |
| wh (white) | Cleric | Singer |
| pu (purple) | Wizard | Drummer |
| wild / ? | Any adventurer type (not coins) | Any musician type (not coins) |
| Gold | Gold | Coins |
| Corruption | Anti-resource; escalating VP penalty at end of game | TBD |

---

### Undermountain Expansion (12 buildings)

Priority: **First expansion to implement.**

#### Resource Distribution Buildings

These buildings give the visitor resources AND place additional resources from the supply onto other action spaces (chosen by the building owner). Those placed resources sit on the spaces until someone visits them (similar to accumulation).

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| UN-1 | Citadel Of The Bloody Hand | 7g | 2 Fighters | 4 Fighters. Place 1 Fighter on each of 2 different action spaces. | Heavy Fighter supply + distributes 2 more |
| UN-2 | High Duke's Tomb | 7g | 4 Gold | 8 Gold. Place 2 Gold on each of 2 different action spaces. | Heavy Gold supply + distributes 4 more |
| UN-3 | Room Of Wisdom | 7g | 1 Cleric | 2 Clerics. Place 1 Cleric on 1 action space. | Cleric supply + distributes 1 more |
| UN-4 | Shadowdusk Hold | 7g | 2 Rogues | 4 Rogues. Place 1 Rogue on each of 2 different action spaces. | Heavy Rogue supply + distributes 2 more |
| UN-5 | The Librarium | 7g | 1 Wizard | 2 Wizards. Place 1 Wizard on 1 action space. | Wizard supply + distributes 1 more |

**New mechanic required:** "Place resources on action spaces" — owner chooses which spaces; resources accumulate there until claimed by a future visitor.

#### Standard Reward + Play Intrigue Buildings

Visitor gets resources AND immediately plays 1 Intrigue card from hand (bonus action, not draw).

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| UN-6 | Belkram's Tomb | 5g | 2 Gold | 5 Gold + play 1 Intrigue | Gold-heavy + intrigue play |
| UN-7 | Hall Of Sleeping Kings | 4g | pick 1 Fighter or 1 Rogue | 1 Fighter + 1 Rogue + play 1 Intrigue | Mixed resources + intrigue play |
| UN-8 | The Eye's Lair | 3g | 2 VP | 1 wild + play 1 Intrigue | Cheap; flexible resource + intrigue play |

**New mechanic required:** "Play Intrigue" — visitor immediately plays an intrigue card from hand as part of the building visit (distinct from "draw Intrigue" which adds to hand).

#### Intrigue-Focused Buildings

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| UN-9 | Hall Of Many Pillars | 5g | 1 Intrigue | Draw 3 Intrigue cards | Pure intrigue draw, large hand refill |
| UN-10 | Tombriand's Graveyard | 3g | 1 Intrigue | Draw 2 Intrigue + 4 Gold, then discard 2 Intrigue | Net: cycle intrigue hand + gain 4 Gold. Cheap building. |

#### Special Mechanic Buildings

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| UN-11 | Hall Of Three Lords | 6g | 2 VP | Remove 3 wild from your Tavern, place 1 on each of 3 different action spaces: 10 VP | **High complexity.** Visitor spends 3 any-type adventurers, distributes them to 3 different spaces, earns 10 VP. Combines resource-spending with resource-distribution. |
| UN-12 | The Lost Cavern | 6g | 1 wild | Discard 1 non-Mandatory Quest: gain 1 Fighter + 1 Rogue + 1 wild | Visitor permanently discards an incomplete (non-mandatory) quest from hand for resources. Quest-discard mechanic. |

#### Undermountain Mechanic Summary

| New Mechanic | Buildings Using It | Complexity |
|---|---|---|
| **Place resources on action spaces** (owner chooses) | UN-1 through UN-5, UN-11 | Medium — needs UI for owner to select target spaces |
| **Play Intrigue from hand** (bonus action during visit) | UN-6, UN-7, UN-8 | Medium — triggers intrigue play flow mid-visit |
| **Draw + discard Intrigue** (cycling) | UN-10 | Low — draw then discard from hand |
| **Discard quest for reward** | UN-12 | Medium — needs quest selection UI, must exclude mandatory quests |
| **Spend resources + distribute + earn VP** | UN-11 | High — combines spending, distribution, and conditional VP |

---

### Skullport Expansion (12 buildings)

Priority: **Second expansion, if implemented.** Requires the Corruption mechanic.

#### Corruption Overview

Corruption is a shared-pool anti-resource. There is a fixed supply of corruption tokens in the game. At end of game, each corruption token a player holds costs VP. The penalty **escalates based on how much total corruption has been taken from the shared pool** (by all players combined):

- Penalty increases in groups of 3 corruption removed from the pool
- 1–3 total taken from pool → each corruption a player holds = **-1 VP**
- 4–6 total taken → each = **-2 VP**
- 7–9 total taken → each = **-3 VP**
- (and so on)

This creates a game-theory dynamic: taking corruption early is cheap, but every player taking corruption raises the penalty for everyone.

#### Powerful Rewards + Take Corruption

These buildings offer above-rate rewards but force the visitor to take corruption.

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| SP-1 | Cryptkey Facilitations | 7g | 3 Gold | 3 Rogues + 5 Gold + 1 Corruption | Massive resource haul |
| SP-2 | Shradin's Excellent Zombies | 6g | 3 Gold | 3 Fighters + 1 Cleric + 1 Corruption | 4 adventurers for 1 corruption |
| SP-3 | The Deepfires | 6g | 3 VP | 1 wild + 5 Gold + 1 Corruption + draw 1 face-up Quest | Resources + quest draw, very flexible |
| SP-4 | The Frontal Lobe | 4g | The returned wild | Spend 1 wild: gain 3 Wizards + 1 Corruption | Trade 1 any-type for 3 Wizards. Owner gets the returned adventurer. |
| SP-5 | The Hell Hound's Muzzle | 8g | 1 wild | 1 of each adventurer type (Fighter + Rogue + Cleric + Wizard) + 1 Corruption | Rainbow building — one of everything |
| SP-6 | The Thrown Gauntlet | 8g | 1 Fighter + 1 Rogue | 3 Fighters + 3 Rogues + 1 Corruption | 6 adventurers, combat-heavy |

#### Corruption Removal / Cleansing Buildings

These buildings let visitors get rid of corruption.

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| SP-7 | Delver's Folly | 6g | 2 VP | Remove 1 Corruption from your Tavern and place it on any action space | Moves corruption to a space (another player may have to deal with it) |
| SP-8 | Promenade Of The Dark Maiden | 9g | 3 VP | Remove up to 2 Corruption from the game entirely | Most expensive building; permanently destroys corruption. Reduces shared pool penalty for everyone. |

#### Corruption Spending Buildings

These buildings let visitors trade corruption for benefits (spend corruption as a cost).

| # | Waterdeep Name | Cost | Owner Bonus | Visitor Reward | Notes |
|---|---|---|---|---|---|
| SP-9 | Secret Shrine | 8g | 1 Cleric | Spend 1 Corruption: gain 1 Cleric | Weak rate, but removes corruption |
| SP-10 | The Poisoned Quill | 5g | 1 Intrigue | Spend 1 Corruption: gain 1 Intrigue | Trade corruption for card draw |
| SP-11 | Thimblewine's Pawnshop | 4g | 2 Gold | Spend 1 Corruption: gain 1 Gold | Trade corruption for gold |

#### Corruption Accumulation Building

| # | Waterdeep Name | Cost | Owner Bonus | Accumulates | Visitor Reward | Notes |
|---|---|---|---|---|---|---|
| SP-12 | Monsters Made To Order | 3g | 2 VP | 1 Corruption/round | Take all Corruption on this space. Return 1 Agent to your pool for each Corruption taken. | Unique: corruption accumulates, but taking it gives you extra workers for future rounds. High risk/reward. |

#### Skullport Mechanic Summary

| New Mechanic | Buildings Using It | Complexity |
|---|---|---|
| **Corruption system** (shared pool, escalating penalty) | All 12 Skullport buildings | **High** — new resource type, shared pool tracking, end-game scoring, UI for corruption display |
| **Take corruption with reward** | SP-1 through SP-6, SP-12 | Low (once corruption exists) — just add corruption to visitor rewards |
| **Remove corruption from game** | SP-7, SP-8 | Medium — need to track removal vs. redistribution |
| **Spend corruption as cost** | SP-9, SP-10, SP-11 | Low (once corruption exists) — corruption as input cost |
| **Corruption accumulation on space** | SP-12 | Medium — reuses accumulation mechanic but with corruption |
| **Return agents to pool** (gain extra workers) | SP-12 | **High** — new mechanic; changes worker count mid-game |
| **Owner gets the returned resource** | SP-4 | Medium — owner bonus depends on what visitor spent |
| **Place corruption on action spaces** | SP-7 | Medium — corruption on spaces, others must deal with it |

---

## Implementation Roadmap

### Phase 1: Undermountain Expansion

New mechanics needed:
1. **Place resources on action spaces** — owner selects target spaces after visiting
2. **Play Intrigue from hand** — bonus intrigue play during building visit
3. **Draw + discard Intrigue** — hand cycling
4. **Discard quest for reward** — quest selection with mandatory-quest exclusion
5. **Spend resources + distribute + earn VP** — Hall of Three Lords combo

### Phase 2: Skullport Expansion (if pursued)

New mechanics needed:
1. **Corruption resource system** — shared pool, per-player tracking, escalating end-game penalty
2. **Corruption removal/spending** — multiple ways to use or remove corruption
3. **Return agents to pool** — dynamically changing worker count
4. **Owner receives returned resource** — The Frontal Lobe's unique owner bonus
5. **Corruption on action spaces** — corruption as a space modifier
