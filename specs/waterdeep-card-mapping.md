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

## Implementation Status

Tracks which special mechanics are implemented in the game engine.

### One-Time Completion Rewards

| Mechanic ID          | Status      | Notes                                              |
|----------------------|-------------|----------------------------------------------------|
| choose_building      | DONE        | reward_building = "market_choice"                  |
| random_building      | DONE        | reward_building = "random_draw"                    |
| face_up_quest        | DONE        | reward_draw_quests + reward_quest_draw_mode="choose"|
| random_quest         | DONE        | reward_draw_quests + reward_quest_draw_mode="random"|
| play_intrigue        | NOT STARTED | Data in JSON but no ContractCard field or logic    |
| opponent_gains_coins | NOT STARTED | Data in JSON but no ContractCard field or logic    |

### Scoring Plot Quests

| Mechanic ID              | Status      | Notes                                          |
|--------------------------|-------------|-------------------------------------------------|
| score_per_genre (×5)     | DONE        | bonus_vp_per_genre_quest + bonus_vp_genre fields|
| score_per_intrigue       | DONE        | bonus_vp_per_intrigue_played field              |
| score_per_building       | DONE        | +4 VP per future building purchased             |
| score_existing_buildings | DONE        | bonus_vp_per_building_owned field               |

### Resource Trigger Plot Quests

| Mechanic ID         | Status      | Notes |
|---------------------|-------------|-------|
| on_gain_guitarist   | NOT STARTED |       |
| on_gain_guitarist_i | NOT STARTED |       |
| on_gain_singer_swap | NOT STARTED |       |
| on_gain_bass_coins  | NOT STARTED |       |
| on_gain_coins_bass  | NOT STARTED |       |

### Persistent Ability Plot Quests

| Mechanic ID         | Status      | Notes |
|---------------------|-------------|-------|
| extra_worker        | NOT STARTED |       |
| gain_resource_round | NOT STARTED |       |
| worker_recall       | NOT STARTED |       |
| use_occupied        | NOT STARTED |       |
