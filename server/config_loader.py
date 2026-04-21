"""Load and validate all JSON configuration files on server startup."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from server.models.config import (
    BoardConfig,
    BuildingsConfig,
    ContractsConfig,
    GameRulesConfig,
    IntrigueConfig,
    ProducersConfig,
)
from shared.card_models import ContractCard, IntrigueCard, BuildingTile, ProducerCard

logger = logging.getLogger(__name__)


class GameConfig:
    """Holds all validated game configuration data."""

    def __init__(
        self,
        contracts: list[ContractCard],
        intrigue_cards: list[IntrigueCard],
        buildings: list[BuildingTile],
        producers: list[ProducerCard],
        board: BoardConfig,
        rules: GameRulesConfig,
    ) -> None:
        self.contracts = contracts
        self.intrigue_cards = intrigue_cards
        self.buildings = buildings
        self.producers = producers
        self.board = board
        self.rules = rules


def _load_json(path: Path) -> dict:
    """Load a JSON file, raising on missing or malformed files."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _warn_suspicious_contracts(contracts: list[ContractCard]) -> None:
    for c in contracts:
        cost = c.cost
        total_cost = (
            cost.guitarists
            + cost.bass_players
            + cost.drummers
            + cost.singers
            + cost.coins
        )
        if total_cost == 0:
            logger.warning("Contract '%s' (%s) has zero cost", c.name, c.id)
        if c.victory_points > 20:
            logger.warning(
                "Contract '%s' (%s) has unusually high VP: %d",
                c.name,
                c.id,
                c.victory_points,
            )
        if not c.description:
            logger.warning("Contract '%s' (%s) has empty description", c.name, c.id)


def _warn_suspicious_intrigue(cards: list[IntrigueCard]) -> None:
    for c in cards:
        if not c.effect_value:
            logger.warning("Intrigue card '%s' (%s) has no effect value", c.name, c.id)
        if not c.description:
            logger.warning(
                "Intrigue card '%s' (%s) has empty description", c.name, c.id
            )


def _warn_suspicious_buildings(buildings: list[BuildingTile]) -> None:
    for b in buildings:
        reward_total = (
            b.visitor_reward.guitarists
            + b.visitor_reward.bass_players
            + b.visitor_reward.drummers
            + b.visitor_reward.singers
            + b.visitor_reward.coins
        )
        bonus_total = (
            b.owner_bonus.guitarists
            + b.owner_bonus.bass_players
            + b.owner_bonus.drummers
            + b.owner_bonus.singers
            + b.owner_bonus.coins
        )
        if (
            reward_total == 0
            and not b.visitor_reward_special
            and bonus_total == 0
            and not b.owner_bonus_special
        ):
            logger.warning(
                "Building '%s' (%s) has no visitor reward and no owner bonus",
                b.name,
                b.id,
            )


def _warn_card_counts(
    contracts: list[ContractCard],
    intrigue_cards: list[IntrigueCard],
    buildings: list[BuildingTile],
) -> None:
    if len(contracts) < 60:
        logger.warning("Expected ~60 contracts, found %d", len(contracts))
    if len(intrigue_cards) < 50:
        logger.warning("Expected ~50 intrigue cards, found %d", len(intrigue_cards))
    if len(buildings) < 24:
        logger.warning("Expected ~24 buildings, found %d", len(buildings))


def load_config(config_dir: str | Path) -> GameConfig:
    """Load and validate all config files from the given directory.

    Raises on structural/schema errors. Logs warnings for suspicious values.
    """
    config_dir = Path(config_dir)

    # --- Load and validate each config file ---
    try:
        contracts_data = _load_json(config_dir / "contracts.json")
        contracts_cfg = ContractsConfig.model_validate(contracts_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load contracts.json: {e}") from e

    try:
        intrigue_data = _load_json(config_dir / "intrigue.json")
        intrigue_cfg = IntrigueConfig.model_validate(intrigue_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load intrigue.json: {e}") from e

    try:
        buildings_data = _load_json(config_dir / "buildings.json")
        buildings_cfg = BuildingsConfig.model_validate(buildings_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load buildings.json: {e}") from e

    try:
        producers_data = _load_json(config_dir / "producers.json")
        producers_cfg = ProducersConfig.model_validate(producers_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load producers.json: {e}") from e

    try:
        board_data = _load_json(config_dir / "board.json")
        board_cfg = BoardConfig.model_validate(board_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load board.json: {e}") from e

    try:
        rules_data = _load_json(config_dir / "game_rules.json")
        rules_cfg = GameRulesConfig.model_validate(rules_data)
    except (ValidationError, FileNotFoundError) as e:
        raise SystemExit(f"Failed to load game_rules.json: {e}") from e

    # --- Suspicious value warnings ---
    _warn_suspicious_contracts(contracts_cfg.contracts)
    _warn_suspicious_intrigue(intrigue_cfg.intrigue_cards)
    _warn_suspicious_buildings(buildings_cfg.buildings)
    _warn_card_counts(
        contracts_cfg.contracts,
        intrigue_cfg.intrigue_cards,
        buildings_cfg.buildings,
    )

    logger.info(
        "Config loaded: %d contracts, %d intrigue, %d buildings, %d producers",
        len(contracts_cfg.contracts),
        len(intrigue_cfg.intrigue_cards),
        len(buildings_cfg.buildings),
        len(producers_cfg.producers),
    )

    return GameConfig(
        contracts=contracts_cfg.contracts,
        intrigue_cards=intrigue_cfg.intrigue_cards,
        buildings=buildings_cfg.buildings,
        producers=producers_cfg.producers,
        board=board_cfg,
        rules=rules_cfg,
    )
