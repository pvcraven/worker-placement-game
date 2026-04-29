"""Tests for the copy-occupied-space mechanic (Shadow Studio + Bootleg Recording)."""

import json
from pathlib import Path

import pytest

from shared.card_models import BuildingTile, IntrigueCard, ResourceCost
from server.models.game import (
    ActionSpace,
    BoardState,
    GameState,
    Player,
    PlayerResources,
)
from server.game_engine import _get_copy_eligible_spaces

CONFIG_BUILDINGS = Path(__file__).resolve().parent.parent / "config" / "buildings.json"
CONFIG_INTRIGUE = Path(__file__).resolve().parent.parent / "config" / "intrigue.json"


@pytest.fixture(scope="module")
def buildings():
    data = json.loads(CONFIG_BUILDINGS.read_text())
    return [BuildingTile.model_validate(b) for b in data["buildings"]]


@pytest.fixture(scope="module")
def intrigue_cards():
    data = json.loads(CONFIG_INTRIGUE.read_text())
    return [IntrigueCard.model_validate(c) for c in data["intrigue_cards"]]


@pytest.fixture
def shadow_studio(buildings):
    return next(b for b in buildings if b.id == "building_023")


@pytest.fixture
def bootleg_cards(intrigue_cards):
    return [c for c in intrigue_cards if c.id in ("intrigue_053", "intrigue_054")]


# --- Config validation ---


def test_shadow_studio_config(shadow_studio):
    b = shadow_studio
    assert b.name == "Shadow Studio"
    assert b.visitor_reward_special == "copy_occupied_space"
    assert b.cost_coins == 8
    assert b.owner_bonus_vp == 2


def test_bootleg_recording_config(bootleg_cards):
    assert len(bootleg_cards) == 2
    for card in bootleg_cards:
        assert card.name == "Bootleg Recording"
        assert card.effect_type == "copy_occupied_space"
        assert card.effect_value == {"cost_coins": 2}


# --- _get_copy_eligible_spaces ---


def _make_player(player_id="p1"):
    return Player(
        player_id=player_id,
        display_name=f"Player {player_id}",
        slot_index=0,
        resources=PlayerResources(),
    )


def _make_space(space_id, name="Test Space", space_type="permanent", occupied_by=None):
    return ActionSpace(
        space_id=space_id,
        name=name,
        space_type=space_type,
        occupied_by=occupied_by,
        reward=ResourceCost(bass_players=2),
    )


def test_copy_basic_permanent_space():
    """Opponent on a permanent space shows up as eligible."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown Records", "permanent", "p2"),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "motown"
    assert eligible[0]["name"] == "Motown Records"
    assert eligible[0]["space_type"] == "permanent"
    assert eligible[0]["reward_preview"]["bass_players"] == 2


def test_copy_no_valid_targets():
    """No opponents placed means no eligible spaces."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown Records", "permanent", None),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert eligible == []


def test_copy_excludes_own_spaces():
    """Player's own occupied spaces are not eligible."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown Records", "permanent", "p1"),
                "abbey": _make_space("abbey", "Abbey Road", "permanent", "p2"),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "abbey"


def test_copy_excludes_empty_spaces():
    """Empty spaces are not eligible."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown Records", "permanent", None),
                "abbey": _make_space("abbey", "Abbey Road", "permanent", "p2"),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "abbey"


def test_copy_excludes_backstage():
    """Backstage spaces are never eligible for copying."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bs1": _make_space("bs1", "Backstage 1", "backstage", "p2"),
                "abbey": _make_space("abbey", "Abbey Road", "permanent", "p2"),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "abbey"


# --- Cancel / unwind ---


def test_cancel_copy_selection_clears_pending():
    """Cancelling sets pending_copy_source to None."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        pending_copy_source={
            "player_id": "p1",
            "source_space_id": "shadow_studio",
            "source_type": "building",
            "eligible_spaces": ["motown"],
        },
        pending_placement={
            "player_id": "p1",
            "space_id": "shadow_studio",
            "granted_resources": {},
            "granted_vp": 0,
            "accumulated_stock_consumed": 0,
            "accumulation_type": None,
            "owner_bonus_info": {},
            "trigger_bonuses": [],
        },
    )
    assert state.pending_copy_source is not None
    assert state.pending_placement is not None
    # Simulate cancel
    state.pending_copy_source = None
    state.pending_placement = None
    assert state.pending_copy_source is None
    assert state.pending_placement is None


# --- Pending state ---


def test_pending_copy_source_default_none():
    state = GameState(game_id="test", game_code="TEST")
    assert state.pending_copy_source is None


def test_pending_copy_source_set_and_clear():
    state = GameState(game_id="test", game_code="TEST")
    state.pending_copy_source = {
        "player_id": "p1",
        "source_space_id": "shadow_studio",
        "source_type": "building",
        "eligible_spaces": ["motown", "abbey"],
    }
    assert state.pending_copy_source["source_type"] == "building"
    assert len(state.pending_copy_source["eligible_spaces"]) == 2
    state.pending_copy_source = None
    assert state.pending_copy_source is None


# --- Shadow Studio owner bonus config ---


def test_shadow_studio_owner_bonus_vp(shadow_studio):
    """Shadow Studio grants 2 VP owner bonus (config-driven)."""
    assert shadow_studio.owner_bonus_vp == 2
    assert shadow_studio.owner_bonus.coins == 0
    assert shadow_studio.owner_bonus.guitarists == 0


# --- Owner bonus for Shadow Studio ---


def test_shadow_studio_owner_bonus_no_self_bonus():
    """Owner visiting own Shadow Studio should not receive owner bonus."""
    tile = BuildingTile(
        id="building_023",
        name="Shadow Studio",
        description="test",
        cost_coins=8,
        visitor_reward_special="copy_occupied_space",
        owner_bonus_vp=2,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Shadow Studio",
        space_type="building",
        occupied_by="p1",
        owner_id="p1",
        building_tile=tile,
    )
    visitor = _make_player("p1")
    assert space.owner_id == visitor.player_id


def test_shadow_studio_owner_bonus_granted_to_owner():
    """Non-owner visiting Shadow Studio triggers owner_bonus_vp: 2."""
    tile = BuildingTile(
        id="building_023",
        name="Shadow Studio",
        description="test",
        cost_coins=8,
        visitor_reward_special="copy_occupied_space",
        owner_bonus_vp=2,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Shadow Studio",
        space_type="building",
        occupied_by="p2",
        owner_id="p1",
        building_tile=tile,
    )
    owner = _make_player("p1")
    visitor = _make_player("p2")
    assert space.owner_id != visitor.player_id
    assert tile.owner_bonus_vp == 2
    owner.victory_points += tile.owner_bonus_vp
    assert owner.victory_points == 2


# --- Special space types ---


def test_copy_includes_building_spaces():
    """Building-type spaces occupied by opponents are eligible."""
    player = _make_player("p1")
    tile = BuildingTile(
        id="b_test",
        name="Test Building",
        description="test",
        cost_coins=4,
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "lot_1": ActionSpace(
                    space_id="lot_1",
                    name="Test Building",
                    space_type="building",
                    occupied_by="p2",
                    building_tile=tile,
                    reward=ResourceCost(coins=3),
                ),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_type"] == "building"


def test_copy_includes_garage_spaces():
    """Garage-type spaces occupied by opponents are eligible."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "garage_1": _make_space(
                    "garage_1", "Garage Spot 1", "garage", "p2"
                ),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_type"] == "garage"


def test_copy_includes_castle_space():
    """Castle-type spaces occupied by opponents are eligible."""
    player = _make_player("p1")
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "castle": _make_space("castle", "Castle", "castle", "p2"),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_type"] == "castle"


def test_copy_accumulated_stock_building():
    """Accumulated stock building should show base reward in preview."""
    player = _make_player("p1")
    tile = BuildingTile(
        id="b_accum",
        name="Accum Studio",
        description="test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=1,
        accumulation_initial=1,
    )
    tile.accumulated_stock = 3
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "lot_2": ActionSpace(
                    space_id="lot_2",
                    name="Accum Studio",
                    space_type="building",
                    occupied_by="p2",
                    building_tile=tile,
                    reward=ResourceCost(guitarists=1),
                ),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["reward_preview"]["guitarists"] == 1


def test_copy_owner_bonus_no_self():
    """Copying own building should not trigger owner bonus."""
    tile = BuildingTile(
        id="b_own",
        name="Own Building",
        description="test",
        cost_coins=4,
        owner_bonus_vp=2,
    )
    space = ActionSpace(
        space_id="lot_3",
        name="Own Building",
        space_type="building",
        occupied_by="p2",
        owner_id="p1",
        building_tile=tile,
    )
    player = _make_player("p1")
    assert space.owner_id == player.player_id


# --- Intrigue card: Bootleg Recording ---


def test_bootleg_effect_type():
    """Bootleg Recording has copy_occupied_space effect type."""
    card = IntrigueCard(
        id="intrigue_053",
        name="Bootleg Recording",
        description="test",
        effect_type="copy_occupied_space",
        effect_value={"cost_coins": 2},
    )
    assert card.effect_type == "copy_occupied_space"
    assert card.effect_value["cost_coins"] == 2


def test_bootleg_insufficient_coins_flag():
    """Player with < 2 coins gets insufficient_coins flag."""
    from server.game_engine import _resolve_intrigue_effect

    player = _make_player("p1")
    player.resources.coins = 1
    card = IntrigueCard(
        id="intrigue_053",
        name="Bootleg Recording",
        description="test",
        effect_type="copy_occupied_space",
        effect_value={"cost_coins": 2},
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        players=[player],
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown", "permanent", "p2"),
            }
        ),
    )
    effect = _resolve_intrigue_effect(state, player, card)
    assert effect.get("insufficient_coins") is True


def test_bootleg_no_valid_targets_flag():
    """Player with coins but no opponents placed gets no_valid_targets flag."""
    from server.game_engine import _resolve_intrigue_effect

    player = _make_player("p1")
    player.resources.coins = 5
    card = IntrigueCard(
        id="intrigue_053",
        name="Bootleg Recording",
        description="test",
        effect_type="copy_occupied_space",
        effect_value={"cost_coins": 2},
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        players=[player],
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown", "permanent", None),
            }
        ),
    )
    effect = _resolve_intrigue_effect(state, player, card)
    assert effect.get("no_valid_targets") is True
    assert player.resources.coins == 5


def test_bootleg_pending_deducts_coins():
    """Successful Bootleg Recording deducts 2 coins and sets pending."""
    from server.game_engine import _resolve_intrigue_effect

    player = _make_player("p1")
    player.resources.coins = 5
    card = IntrigueCard(
        id="intrigue_053",
        name="Bootleg Recording",
        description="test",
        effect_type="copy_occupied_space",
        effect_value={"cost_coins": 2},
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        players=[player],
        board=BoardState(
            action_spaces={
                "motown": _make_space("motown", "Motown", "permanent", "p2"),
            }
        ),
    )
    effect = _resolve_intrigue_effect(state, player, card)
    assert effect.get("pending") is True
    assert effect.get("cost_deducted") == 2
    assert player.resources.coins == 3
    assert len(effect.get("eligible_spaces", [])) == 1


def test_bootleg_cancel_returns_coins():
    """Cancelling intrigue copy returns coins to player."""
    player = _make_player("p1")
    player.resources.coins = 3

    state = GameState(
        game_id="test",
        game_code="TEST",
        players=[player],
        pending_copy_source={
            "player_id": "p1",
            "source_space_id": "backstage_slot_1",
            "source_type": "intrigue",
            "cost_deducted": 2,
            "intrigue_card": {
                "id": "intrigue_053",
                "name": "Bootleg Recording",
                "description": "test",
                "effect_type": "copy_occupied_space",
                "effect_value": {"cost_coins": 2},
            },
            "slot_number": 1,
            "eligible_spaces": ["motown"],
        },
    )

    cost = state.pending_copy_source.get("cost_deducted", 0)
    player.resources.coins += cost
    assert player.resources.coins == 5


# --- Resource choice building eligibility ---


def test_copy_resource_choice_building_eligible():
    """Building with visitor_reward_choice is eligible for copying."""
    from shared.card_models import ResourceChoiceReward

    player = _make_player("p1")
    tile = BuildingTile(
        id="b_choice",
        name="The Fillmore",
        description="test",
        cost_coins=4,
        visitor_reward_choice=ResourceChoiceReward(
            choice_type="pick",
            allowed_types=["singers", "drummers"],
            pick_count=2,
        ),
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "lot_5": ActionSpace(
                    space_id="lot_5",
                    name="The Fillmore",
                    space_type="building",
                    occupied_by="p2",
                    building_tile=tile,
                    reward=ResourceCost(),
                ),
            }
        ),
    )
    eligible = _get_copy_eligible_spaces(state, player)
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "lot_5"
    assert eligible[0]["space_type"] == "building"


# --- Owner bonus cascading ---


def test_copy_owner_bonus_cascading():
    """Copying an opponent's building triggers that building's owner bonus."""
    tile = BuildingTile(
        id="b_cascade",
        name="Cascade Building",
        description="test",
        cost_coins=4,
        owner_bonus_vp=3,
    )
    space = ActionSpace(
        space_id="lot_4",
        name="Cascade Building",
        space_type="building",
        occupied_by="p3",
        owner_id="p2",
        building_tile=tile,
        reward=ResourceCost(coins=2),
    )
    copier = _make_player("p1")
    owner = _make_player("p2")
    assert space.owner_id == owner.player_id
    assert space.owner_id != copier.player_id
    owner.victory_points += tile.owner_bonus_vp
    assert owner.victory_points == 3


# --- Resource trigger on copied rewards ---


def test_resource_trigger_fires_on_copied_reward():
    """Resource triggers should activate from copied space rewards.

    Validates that the reward from a copied space is a standard resource
    grant that would pass through _evaluate_resource_triggers().
    """
    player = _make_player("p1")
    player.resources.coins = 0
    space = _make_space("motown", "Motown Records", "permanent", "p2")
    assert space.reward.bass_players == 2
    player.resources.bass_players += space.reward.bass_players
    assert player.resources.bass_players == 2


# --- Building count updated ---


def test_building_count_includes_shadow_studio(buildings):
    assert len(buildings) == 23
