from __future__ import annotations

from pydantic import BaseModel, Field

from shared.constants import Genre


class ResourceCost(BaseModel):
    """A set of resources required or granted."""

    guitarists: int = 0
    bass_players: int = 0
    drummers: int = 0
    singers: int = 0
    coins: int = 0


class ContractCard(BaseModel):
    """A quest/contract card - assemble a band."""

    id: str
    name: str
    description: str
    genre: Genre
    cost: ResourceCost
    victory_points: int = Field(ge=0)
    bonus_resources: ResourceCost = Field(
        default_factory=ResourceCost,
    )
    reward_draw_intrigue: int = 0
    reward_draw_quests: int = 0
    reward_quest_draw_mode: str = "random"
    reward_building: str | None = None
    is_plot_quest: bool = False
    ongoing_benefit_description: str | None = None


class IntrigueCard(BaseModel):
    """An intrigue card played at The Garage."""

    id: str
    name: str
    description: str
    effect_type: str  # "gain_resources", "steal_resources", "all_players", "vp_bonus"
    effect_target: str = "self"  # "self", "opponent", "all", "choose_opponent"
    effect_value: dict = Field(default_factory=dict)


class BuildingTile(BaseModel):
    """A building tile - famous recording studio or music venue."""

    id: str
    name: str
    description: str
    cost_coins: int = Field(ge=0)
    visitor_reward: ResourceCost
    visitor_reward_special: str | None = None
    owner_bonus: ResourceCost
    owner_bonus_special: str | None = None
    accumulated_vp: int = 0


class ProducerCard(BaseModel):
    """A secret producer card - end-game scoring bonus."""

    id: str
    name: str
    description: str
    bonus_genres: list[Genre]
    bonus_vp_per_contract: int = Field(default=4, ge=0)
