# Plot Quest Genre Bonus Implementation

## Overview

Five plot quest cards each grant "+2 VP each time you complete a [Genre] quest" as an ongoing benefit after the plot quest itself is completed. This bonus is not currently implemented — the `ongoing_benefit_description` field exists in the data but no game logic acts on it.

This spec covers only the genre-based VP bonus plot quests. Other plot quest types (extra workers, resource-on-gain triggers, building bonuses, recall workers, per-intrigue bonuses, per-building bonuses, etc.) are separate features that will be implemented independently.

## Cards Affected

| ID | Name | Genre | Ongoing Benefit |
|----|------|-------|-----------------|
| contract_pop_005 | Record Label Empire | pop | +2 VP per completed Pop quest |
| contract_rock_002 | Rock Union Takeover | rock | +2 VP per completed Rock quest |
| contract_soul_005 | Protect the Soul Legacy | soul | +2 VP per completed Soul quest |
| contract_funk_004 | Study the Funk Masters | funk | +2 VP per completed Funk quest |
| contract_jazz_003 | Plant a Mole at Rival Label | jazz | +2 VP per completed Jazz quest |

## Behavior

1. **When a player completes one of these plot quests**, it goes into their `completed_contracts` list (this already happens). No bonus is awarded at this point.

2. **Only future quests get the bonus.** The +2 VP bonus applies exclusively to same-genre quests completed *after* the plot quest. Quests completed before the plot quest do not retroactively receive the bonus, and the plot quest itself does not trigger its own bonus.

   **Example:** A player completes Jazz Quest A (no bonus), then completes "Plant a Mole at Rival Label" (the jazz plot quest — no bonus on this either), then completes Jazz Quest B → Jazz Quest B gets +2 VP bonus. Only that last quest benefits.

3. **Stacking**: If a player somehow has multiple completed plot quests that match the same genre, bonuses stack (unlikely in practice since each genre has exactly one such card).

4. **Immediate, not end-of-game**: The bonus VP is added to `player.victory_points` at quest completion time, not during final scoring. This is distinct from the producer card genre bonus, which is calculated only at end-of-game. Both bonuses apply independently — a player with a jazz plot quest AND a jazz producer card would get +2 VP immediately on quest completion AND the producer bonus at final tally.

5. **No separate score line item**: The bonus VP folds into the player's running VP total (game VP). It does not appear as a separate category in the final score breakdown.

6. **Game log**: The bonus VP should be mentioned in the game log entry so players understand why extra points were awarded.

7. **Broadcast**: The `QuestCompletedResponse` should include the bonus VP so the client can display it.

## Implementation Scope

### Server: `server/game_engine.py`

**In `handle_complete_quest()`** (around line 1542-1546):
- Before appending the current quest to `completed_contracts`, scan the existing list for any completed plot quests whose `bonus_vp_genre` matches the just-completed quest's genre.
- Sum up any matching bonuses and add to `player.victory_points`.
- Include the bonus amount in the game log entry and broadcast response.

Key detail: the plot quest must already be in `completed_contracts` *before* the current quest is appended. Check the list before the append on line 1545, so completing a plot quest never triggers its own bonus.

### Shared: `shared/card_models.py`

Add structured fields to `ContractCard` so the server can programmatically determine the bonus rather than parsing the description string:

```python
bonus_vp_per_genre_quest: int = 0       # e.g. 2
bonus_vp_genre: str | None = None       # e.g. "rock"
```

These fields are specific to this plot quest type. Other plot quest types will use different fields appropriate to their mechanics.

### Config: `config/contracts.json`

Add `bonus_vp_per_genre_quest` and `bonus_vp_genre` fields to the 5 cards listed above. Example:

```json
{
  "id": "contract_rock_002",
  "bonus_vp_per_genre_quest": 2,
  "bonus_vp_genre": "rock",
  ...
}
```

All other cards default to `bonus_vp_per_genre_quest: 0` and `bonus_vp_genre: null` (via the model defaults — no need to add these fields to every card in the JSON).

### Server response: `QuestCompletedResponse`

Add a `plot_quest_bonus_vp` field (int, default 0) so the client knows bonus VP was awarded.

### Client: display

No client changes are strictly required — the VP total updates automatically from server state. The game log entry will explain the bonus. If the client currently shows "Completed X for Y VP", it could show "Completed X for Y + 2 VP (genre bonus)" but this is polish, not blocking.

## Out of Scope

- Other plot quest mechanics — each type will be implemented as a separate feature:
  - Resource-on-gain triggers (e.g. "when you gain a guitarist, gain 1 extra")
  - Extra permanent workers
  - Worker recall abilities
  - Per-building VP bonuses
  - Per-intrigue VP bonuses
  - Resource-trading triggers
  - Building action space sharing
- Retroactive scoring: quests completed *before* the plot quest do NOT get the bonus.

## Testing

- Complete a genre quest without the plot quest → no bonus VP.
- Complete a same-genre quest, then the plot quest, then another same-genre quest → only the last quest gets +2 VP. The first quest completed before the plot quest gets nothing.
- Complete the plot quest, then complete a different-genre quest → no bonus.
- Complete the plot quest itself → no bonus on the plot quest (it doesn't trigger its own effect).
- Player has both a plot quest and a producer card for the same genre → both bonuses apply (plot quest immediately, producer at end-of-game).
- Verify game log mentions the bonus.
- Verify `QuestCompletedResponse` includes the bonus amount.
