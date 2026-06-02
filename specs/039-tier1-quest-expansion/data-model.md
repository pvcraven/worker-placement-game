# Data Model: Tier 1 Quest Card Expansion

**Date**: 2026-06-02

## Entity: ContractCard (existing — no changes)

No new fields or model changes. All 15 cards use existing fields:

| Field | Type | Used By New Cards |
|-------|------|-------------------|
| id | str | Yes — `contract_{genre}_{NNN}` |
| name | str | Yes |
| description | str | Yes |
| genre | Genre enum | Yes |
| cost | ResourceCost | Yes |
| victory_points | int | Yes (6–40 range) |
| bonus_resources | ResourceCost | Yes (5 cards have bonuses) |
| is_plot_quest | bool | Yes — always `false` |

All other ContractCard fields (reward_draw_quests, reward_building, bonus_vp_*, resource_trigger_*, etc.) are omitted from the new card entries and default to their zero/null values.

## New Card Data (15 entries for contracts.json)

### Pop (Commerce) — 4 cards

| ID | Name | Cost | VP | Bonus |
|----|------|------|----|-------|
| contract_pop_013 | Platinum Record Heist | 4 bass, 2 drum | 7 | 10 coins |
| contract_pop_014 | Street Team Recruitment | 1 singer, 1 drum | 8 | — |
| contract_pop_015 | International Pop Tour | 1 singer, 1 guitar, 2 bass, 5 coins | 16 | — |
| contract_pop_016 | Global Pop Domination | 2 singers, 3 guitar, 4 bass, 10 coins | 40 | — |

### Rock (Warfare) — 3 cards

| ID | Name | Cost | VP | Bonus |
|----|------|------|----|-------|
| contract_rock_013 | Wake the Sleeping Legends | 3 singers, 3 bass | 8 | 6 guitarists |
| contract_rock_014 | Demolish the Rival Arena | 1 singer, 2 guitar, 2 coins | 10 | — |
| contract_rock_015 | Rock Legends World Tour | 2 singers, 7 guitar, 2 drum, 2 coins | 40 | — |

### Soul (Piety) — 3 cards

| ID | Name | Cost | VP | Bonus |
|----|------|------|----|-------|
| contract_soul_013 | Rescue the Gospel Choir | 6 guitar, 2 drum | 10 | 3 singers |
| contract_soul_014 | Soul Heritage Foundation | 2 singers, 1 drum, 5 coins | 18 | — |
| contract_soul_015 | Soul Music Magnum Opus | 5 singers, 2 guitar, 2 bass, 1 drum | 40 | — |

### Funk (Arcana) — 2 cards

| ID | Name | Cost | VP | Bonus |
|----|------|------|----|-------|
| contract_funk_013 | Resurrect the Funk Pioneers | 3 singers, 5 coins | 6 | 3 drummers |
| contract_funk_014 | Funkadelic Magnum Opus | 2 guitar, 3 bass, 4 drum, 6 coins | 40 | — |

### Jazz (Skullduggery) — 3 cards

| ID | Name | Cost | VP | Bonus |
|----|------|------|----|-------|
| contract_jazz_013 | Survive the Genre Crossover | 6 guitar, 5 coins | 6 | 6 bass players |
| contract_jazz_014 | Underground Jazz Blitz | 1 singer, 1 guitar, 1 bass, 1 drum | 12 | — |
| contract_jazz_015 | Jazz Empire Conspiracy | 1 singer, 7 bass, 2 drum, 9 coins | 40 | — |

## Validation Rules (existing — no changes)

- `ContractsConfig` validates no duplicate IDs
- Pydantic enforces field types and defaults
- Test suite validates balance constraints (benefit ratio, genre specialization)
