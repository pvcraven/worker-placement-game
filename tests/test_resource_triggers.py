"""Tests for resource trigger plot quest mechanics."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from shared.card_models import ContractCard, IntrigueCard, ResourceCost
from server.models.game import PlayerResources
from server.game_engine import _evaluate_resource_triggers

CONFIG = Path(__file__).resolve().parent.parent / "config" / "contracts.json"


@pytest.fixture(scope="module")
def all_contracts():
    data = json.loads(CONFIG.read_text())
    return [ContractCard.model_validate(c) for c in data["contracts"]]


@pytest.fixture(scope="module")
def trigger_contracts(all_contracts):
    return [c for c in all_contracts if c.resource_trigger_type]


def _make_intrigue():
    return IntrigueCard(
        id="test_intrigue_1",
        name="Test Card",
        description="Test",
        effect_type="gain",
    )


def _make_player(completed=None, resources=None, player_id="player_1"):
    p = SimpleNamespace()
    p.player_id = player_id
    p.completed_contracts = completed or []
    if resources is None:
        p.resources = PlayerResources()
    elif isinstance(resources, ResourceCost):
        p.resources = PlayerResources(**resources.model_dump())
    else:
        p.resources = resources
    p.intrigue_hand = []
    return p


def _make_state(intrigue_count=5):
    s = SimpleNamespace()

    class Board:
        intrigue_deck = [_make_intrigue() for _ in range(intrigue_count)]

    s.board = Board()
    return s


def test_trigger_contracts_exist(trigger_contracts):
    assert len(trigger_contracts) == 5


def test_trigger_types_cover_expected(trigger_contracts):
    types = {c.resource_trigger_type for c in trigger_contracts}
    assert types == {"guitarists", "bass_players", "singers", "coins"}


def test_no_trigger_without_completed_quest():
    state = _make_state()
    player = _make_player()
    reward = ResourceCost(guitarists=1)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert results == []
    assert swap is None


def test_no_trigger_when_resource_not_gained():
    contract = ContractCard(
        id="test",
        name="Test",
        description="Test",
        genre="rock",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_bonus=ResourceCost(guitarists=1),
    )
    state = _make_state()
    player = _make_player(completed=[contract])
    reward = ResourceCost(coins=2)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert results == []


def test_simple_resource_bonus():
    contract = ContractCard(
        id="test_rock",
        name="Rock Loyalty",
        description="Test",
        genre="rock",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_bonus=ResourceCost(guitarists=1),
    )
    state = _make_state()
    player = _make_player(completed=[contract], resources=ResourceCost(guitarists=3))
    reward = ResourceCost(guitarists=2)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert results[0]["contract_id"] == "test_rock"
    assert results[0]["bonus_resources"]["guitarists"] == 1
    assert player.resources.guitarists == 4


def test_coins_trigger_grants_bass():
    contract = ContractCard(
        id="test_pop",
        name="Payola",
        description="Test",
        genre="pop",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="coins",
        resource_trigger_bonus=ResourceCost(bass_players=1),
    )
    state = _make_state()
    player = _make_player(completed=[contract], resources=ResourceCost(coins=5))
    reward = ResourceCost(coins=4)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert player.resources.bass_players == 1


def test_intrigue_draw_trigger():
    contract = ContractCard(
        id="test_funk",
        name="Groove Archive",
        description="Test",
        genre="funk",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_draw_intrigue=1,
    )
    state = _make_state(intrigue_count=3)
    player = _make_player(completed=[contract])
    reward = ResourceCost(guitarists=1)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert len(results[0]["drawn_intrigue"]) == 1
    assert len(player.intrigue_hand) == 1
    assert len(state.board.intrigue_deck) == 2


def test_singer_swap_trigger_flags_pending():
    contract = ContractCard(
        id="test_soul",
        name="Miracle Mic",
        description="Test",
        genre="soul",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="singers",
        resource_trigger_is_swap=True,
    )
    state = _make_state()
    player = _make_player(
        completed=[contract],
        resources=ResourceCost(singers=1, guitarists=2),
    )
    reward = ResourceCost(singers=1)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert results[0].get("swap_pending") is True
    assert swap is not None
    assert swap["contract_id"] == "test_soul"


def test_singer_swap_no_tradeable_resources():
    contract = ContractCard(
        id="test_soul",
        name="Miracle Mic",
        description="Test",
        genre="soul",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="singers",
        resource_trigger_is_swap=True,
    )
    state = _make_state()
    player = _make_player(completed=[contract], resources=ResourceCost(singers=3))
    reward = ResourceCost(singers=1)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert results[0].get("swap_pending") is None
    assert swap is None


def test_multiple_triggers_same_resource():
    contract_a = ContractCard(
        id="rock_bonus",
        name="Rock Loyalty",
        description="Test",
        genre="rock",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_bonus=ResourceCost(guitarists=1),
    )
    contract_b = ContractCard(
        id="funk_intrigue",
        name="Groove Archive",
        description="Test",
        genre="funk",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_draw_intrigue=1,
    )
    state = _make_state()
    player = _make_player(completed=[contract_a, contract_b])
    reward = ResourceCost(guitarists=1)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 2
    assert player.resources.guitarists == 1
    assert len(player.intrigue_hand) == 1


def test_no_trigger_from_zero_reward():
    contract = ContractCard(
        id="test",
        name="Test",
        description="Test",
        genre="rock",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="guitarists",
        resource_trigger_bonus=ResourceCost(guitarists=1),
    )
    state = _make_state()
    player = _make_player(completed=[contract])
    reward = ResourceCost()
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert results == []


def test_no_cascade_bonuses_do_not_retrigger():
    contract_coins = ContractCard(
        id="payola",
        name="Payola Pipeline",
        description="Test",
        genre="pop",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="coins",
        resource_trigger_bonus=ResourceCost(bass_players=1),
    )
    contract_bass = ContractCard(
        id="fence",
        name="Fence Bootleg",
        description="Test",
        genre="jazz",
        cost=ResourceCost(),
        victory_points=5,
        resource_trigger_type="bass_players",
        resource_trigger_bonus=ResourceCost(coins=2),
    )
    state = _make_state()
    player = _make_player(completed=[contract_coins, contract_bass])
    reward = ResourceCost(coins=4)
    results, swap = _evaluate_resource_triggers(state, player, reward)
    assert len(results) == 1
    assert results[0]["contract_id"] == "payola"
    assert player.resources.bass_players == 1
    assert player.resources.coins == 0
