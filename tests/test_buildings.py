"""Unit tests for building data integrity and accumulation mechanics."""

import json
from pathlib import Path

import pytest

from shared.card_models import BuildingTile, ResourceChoiceReward

CONFIG = Path(__file__).resolve().parent.parent / "config" / "buildings.json"


@pytest.fixture(scope="module")
def buildings():
    data = json.loads(CONFIG.read_text())
    return [BuildingTile.model_validate(b) for b in data["buildings"]]


def test_all_buildings_have_unique_ids(buildings):
    ids = [b.id for b in buildings]
    assert len(ids) == len(
        set(ids)
    ), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


def test_building_count(buildings):
    assert len(buildings) == 23


def test_cost_coins_range(buildings):
    bad = [(b.name, b.cost_coins) for b in buildings if not (3 <= b.cost_coins <= 8)]
    assert not bad, f"Buildings with cost outside 3-8: {bad}"


def test_accumulating_buildings_have_per_round(buildings):
    bad = []
    for b in buildings:
        if b.accumulation_type and b.accumulation_per_round <= 0:
            bad.append((b.name, b.accumulation_type, b.accumulation_per_round))
    assert not bad, f"Accumulating buildings with per_round <= 0: {bad}"


def test_non_accumulating_have_zero_accum_fields(buildings):
    bad = []
    for b in buildings:
        if not b.accumulation_type:
            if b.accumulation_per_round > 0 or b.accumulation_initial > 0:
                bad.append(b.name)
    assert not bad, f"Non-accumulating buildings with accum values: {bad}"


def test_accumulation_initial_stock():
    tile = BuildingTile(
        id="test_001",
        name="Test Accum",
        description="test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
    )
    assert tile.accumulated_stock == 0
    tile.accumulated_stock = tile.accumulation_initial
    assert tile.accumulated_stock == 2


def test_accumulation_increment():
    tile = BuildingTile(
        id="test_001",
        name="Test Accum",
        description="test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
    )
    tile.accumulated_stock = tile.accumulation_initial
    tile.accumulated_stock += tile.accumulation_per_round
    assert tile.accumulated_stock == 4
    tile.accumulated_stock += tile.accumulation_per_round
    assert tile.accumulated_stock == 6


def test_accumulation_reset_on_visit():
    tile = BuildingTile(
        id="test_001",
        name="Test Accum",
        description="test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
    )
    tile.accumulated_stock = 6
    collected = tile.accumulated_stock
    tile.accumulated_stock = 0
    assert collected == 6
    assert tile.accumulated_stock == 0


def test_free_building_starts_at_zero():
    tile = BuildingTile(
        id="test_001",
        name="Test Accum",
        description="test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
    )
    assert tile.accumulated_stock == 0


def test_vp_reward_fields():
    tile = BuildingTile(
        id="test_vp",
        name="VP Building",
        description="test",
        cost_coins=4,
        owner_bonus_vp=2,
        visitor_reward_vp=3,
    )
    assert tile.owner_bonus_vp == 2
    assert tile.visitor_reward_vp == 3


def test_owner_bonus_choice():
    tile = BuildingTile(
        id="test_choice",
        name="Choice Building",
        description="test",
        cost_coins=8,
        owner_bonus_choice=ResourceChoiceReward(
            choice_type="pick",
            allowed_types=["guitarists", "singers"],
            pick_count=1,
        ),
    )
    assert tile.owner_bonus_choice is not None
    assert tile.owner_bonus_choice.choice_type == "pick"
    assert tile.owner_bonus_choice.pick_count == 1
    assert set(tile.owner_bonus_choice.allowed_types) == {"guitarists", "singers"}


def test_buildings_with_owner_bonus_vp(buildings):
    vp_buildings = [b for b in buildings if b.owner_bonus_vp > 0]
    assert len(vp_buildings) >= 3
    for b in vp_buildings:
        assert b.owner_bonus_vp > 0


def test_buildings_with_owner_bonus_choice(buildings):
    choice_buildings = [b for b in buildings if b.owner_bonus_choice is not None]
    assert len(choice_buildings) == 6
    for b in choice_buildings:
        assert b.owner_bonus_choice.choice_type == "pick"
        assert b.owner_bonus_choice.pick_count == 1
        assert len(b.owner_bonus_choice.allowed_types) >= 2


def test_six_accumulating_buildings(buildings):
    accum = [b for b in buildings if b.accumulation_type]
    assert len(accum) == 6


def test_accumulating_building_types(buildings):
    accum = {b.accumulation_type for b in buildings if b.accumulation_type}
    expected = {
        "guitarists",
        "bass_players",
        "singers",
        "drummers",
        "coins",
        "victory_points",
    }
    assert accum == expected
