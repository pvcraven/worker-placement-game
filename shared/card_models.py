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

    def total(self) -> int:
        return (
            self.guitarists
            + self.bass_players
            + self.drummers
            + self.singers
            + self.coins
        )


class ResourceBundle(BaseModel):
    """A predefined bundle of resources offered as one selectable option."""

    label: str
    resources: ResourceCost


class ResourceChoiceReward(BaseModel):
    """Configuration for a choice-based resource reward."""

    choice_type: str  # "pick", "bundle", "combo", "exchange"
    allowed_types: list[str] = Field(default_factory=list)
    pick_count: int = 1
    total: int = 0
    bundles: list[ResourceBundle] = Field(
        default_factory=list,
    )
    cost: ResourceCost = Field(default_factory=ResourceCost)
    gain_count: int = 0
    others_pick_count: int = 0


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
    bonus_vp_per_genre_quest: int = 0
    bonus_vp_genre: Genre | None = None
    bonus_vp_per_intrigue_played: int = 0
    bonus_vp_per_building_owned: int = 0
    resource_trigger_type: str | None = None
    resource_trigger_bonus: ResourceCost = Field(default_factory=ResourceCost)
    resource_trigger_draw_intrigue: int = 0
    resource_trigger_is_swap: bool = False


class IntrigueCard(BaseModel):
    """An intrigue card played at The Garage."""

    id: str
    name: str
    description: str
    effect_type: str
    effect_target: str = "self"
    effect_value: dict = Field(default_factory=dict)
    choice_reward: ResourceChoiceReward | None = None


class BuildingTile(BaseModel):
    """A building tile - famous recording studio or music venue."""

    id: str
    name: str
    description: str
    cost_coins: int = Field(ge=0)
    visitor_reward: ResourceCost = Field(
        default_factory=ResourceCost,
    )
    visitor_reward_special: str | None = None
    visitor_reward_choice: ResourceChoiceReward | None = None
    owner_bonus: ResourceCost = Field(
        default_factory=ResourceCost,
    )
    owner_bonus_special: str | None = None
    owner_bonus_vp: int = 0
    owner_bonus_choice: ResourceChoiceReward | None = None
    accumulated_vp: int = 0
    accumulation_type: str | None = None
    accumulation_per_round: int = 0
    accumulation_initial: int = 0
    accumulated_stock: int = 0
    visitor_reward_vp: int = 0


class ProducerCard(BaseModel):
    """A secret producer card - end-game scoring bonus."""

    id: str
    name: str
    description: str
    bonus_genres: list[Genre]
    bonus_vp_per_contract: int = Field(default=4, ge=0)
