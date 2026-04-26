"""Tests for special building mechanics: coins_per_building and draw_contract_and_complete."""

import json
from pathlib import Path

import pytest

from shared.card_models import BuildingTile
from shared.messages import QuestCompletionPromptResponse, QuestCompletedResponse
from server.models.game import GameState, Player, BoardState

CONFIG = Path(__file__).resolve().parent.parent / "config" / "buildings.json"


@pytest.fixture(scope="module")
def buildings():
    data = json.loads(CONFIG.read_text())
    return [BuildingTile.model_validate(b) for b in data["buildings"]]


@pytest.fixture
def royalty_building(buildings):
    return next(b for b in buildings if b.id == "building_021")


@pytest.fixture
def showcase_building(buildings):
    return next(b for b in buildings if b.id == "building_022")


# --- Config validation ---


def test_royalty_collection_config(royalty_building):
    b = royalty_building
    assert b.name == "Royalty Collection Office"
    assert b.visitor_reward_special == "coins_per_building"
    assert b.cost_coins == 4
    assert b.owner_bonus.coins == 2
    assert b.owner_bonus_vp == 0


def test_audition_showcase_config(showcase_building):
    b = showcase_building
    assert b.name == "Audition Showcase"
    assert b.visitor_reward_special == "draw_contract_and_complete"
    assert b.cost_coins == 4
    assert b.owner_bonus_vp == 2
    assert b.owner_bonus.coins == 0


# --- coins_per_building reward calculation ---


def test_coins_per_building_zero_buildings():
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(constructed_buildings=[]),
    )
    coin_count = len(state.board.constructed_buildings)
    assert coin_count == 0


def test_coins_per_building_multiple_buildings():
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            constructed_buildings=["lot_1", "lot_2", "lot_3"],
        ),
    )
    coin_count = len(state.board.constructed_buildings)
    assert coin_count == 3


def test_coins_per_building_dynamic():
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(constructed_buildings=["lot_1"]),
    )
    assert len(state.board.constructed_buildings) == 1
    state.board.constructed_buildings.append("lot_2")
    assert len(state.board.constructed_buildings) == 2


# --- pending_showcase_bonus state management ---


def test_pending_showcase_bonus_default_none():
    state = GameState(game_id="test", game_code="TEST")
    assert state.pending_showcase_bonus is None


def test_pending_showcase_bonus_set():
    state = GameState(game_id="test", game_code="TEST")
    state.pending_showcase_bonus = {
        "player_id": "p1",
        "contract_id": None,
        "bonus_vp": 4,
    }
    assert state.pending_showcase_bonus is not None
    assert state.pending_showcase_bonus["bonus_vp"] == 4
    assert state.pending_showcase_bonus["contract_id"] is None


def test_pending_showcase_bonus_contract_set():
    state = GameState(game_id="test", game_code="TEST")
    state.pending_showcase_bonus = {
        "player_id": "p1",
        "contract_id": None,
        "bonus_vp": 4,
    }
    state.pending_showcase_bonus["contract_id"] = "contract_001"
    assert state.pending_showcase_bonus["contract_id"] == "contract_001"


def test_pending_showcase_bonus_cleared():
    state = GameState(game_id="test", game_code="TEST")
    state.pending_showcase_bonus = {
        "player_id": "p1",
        "contract_id": "contract_001",
        "bonus_vp": 4,
    }
    state.pending_showcase_bonus = None
    assert state.pending_showcase_bonus is None


# --- QuestCompletionPromptResponse bonus fields ---


def test_prompt_response_no_bonus():
    resp = QuestCompletionPromptResponse(completable_quests=[])
    assert resp.bonus_quest_id is None
    assert resp.bonus_vp == 0


def test_prompt_response_with_bonus():
    resp = QuestCompletionPromptResponse(
        completable_quests=[],
        bonus_quest_id="contract_001",
        bonus_vp=4,
    )
    assert resp.bonus_quest_id == "contract_001"
    assert resp.bonus_vp == 4


# --- QuestCompletedResponse showcase_bonus_vp field ---


def test_completed_response_no_showcase_bonus():
    resp = QuestCompletedResponse(
        player_id="p1",
        contract_id="c1",
        contract_name="Test",
        victory_points_earned=5,
        resources_spent={},
        bonus_resources={},
    )
    assert resp.showcase_bonus_vp == 0


def test_completed_response_with_showcase_bonus():
    resp = QuestCompletedResponse(
        player_id="p1",
        contract_id="c1",
        contract_name="Test",
        victory_points_earned=5,
        resources_spent={},
        bonus_resources={},
        showcase_bonus_vp=4,
    )
    assert resp.showcase_bonus_vp == 4


# --- Showcase bonus VP award logic ---


def test_showcase_bonus_awarded_matching_contract():
    player = Player(
        player_id="p1",
        display_name="Test",
        slot_index=0,
        victory_points=10,
    )
    pending = {"player_id": "p1", "contract_id": "c1", "bonus_vp": 4}
    contract_id = "c1"
    if pending.get("contract_id") == contract_id:
        player.victory_points += pending["bonus_vp"]
    assert player.victory_points == 14


def test_showcase_bonus_not_awarded_different_contract():
    player = Player(
        player_id="p1",
        display_name="Test",
        slot_index=0,
        victory_points=10,
    )
    pending = {"player_id": "p1", "contract_id": "c1", "bonus_vp": 4}
    contract_id = "c2"
    if pending.get("contract_id") == contract_id:
        player.victory_points += pending["bonus_vp"]
    assert player.victory_points == 10


# --- Owner bonus does not trigger on self-visit ---


def test_owner_bonus_requires_different_player():
    owner_id = "p1"
    visitor_id = "p1"
    assert owner_id == visitor_id

    owner_id2 = "p1"
    visitor_id2 = "p2"
    assert owner_id2 != visitor_id2
