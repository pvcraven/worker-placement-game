"""Config file Pydantic schemas for JSON validation on startup."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from shared.card_models import (
    BuildingTile,
    ContractCard,
    IntrigueCard,
    ProducerCard,
    ResourceCost,
)


class ContractsConfig(BaseModel):
    """Schema for config/contracts.json"""

    contracts: list[ContractCard]

    @field_validator("contracts")
    @classmethod
    def validate_unique_ids(cls, v: list[ContractCard]) -> list[ContractCard]:
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate contract IDs found")
        return v


class IntrigueConfig(BaseModel):
    """Schema for config/intrigue.json"""

    intrigue_cards: list[IntrigueCard]

    @field_validator("intrigue_cards")
    @classmethod
    def validate_unique_ids(cls, v: list[IntrigueCard]) -> list[IntrigueCard]:
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate intrigue card IDs found")
        return v


class BuildingsConfig(BaseModel):
    """Schema for config/buildings.json"""

    buildings: list[BuildingTile]

    @field_validator("buildings")
    @classmethod
    def validate_buildings(cls, v: list[BuildingTile]) -> list[BuildingTile]:
        ids = [b.id for b in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate building IDs found")
        for b in v:
            if not (3 <= b.cost_coins <= 8):
                raise ValueError(
                    f"Building '{b.name}' cost_coins={b.cost_coins}"
                    f" is outside allowed range 3-8"
                )
        return v


class ProducersConfig(BaseModel):
    """Schema for config/producers.json"""

    producers: list[ProducerCard]

    @field_validator("producers")
    @classmethod
    def validate_unique_ids(cls, v: list[ProducerCard]) -> list[ProducerCard]:
        ids = [p.id for p in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate producer IDs found")
        return v


class ActionSpaceConfig(BaseModel):
    """A permanent action space definition in board.json."""

    space_id: str
    name: str
    space_type: str
    reward: ResourceCost = Field(default_factory=ResourceCost)
    reward_special: str | None = None
    slots: int = 1


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
    starting_workers: dict[str, int] = Field(default={"2": 4, "3": 3, "4": 2, "5": 2})
    min_players: int = 1
    max_players: int = 5
