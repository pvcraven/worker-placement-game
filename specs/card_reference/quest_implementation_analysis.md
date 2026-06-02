# Quest Card Implementation Analysis

## Resource & Genre Mapping

| Original (Lords of Waterdeep) | Our Game          |
|-------------------------------|-------------------|
| White (Cleric)                | Singers           |
| Orange (Fighter)              | Guitarists        |
| Black (Rogue)                 | Bass Players      |
| Purple (Wizard)               | Drummers          |
| Gold                          | Coins             |
| Arcana                        | Funk              |
| Commerce                      | Pop               |
| Piety                         | Soul              |
| Skullduggery                  | Jazz              |
| Warfare                       | Rock              |

---

## Currently Implemented (60 cards across 5 genres)

All 60 cards are drawn primarily from the **Base game**. Every implemented mechanic is listed below.

### Implemented Mechanics

| Mechanic | Example Card | Code Support |
|----------|-------------|--------------|
| Simple cost → VP + bonus resources | Many cards | Yes |
| Plot: +2 VP per genre quest completed | Record Label Empire (pop_005) | Yes |
| Plot: Resource trigger → gain resources | Rock Loyalty Program (rock_001) | Yes |
| Plot: Resource trigger → draw intrigue | Explore the Groove Archive (funk_002) | Yes |
| Plot: Resource trigger → swap resource | Miracle at the Microphone (soul_004) | Yes |
| Plot: Choose 1 resource per round | Soul Music Residency (soul_007) | Yes |
| Plot: Extra permanent worker | Hire a Tour Manager (rock_009) | Yes |
| Plot: +4 VP per building purchased | Venue Investment Fund (pop_006) | Yes |
| Plot: +2 VP per intrigue played | Sleeper Agent at the Label (jazz_007) | Yes |
| Plot: Use occupied building once/round | Recover the Master Tapes (funk_005) | Yes |
| Reward: Draw quest (choose from market) | Convert a Classical Musician (soul_001) | Yes |
| Reward: Draw intrigue cards | A&R Talent Scout (pop_004) | Yes |
| Reward: Play intrigue immediately | Jailhouse Jazz Session (jazz_010) | Yes |
| Reward: Gain building (market choice) | Pop-Up Venue Launch (pop_001) | Yes |
| Reward: Gain building (random draw) | Lottery Venue Prize (pop_009) | Yes |
| Reward: Opponent gains resources | Charity Gala Showcase (pop_008) | Yes |
| Reward: Recall a placed worker | Time Warp Remix (funk_001) | Yes |
| Reward: +VP per building already owned | Establish a Speakeasy Network (jazz_004) | Yes |

### Card-by-Card Mapping (Current → Original)

<details>
<summary><b>Pop (Commerce) — 12 cards</b></summary>

| Our Card | Original Card | Match |
|----------|--------------|-------|
| Pop-Up Venue Launch | Lure Artisans Of Mirabar | Exact |
| Corporate Sponsorship Deal | Spy On The Lighthouse | Exact |
| Producer Security Detail | Safeguard Eltorchul Mage | Exact |
| A&R Talent Scout | Loot The Crypt Of Chauntea | Close |
| Record Label Empire | Establish New Merchant Guild | Exact |
| Venue Investment Fund | Infiltrate Builder's Hall | Exact |
| Session Musician Poach | Thin The City Watch | Exact |
| Charity Gala Showcase | Send Aid To The Harpers | Exact |
| Lottery Venue Prize | Placate The Walking Statue | Exact |
| Payola Pipeline | Bribe The Shipwrights | Exact |
| VIP Industry Gala | Impersonate Adarbrent Noble | Exact |
| Grammy Night Showcase | Ally With House Thann | Exact |

</details>

<details>
<summary><b>Rock (Warfare) — 12 cards</b></summary>

| Our Card | Original Card | Match |
|----------|--------------|-------|
| Rock Loyalty Program | Bolster Griffon Cavalry | Exact |
| Rock Union Takeover | Quell Mercenary Uprising | Exact |
| Ambush at the Arena | Ambush Artor Morlin | Exact |
| Raid the Rival Studio | Raid Orc Stronghold | Exact |
| Crush the Underground Revolt | Defeat Uprising From Undermountain | Exact |
| Deliver an Ultimatum | Deliver An Ultimatum | Exact |
| Reunion Tour Penance | Perform The Penance Of Duty | Exact |
| Repel the Critics | Repel Seawraiths | Exact |
| Hire a Tour Manager | Recruit Lieutenant | Exact |
| Stadium Rock Revival | Recruit Paladins For Tyr | Exact |
| Confront the Kingpin | Confront The Xanathar | Exact |
| Rock Army Mobilization | Bolster City Guard | Exact |

</details>

<details>
<summary><b>Soul (Piety) — 12 cards</b></summary>

| Our Card | Original Card | Match |
|----------|--------------|-------|
| Convert a Classical Musician | Convert A Noble To Lathander | Exact |
| Discover Hidden Soul Venue | Discover Hidden Temple Of Lolth | Exact |
| Gospel Alliance | Form An Alliance With The Rashemi | Exact |
| Miracle at the Microphone | Produce Miracle For The Masses | Exact |
| Protect the Soul Legacy | Protect The House Of Wonder | Exact |
| Eliminate the Rival Revue | Eliminate Vampire Coven | Exact |
| Soul Music Residency | Defend The Tower Of Luck | Exact |
| Rehabilitate Burned-Out Artists | Heal Fallen Gray Hand Soldiers | Exact |
| Soul Revival Festival | Host Festival For Sune | Exact |
| Soul Train Anniversary Special | Seal Gate To Cyric's Realm | Exact |
| Church of Soul Music | Create A Shrine To Oghma | Exact |
| Donate Instruments to Charity | Deliver Weapons To Selune's Temple | Exact |

</details>

<details>
<summary><b>Funk (Arcana) — 12 cards</b></summary>

| Our Card | Original Card | Match |
|----------|--------------|-------|
| Time Warp Remix | Research Chronomancy | Exact |
| Explore the Groove Archive | Explore Ahghairon's Tower | Exact |
| Tame the Wild Sessions | Domesticate Owlbears | Exact |
| Study the Funk Masters | Study The Illusk Arch | Exact |
| Recover the Master Tapes | Recover The Magister's Orb | Exact |
| Steal the Secret Arrangements | Steal Spellbook From Silverhand | Exact |
| Retrieve Vintage Instruments | Retrieve Ancient Artifacts | Exact |
| Investigate the Underground | Investigate Aberrant Infestation | Exact |
| Funk Academy Recruitment | Recruit For Blackstaff Academy | Exact |
| Mothership Connection Tour | Expose Red Wizards' Spies | Exact |
| Interstellar Funk Odyssey | Infiltrate Halaster's Circle | Exact |
| Funk Boot Camp | Train Bladesingers | Exact |

</details>

<details>
<summary><b>Jazz (Skullduggery) — 12 cards</b></summary>

| Our Card | Original Card | Match |
|----------|--------------|-------|
| Expose Industry Corruption | Expose Cult Corruption | Exact |
| Fence Bootleg Recordings | Fence Goods For Duke Of Darkness | Exact |
| Plant a Mole at Rival Label | Install A Spy In Castle Waterdeep | Exact |
| Establish a Speakeasy Network | Establish Harpers Safe House | Exact |
| Procure Rare Pressings | Procure Stolen Goods | Close |
| Underground Reputation | Build A Reputation In Skullport | Exact |
| Sleeper Agent at the Label | Place A Sleeper Agent In Skullport | Exact |
| Rob the Jazz Aristocrats | Steal From House Adarbrent | Exact |
| Hostile Label Takeover | Take Over Rival Organization | Exact |
| Jailhouse Jazz Session | Prison Break | Exact |
| Jazz Underground Raid | Raid On Undermountain | Exact |
| Shadow Jazz Syndicate | Establish Shadow Thieves' Guild | Exact |

</details>

---

## Implemented in Feature 039 (Tier 1 Expansion)

15 cards added to the game with zero code changes — only `config/contracts.json` entries and card image generation.

| Original Card | Type | Our Card | Genre | VP |
|---------------|------|----------|-------|----|
| Wake the Six Sleepers | Warfare | Wake the Sleeping Legends | Rock | 8 |
| Resurrect Dead Wizards | Arcana | Resurrect the Funk Pioneers | Funk | 6 |
| Survive Arcturia's Transformation | Skullduggery | Survive the Genre Crossover | Jazz | 6 |
| Rescue Clerics of Tymora | Piety | Rescue the Gospel Choir | Soul | 10 |
| Steal Gems from the Bone Throne | Commerce | Platinum Record Heist | Pop | 7 |
| Recruit for City Watch (base) | Commerce | Street Team Recruitment | Pop | 8 |
| Destroy Temple of Selvetarm (base) | Warfare | Demolish the Rival Arena | Rock | 10 |
| Unleash Crime Spree (base) | Skullduggery | Underground Jazz Blitz | Jazz | 12 |
| Explore Trobriand's Graveyard | Arcana | Funkadelic Magnum Opus | Funk | 40 |
| Ransack Whitehelm's Tomb | Commerce | Global Pop Domination | Pop | 40 |
| Plunder the Island Temple | Piety | Soul Music Magnum Opus | Soul | 40 |
| Battle in Muiral's Gauntlet | Warfare | Rock Legends World Tour | Rock | 40 |
| Break Into Blackstaff Tower | Skullduggery | Jazz Empire Conspiracy | Jazz | 40 |
| Fund Pilgrimage of Waukeen | Commerce | International Pop Tour | Pop | 16 |
| Sanctify Temple to Oghma | Piety | Soul Heritage Foundation | Soul | 18 |

---

## Unimplemented Cards by Expansion

### TBD: Defend the Lanceboard Room (Skullduggery → Jazz)

**Original**: Cost 3oj+6bl+1pu+10g, VP=12, Reward: 8 resources of player's choice ("any").
**Deferred**: Requires a "choose any resource" one-time reward mechanic not yet implemented. Will be added as "Grand Jazz Caper" in a future feature alongside that mechanic.

---

### Tier 2: Minor Code Changes (new mechanic variant, ~1-2 days each)

#### 2A. "When you take a [genre] quest" trigger (Undermountain plot quests)

Trigger fires when the player picks up a quest of a specific genre from the market, granting a small bonus.

| Original Card | Type | Genre Trigger | Bonus |
|---------------|------|--------------|-------|
| Sponsor Bounty Hunters | Commerce | Take Commerce quest → | +4 gold |
| Sanctify a Desecrated Temple | Piety | Take Piety quest → | +1 white |
| Ally with Xanathar's Guild | Skullduggery | Take Skullduggery quest → | +1 black |
| Recover the Flame of the North | Warfare | Take Warfare quest → | +1 orange |
| Establish Wizard Academy | Arcana | Take Arcana quest → | +1 purple |

**Effort: Medium.** Need a new plot quest hook that fires when a player selects a quest from the market. One new field like `quest_take_trigger_genre` and `quest_take_trigger_bonus`. 5 cards.

#### 2B. Variable rewards based on resources spent

VP or rewards scale with how many of a specific resource was used to pay the cost.

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Survive a Meeting With Halaster | Arcana | Draw 1 intrigue per purple spent |
| Root Out Loviatar's Faithful | Piety | +2 VP per white spent |

**Effort: Medium.** Need to track which resources were used at quest completion and apply a per-unit bonus. 2 cards initially but a reusable mechanic.

#### 2C. Resource recycling on quest completion

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Seize Citadel of the Bloody Hand | Warfare | When completing any quest, return 1 resource used |

**Effort: Medium.** The quest completion flow needs to optionally return resources. 1 card but interesting strategy mechanic.

#### 2D. Optional additional costs for better rewards

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Recruit for City Watch (+ optional) | Commerce | Pay extra for different reward tier |
| Destroy Temple of Selvetarm (+ optional) | Warfare | Pay extra for different reward tier |
| Unleash Crime Spree (+ optional) | Skullduggery | Pay extra for different reward tier |

**Effort: Medium-High.** Need UI for "pay extra?" prompt during quest completion, and a data model for optional costs/rewards. 3 cards but the mechanic is niche.

#### 2E. Deal With the Black Viper variant

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Deal With the Black Viper | Arcana | Draw intrigue cards as reward; may play each immediately as drawn |

**Effort: Low-Medium.** Similar to existing play-intrigue-immediately, but involves drawing then optionally playing in sequence. 1 card.

#### 2F. Mass building acquisition

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Threaten the Builders' Guilds | Commerce | Take ALL face-up buildings for free |

**Effort: Medium.** Need a reward action that transfers all market buildings. 1 card, very powerful effect.

#### 2G. Return multiple workers

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Defend the Yawning Portal | Warfare | Return up to 3 workers to your pool |

**Effort: Low.** Already have recall-1-worker mechanic. Extend to recall N. 1 card.

#### 2H. "Take all quests from market" reward

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Establish Temple to Ibrandul | Piety | Take all quests from the quest market + bonus resources |

**Effort: Medium.** Need a reward that sweeps the quest market. 1 card.

---

### Tier 3: Significant New Systems (weeks of work)

#### 3A. Corruption System (entire Skullport expansion)

The corruption mechanic is the defining feature of the Skullport expansion. Players can take corruption tokens for powerful bonuses, but each corruption is worth **-1 VP at end of game** (and potentially more with scaling penalties).

**Cards that require corruption:**

| Original Card | Type | Corruption | Key Mechanic |
|---------------|------|-----------|--------------|
| Save Kidnapped Nobles | Skullduggery | -3 | Remove 3 corruption + bonus resources |
| Banish Evil Spirits | Piety | -2 | Remove 2 corruption |
| Donate to the City | Commerce | -3 | Remove 3 corruption |
| Institute Reforms | Piety | -3 | Remove 3 corruption |
| Seal Entrance to Skullport | Arcana | -3 | Remove 3 corruption |
| Renew Guards and Wards | Arcana | -2 | Remove 2 corruption |
| Rescue Victim from Skulls | Skullduggery | -1 | Remove 1 corruption |
| Uncover Drow Plot | Warfare | -2 | Remove 2 corruption |
| Improve Prison Security | Warfare | -3 | Remove 3 corruption |
| Pay Fines | Commerce | -2 | Remove 2 corruption |
| Bury the Bodies | Skullduggery | +2 | Gain 2 corruption, high VP |
| Fund Alchemical Research | Commerce | +3 | Gain 3 corruption, huge gold reward |
| Establish Cult Cell | Arcana | +3 | Gain corruption, multi-reward |
| Enter Tower of Seven Woes | Piety | +4 | 7 "any" resource cost, gain corruption |
| Shelter Zhentarim Agents | Skullduggery | +1 | When gaining corruption → draw intrigue |
| Assassinate Rivals | Warfare | +2 | Opponents lose resources |
| Swindle Builder's Guilds | Skullduggery | +3 | Take 2 buildings + corruption |
| Protect Converts to Eilistraee | Piety | — | When removing corruption, remove extra |
| Defame Rival Business | Commerce | — | When buying building, remove corruption |

**Cards that use corruption + specific board space triggers:**

| Original Card | Type | Mechanic |
|---------------|------|----------|
| Recruit Academy Castoffs | Arcana | At Blackstaff Tower → take purple + corruption |
| Extort Aurora | Commerce | At Aurora's Shop → take 4 gold + corruption |
| Give Honor to Mask | Piety | At Plinth → take white + corruption |
| Expand Guild Activities | Skullduggery | At Grinning Lion → take black + corruption |
| Fix Champion's Games | Warfare | At Field of Triumph → take 2 orange + corruption |
| Train Castle Guards | Warfare | First-player trigger → both gain orange |
| Uncover Forbidden Lore | Arcana | At Harbor → play 2 extra intrigue + corruption |

**Effort: Very High.** Requires:
- Corruption token system (gain/remove/track)
- End-game scoring penalty
- "Any" resource type for costs
- Specific board-space triggers for plot quests
- UI for corruption display
- ~26 cards total

#### 3B. Other Complex Mechanics

| Original Card | Mechanic | Effort |
|---------------|----------|--------|
| Obtain Builders' Plans | Virtual worker placement at Builder's Hall once/turn | High |
| Study in the Librarium | After playing intrigue → draw + play another free | High |
| Diplomatic Mission to Suzail | Complete face-up quests without picking them up | High |
| Impersonate Tax Collector | Gain owner benefit when using own buildings | Medium |

---

## Recommended Implementation Order

### Phase 1: Quick Wins (no code changes)
**Add 16 simple cards** from Tier 1 to `contracts.json`. This expands the card pool by 27% with zero risk. The 5 mega quests (40 VP) add a meaningful strategic option.

### Phase 2: Undermountain Plot Quests
**"Take genre quest" triggers** (Tier 2A) — 5 cards with one new mechanic. These plot quests add interesting draft-phase strategy.

### Phase 3: Return Multiple Workers
**Extend recall-worker to N** (Tier 2G) — 1 card, minimal code change. Already have the single-recall mechanic.

### Phase 4: Variable Rewards
**Per-resource-spent bonuses** (Tier 2B) — 2 cards. Interesting decision-making during quest completion.

### Phase 5: Resource Recycling
**Return resources on quest completion** (Tier 2C) — 1 card, but a strategically rich ongoing effect.

### Phase 6: Mass Effects
**Take all buildings/quests** (Tier 2F, 2H) — 2 cards. Dramatic, game-changing effects.

### Phase 7: Optional Costs
**Optional quest upgrades** (Tier 2D) — 3 cards. Needs UI work for the choice prompt.

### Phase 8: Corruption System
**Full Skullport expansion** (Tier 3A) — 26+ cards. Major feature requiring new token system, scoring changes, board-space triggers, and UI. This is effectively a full expansion pack.

---

## Summary Table

| Tier | Cards | New Mechanics | Estimated Effort |
|------|-------|---------------|-----------------|
| 1: JSON-only | 16 | None | Hours |
| 2A: Quest-take triggers | 5 | 1 new trigger type | 1-2 days |
| 2B: Variable rewards | 2 | Per-resource scaling | 1-2 days |
| 2C: Resource recycling | 1 | Return spent resources | 1 day |
| 2D: Optional costs | 3 | Cost upgrade prompt | 2-3 days |
| 2E: Draw-and-play intrigue | 1 | Sequential draw/play | 1 day |
| 2F: Mass building grab | 1 | Market sweep | 1 day |
| 2G: Return N workers | 1 | Extend existing recall | Hours |
| 2H: Take all quests | 1 | Quest market sweep | 1 day |
| 3A: Corruption system | 26+ | Entire subsystem | 1-2 weeks |
| 3B: Complex uniques | 4 | Various | 1 week+ |
| **Total** | **~61** | | |
