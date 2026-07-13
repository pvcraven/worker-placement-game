# Message Contracts: Resource Distribution Buildings

## New Message Types

### ResourceDistributionPromptResponse (Server → Player)

Sent to the building owner (or visitor if unowned) to prompt target space selection.

```json
{
  "action": "resource_distribution_prompt",
  "player_id": "player_1",
  "resource_type": "guitarists",
  "per_space": 1,
  "remaining_selections": 2,
  "eligible_spaces": [
    {"space_id": "merch_store", "name": "The Merch Store"},
    {"space_id": "motown", "name": "Motown"},
    {"space_id": "building_001", "name": "The Troubadour"}
  ],
  "selected_spaces": []
}
```

**Notes**:
- `eligible_spaces` excludes: the building being visited, and any spaces already selected in this phase
- Sent once per required selection (if building requires 2 spaces, sent twice — once after each pick)
- `remaining_selections` decrements with each accepted pick

### ResourceDistributionRequest (Player → Server)

Player submits their target space choice.

```json
{
  "action": "resource_distribution_select",
  "space_id": "merch_store"
}
```

**Validation**:
- `space_id` must be in the current `eligible_spaces` list
- `pending_resource_distribution` must be active for this player
- Space must not already be in `selected_spaces`

### ResourceDistributionResolvedResponse (Server → All)

Broadcast after each space receives its resources.

```json
{
  "action": "resource_distribution_resolved",
  "space_id": "merch_store",
  "resource_type": "guitarists",
  "quantity": 1,
  "all_placed_resources": {
    "merch_store": {"guitarists": 1},
    "motown": {"guitarists": 1, "coins": 2}
  }
}
```

**Notes**:
- `all_placed_resources` is the complete snapshot of all placed resources across the board (for client state sync)
- Sent after each individual space selection is confirmed
- After the final selection, the distribution phase ends and normal turn flow resumes

## Modified Message Types

### WorkerPlacedResponse (addition)

Add field to the existing response:

```json
{
  "action": "worker_placed",
  "player_id": "player_1",
  "space_id": "merch_store",
  "reward_granted": {"guitarists": 2},
  "collected_placed_resources": {"guitarists": 1, "coins": 2},
  "owner_bonus": null,
  "next_player_id": "player_2"
}
```

- `collected_placed_resources`: Resources collected from the `placed_resources` pool on the visited space. `null` if no placed resources were present.

## Flow Sequence

```
1. Player visits distribution building
   → Server: grant visitor_reward + accumulated_stock + placed_resources
   → Server: grant owner_bonus (if applicable)  
   → Server: create pending_resource_distribution
   → Server: send ResourceDistributionPromptResponse to selecting player

2. Selecting player picks target space
   → Client: send ResourceDistributionRequest
   → Server: validate, place resources on target space
   → Server: broadcast ResourceDistributionResolvedResponse
   → If remaining_selections > 0:
       → Server: send another ResourceDistributionPromptResponse
   → If remaining_selections == 0:
       → Server: clear pending_resource_distribution
       → Server: check quest completion + advance turn
```
