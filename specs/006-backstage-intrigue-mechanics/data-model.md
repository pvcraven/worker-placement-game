# Data Model: Backstage & Intrigue Mechanics

## Existing Entities (no changes needed)

### IntrigueCard (shared/card_models.py)
Already defined with all required fields:
- `id: str` — unique identifier (e.g., "intrigue_001")
- `name: str` — display name
- `description: str` — effect description text
- `effect_type: str` — one of: gain_resources, steal_resources, opponent_loses, gain_coins, vp_bonus, draw_contracts, draw_intrigue, all_players_gain
- `effect_target: str` — "self", "choose_opponent", or "all"
- `effect_value: dict` — resource/coin/VP amounts

### BackstageSlot (server/models/game.py)
Already defined with all required fields:
- `slot_number: int` — 1, 2, or 3
- `occupied_by: str | None` — player_id of occupying player, or None
- `intrigue_card_played: IntrigueCard | None` — the intrigue card played on this slot

### Player (server/models/game.py)
Already has:
- `intrigue_hand: list[IntrigueCard]` — cards in hand
- `resources: PlayerResources` — includes `coins: int`
- `available_workers: int` — workers available to place
- `total_workers: int` — total workers for the round

### BoardState (server/models/game.py)
Already has:
- `backstage_slots: list[BackstageSlot]` — the 3 backstage slots
- `intrigue_deck: list[IntrigueCard]` — draw pile

### GameState (server/models/game.py)
Already has:
- `phase: GamePhase` — includes PLACEMENT, REASSIGNMENT values
- `reassignment_queue: list[dict]` — populated during reassignment phase

## State Transitions

### Backstage Placement Flow
```
Player clicks backstage slot
  → Client validates: player has intrigue cards, slot is next available
  → Client shows intrigue card selection dialog
  → Player selects card → Client sends PlaceWorkerBackstageRequest
  → Player cancels → Dialog closes, no message sent

Server receives PlaceWorkerBackstageRequest
  → Validates: player's turn, has card, slot sequential order, slot unoccupied
  → Places worker on slot (occupied_by = player_id)
  → Attaches intrigue card to slot
  → Removes card from player's intrigue_hand
  → Resolves intrigue effect via _resolve_intrigue_effect()
  → Decrements available_workers
  → Broadcasts WorkerPlacedBackstageResponse
  → Checks quest completion → advances turn
```

### Reassignment Phase Flow
```
All workers placed → _end_placement_phase()
  → If any backstage slots occupied:
    → Phase = REASSIGNMENT
    → Build reassignment_queue from occupied slots (order 1→2→3)
    → Broadcast ReassignmentPhaseStartResponse
    → Prompt first player in queue
  → If no backstage slots occupied:
    → Skip to _end_round()

For each occupied slot in order:
  → Free worker (return to player's available_workers)
  → Prompt player to place on any open action space (not Backstage)
  → Player places → reward granted → next slot processed
  → All slots processed → _end_round()
```

### Round Advancement (FR-014, FR-015)
```
_advance_turn() detects all workers placed
  → Calls _end_placement_phase()
  → _end_placement_phase() checks backstage slots:
    → If occupied slots exist → enter REASSIGNMENT phase
    → If no occupied slots → call _end_round() directly (FR-014)
  
_end_round():
  → Returns all workers to players (reset available_workers = total_workers)
  → Clears board occupants (action spaces + backstage slots)
  → Increments round counter
  → If total_rounds reached → game over
  → Else → start next round (Phase = PLACEMENT)

After reassignment completes (all slots processed):
  → Call _end_round() (FR-015)
```

### Starting Resources (Game Initialization)
```
Game starts → for each player in turn order:
  → Deal 2 intrigue cards from shuffled intrigue_deck
  → Grant coins: 4 + (position_index * 2)
    - Position 0 (first player): 4 coins
    - Position 1: 6 coins
    - Position 2: 8 coins
    - etc.
```
