# Phase 1 Data Model: Multiplayer Worker Placement Game

**Branch**: `001-worker-placement-game` | **Date**: 2026-04-13 | **Plan**: [plan.md](plan.md)

## Overview

All models use Pydantic v2 `BaseModel`. The data model is split across three packages:

- **`shared/`** — Models used by both server and client (network messages, card attributes, constants)
- **`server/models/`** — Server-only models (full game state, config schemas)
- **Client** — No separate models; client uses `shared/` models directly

## Shared Constants (`shared/constants.py`)

```python
from enum import StrEnum

class ResourceType(StrEnum):
    GUITARIST = "guitarist"
    BASS_PLAYER = "bass_player"
    DRUMMER = "drummer"
    SINGER = "singer"

class Genre(StrEnum):
    JAZZ = "jazz"
    POP = "pop"
    SOUL = "soul"
    FUNK = "funk"
    ROCK = "rock"

class GamePhase(StrEnum):
    LOBBY = "lobby"
    PLACEMENT = "placement"
    REASSIGNMENT = "reassignment"
    ROUND_END = "round_end"
    GAME_OVER = "game_over"

# Resource colors for UI rendering
RESOURCE_COLORS = {
    ResourceType.GUITARIST: "red",
    ResourceType.BASS_PLAYER: "black",
    ResourceType.DRUMMER: "white",
    ResourceType.SINGER: "purple",
}
COIN_COLOR = "gold"

# Game constants
MIN_PLAYERS = 2
MAX_PLAYERS = 5
TOTAL_ROUNDS = 8
BONUS_WORKER_ROUND = 5
TURN_TIMEOUT_SECONDS = 60
GAME_PRESERVE_TIMEOUT_SECONDS = 1800  # 30 minutes
FACE_UP_QUEST_COUNT = 5
GARAGE_SLOTS = 3

# Starting workers by player count
STARTING_WORKERS = {2: 4, 3: 3, 4: 2, 5: 2}
```

## Shared Card Models (`shared/card_models.py`)

These represent the card data as seen by both server and client.

```python
from pydantic import BaseModel, Field
from shared.constants import ResourceType, Genre

class ResourceCost(BaseModel):
    """A set of resources required or granted."""
    guitarists: int = 0
    bass_players: int = 0
    drummers: int = 0
    singers: int = 0
    coins: int = 0

class ContractCard(BaseModel):
    """A quest/contract card — assemble a band."""
    id: str
    name: str
    description: str
    genre: Genre
    cost: ResourceCost
    victory_points: int = Field(ge=0)
    bonus_resources: ResourceCost = Field(default_factory=ResourceCost)
    is_plot_quest: bool = False
    ongoing_benefit_description: str | None = None
    # Plot quest effect is deferred — described in text for now

class IntrigueCard(BaseModel):
    """An intrigue card played at The Garage."""
    id: str
    name: str
    description: str
    effect_type: str  # e.g., "gain_resources", "steal_resources", "all_players", "vp_bonus"
    effect_target: str = "self"  # "self", "opponent", "all", "choose_opponent"
    effect_value: dict = Field(default_factory=dict)
    # effect_value schema varies by effect_type — validated at config load

class BuildingTile(BaseModel):
    """A building tile — famous recording studio or music venue."""
    id: str
    name: str
    description: str
    cost_coins: int = Field(ge=0)
    visitor_reward: ResourceCost
    visitor_reward_special: str | None = None  # Non-resource rewards (e.g., "draw_intrigue")
    owner_bonus: ResourceCost
    owner_bonus_special: str | None = None

class ProducerCard(BaseModel):
    """A secret producer card — end-game scoring bonus."""
    id: str
    name: str
    description: str
    bonus_genres: list[Genre]  # Genres that score bonus VP
    bonus_vp_per_contract: int = Field(default=4, ge=0)
```

## Server Game State Models (`server/models/game.py`)

### Player State

```python
from pydantic import BaseModel, Field
from shared.card_models import ContractCard, IntrigueCard, ProducerCard, ResourceCost

class PlayerResources(BaseModel):
    """Tracks a player's current resource pool."""
    guitarists: int = 0
    bass_players: int = 0
    drummers: int = 0
    singers: int = 0
    coins: int = 0

    def can_afford(self, cost: ResourceCost) -> bool:
        return (
            self.guitarists >= cost.guitarists
            and self.bass_players >= cost.bass_players
            and self.drummers >= cost.drummers
            and self.singers >= cost.singers
            and self.coins >= cost.coins
        )

    def deduct(self, cost: ResourceCost) -> None:
        self.guitarists -= cost.guitarists
        self.bass_players -= cost.bass_players
        self.drummers -= cost.drummers
        self.singers -= cost.singers
        self.coins -= cost.coins

    def add(self, reward: ResourceCost) -> None:
        self.guitarists += reward.guitarists
        self.bass_players += reward.bass_players
        self.drummers += reward.drummers
        self.singers += reward.singers
        self.coins += reward.coins

class Player(BaseModel):
    """A player in the game."""
    player_id: str  # Server-assigned unique ID
    display_name: str
    slot_index: int  # Position in the game (0-4)
    resources: PlayerResources = Field(default_factory=PlayerResources)
    contract_hand: list[ContractCard] = Field(default_factory=list)
    intrigue_hand: list[IntrigueCard] = Field(default_factory=list)
    completed_contracts: list[ContractCard] = Field(default_factory=list)
    producer_card: ProducerCard | None = None
    total_workers: int = 0
    available_workers: int = 0
    victory_points: int = 0
    is_connected: bool = True
    has_first_player_marker: bool = False
    consecutive_timeouts: int = 0
```

### Board State

```python
class WorkerPlacement(BaseModel):
    """Records a worker placed on a specific space."""
    player_id: str
    space_id: str
    round_number: int

class ActionSpace(BaseModel):
    """An action space on the board."""
    space_id: str
    name: str
    space_type: str  # "permanent", "building", "garage", "castle", "cliffwatch"
    occupied_by: str | None = None  # player_id or None
    owner_id: str | None = None  # For buildings — the player who built it
    building_tile: BuildingTile | None = None  # For building spaces

class GarageSlot(BaseModel):
    """A numbered slot in The Garage."""
    slot_number: int  # 1, 2, or 3
    occupied_by: str | None = None  # player_id
    intrigue_card_played: IntrigueCard | None = None

class BoardState(BaseModel):
    """The full board state."""
    action_spaces: dict[str, ActionSpace] = Field(default_factory=dict)
    garage_slots: list[GarageSlot] = Field(default_factory=list)
    building_lots: list[str] = Field(default_factory=list)  # IDs of empty lots
    constructed_buildings: list[str] = Field(default_factory=list)  # space_ids
    face_up_contracts: list[ContractCard] = Field(default_factory=list)
    contract_deck: list[ContractCard] = Field(default_factory=list)
    intrigue_deck: list[IntrigueCard] = Field(default_factory=list)
    building_supply: list[BuildingTile] = Field(default_factory=list)
    first_player_id: str | None = None
```

### Game State

```python
from shared.constants import GamePhase, TOTAL_ROUNDS

class GameLog(BaseModel):
    """A single game log entry."""
    round_number: int
    player_id: str | None = None
    action: str
    details: str
    timestamp: float  # time.time()

class GameState(BaseModel):
    """The authoritative game state (server-side)."""
    game_id: str
    game_code: str  # Joinable code
    phase: GamePhase = GamePhase.LOBBY
    players: list[Player] = Field(default_factory=list)
    board: BoardState = Field(default_factory=BoardState)
    current_round: int = 0
    total_rounds: int = TOTAL_ROUNDS
    current_player_index: int = 0
    turn_order: list[str] = Field(default_factory=list)  # player_ids in turn order
    game_log: list[GameLog] = Field(default_factory=list)
    reassignment_queue: list[int] = Field(default_factory=list)  # Garage slot numbers pending reassignment
    producer_deck: list[ProducerCard] = Field(default_factory=list)
    created_at: float = 0.0
    last_activity: float = 0.0
```

## Entity Relationships

```
GameState (1)
├── Players (2-5)
│   ├── PlayerResources (1)
│   ├── ContractCards in hand (0-N)
│   ├── IntrigueCards in hand (0-N)
│   ├── Completed ContractCards (0-N)
│   └── ProducerCard (1, secret)
├── BoardState (1)
│   ├── ActionSpaces (9 permanent + 0-N buildings)
│   │   └── BuildingTile (0-1, for constructed spaces)
│   ├── GarageSlots (3)
│   ├── Face-up ContractCards (up to 5)
│   ├── Contract Deck (remaining cards)
│   ├── Intrigue Deck (remaining cards)
│   └── Building Supply (remaining tiles)
└── GameLog entries (0-N)
```

## State Transitions

### Game Phase Lifecycle

```
LOBBY → PLACEMENT → [REASSIGNMENT] → ROUND_END → PLACEMENT → ... → GAME_OVER
         ↑                              │
         └──────────────────────────────┘  (next round, if round < 8)
```

1. **LOBBY**: Players join, ready up. Host starts game → transitions to PLACEMENT (round 1).
2. **PLACEMENT**: Players take turns placing workers. When all workers placed:
   - If any Garage slots occupied → transition to REASSIGNMENT
   - Otherwise → transition to ROUND_END
3. **REASSIGNMENT**: Garage workers reassigned in slot order (1, 2, 3). After all reassigned → ROUND_END.
4. **ROUND_END**: All workers returned. If round < 8, increment round, apply round-5 bonus worker if applicable, rotate first player → PLACEMENT. If round = 8 → GAME_OVER.
5. **GAME_OVER**: Calculate final scores (VP + Producer bonuses). Display results.

### Player Turn Actions (during PLACEMENT phase)

```
Turn Start
├── [Optional] Complete one quest (if resources sufficient)
├── [Required] Place one worker on unoccupied space
│   ├── Regular space → receive reward
│   ├── Garage slot → play intrigue card (mandatory)
│   ├── Castle Waterdeep → gain first-player marker + 1 intrigue card
│   ├── Cliffwatch Inn → acquire contract or intrigue card
│   └── Builder's Hall → purchase building tile
└── Turn End → next player
```

### Worker Lifecycle

```
Available → Placed (on action space) → [Garage: Reassigned to new space] → Returned (end of round) → Available
```

## Config File Schemas (`server/models/config.py`)

```python
from pydantic import BaseModel, Field, field_validator
from shared.card_models import ContractCard, IntrigueCard, BuildingTile, ProducerCard

class ContractsConfig(BaseModel):
    """Schema for config/contracts.json"""
    contracts: list[ContractCard]

    @field_validator("contracts")
    @classmethod
    def validate_unique_ids(cls, v):
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate contract IDs found")
        return v

class IntrigueConfig(BaseModel):
    """Schema for config/intrigue.json"""
    intrigue_cards: list[IntrigueCard]

    @field_validator("intrigue_cards")
    @classmethod
    def validate_unique_ids(cls, v):
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate intrigue card IDs found")
        return v

class BuildingsConfig(BaseModel):
    """Schema for config/buildings.json"""
    buildings: list[BuildingTile]

    @field_validator("buildings")
    @classmethod
    def validate_unique_ids(cls, v):
        ids = [b.id for b in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate building IDs found")
        return v

class ProducersConfig(BaseModel):
    """Schema for config/producers.json"""
    producers: list[ProducerCard]

class ActionSpaceConfig(BaseModel):
    """A permanent action space definition."""
    space_id: str
    name: str
    space_type: str
    reward: dict = Field(default_factory=dict)
    slots: int = 1  # >1 for Cliffwatch Inn, Garage

class BoardConfig(BaseModel):
    """Schema for config/board.json"""
    permanent_spaces: list[ActionSpaceConfig]
    building_lot_count: int = Field(default=10, ge=0)

class GameRulesConfig(BaseModel):
    """Schema for config/game_rules.json"""
    total_rounds: int = 8
    bonus_worker_round: int = 5
    turn_timeout_seconds: int = 60
    game_preserve_timeout_seconds: int = 1800
    face_up_quest_count: int = 5
    starting_workers: dict[str, int] = Field(
        default={"2": 4, "3": 3, "4": 2, "5": 2}
    )
    min_players: int = 2
    max_players: int = 5
```

## Validation Rules

### Hard Errors (prevent startup)
- Missing required fields on any card/config model
- Duplicate IDs within any card category
- Invalid genre values (must be one of the 5 defined genres)
- Invalid resource type references
- Player count outside 2-5 range in game rules
- Negative resource costs or VP values

### Warnings (log but allow)
- Zero-cost contracts (cost all zeros)
- Contracts with VP > 20
- Buildings with zero visitor reward and zero owner bonus
- Intrigue cards with no apparent effect
- Empty description text
- Fewer than expected cards (e.g., <60 contracts, <50 intrigue)
