# Data Model: Remaining Special Quest Mechanics

## Modified Entities

### ContractCard (shared/card_models.py)

New fields added to existing model:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `reward_play_intrigue` | `int` | `0` | On completion, play N intrigue cards from hand |
| `reward_opponent_gains_coins` | `int` | `0` | On completion, one opponent receives N coins |
| `reward_extra_worker` | `int` | `0` | On completion, permanently gain N workers |
| `reward_choose_resource_per_round` | `bool` | `False` | Each round start, choose 1 non-coin resource to gain |
| `reward_recall_worker` | `bool` | `False` | On completion, recall one placed worker |
| `reward_use_occupied_building` | `bool` | `False` | Once per round, use an occupied building |

### Player (server/models/game.py)

New fields:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `use_occupied_used_this_round` | `bool` | `False` | Tracks once-per-round occupied-building usage |

Reset at round end in `_end_round()`.

### ActionSpace (server/models/game.py)

New field:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `also_occupied_by` | `str \| None` | `None` | Second worker on building via use-occupied ability |

Cleared at round end alongside `occupied_by`.

### GameState (server/models/game.py)

New pending state fields:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `pending_play_intrigue` | `dict \| None` | `None` | Tracks pending intrigue play from quest completion |
| `pending_opponent_coins` | `dict \| None` | `None` | Tracks pending opponent coin choice |
| `pending_worker_recall` | `dict \| None` | `None` | Tracks pending worker recall from quest completion |
| `pending_round_start_choices` | `list[str]` | `[]` | Player IDs still needing round-start resource choice |

## New Message Types (shared/messages.py)

### IntriguePlayPromptResponse
Sent to player after quest completion when they must play an intrigue card.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["intrigue_play_prompt"]` | |
| `intrigue_hand` | `list[dict]` | Player's available intrigue cards |
| `source` | `str` | `"quest_completion"` |

### PlayIntrigueFromQuestRequest
Player's choice of which intrigue card to play.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["play_intrigue_from_quest"]` | |
| `intrigue_card_id` | `str` | Selected card ID |

### OpponentChoicePromptResponse
Sent to player when they must choose which opponent receives a benefit.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["opponent_choice_prompt"]` | |
| `opponents` | `list[dict]` | `[{player_id, player_name}]` |
| `coins` | `int` | Amount to grant |

### ChooseOpponentRequest
Player's choice of opponent.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["choose_opponent"]` | |
| `target_player_id` | `str` | Chosen opponent |

### WorkerRecallPromptResponse
Sent to player after quest completion when they must select a placed worker to recall.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["worker_recall_prompt"]` | |
| `player_id` | `str` | Player being prompted |
| `occupied_spaces` | `list[dict]` | `[{space_id, space_name}]` — spaces with player's workers |

### RecallWorkerRequest
Player selects which worker to recall.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["recall_worker"]` | |
| `space_id` | `str` | Space to recall from |

### WorkerRecalledResponse
Broadcast when a worker is recalled.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["worker_recalled"]` | |
| `player_id` | `str` | |
| `space_id` | `str` | Space freed |

### RoundStartResourceChoicePromptResponse
Sent to player at round start when they must choose a non-coin resource.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["round_start_resource_choice_prompt"]` | |
| `player_id` | `str` | Player being prompted |
| `source_contract` | `str` | Contract name granting this benefit |

### RoundStartResourceChoiceRequest
Player's chosen resource at round start.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["round_start_resource_choice"]` | |
| `resource_type` | `str` | One of: guitarists, bass_players, drummers, singers |

### RoundStartBonusResponse
Broadcast after a player's round-start resource choice is resolved.

| Field | Type | Notes |
|-------|------|-------|
| `action` | `Literal["round_start_bonus"]` | |
| `player_id` | `str` | Player who received the resource |
| `resource_type` | `str` | Chosen resource type |
| `amount` | `int` | Always 1 |
| `source_contract` | `str` | Contract name |

## Updated Message Types

### QuestCompletedResponse
Add fields:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `pending_play_intrigue` | `bool` | `False` | Client awaits intrigue play prompt |
| `opponent_coins_granted` | `dict \| None` | `None` | `{player_id, player_name, coins}` |
| `extra_workers_granted` | `int` | `0` | Permanent workers gained |

## Card-to-Field Mapping

| Card ID | Card Name | New Field | Value |
|---------|-----------|-----------|-------|
| `contract_jazz_010` | Jailhouse Jazz Session | `reward_play_intrigue` | `1` |
| `contract_pop_008` | Charity Gala Showcase | `reward_opponent_gains_coins` | `4` |
| `contract_rock_009` | Hire a Tour Manager | `reward_extra_worker` | `1` |
| `contract_soul_007` | Soul Music Residency | `reward_choose_resource_per_round` | `true` |
| `contract_funk_001` | Time Warp Remix | `reward_recall_worker` | `true` |
| `contract_funk_005` | Recover the Master Tapes | `reward_use_occupied_building` | `true` |
