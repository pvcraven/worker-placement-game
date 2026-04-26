"""Server-side game state models (authoritative)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from shared.card_models import (
    BuildingTile,
    ContractCard,
    IntrigueCard,
    ProducerCard,
    ResourceCost,
)
from shared.constants import TOTAL_ROUNDS, GamePhase

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------


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

    def total(self) -> int:
        return (
            self.guitarists
            + self.bass_players
            + self.drummers
            + self.singers
            + self.coins
        )


class Player(BaseModel):
    """A player in the game."""

    player_id: str
    display_name: str
    slot_index: int
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
    completed_quest_this_turn: bool = False
    use_occupied_used_this_round: bool = False


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------


class ActionSpace(BaseModel):
    """An action space on the board."""

    space_id: str
    name: str
    space_type: str  # "permanent", "building", "garage", "backstage", "castle"
    occupied_by: str | None = None
    owner_id: str | None = None
    building_tile: BuildingTile | None = None
    reward: ResourceCost = Field(default_factory=ResourceCost)
    reward_special: str | None = None  # Non-resource effects
    also_occupied_by: str | None = None


class BackstageSlot(BaseModel):
    """A numbered slot in Backstage (intrigue play + reassignment)."""

    slot_number: int  # 1, 2, or 3
    occupied_by: str | None = None
    intrigue_card_played: IntrigueCard | None = None


class BoardState(BaseModel):
    """The full board state."""

    action_spaces: dict[str, ActionSpace] = Field(default_factory=dict)
    backstage_slots: list[BackstageSlot] = Field(default_factory=list)
    face_up_quests: list[ContractCard] = Field(default_factory=list)
    quest_deck: list[ContractCard] = Field(default_factory=list)
    quest_discard: list[ContractCard] = Field(default_factory=list)
    building_lots: list[str] = Field(default_factory=list)
    constructed_buildings: list[str] = Field(default_factory=list)
    face_up_contracts: list[ContractCard] = Field(default_factory=list)
    contract_deck: list[ContractCard] = Field(default_factory=list)
    intrigue_deck: list[IntrigueCard] = Field(default_factory=list)
    building_deck: list[BuildingTile] = Field(default_factory=list)
    face_up_buildings: list[BuildingTile] = Field(default_factory=list)
    first_player_id: str | None = None


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------


class GameLog(BaseModel):
    """A single game log entry."""

    round_number: int
    player_id: str | None = None
    action: str
    details: str
    timestamp: float


class GameState(BaseModel):
    """The authoritative game state (server-side)."""

    game_id: str
    game_code: str
    phase: GamePhase = GamePhase.LOBBY
    players: list[Player] = Field(default_factory=list)
    board: BoardState = Field(default_factory=BoardState)
    current_round: int = 0
    total_rounds: int = TOTAL_ROUNDS
    current_player_index: int = 0
    turn_order: list[str] = Field(default_factory=list)
    game_log: list[GameLog] = Field(default_factory=list)
    reassignment_queue: list[int] = Field(default_factory=list)
    reassignment_active_player_id: str | None = None
    pending_intrigue_target: dict | None = None
    producer_deck: list[ProducerCard] = Field(default_factory=list)
    waiting_for_quest_completion: bool = False
    max_players: int = 4
    host_player_id: str | None = None
    created_at: float = 0.0
    last_activity: float = 0.0
    pending_quest_reward: dict | None = None
    pending_resource_choice: dict | None = None
    pending_resource_trigger_swap: dict | None = None
    pending_play_intrigue: dict | None = None
    pending_opponent_coins: dict | None = None
    pending_worker_recall: dict | None = None
    pending_round_start_choices: list[str] = Field(default_factory=list)

    def get_player(self, player_id: str) -> Player | None:
        for p in self.players:
            if p.player_id == player_id:
                return p
        return None

    def current_player(self) -> Player | None:
        if not self.turn_order:
            return None
        if self.current_player_index >= len(self.turn_order):
            return None
        pid = self.turn_order[self.current_player_index]
        return self.get_player(pid)

    def all_workers_placed(self) -> bool:
        return all(p.available_workers == 0 for p in self.players)
