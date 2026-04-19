# Quickstart: Resource Choice Rewards

**Feature**: 012-resource-choice-rewards
**Date**: 2026-04-19

## Test Scenarios

These scenarios verify end-to-end resource choice functionality. Run with `cd src && pytest tests/test_resource_choice.py`.

### Scenario 1: Pick mode — single resource selection

**Setup**: Create a game with 2 players. Add a building with `visitor_reward_choice` of type "pick", `allowed_types: ["guitarists", "bass_players", "drummers", "singers"]`, `pick_count: 1`, and `visitor_reward: {coins: 2}`.

**Steps**:
1. Player places worker on the choice building
2. Server sends `resource_choice_prompt` with `choice_type: "pick"`, `pick_count: 1`
3. Player sends `resource_choice` with `chosen_resources: {guitarists: 1}`
4. Server validates: exactly 1 resource chosen, type is in allowed list
5. Server grants 1 guitarist + 2 coins (fixed reward)
6. Server broadcasts `resource_choice_resolved`
7. Turn advances to next player

**Expected**: Player's resources increase by 1 guitarist and 2 coins. No other player resources change.

### Scenario 2: Pick mode — multiple resource selection

**Setup**: Building with `pick_count: 2`, `allowed_types: ["guitarists", "bass_players", "drummers", "singers"]`.

**Steps**:
1. Player places worker, receives prompt
2. Player sends `chosen_resources: {guitarists: 1, drummers: 1}`
3. Server validates: total chosen equals 2, all types allowed

**Expected**: Player gains 1 guitarist and 1 drummer. Player can pick the same type twice (e.g., `{guitarists: 2}`).

### Scenario 3: Bundle mode — predefined option selection

**Setup**: Intrigue card with `choice_type: "bundle"`, bundles: [{label: "1 Singer", resources: {singers: 1}}, {label: "2 Guitarists", resources: {guitarists: 2}}, {label: "4 Coins", resources: {coins: 4}}].

**Steps**:
1. Player plays intrigue card on backstage
2. Server sends `resource_choice_prompt` with `choice_type: "bundle"`, bundles list
3. Player sends `chosen_resources: {guitarists: 2}` (matching bundle index 1)
4. Server validates: chosen resources exactly match one bundle

**Expected**: Player receives exactly 2 guitarists.

### Scenario 4: Combo mode — constrained allocation

**Setup**: Building with `choice_type: "combo"`, `allowed_types: ["guitarists", "bass_players"]`, `total: 4`, `cost: {coins: 2}`.

**Steps**:
1. Player (with 3+ coins) places worker
2. Server deducts 2 coins
3. Server sends prompt with `choice_type: "combo"`, `total: 4`
4. Player sends `chosen_resources: {guitarists: 3, bass_players: 1}`
5. Server validates: total equals 4, only allowed types used

**Expected**: Player loses 2 coins, gains 3 guitarists and 1 bass player.

### Scenario 5: Combo mode — insufficient funds blocked

**Setup**: Same combo building. Player has only 1 coin.

**Steps**:
1. Player attempts to place worker
2. Server checks cost affordability

**Expected**: Server rejects placement with error "insufficient resources".

### Scenario 6: Exchange mode — two-phase trade

**Setup**: Building with `choice_type: "exchange"`, `allowed_types: ["guitarists", "bass_players", "drummers", "singers"]`, `pick_count: 2` (spend), `gain_count: 3` (gain).

**Steps**:
1. Player (with 1 guitarist, 1 drummer) places worker
2. Server sends spend prompt: `is_spend: true`, `pick_count: 2`
3. Player sends `chosen_resources: {guitarists: 1, drummers: 1}`
4. Server validates player owns those resources, deducts them
5. Server sends gain prompt: `is_spend: false`, `pick_count: 3`
6. Player sends `chosen_resources: {singers: 2, bass_players: 1}`
7. Server grants chosen resources
8. Turn advances

**Expected**: Player loses 1 guitarist + 1 drummer, gains 2 singers + 1 bass player.

### Scenario 7: Exchange mode — insufficient resources blocked

**Setup**: Same exchange building. Player has only 1 non-coin resource.

**Steps**:
1. Player attempts to place worker

**Expected**: Server rejects — player cannot turn in 2 non-coin resources.

### Scenario 8: Multi-player pick

**Setup**: 3-player game. Intrigue card with `effect_type: "resource_choice_multi"`, `pick_count: 2`, `others_pick_count: 1`.

**Steps**:
1. Player A plays intrigue card on backstage
2. Server sends prompt to Player A: `pick_count: 2`
3. Player A sends `chosen_resources: {guitarists: 1, singers: 1}`
4. Server grants, then sends prompt to Player B: `pick_count: 1`
5. Player B sends `chosen_resources: {drummers: 1}`
6. Server grants, then sends prompt to Player C: `pick_count: 1`
7. Player C sends `chosen_resources: {bass_players: 1}`
8. Server grants, turn advances

**Expected**: A gains 2 resources, B gains 1, C gains 1. Prompts arrive in turn order.

### Scenario 9: Validation — invalid resource type rejected

**Setup**: Pick mode with `allowed_types: ["guitarists", "bass_players"]`.

**Steps**:
1. Player receives prompt
2. Player sends `chosen_resources: {singers: 1}`

**Expected**: Server rejects — singers not in allowed types. Player prompted again.

### Scenario 10: Validation — wrong count rejected

**Setup**: Pick mode with `pick_count: 1`.

**Steps**:
1. Player sends `chosen_resources: {guitarists: 2}`

**Expected**: Server rejects — total chosen (2) exceeds pick_count (1). Player prompted again.
