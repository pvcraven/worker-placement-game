# Waterdeep to Worker Placement Game - Card Mapping Reference

## Resource Mapping

| Waterdeep Name | Game Resource   | Icon             |
|----------------|-----------------|------------------|
| Warrior        | Guitarist       | Orange square    |
| Cleric         | Singer          | White square     |
| Rogue          | Bass Player     | Black square     |
| Wizard         | Drummer         | Purple square    |
| Gold           | Coins           | Gold circle      |

## Quest Type Mapping

| Code | Waterdeep Name | Game Genre | Primary Resource | Abbreviation |
|------|----------------|------------|------------------|--------------|
| C    | Commerce       | Pop        | Coins            | CQ           |
| W    | Warfare        | Rock       | Guitarist        | WQ           |
| P    | Piety          | Soul       | Singer           | PQ           |
| A    | Arcana         | Funk       | Drummer          | AQ           |
| S    | Skullduggery   | Jazz       | Bass Player      | SQ           |

---

## Card Name Mapping (Waterdeep → Game)

Each Waterdeep card is mapped to a music-industry-themed game card. Genre follows the quest type mapping above. Costs and rewards carry over from Waterdeep (see Complete Quest Card List below). Cards marked (PLOT) have ongoing effects after completion.

Note: Waterdeep has an uneven distribution (Pop:12, Rock:14, Soul:11, Funk:11, Jazz:12 = 60 total). The current game enforces equal cards per genre, so 2 Rock cards may need reassignment or the test updated.

### Pop (Commerce) — 12 cards

| # | Waterdeep Name                  | Game Card Name              | Description                                                                                     | Special           |
|---|--------------------------------|-----------------------------|-------------------------------------------------------------------------------------------------|--------------------|
| 1 | Lure Artisans of Mirabar       | Pop-Up Venue Launch         | Scout a prime location and launch a pop-up venue to expand your music empire.                   | choose_building    |
| 2 | Spy on the House of Light      | Corporate Sponsorship Deal  | Land a massive corporate sponsorship for a pop act, earning a fortune in cash and prestige.     | -                  |
| 3 | Safeguard Eltorchul Mage       | Producer Security Detail    | Protect a sought-after producer from rival headhunters, earning their studio time and loyalty.  | -                  |
| 4 | Loot the Crypt of Chauntea     | A&R Talent Scout            | Scout talent at open mic nights, picking up street cred, insider intel, and a new contract.     | random_quest, 1 intrigue |
| 5 | Establish New Merchant Guild   | Record Label Empire         | Found your own pop label. Each future pop release adds to your growing reputation. (PLOT)       | score_per_pop      |
| 6 | Infiltrate Builder's Hall      | Venue Investment Fund       | Build an investment network in the venue market, reaping returns on every new property. (PLOT)  | score_per_building |
| 7 | Thin the City Watch            | Session Musician Poach      | Raid a rival's session musician pool, walking away with their entire bass section.              | -                  |
| 8 | Send Aid to the Harpers        | Charity Gala Showcase       | Host a star-studded charity gala that rockets your reputation — but a rival basks in the press. | opponent_gains_coins |
| 9 | Placate the Walking Statue     | Lottery Venue Prize         | Win a mystery venue in an industry charity raffle — you never know what you'll get.             | random_building    |
|10 | Bribe the Shipwrights          | Payola Pipeline             | Grease the right palms at radio stations so every payday brings fresh bass talent to your door. (PLOT) | on_gain_coins_bass |
|11 | Impersonate Adarbrent Noble    | VIP Industry Gala           | Infiltrate the most exclusive industry events, gaining massive fame and insider intelligence.   | -                  |
|12 | Ally with House Thann          | Grammy Night Showcase       | Pour everything into a career-defining Grammy performance with full production and backing band.| -                  |

### Rock (Warfare) — 14 cards

| # | Waterdeep Name                       | Game Card Name              | Description                                                                                       | Special              |
|---|-------------------------------------|-----------------------------|----------------------------------------------------------------------------------------------------|----------------------|
| 1 | Train Bladesingers                   | Battle of the Bands         | Enter the city's fiercest battle of the bands, emerging with battle-hardened guitarists and a drummer. | -                |
| 2 | Bolster Griffon Cavalry              | Rock Loyalty Program        | Build fierce loyalty among your guitarists — every new recruit inspires another to join. (PLOT)    | on_gain_guitarist    |
| 3 | Quell Mercenary Uprising             | Rock Union Takeover         | Crush a rival rock collective's uprising, cementing your dominance in the genre. (PLOT)           | score_per_rock       |
| 4 | Ambush Artor Morlin                  | Ambush at the Arena         | Hijack a rival's arena slot with a surprise guerrilla set, cashing in on their audience.          | -                    |
| 5 | Raid Orc Stronghold                  | Raid the Rival Studio       | Storm a competitor's studio during downtime and walk out with their cash reserves.                | -                    |
| 6 | Defeat Uprising from Undermountain   | Crush the Underground Revolt| Put down an upstart band threatening your territory, recruiting their best guitarist in the process.| -                   |
| 7 | Deliver an Ultimatum                 | Deliver an Ultimatum        | Confront a rival promoter with a final offer — accept the terms or face a hostile takeover.       | -                    |
| 8 | Deliver Weapons to Selune's Temple   | Donate Instruments to Charity| Donate instruments to a music charity, earning devoted new singers in return.                     | -                    |
| 9 | Perform the Penance of Duty          | Reunion Tour Penance        | Force a feuding rock band back together for one last tour, reuniting estranged musicians.         | -                    |
|10 | Repel Seawraiths                     | Repel the Critics           | Silence your harshest critics with an undeniable sold-out show that proves the haters wrong.      | -                    |
|11 | Recruit Lieutenant                   | Hire a Tour Manager         | Recruit a legendary tour manager who runs your operation so well, you gain an extra worker permanently. (PLOT) | extra_worker |
|12 | Recruit Paladins for Tyr             | Stadium Rock Revival        | Rally a massive roster of musicians for a landmark stadium recording session.                     | -                    |
|13 | Confront the Xanathar                | Confront the Kingpin        | Take on the most powerful figure in the industry with your full band and crew backing you up.     | -                    |
|14 | Bolster City Guard                   | Rock Army Mobilization      | Assemble the largest rock army the city has ever seen for an unprecedented multi-stage festival.  | -                    |

### Soul (Piety) — 11 cards

| # | Waterdeep Name                       | Game Card Name                 | Description                                                                                       | Special                |
|---|-------------------------------------|--------------------------------|----------------------------------------------------------------------------------------------------|------------------------|
| 1 | Convert a Noble to Lathander         | Convert a Classical Musician   | Win over a classical musician to the soul sound, and pick a new quest from the inspiration.       | face_up_quest          |
| 2 | Discover Hidden Temple of Lolth      | Discover Hidden Soul Venue     | Uncover a legendary secret soul venue and claim a quest from its storied archives.                | face_up_quest          |
| 3 | Form an Alliance with the Rashemi    | Gospel Alliance                | Form a powerful alliance with a gospel choir, unlocking new creative opportunities.               | face_up_quest          |
| 4 | Produce a Miracle for the Masses     | Miracle at the Microphone      | A transcendent vocal performance lets you convert any musician into a singer. (PLOT)              | on_gain_singer_swap    |
| 5 | Protect the House of Wonder          | Protect the Soul Legacy        | Guard the soul music heritage — each future soul project adds to your legacy. (PLOT)             | score_per_soul         |
| 6 | Eliminate Vampire Coven              | Eliminate the Rival Revue      | Take down a competing revue show with a superior lineup of musicians and cash.                    | -                      |
| 7 | Defend the Tower of Luck             | Soul Music Residency           | Secure a permanent soul residency that attracts one new musician every round. (PLOT)             | gain_resource_round    |
| 8 | Heal Fallen Gray Hand Soldiers       | Rehabilitate Burned-Out Artists| Use soul therapy to rehabilitate burned-out musicians, transforming them into a guitarist army.   | -                      |
| 9 | Host Festival for Sune               | Soul Revival Festival          | Host a massive soul revival that draws devoted singers from across the country.                    | -                      |
|10 | Seal Gate to Cyric's Realm           | Soul Train Anniversary Special | Produce the definitive soul television special, cementing your legacy forever.                    | -                      |
|11 | Create a Shrine to Oghma             | Church of Soul Music           | Build a cathedral dedicated to soul music history, requiring a devoted choir of singers.          | -                      |

### Funk (Arcana) — 11 cards

| # | Waterdeep Name                       | Game Card Name                 | Description                                                                                       | Special                |
|---|-------------------------------------|--------------------------------|----------------------------------------------------------------------------------------------------|------------------------|
| 1 | Research Chronomancy                 | Time Warp Remix                | Master the art of temporal remixing, gaining the ability to recall your already-placed workers. (PLOT) | worker_recall      |
| 2 | Explore Ahghairon's Tower            | Explore the Groove Archive     | Dig through legendary funk archives — every guitarist discovery yields insider intel. (PLOT)      | on_gain_guitarist_i    |
| 3 | Domesticate Owlbears                 | Tame the Wild Sessions         | Wrangle chaotic jam sessions into tight funk recordings with a mix of singers and drummers.       | -                      |
| 4 | Study the Illusk Arch                | Study the Funk Masters         | Study the masters' techniques — each future funk project reflects your growing expertise. (PLOT)  | score_per_funk         |
| 5 | Recover the Magister's Orb           | Recover the Master Tapes       | Find legendary lost master tapes, granting access to studios others are using. (PLOT)            | use_occupied           |
| 6 | Steal Spellbook from Silverhand      | Steal the Secret Arrangements  | Swipe a rival's secret horn arrangements and cash in on their studio work.                        | -                      |
| 7 | Retrieve Ancient Artifacts           | Retrieve Vintage Instruments   | Track down priceless vintage instruments from estate sales and pawn shops.                         | -                      |
| 8 | Investigate Aberrant Infestation     | Investigate the Underground    | Probe the underground funk scene, gaining massive street cred and insider intel.                   | -                      |
| 9 | Recruit for Blackstaff Academy       | Funk Academy Recruitment       | Recruit a squad of drummers for an elite funk training academy.                                   | -                      |
|10 | Expose Red Wizards' Spies            | Mothership Connection Tour     | Launch an epic interstellar funk tour, exposing the cosmic truth to massive audiences.             | -                      |
|11 | Infiltrate Halaster's Circle         | Interstellar Funk Odyssey      | Journey to the furthest reaches of experimental funk, requiring a massive drum section.           | -                      |

### Jazz (Skullduggery) — 12 cards

| # | Waterdeep Name                        | Game Card Name                 | Description                                                                                       | Special                  |
|---|--------------------------------------|--------------------------------|----------------------------------------------------------------------------------------------------|--------------------------|
| 1 | Expose Cult Corruption                | Expose Industry Corruption     | Blow the whistle on a corrupt promoter, gaining loyal singers who respect your integrity.          | -                        |
| 2 | Fence Goods for Duke of Darkness      | Fence Bootleg Recordings       | Sell bootleg recordings underground — every new bass player connection pays cash dividends. (PLOT)| on_gain_bass_coins       |
| 3 | Install a Spy in Castle Waterdeep     | Plant a Mole at Rival Label    | Install a spy at a competing label — each future jazz success deepens your intel network. (PLOT)  | score_per_jazz           |
| 4 | Establish Harpers Safe House          | Establish a Speakeasy Network  | Set up hidden speakeasy venues across the city — your existing properties multiply your influence. (PLOT) | score_existing_buildings |
| 5 | Procure Stolen Goods                  | Procure Rare Pressings         | Acquire rare vinyl pressings from questionable sources at a premium.                               | -                        |
| 6 | Build a Reputation in Skullport       | Underground Reputation         | Build street cred in the underground jazz scene through shadowy deals and late-night sessions.     | -                        |
| 7 | Place a Sleeper Agent in Skullport    | Sleeper Agent at the Label     | Plant a deep-cover agent at a rival label — each intrigue card played expands your spy network. (PLOT) | score_per_intrigue  |
| 8 | Steal from House Adarbrent            | Rob the Jazz Aristocrats       | Plunder the old-guard jazz establishment's vault, walking away with their cash and prestige.       | -                        |
| 9 | Take Over Rival Organization          | Hostile Label Takeover         | Execute a hostile takeover of a rival jazz label, absorbing their entire bass player roster.       | -                        |
|10 | Prison Break                          | Jailhouse Jazz Session         | Stage a legendary jailhouse jam that recruits guitarists and lets you play your best intrigue card.| play_intrigue            |
|11 | Raid on Undermountain                 | Jazz Underground Raid          | Lead a daring raid on the underground jazz circuit, hauling away cash and fame.                    | -                        |
|12 | Establish Shadow Thieves' Guild       | Shadow Jazz Syndicate          | Build a vast underground jazz syndicate with an army of bass players and deep connections.         | -                        |

---

## Special Mechanics Taxonomy

### One-Time Completion Rewards

These trigger once when the quest is completed, as part of the reward.

| Mechanic ID          | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| choose_building      | Player selects any available building to purchase for free                   |
| random_building      | Player receives a random available building for free                        |
| face_up_quest        | Player takes one of the face-up quest cards from the tavern display         |
| random_quest         | Player draws a random quest card from the deck                              |
| play_intrigue        | Player immediately plays one intrigue card from their hand                  |
| worker_recall        | Player picks up one of their already-placed workers and returns it to pool  |
| opponent_gains_coins | One opponent of the completing player receives 4 coins                      |

### Ongoing Effects (Plot Quests)

These provide permanent benefits for the rest of the game after the quest is completed.

**Resource Triggers** - When you gain a specific resource through a board action, gain a bonus:

| Mechanic ID         | Trigger Resource | Bonus                                    |
|---------------------|------------------|------------------------------------------|
| on_gain_guitarist   | Guitarist        | +1 extra Guitarist                       |
| on_gain_guitarist_i | Guitarist        | +1 Intrigue card                         |
| on_gain_singer_swap | Singer           | May trade any 1 owned resource for 1 Singer |
| on_gain_bass_coins  | Bass Player      | +2 Coins                                 |
| on_gain_coins_bass  | Coins            | +1 Bass Player                           |

**Scoring Triggers** - Earn bonus VP when completing future quests of a specific type:

| Mechanic ID          | Trigger               | Bonus VP |
|----------------------|-----------------------|----------|
| score_per_arcana     | Complete Arcana quest | +2       |
| score_per_commerce   | Complete Commerce quest | +2     |
| score_per_piety      | Complete Piety quest  | +2       |
| score_per_skulduggery| Complete Skullduggery quest | +2 |
| score_per_warfare    | Complete Warfare quest | +2      |
| score_per_building   | Purchase a building   | +4       |
| score_per_intrigue   | Play an intrigue card | +2       |

**One-Time Scoring Based on Current State:**

| Mechanic ID              | Counted At Completion      | Bonus VP |
|--------------------------|----------------------------|----------|
| score_existing_buildings | Buildings already owned     | +2 each  |

**Persistent Abilities:**

| Mechanic ID         | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| use_occupied        | Once per round, use a building action space occupied by another player's worker |
| gain_resource_round | Gain 1 random non-coin resource at the start of each round              |
| extra_worker        | Gain 1 permanent extra worker for the rest of the game                  |

---

## Complete Quest Card List

Cost and reward columns use shorthand: G=Guitarist, S=Singer, B=Bass Player, D=Drummer, $=Coins.

### Commerce Quests (C)

| Card Name                       | Cost              | Reward Resources | VP | Intrigue | Special                  |
|---------------------------------|-------------------|------------------|----|----------|--------------------------|
| Lure Artisans of Mirabar        | 1S 1G 1B 2$       | -                | 4  | -        | choose_building          |
| Spy on the House of Light       | 3G 2B             | 6$               | 6  | -        | -                        |
| Safeguard Eltorchul Mage        | 1G 1B 1D 4$       | 2D               | 4  | -        | -                        |
| Loot the Crypt of Chauntea      | 1S 3B 2$          | -                | 7  | 1        | random_quest             |
| Establish New Merchant Guild    | 1S 2G 4$          | -                | 8  | -        | score_per_commerce (PLOT)|
| Infiltrate Builder's Hall       | 2G 2B 4$          | -                | 6  | -        | score_per_building (PLOT)|
| Thin the City Watch             | 1S 1G 1B 4$       | 4B               | 9  | -        | -                        |
| Send Aid to the Harpers         | 1S 1G 1B 4$       | -                | 15 | -        | opponent_gains_coins     |
| Placate the Walking Statue      | 2S 2B 4$          | -                | 10 | -        | random_building          |
| Bribe the Shipwrights           | 4B 1D 4$          | -                | 10 | -        | on_gain_coins_bass (PLOT)|
| Impersonate Adarbrent Noble     | 1S 2G 2B 1D 4$    | -                | 18 | 2        | -                        |
| Ally with House Thann           | 1S 3B 1D 8$       | -                | 25 | -        | -                        |

### Warfare Quests (W)

| Card Name                          | Cost              | Reward Resources | VP | Intrigue | Special                    |
|------------------------------------|-------------------|------------------|----|----------|----------------------------|
| Train Bladesingers                  | 3G 1D             | 1G 1D            | 4  | -        | -                          |
| Bolster Griffon Cavalry             | 4G 4$             | -                | 6  | -        | on_gain_guitarist (PLOT)   |
| Quell Mercenary Uprising            | 1S 4G             | -                | 8  | -        | score_per_warfare (PLOT)   |
| Ambush Artor Morlin                 | 1S 3G 1B          | 4$               | 8  | -        | -                          |
| Raid Orc Stronghold                 | 4G 2B             | 4$               | 8  | -        | -                          |
| Defeat Uprising from Undermountain  | 1S 3G 1B 2$       | 2G               | 11 | -        | -                          |
| Deliver an Ultimatum                | 4G 1B 1D          | 4$               | 11 | -        | -                          |
| Deliver Weapons to Selune's Temple  | 4G 1B 1D 2$       | 2S               | 9  | -        | -                          |
| Perform the Penance of Duty         | 2S 2G 4$          | 1S 1G            | 12 | -        | -                          |
| Repel Seawraiths                    | 1S 4G 1D          | 2$               | 15 | -        | -                          |
| Recruit Lieutenant                  | 1S 5G 1B 1D       | -                | 0  | -        | extra_worker (PLOT)        |
| Recruit Paladins for Tyr            | 2S 4G 4$          | 3S               | 10 | -        | -                          |
| Confront the Xanathar               | 1S 4G 2B 1D       | 2$               | 20 | -        | -                          |
| Bolster City Guard                  | 9G 2B             | -                | 25 | -        | -                          |

### Piety Quests (P)

| Card Name                          | Cost              | Reward Resources | VP | Intrigue | Special                    |
|------------------------------------|-------------------|------------------|----|----------|----------------------------|
| Convert a Noble to Lathander        | 2S 1D             | -                | 8  | -        | face_up_quest              |
| Discover Hidden Temple of Lolth     | 2S 1G 1B          | -                | 10 | -        | face_up_quest              |
| Form an Alliance with the Rashemi   | 2S 1D             | -                | 10 | -        | face_up_quest              |
| Produce a Miracle for the Masses    | 2S 4$             | -                | 5  | -        | on_gain_singer_swap (PLOT) |
| Protect the House of Wonder         | 2S 1G 2$          | -                | 8  | -        | score_per_piety (PLOT)     |
| Eliminate Vampire Coven             | 2S 2G 1B          | 4$               | 11 | -        | -                          |
| Defend the Tower of Luck            | 2S 1G 1B 1D       | -                | 0  | -        | gain_resource_round (PLOT) |
| Heal Fallen Gray Hand Soldiers      | 2S 1D 4$          | 6G               | 6  | -        | -                          |
| Host Festival for Sune              | 2G 2D 4$          | 2S               | 9  | -        | -                          |
| Seal Gate to Cyric's Realm          | 2S 3B 4$          | -                | 20 | -        | -                          |
| Create a Shrine to Oghma            | 5S 2$             | -                | 25 | -        | -                          |

### Arcana Quests (A)

| Card Name                          | Cost              | Reward Resources | VP | Intrigue | Special                      |
|------------------------------------|-------------------|------------------|----|----------|------------------------------|
| Research Chronomancy                | 2D 4$             | 1D               | 4  | -        | worker_recall (PLOT)         |
| Explore Ahghairon's Tower           | 1G 2D 2$          | -                | 6  | -        | on_gain_guitarist_i (PLOT)   |
| Domesticate Owlbears                | 1S 2D             | 1G 2D            | 8  | -        | -                            |
| Study the Illusk Arch               | 1S 2D             | -                | 8  | -        | score_per_arcana (PLOT)      |
| Recover the Magister's Orb          | 3B 2D             | -                | 6  | -        | use_occupied (PLOT)          |
| Steal Spellbook from Silverhand     | 1G 2B 2D          | 4$               | 7  | 2        | -                            |
| Retrieve Ancient Artifacts          | 2G 1B 2D          | 4$               | 11 | -        | -                            |
| Investigate Aberrant Infestation    | 1S 1G 2D          | -                | 13 | 1        | -                            |
| Recruit for Blackstaff Academy      | 1G 1B 2D 4$       | 3D               | 6  | -        | -                            |
| Expose Red Wizards' Spies           | 1S 1G 2B 2D 2$    | -                | 20 | 1        | -                            |
| Infiltrate Halaster's Circle        | 5D 2$             | -                | 25 | -        | -                            |

### Skullduggery Quests (S)

| Card Name                            | Cost              | Reward Resources | VP | Intrigue | Special                        |
|--------------------------------------|-------------------|------------------|----|----------|--------------------------------|
| Expose Cult Corruption                | 1S 4B             | 2S               | 4  | -        | -                              |
| Fence Goods for Duke of Darkness      | 1G 3B 4$          | -                | 6  | -        | on_gain_bass_coins (PLOT)      |
| Install a Spy in Castle Waterdeep     | 4B 4$             | -                | 8  | -        | score_per_skulduggery (PLOT)   |
| Establish Harpers Safe House          | 2G 3B 2$          | -                | 8  | -        | score_existing_buildings (PLOT)|
| Procure Stolen Goods                  | 3B 6$             | -                | 8  | 2        | -                              |
| Build a Reputation in Skullport       | 1G 3B 4$          | -                | 10 | 1        | -                              |
| Place a Sleeper Agent in Skullport    | 1G 4B 1D          | -                | 0  | -        | score_per_intrigue (PLOT)      |
| Steal from House Adarbrent            | 1G 4B 1D          | 6$               | 10 | -        | -                              |
| Take Over Rival Organization          | 1G 2B 1D 6$       | 4B               | 10 | -        | -                              |
| Prison Break                          | 4B 2D 2$          | 2G               | 14 | -        | play_intrigue                  |
| Raid on Undermountain                 | 1S 2G 4B 1D       | 2$               | 20 | -        | -                              |
| Establish Shadow Thieves' Guild       | 1G 8B 1D          | -                | 25 | -        | -                              |

---

## Plot Quest Summary

Plot quests provide ongoing benefits after completion. They are high-priority strategic cards.

| Card Name                        | Type | Cost            | VP | Ongoing Effect                                       |
|----------------------------------|------|-----------------|----|------------------------------------------------------|
| Bolster Griffon Cavalry          | W    | 4G 4$           | 6  | When you gain a Guitarist, +1 extra Guitarist        |
| Explore Ahghairon's Tower        | A    | 1G 2D 2$        | 6  | When you gain a Guitarist, +1 Intrigue card          |
| Produce a Miracle for the Masses | P    | 2S 4$           | 5  | When you gain a Singer, trade any 1 resource for 1 Singer |
| Fence Goods for Duke of Darkness | S    | 1G 3B 4$        | 6  | When you gain a Bass Player, +2 Coins                |
| Bribe the Shipwrights            | C    | 4B 1D 4$        | 10 | When you gain Coins, +1 Bass Player                  |
| Study the Illusk Arch            | A    | 1S 2D           | 8  | +2 VP per future Arcana quest completed              |
| Establish New Merchant Guild     | C    | 1S 2G 4$        | 8  | +2 VP per future Commerce quest completed            |
| Protect the House of Wonder      | P    | 2S 1G 2$        | 8  | +2 VP per future Piety quest completed               |
| Install a Spy in Castle Waterdeep| S    | 4B 4$           | 8  | +2 VP per future Skullduggery quest completed        |
| Quell Mercenary Uprising         | W    | 1S 4G           | 8  | +2 VP per future Warfare quest completed             |
| Infiltrate Builder's Hall        | C    | 2G 2B 4$        | 6  | +4 VP per future building purchased                  |
| Establish Harpers Safe House     | S    | 2G 3B 2$        | 8  | +2 VP per building already owned (one-time count at completion) |
| Place a Sleeper Agent            | S    | 1G 4B 1D        | 0  | +2 VP per future intrigue card played                |
| Recover the Magister's Orb       | A    | 3B 2D           | 6  | Once per round, use a building occupied by another player |
| Defend the Tower of Luck         | P    | 2S 1G 1B 1D     | 0  | Gain 1 random non-coin resource each round           |
| Recruit Lieutenant               | W    | 1S 5G 1B 1D     | 0  | Gain 1 extra permanent worker                        |
| Research Chronomancy             | A    | 2D 4$           | 4  | Once per round, recall one of your placed workers    |

---

## Card Distribution Statistics

| Quest Type    | Total Cards | Plot Quests | VP Range |
|---------------|-------------|-------------|----------|
| Commerce (C)  | 12          | 3           | 4-25     |
| Warfare (W)   | 14          | 3           | 0-25     |
| Piety (P)     | 11          | 4           | 0-25     |
| Arcana (A)    | 11          | 4           | 4-25     |
| Skullduggery (S)| 12        | 4           | 0-25     |
| **Total**     | **60**      | **18**      |          |

## Resource Demand Summary (Total Cost Across All Cards)

| Resource    | Total Demand | Most Demanding Type |
|-------------|-------------|---------------------|
| Guitarist   | 113         | Warfare (67)        |
| Singer      | 42          | Piety (23)          |
| Bass Player | 89          | Skullduggery (41)   |
| Drummer     | 46          | Arcana (28)         |
| Coins       | 136         | Commerce (50)       |

This shows each quest type has a primary resource affinity:
- **Rock** (Warfare) favors Guitarists heavily
- **Soul** (Piety) favors Singers
- **Jazz** (Skullduggery) favors Bass Players
- **Funk** (Arcana) favors Drummers
- **Pop** (Commerce) favors Coins (and is more spread across other resources)

---

## Expansion Quest Cards

Both expansions add 30 quest cards each (6 per quest type), for a total of 120 quests across base + both expansions.

### Undermountain Expansion (30 quests)

Priority: **First expansion to implement.**

#### Undermountain New Mechanics

**One-Time Completion Rewards (new)**

| Mechanic ID                | Description                                                                                     |
|----------------------------|-------------------------------------------------------------------------------------------------|
| optional_cost              | Card has a base cost/reward and an optional enhanced tier — player chooses at completion         |
| take_all_faceup_quests     | Take all face-up quests from Cliffwatch Inn (quest display)                                     |
| take_all_faceup_buildings  | Put all face-up buildings from Builder's Hall (building marketplace) under your control for free |
| return_workers             | Return up to N workers to your pool (they can be re-placed in future rounds)                    |
| draw_intrigue_per_resource | Draw 1 intrigue card for each specific resource type used to complete the quest                  |
| vp_per_resource_used       | Gain +2 VP for each specific resource type used to complete the quest                           |
| draw_and_play_intrigue     | Draw N intrigue cards, may play each one immediately as drawn                                   |

**Ongoing Effects / Plot Quests (new)**

| Mechanic ID             | Description                                                                                       |
|-------------------------|---------------------------------------------------------------------------------------------------|
| use_marketplace_building| Once per turn, assign a worker to an unpurchased building in the marketplace and use its effect    |
| intrigue_chain          | After any action that lets you play intrigue, draw an intrigue card and may play it immediately    |
| return_quest_resource   | When completing any quest, you may return 1 resource used on that quest to your pool               |
| on_take_quest_resource  | When you pick up a quest of a specific genre, gain 1 resource (×5 variants, one per genre)        |
| complete_faceup_quests  | You may complete face-up quests in the quest display as though they were your active quests        |
| gain_owner_benefit      | When you assign a worker to a building you own, you also gain the owner benefit                   |

**Mega Quests:** Undermountain introduces 40-VP mega quests — one per quest type, with very high costs and no special effects.

#### Undermountain Commerce Quests (6)

| Card Name                       | Cost                | Reward Resources | VP | Special                            |
|---------------------------------|---------------------|------------------|----|-------------------------------------|
| Obtain Builders' Plans          | 2G 2B 1D 10$        | -                | 13 | use_marketplace_building (PLOT)     |
| Recruit for City Watch          | 1S 1D (opt: +10$)   | (opt: 3G 3B)     | 8  | optional_cost                       |
| Steal Gems from the Bone Throne | 4B 2D               | 10$              | 7  | -                                   |
| Threaten the Builders' Guilds   | 2G 4B 2D 10$        | -                | 13 | take_all_faceup_buildings           |
| Sponsor Bounty Hunters          | 1S 4G 3B 6$         | -                | 12 | on_take_commerce_resource (PLOT): +4$ when you take a Commerce quest |
| Ransack Whitehelm's Tomb        | 2S 3G 4B 10$        | -                | 40 | mega_quest                          |

#### Undermountain Arcana Quests (6)

| Card Name                         | Cost              | Reward Resources | VP | Special                              |
|-------------------------------------|-------------------|------------------|----|---------------------------------------|
| Study in the Librarium              | 2B 5D 5$          | -                | 11 | intrigue_chain (PLOT)                 |
| Deal With the Black Viper           | 1G 4B 2D 5$       | 4 Intrigue       | 10 | draw_and_play_intrigue                |
| Resurrect Dead Wizards              | 3S 5$             | 3D               | 6  | -                                     |
| Explore Trobriand's Graveyard       | 2G 3B 4D 6$       | -                | 40 | mega_quest                            |
| Survive a Meeting With Halaster     | 1S 1G 4?          | -                | 15 | draw_intrigue_per_resource (per D used) |
| Establish Wizard Academy            | 1S 1G 3B 3D       | -                | 12 | on_take_arcana_resource (PLOT): +1D when you take an Arcana quest |

#### Undermountain Piety Quests (6)

| Card Name                       | Cost              | Reward Resources     | VP | Special                               |
|---------------------------------|-------------------|----------------------|----|----------------------------------------|
| Establish Temple to Ibrandul    | 3S 4B 5$          | 1S 1G 1B 1D         | 11 | take_all_faceup_quests                 |
| Rescue Clerics of Tymora        | 6G 2D             | 3S                   | 10 | -                                      |
| Sanctify a Desecrated Temple    | 4S 2G 5$          | -                    | 13 | on_take_piety_resource (PLOT): +1S when you take a Piety quest |
| Diplomatic Mission to Suzail    | 3S 3G 3$          | -                    | 10 | complete_faceup_quests (PLOT)          |
| Plunder the Island Temple       | 5S 2G 2B 1D       | -                    | 40 | mega_quest                             |
| Root Out Loviatar's Faithful    | 1G 1D 4?          | -                    | 15 | vp_per_resource_used (per S used)      |

#### Undermountain Warfare Quests (6)

| Card Name                          | Cost                 | Reward Resources | VP     | Special                               |
|------------------------------------|----------------------|------------------|--------|----------------------------------------|
| Seize Citadel of the Bloody Hand   | 1S 4G 2D             | -                | 6      | return_quest_resource (PLOT)           |
| Defend the Yawning Portal          | 3S 6G 1B 1D          | 2?               | 15     | return_workers (up to 3)               |
| Wake the Six Sleepers              | 3S 3B                | 6G               | 8      | -                                      |
| Battle in Muiral's Gauntlet        | 2S 7G 2D 2$          | -                | 40     | mega_quest                             |
| Recover the Flame of the North     | 5G 3B 1D 3$          | -                | 10     | on_take_warfare_resource (PLOT): +1G when you take a Warfare quest |
| Destroy a Temple of Selvetarm      | 1S 2G 2$ (opt: +4G)  | -                | 10 (20)| optional_cost                          |

#### Undermountain Skullduggery Quests (6)

| Card Name                          | Cost                 | Reward Resources | VP     | Special                              |
|------------------------------------|----------------------|------------------|--------|---------------------------------------|
| Defend the Lanceboard Room         | 3G 6B 1D 10$         | 8?               | 12     | -                                     |
| Survive Arcturia's Transformation  | 6G 5$                | 6B               | 6      | -                                     |
| Ally with Xanathar's Guild         | 2G 5B 1D 5$          | -                | 10     | on_take_skullduggery_resource (PLOT): +1B when you take a Skullduggery quest |
| Break Into Blackstaff Tower        | 1S 7B 2D 9$          | -                | 40     | mega_quest                            |
| Unleash Crime Spree                | 1S 1G 1B 1D (opt: +4B) | -              | 12 (22)| optional_cost                         |
| Impersonate Tax Collector           | 1G 4B 1D 5$          | -                | 9      | gain_owner_benefit (PLOT)             |

#### Undermountain Plot Quest Summary

| Card Name                        | Type | Cost              | VP | Ongoing Effect                                              |
|----------------------------------|------|-------------------|----|--------------------------------------------------------------|
| Obtain Builders' Plans           | C    | 2G 2B 1D 10$      | 13 | Once per turn, use an unpurchased building's effect           |
| Sponsor Bounty Hunters           | C    | 1S 4G 3B 6$       | 12 | When you take a Commerce quest, +4$                          |
| Study in the Librarium           | A    | 2B 5D 5$          | 11 | After playing intrigue, draw 1 intrigue and may play it      |
| Establish Wizard Academy         | A    | 1S 1G 3B 3D       | 12 | When you take an Arcana quest, +1D                           |
| Sanctify a Desecrated Temple     | P    | 4S 2G 5$          | 13 | When you take a Piety quest, +1S                             |
| Diplomatic Mission to Suzail     | P    | 3S 3G 3$          | 10 | Complete face-up quests as if they were your active quests    |
| Seize Citadel of the Bloody Hand | W    | 1S 4G 2D          | 6  | When completing any quest, return 1 resource used             |
| Recover the Flame of the North   | W    | 5G 3B 1D 3$       | 10 | When you take a Warfare quest, +1G                           |
| Ally with Xanathar's Guild       | S    | 2G 5B 1D 5$       | 10 | When you take a Skullduggery quest, +1B                      |
| Impersonate Tax Collector        | S    | 1G 4B 1D 5$       | 9  | When visiting your own building, also gain owner benefit      |

---

### Skullport Expansion (30 quests)

Priority: **Second expansion, if implemented.** Requires the Corruption mechanic.

#### Corruption in Quests

Skullport quests interact with corruption in three ways:
- **Gain corruption** — quest reward includes taking corruption from the shared pool (shown as positive numbers)
- **Remove corruption** — quest reward lets you return corruption to the pool (shown as negative numbers)
- **Corruption-enhanced board spaces** — plot quests that let you gain extra resources + corruption when visiting specific permanent board spaces

See the building-mapping-analysis.md for full corruption scoring rules (escalating shared-pool penalty).

#### Skullport Board Space Reference

Several Skullport plot quests enhance specific permanent board spaces. These are the Waterdeep names — music-themed equivalents TBD:

| Waterdeep Board Space       | Normal Effect           | Enhanced Effect (after plot quest)                |
|-----------------------------|-------------------------|---------------------------------------------------|
| Blackstaff Tower            | 1 Wizard                | Also take 1 Wizard + 1 Corruption                |
| Aurora's Realms Shop        | Buy from marketplace    | Also take 4 Gold + 1 Corruption                  |
| The Plinth                  | Assign quest/intrigue   | Also take 1 Cleric + 1 Corruption                |
| Grinning Lion Tavern        | Rogues                  | Also take 2 Rogues + 1 Corruption                |
| Field of Triumph            | Fighters                | Also take 2 Fighters + 1 Corruption              |
| Waterdeep Harbor            | Play intrigue           | May play up to 2 extra intrigue + 1 Corruption   |
| Castle Waterdeep (FastPass) | First-player token      | You + visiting player each take 1 Fighter         |

#### Skullport New Mechanics

**One-Time Completion Rewards (new)**

| Mechanic ID                   | Description                                                                  |
|-------------------------------|------------------------------------------------------------------------------|
| corruption_removal            | Remove N corruption from your pool (return to shared supply)                  |
| corruption_gain               | Take N corruption from the shared supply                                      |
| opponents_return_resource     | Each opponent must return 1 resource of their choice                          |
| take_2_faceup_buildings       | Put 2 face-up buildings under your control for free (+ corruption)            |

**Ongoing Effects / Plot Quests (new)**

| Mechanic ID                    | Description                                                                              |
|--------------------------------|------------------------------------------------------------------------------------------|
| enhanced_board_space (×5)      | Gain bonus resources + corruption when visiting a specific permanent board space           |
| play_extra_intrigue_corruption | Play up to 2 extra intrigue at Waterdeep Harbor, take corruption if you do                |
| first_player_bonus             | When any player takes FastPass, you and that player each gain 1 Fighter (no double-dip)   |
| remove_corruption_on_purchase  | When you buy a building, remove 1 corruption and place it on any action space             |
| draw_intrigue_on_corruption    | Once per turn, when you gain corruption, draw 1 intrigue card                             |
| double_corruption_return       | When you return any corruption, you may return 1 additional corruption                    |

#### Skullport Commerce Quests (6)

| Card Name                  | Cost              | Reward Resources | VP | Corruption | Special                              |
|----------------------------|-------------------|------------------|----|------------|---------------------------------------|
| Donate to the City         | 2S 1D 10$         | -                | 13 | -3         | -                                     |
| Fund Alchemical Research   | 1S 1B 2D 4$       | 12$              | 20 | +3         | -                                     |
| Extort Aurora              | 2B 4$             | -                | 8  | -          | enhanced_board_space (PLOT): +4$ +corruption at Aurora's Realms Shop |
| Defame Rival Business      | 1S 2G 2B 4$       | -                | 9  | -          | remove_corruption_on_purchase (PLOT)  |
| Fund Pilgrimage of Waukeen | 1S 1G 2B 5$       | -                | 16 | -          | -                                     |
| Pay Fines                  | 1S 3B 4$          | -                | 4  | -2         | -                                     |

#### Skullport Arcana Quests (6)

| Card Name                    | Cost                | Reward Resources   | VP | Corruption | Special                                 |
|------------------------------|---------------------|--------------------|----|------------|-----------------------------------------|
| Investigate Thayan Vessel    | 1S 2G 2B 2D 2$     | 2? 2$              | 13 | -          | -                                       |
| Seal an Entrance to Skullport| 1S 2G 2B 2D        | -                  | 10 | -3         | -                                       |
| Renew Guards and Wards       | 1S 1G 2D 2$        | -                  | 9  | -2         | -                                       |
| Recruit Academy Castoffs     | 1G 1D 2$           | -                  | 8  | -          | enhanced_board_space (PLOT): +1D +corruption at Blackstaff Tower |
| Uncover Forbidden Lore       | 2B 3D              | -                  | 17 | -          | play_extra_intrigue_corruption (PLOT): play 2 extra intrigue at Harbor +corruption |
| Establish Cult Cell          | 2B 2D 3$           | 2G 1D 1 Intrigue   | 18 | +3         | -                                       |

#### Skullport Piety Quests (6)

| Card Name                        | Cost            | Reward Resources | VP | Corruption | Special                                  |
|----------------------------------|-----------------|------------------|----|------------|------------------------------------------|
| Banish Evil Spirits              | 2S 2G 1D        | 1?               | 5  | -2         | -                                        |
| Institute Reforms                | 4S 1G 1B 2$     | -                | 13 | -3         | -                                        |
| Give Honor to Mask               | 1S 1B 2$        | -                | 8  | -          | enhanced_board_space (PLOT): +1S +corruption at the Plinth |
| Sanctify Temple to Oghma         | 2S 1D 5$        | -                | 18 | -          | -                                        |
| Enter the Tower of Seven Woes    | 7?              | 3S               | 19 | +4         | -                                        |
| Protect Converts to Eilistraee   | 3S 2G 1D        | -                | 10 | -          | double_corruption_return (PLOT)           |

#### Skullport Warfare Quests (6)

| Card Name                | Cost              | Reward Resources | VP | Corruption | Special                                      |
|--------------------------|-------------------|------------------|----|------------|-----------------------------------------------|
| Train Castle Guards      | 2G 1D 5$          | -                | 10 | -          | first_player_bonus (PLOT): you + FastPass visitor each get 1G (no double-dip) |
| Patrol Dock Ward         | 1S 3G 2B 2$       | 4B               | 9  | -          | -                                             |
| Uncover Drow Plot        | 1S 5G 2B 5$       | -                | 18 | -2         | -                                             |
| Fix the Champion's Games | 3G 2$             | -                | 8  | -          | enhanced_board_space (PLOT): +2G +corruption at Field of Triumph |
| Improve Prison Security  | 1S 4G 2B 4$       | -                | 8  | -3         | -                                             |
| Assassinate Rivals       | 4G 1B             | -                | 16 | +2         | opponents_return_resource                     |

#### Skullport Skullduggery Quests (6)

| Card Name                       | Cost              | Reward Resources | VP | Corruption | Special                                  |
|---------------------------------|-------------------|------------------|----|------------|------------------------------------------|
| Save Kidnapped Nobles           | 6B 2D 5$          | 4G               | 9  | -3         | -                                        |
| Rescue of Victim from the Skulls| 2G 4B 1D          | 1?               | 9  | -1         | -                                        |
| Expand Guild Activities         | 1G 2B 2$          | -                | 8  | -          | enhanced_board_space (PLOT): +2B +corruption at Grinning Lion |
| Shelter Zhentarim Agents        | 1S 3G 2D          | -                | 16 | +1         | draw_intrigue_on_corruption (PLOT)       |
| Bury the Bodies                 | 2G 3B 2$          | -                | 20 | +2         | -                                        |
| Swindle the Builder's Guilds    | 1S 2G 3B 5$       | -                | 13 | +3         | take_2_faceup_buildings                  |

#### Skullport Plot Quest Summary

| Card Name                      | Type | Cost           | VP | Ongoing Effect                                                          |
|--------------------------------|------|----------------|----|-------------------------------------------------------------------------|
| Extort Aurora                  | C    | 2B 4$          | 8  | At Aurora's Realms Shop: also take 4$ + corruption                       |
| Defame Rival Business          | C    | 1S 2G 2B 4$    | 9  | When buying a building: remove 1 corruption, place on any action space   |
| Recruit Academy Castoffs       | A    | 1G 1D 2$       | 8  | At Blackstaff Tower: also take 1D + corruption                           |
| Uncover Forbidden Lore         | A    | 2B 3D          | 17 | At Waterdeep Harbor: may play 2 extra intrigue + corruption              |
| Give Honor to Mask             | P    | 1S 1B 2$       | 8  | At the Plinth: also take 1S + corruption                                 |
| Protect Converts to Eilistraee | P    | 3S 2G 1D       | 10 | When returning corruption, may return 1 extra                             |
| Train Castle Guards            | W    | 2G 1D 5$       | 10 | When any player takes FastPass: you + that player each gain 1G (no dupes) |
| Fix the Champion's Games       | W    | 3G 2$          | 8  | At Field of Triumph: also take 2G + corruption                           |
| Expand Guild Activities        | S    | 1G 2B 2$       | 8  | At Grinning Lion: also take 2B + corruption                              |
| Shelter Zhentarim Agents       | S    | 1S 3G 2D       | 16 | Once per turn, when gaining corruption: draw 1 intrigue                   |

---

### Expansion Card Distribution Statistics

| Expansion     | Quest Type      | Total Cards | Plot Quests | VP Range |
|---------------|-----------------|-------------|-------------|----------|
| Undermountain | Commerce (C)    | 6           | 2           | 7-40     |
| Undermountain | Arcana (A)      | 6           | 2           | 6-40     |
| Undermountain | Piety (P)       | 6           | 2           | 10-40    |
| Undermountain | Warfare (W)     | 6           | 2           | 6-40     |
| Undermountain | Skullduggery (S)| 6           | 2           | 6-40     |
| **UM Total**  |                 | **30**      | **10**      |          |
| Skullport     | Commerce (C)    | 6           | 2           | 4-20     |
| Skullport     | Arcana (A)      | 6           | 2           | 8-18     |
| Skullport     | Piety (P)       | 6           | 2           | 5-19     |
| Skullport     | Warfare (W)     | 6           | 2           | 8-18     |
| Skullport     | Skullduggery (S)| 6           | 2           | 8-20     |
| **SP Total**  |                 | **30**      | **10**      |          |
| **Grand Total** (all expansions) | | **120** | **38**     |          |

---

## Implementation Status
Tracks which special mechanics are implemented in the game engine.

### One-Time Completion Rewards

| Mechanic ID          | Status      | Notes                                              |
|----------------------|-------------|----------------------------------------------------|
| choose_building      | DONE        | reward_building = "market_choice"                  |
| random_building      | DONE        | reward_building = "random_draw"                    |
| face_up_quest        | DONE        | reward_draw_quests + reward_quest_draw_mode="choose"|
| random_quest         | DONE        | reward_draw_quests + reward_quest_draw_mode="random"|
| play_intrigue        | DONE        | reward_play_intrigue field + handle_play_intrigue_from_quest |
| opponent_gains_coins | DONE        | reward_opponent_gains_coins field + handle_choose_opponent    |

### Scoring Plot Quests

| Mechanic ID              | Status      | Notes                                          |
|--------------------------|-------------|-------------------------------------------------|
| score_per_genre (×5)     | DONE        | bonus_vp_per_genre_quest + bonus_vp_genre fields|
| score_per_intrigue       | DONE        | bonus_vp_per_intrigue_played field              |
| score_per_building       | DONE        | +4 VP per future building purchased             |
| score_existing_buildings | DONE        | bonus_vp_per_building_owned field               |

### Resource Trigger Plot Quests

| Mechanic ID         | Status | Notes                                                    |
|---------------------|--------|----------------------------------------------------------|
| on_gain_guitarist   | DONE   | resource_trigger_type + resource_trigger_bonus fields     |
| on_gain_guitarist_i | DONE   | resource_trigger_type + resource_trigger_draw_intrigue    |
| on_gain_singer_swap | DONE   | resource_trigger_type + resource_trigger_is_swap          |
| on_gain_bass_coins  | DONE   | resource_trigger_type + resource_trigger_bonus fields     |
| on_gain_coins_bass  | DONE   | resource_trigger_type + resource_trigger_bonus fields     |

### Persistent Ability Plot Quests

| Mechanic ID         | Status      | Notes |
|---------------------|-------------|-------|
| extra_worker        | DONE        | reward_extra_worker field, increments total_workers          |
| gain_resource_round | DONE        | reward_choose_resource_per_round + round-start prompt        |
| worker_recall       | DONE        | reward_recall_worker field + handle_recall_worker            |
| use_occupied        | DONE        | reward_use_occupied_building + _can_use_occupied helper      |
