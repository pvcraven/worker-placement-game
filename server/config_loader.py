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
