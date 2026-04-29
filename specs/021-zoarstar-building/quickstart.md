# Quickstart: Shadow Studio + Bootleg Recording

**Date**: 2026-04-29

## Test Scenarios

### Scenario 1: Basic Building Copy (US1)

1. Start a 2-player game
2. Player A purchases Shadow Studio via Realtor (needs 8 coins)
3. Player B places on "Motown" (2 bass players)
4. Player A places on Shadow Studio
5. **Verify**: Player A sees a selection prompt listing "Motown" as a target
6. Player A selects "Motown"
7. **Verify**: Player A receives 2 bass players
8. **Verify**: Player B's worker on Motown is undisturbed
9. **Verify**: Turn advances normally

### Scenario 2: Owner Bonus (US2)

1. Player A owns Shadow Studio
2. Player B places on Shadow Studio
3. **Verify**: Player A receives 2 VP as owner bonus
4. Player A places on Shadow Studio (own building)
5. **Verify**: Player A does NOT receive owner bonus

### Scenario 3: Copy Building with Accumulated Stock (US3)

1. Player B places on Red Rocks (accumulated stock building)
2. Player A places on Shadow Studio, selects Red Rocks
3. **Verify**: Player A receives the accumulated stock from Red Rocks
4. **Verify**: Red Rocks' stock is drained (reset to 0)

### Scenario 4: Copy Building with Resource Choice (US3)

1. Player B places on a building with resource choice (e.g., The Fillmore)
2. Player A places on Shadow Studio, selects that building
3. **Verify**: Player A receives the resource choice prompt
4. Player A makes a choice
5. **Verify**: Resources granted match the choice

### Scenario 5: No Valid Targets (US1 Edge Case)

1. Only Player A has workers placed (Player B has none, or only Player A's own spaces)
2. Player A places on Shadow Studio
3. **Verify**: No selection prompt appears; turn proceeds normally

### Scenario 6: Cancel Copy Selection (US1)

1. Player B occupies a space
2. Player A places on Shadow Studio
3. Player A cancels the space selection
4. **Verify**: Worker returns from Shadow Studio, Shadow Studio is freed
5. **Verify**: No rewards granted, turn returns to Player A

### Scenario 7: Bootleg Recording — Basic Flow (US5)

1. Player A has "Bootleg Recording" intrigue card and 3 coins
2. Player B occupies "Motown"
3. Player A places on backstage, plays "Bootleg Recording"
4. **Verify**: 2 coins deducted from Player A
5. **Verify**: Selection prompt appears listing "Motown"
6. Player A selects "Motown"
7. **Verify**: Player A receives 2 bass players
8. **Verify**: Card is consumed (not in hand)

### Scenario 8: Bootleg Recording — Insufficient Coins (US5)

1. Player A has "Bootleg Recording" but only 1 coin
2. Player A places on backstage, plays "Bootleg Recording"
3. **Verify**: Error message "You need 2 coins to play this card"
4. **Verify**: Backstage placement unwound, card stays in hand, worker returns

### Scenario 9: Bootleg Recording — Cancel (US5)

1. Player A plays Bootleg Recording (2 coins deducted)
2. Player A cancels space selection
3. **Verify**: 2 coins returned
4. **Verify**: Backstage slot freed, worker returned, card returned to hand

### Scenario 10: Owner Bonus Cascading (FR-008/FR-019)

1. Player B owns "The Fillmore" and has a worker on it
2. Player A copies "The Fillmore" via Shadow Studio
3. **Verify**: Player B receives The Fillmore's owner bonus (from the copy "visit")
4. **Verify**: Shadow Studio's owner also receives their 2 VP (if A is not the owner)

### Scenario 11: Resource Triggers on Copied Rewards (Edge Case)

1. Player A has completed "Payola Pipeline" (triggers on coin gains)
2. Player B occupies a space that grants coins
3. Player A copies that space via Shadow Studio
4. **Verify**: Payola Pipeline's resource trigger fires on the copied coin reward

## Running Tests

```bash
cd src && pytest tests/test_copy_occupied_space.py -v
cd src && pytest && ruff check .
```
