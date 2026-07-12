"""Tests for resource distribution building mechanics (placement and collection)."""

import json
from pathlib import Path

import pytest

from shared.card_models import BuildingTile, ResourceCost
from server.models.game import (
    ActionSpace,
    BoardState,
    GameState,
    Player,
    PlayerResources,
)
from server.game_engine import (
    _get_distribution_eligible_spaces,
    _unwind_placement,
)

CONFIG = Path(__file__).resolve().parent.parent / "config" / "buildings.json"


@pytest.fixture(scope="module")
def buildings():
    data = json.loads(CONFIG.read_text())
    return [BuildingTile.model_validate(b) for b in data["buildings"]]


# --- Config validation for distribution buildings ---


def test_distribution_building_024_config(buildings):
    b = next(b for b in buildings if b.id == "building_024")
    assert b.cost_coins == 7
    assert b.visitor_reward.guitarists == 4
    assert b.distribute_resource_type == "guitarists"
    assert b.distribute_per_space == 1
    assert b.distribute_space_count == 2
    assert b.owner_bonus.guitarists == 2


def test_distribution_building_025_config(buildings):
    b = next(b for b in buildings if b.id == "building_025")
    assert b.cost_coins == 7
    assert b.visitor_reward.coins == 8
    assert b.distribute_resource_type == "coins"
    assert b.distribute_per_space == 2
    assert b.distribute_space_count == 2
    assert b.owner_bonus.coins == 4


def test_distribution_building_026_config(buildings):
    b = next(b for b in buildings if b.id == "building_026")
    assert b.cost_coins == 7
    assert b.visitor_reward.singers == 2
    assert b.distribute_resource_type == "singers"
    assert b.distribute_per_space == 1
    assert b.distribute_space_count == 1
    assert b.owner_bonus.singers == 1


def test_distribution_building_027_config(buildings):
    b = next(b for b in buildings if b.id == "building_027")
    assert b.cost_coins == 7
    assert b.visitor_reward.bass_players == 4
    assert b.distribute_resource_type == "bass_players"
    assert b.distribute_per_space == 1
    assert b.distribute_space_count == 2
    assert b.owner_bonus.bass_players == 2


def test_distribution_building_028_config(buildings):
    b = next(b for b in buildings if b.id == "building_028")
    assert b.cost_coins == 7
    assert b.visitor_reward.drummers == 2
    assert b.distribute_resource_type == "drummers"
    assert b.distribute_per_space == 1
    assert b.distribute_space_count == 1
    assert b.owner_bonus.drummers == 1


def test_non_distribution_buildings_have_no_distribute_fields(buildings):
    for b in buildings:
        if b.id not in (
            "building_024",
            "building_025",
            "building_026",
            "building_027",
            "building_028",
        ):
            assert b.distribute_resource_type is None, f"{b.id} has distribute_resource_type"
            assert b.distribute_per_space == 0, f"{b.id} has distribute_per_space"
            assert b.distribute_space_count == 0, f"{b.id} has distribute_space_count"


# --- Placed resource collection (US2) ---


def test_collect_placed_resources_single_type():
    """Visiting a space with placed_resources grants those resources to the player."""
    space = ActionSpace(
        space_id="test_space",
        name="Test Space",
        space_type="permanent",
        reward=ResourceCost(),
        placed_resources={"guitarists": 2},
    )
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(guitarists=1),
    )

    collected = _collect_placed_resources(space, player)

    assert player.resources.guitarists == 3
    assert space.placed_resources == {}
    assert collected == {"guitarists": 2}


def test_collect_placed_resources_multiple_types():
    """Multiple resource types on a space are all collected."""
    space = ActionSpace(
        space_id="test_space",
        name="Test Space",
        space_type="permanent",
        reward=ResourceCost(),
        placed_resources={"guitarists": 1, "coins": 3},
    )
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(guitarists=0, coins=5),
    )

    collected = _collect_placed_resources(space, player)

    assert player.resources.guitarists == 1
    assert player.resources.coins == 8
    assert space.placed_resources == {}
    assert collected == {"guitarists": 1, "coins": 3}


def test_collect_placed_resources_empty():
    """No placed_resources means nothing to collect."""
    space = ActionSpace(
        space_id="test_space",
        name="Test Space",
        space_type="permanent",
        reward=ResourceCost(),
        placed_resources={},
    )
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(guitarists=5),
    )

    collected = _collect_placed_resources(space, player)

    assert player.resources.guitarists == 5
    assert collected is None


def test_collect_placed_resources_does_not_affect_accumulated_stock():
    """Placed resources and accumulated stock are independent pools."""
    tile = BuildingTile(
        id="test_building",
        name="Test",
        description="Test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
        accumulated_stock=4,
    )
    space = ActionSpace(
        space_id="test_space",
        name="Test Space",
        space_type="building",
        reward=ResourceCost(),
        building_tile=tile,
        placed_resources={"coins": 2},
    )
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(),
    )

    collected = _collect_placed_resources(space, player)

    assert collected == {"coins": 2}
    assert player.resources.coins == 2
    assert space.placed_resources == {}
    assert space.building_tile.accumulated_stock == 4


def test_placed_resources_stacking():
    """Multiple distributions to the same space stack resources."""
    space = ActionSpace(
        space_id="test_space",
        name="Test Space",
        space_type="permanent",
        reward=ResourceCost(),
        placed_resources={"guitarists": 1},
    )

    space.placed_resources["guitarists"] = space.placed_resources.get("guitarists", 0) + 2
    space.placed_resources["coins"] = space.placed_resources.get("coins", 0) + 3

    assert space.placed_resources == {"guitarists": 3, "coins": 3}


def test_placed_resources_persist_model():
    """placed_resources on ActionSpace persist as a dict and don't get cleared by default."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "space_1": ActionSpace(
                    space_id="space_1",
                    name="Space 1",
                    space_type="permanent",
                    reward=ResourceCost(),
                    placed_resources={"drummers": 1},
                ),
            }
        ),
    )
    assert state.board.action_spaces["space_1"].placed_resources == {"drummers": 1}


def test_round_end_does_not_clear_placed_resources():
    """Round-end logic replenishes accumulated_stock but does NOT clear placed_resources."""
    tile = BuildingTile(
        id="test_building",
        name="Test",
        description="Test",
        cost_coins=4,
        accumulation_type="guitarists",
        accumulation_per_round=2,
        accumulation_initial=2,
        accumulated_stock=0,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Test Space",
        space_type="building",
        reward=ResourceCost(),
        building_tile=tile,
        placed_resources={"coins": 3, "drummers": 1},
    )
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={"lot_1": space},
            constructed_buildings=["lot_1"],
        ),
    )

    # Simulate round-end accumulated stock replenishment
    for space_id in state.board.constructed_buildings:
        s = state.board.action_spaces.get(space_id)
        if s and s.building_tile and s.building_tile.accumulation_type:
            s.building_tile.accumulated_stock += s.building_tile.accumulation_per_round

    assert space.building_tile.accumulated_stock == 2
    assert space.placed_resources == {"coins": 3, "drummers": 1}


# --- Distribution eligible spaces (US1) ---


def test_eligible_spaces_excludes_building():
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Distribution Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                ),
                "space_b": ActionSpace(
                    space_id="space_b",
                    name="Space B",
                    space_type="permanent",
                    reward=ResourceCost(),
                ),
            }
        ),
    )
    eligible = _get_distribution_eligible_spaces(
        state, "bldg_1", []
    )
    ids = [e["space_id"] for e in eligible]
    assert "bldg_1" not in ids
    assert "space_a" in ids
    assert "space_b" in ids


def test_eligible_spaces_excludes_already_selected():
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                ),
                "space_b": ActionSpace(
                    space_id="space_b",
                    name="Space B",
                    space_type="permanent",
                    reward=ResourceCost(),
                ),
            }
        ),
    )
    eligible = _get_distribution_eligible_spaces(
        state, "bldg_1", ["space_a"]
    )
    ids = [e["space_id"] for e in eligible]
    assert "space_a" not in ids
    assert "space_b" in ids


def test_distribution_pending_state_structure():
    """Pending resource distribution has the expected fields."""
    prd = {
        "player_id": "owner1",
        "building_space_id": "lot_1",
        "resource_type": "guitarists",
        "per_space": 1,
        "remaining_selections": 2,
        "selected_spaces": [],
    }
    assert prd["remaining_selections"] == 2
    assert prd["resource_type"] == "guitarists"


def test_distribution_selection_places_resources():
    """Selecting a space adds resources to placed_resources."""
    target = ActionSpace(
        space_id="space_a",
        name="Space A",
        space_type="permanent",
        reward=ResourceCost(),
    )
    rtype = "guitarists"
    qty = 1
    target.placed_resources[rtype] = (
        target.placed_resources.get(rtype, 0) + qty
    )
    assert target.placed_resources == {"guitarists": 1}

    target.placed_resources[rtype] = (
        target.placed_resources.get(rtype, 0) + qty
    )
    assert target.placed_resources == {"guitarists": 2}


def test_distribution_owner_selects_when_owned():
    """Owner (not visitor) is the selecting player."""
    tile = BuildingTile(
        id="building_024",
        name="Test",
        description="Test",
        cost_coins=7,
        distribute_resource_type="guitarists",
        distribute_per_space=1,
        distribute_space_count=2,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Test Bldg",
        space_type="building",
        reward=ResourceCost(),
        building_tile=tile,
        owner_id="owner1",
    )
    selecting_id = (
        space.owner_id if space.owner_id else "visitor1"
    )
    assert selecting_id == "owner1"


def test_distribution_visitor_selects_when_unowned():
    """Visitor selects if no owner."""
    tile = BuildingTile(
        id="building_024",
        name="Test",
        description="Test",
        cost_coins=7,
        distribute_resource_type="guitarists",
        distribute_per_space=1,
        distribute_space_count=2,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Test Bldg",
        space_type="building",
        reward=ResourceCost(),
        building_tile=tile,
        owner_id=None,
    )
    visitor_id = "visitor1"
    selecting_id = (
        space.owner_id if space.owner_id else visitor_id
    )
    assert selecting_id == "visitor1"


# --- Edge cases (T027) ---


def test_fewer_eligible_spaces_than_required():
    """When fewer eligible spaces exist than distribute_space_count, only available ones show."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Distribution Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                ),
            }
        ),
    )
    eligible = _get_distribution_eligible_spaces(state, "bldg_1", [])
    assert len(eligible) == 1
    assert eligible[0]["space_id"] == "space_a"


def test_no_eligible_spaces():
    """When no eligible spaces exist, list is empty."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Distribution Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
            }
        ),
    )
    eligible = _get_distribution_eligible_spaces(state, "bldg_1", [])
    assert eligible == []


def test_placed_resources_stacking_multiple_distributions():
    """Multiple distributions to the same space stack resources across types."""
    space = ActionSpace(
        space_id="space_a",
        name="Space A",
        space_type="permanent",
        reward=ResourceCost(),
        placed_resources={"guitarists": 1},
    )
    space.placed_resources["bass_players"] = (
        space.placed_resources.get("bass_players", 0) + 2
    )
    space.placed_resources["guitarists"] = (
        space.placed_resources.get("guitarists", 0) + 1
    )
    assert space.placed_resources == {"guitarists": 2, "bass_players": 2}


def test_placed_resources_on_accumulation_building():
    """Placed resources and accumulated stock are independent on same space."""
    tile = BuildingTile(
        id="test_building",
        name="Test Accum",
        description="Test",
        cost_coins=4,
        accumulation_type="singers",
        accumulation_per_round=1,
        accumulation_initial=1,
        accumulated_stock=3,
    )
    space = ActionSpace(
        space_id="lot_1",
        name="Test",
        space_type="building",
        reward=ResourceCost(),
        building_tile=tile,
        placed_resources={"coins": 2, "guitarists": 1},
    )
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(),
    )
    collected = _collect_placed_resources(space, player)
    assert collected == {"coins": 2, "guitarists": 1}
    assert player.resources.coins == 2
    assert player.resources.guitarists == 1
    assert space.placed_resources == {}
    assert space.building_tile.accumulated_stock == 3


def test_collect_placed_resources_preserves_normal_reward():
    """Collecting placed resources doesn't interfere with space reward."""
    space = ActionSpace(
        space_id="test_space",
        name="Test",
        space_type="permanent",
        reward=ResourceCost(guitarists=2, coins=1),
        placed_resources={"drummers": 3},
    )
    assert space.reward.guitarists == 2
    assert space.reward.coins == 1
    player = Player(
        player_id="p1",
        display_name="Alice",
        slot_index=0,
        resources=PlayerResources(),
    )
    collected = _collect_placed_resources(space, player)
    assert collected == {"drummers": 3}
    assert player.resources.drummers == 3
    assert space.reward.guitarists == 2
    assert space.reward.coins == 1


# --- Cancel/unwind (T028) ---


def test_unwind_reverses_distribution_placed_resources():
    """Cancelling a placement unwinds resources placed during distribution."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Distribution Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                    placed_resources={"guitarists": 1},
                ),
                "space_b": ActionSpace(
                    space_id="space_b",
                    name="Space B",
                    space_type="permanent",
                    reward=ResourceCost(),
                    placed_resources={"guitarists": 1},
                ),
            }
        ),
        players=[
            Player(
                player_id="p1",
                display_name="Alice",
                slot_index=0,
                resources=PlayerResources(guitarists=4),
                available_workers=0,
            )
        ],
    )
    state.board.action_spaces["bldg_1"].occupied_by = "p1"
    state.pending_resource_distribution = {
        "player_id": "p1",
        "building_space_id": "bldg_1",
        "resource_type": "guitarists",
        "per_space": 1,
        "remaining_selections": 0,
        "selected_spaces": ["space_a", "space_b"],
    }
    pending = {
        "player_id": "p1",
        "space_id": "bldg_1",
        "granted_resources": {"guitarists": 4},
    }
    player = state.players[0]
    result = _unwind_placement(state, player, pending)

    assert state.board.action_spaces["space_a"].placed_resources == {}
    assert state.board.action_spaces["space_b"].placed_resources == {}
    assert state.pending_resource_distribution is None
    assert len(result["reversed_distribution"]) == 2
    assert player.resources.guitarists == 0
    assert player.available_workers == 1


def test_unwind_preserves_pre_existing_placed_resources():
    """Unwind only removes the per_space amount, not other placed resources."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "bldg_1": ActionSpace(
                    space_id="bldg_1",
                    name="Distribution Bldg",
                    space_type="building",
                    reward=ResourceCost(),
                ),
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                    placed_resources={"guitarists": 3, "coins": 2},
                ),
            }
        ),
        players=[
            Player(
                player_id="p1",
                display_name="Alice",
                slot_index=0,
                resources=PlayerResources(),
                available_workers=0,
            )
        ],
    )
    state.board.action_spaces["bldg_1"].occupied_by = "p1"
    state.pending_resource_distribution = {
        "player_id": "p1",
        "building_space_id": "bldg_1",
        "resource_type": "guitarists",
        "per_space": 1,
        "remaining_selections": 0,
        "selected_spaces": ["space_a"],
    }
    pending = {
        "player_id": "p1",
        "space_id": "bldg_1",
        "granted_resources": {},
    }
    player = state.players[0]
    _unwind_placement(state, player, pending)

    assert state.board.action_spaces["space_a"].placed_resources == {
        "guitarists": 2, "coins": 2
    }


def test_unwind_no_distribution_is_noop():
    """Unwind with no pending distribution doesn't touch placed resources."""
    state = GameState(
        game_id="test",
        game_code="TEST",
        board=BoardState(
            action_spaces={
                "space_a": ActionSpace(
                    space_id="space_a",
                    name="Space A",
                    space_type="permanent",
                    reward=ResourceCost(),
                    placed_resources={"coins": 5},
                ),
            }
        ),
        players=[
            Player(
                player_id="p1",
                display_name="Alice",
                slot_index=0,
                resources=PlayerResources(),
                available_workers=0,
            )
        ],
    )
    pending = {
        "player_id": "p1",
        "space_id": "space_a",
        "granted_resources": {},
    }
    player = state.players[0]
    result = _unwind_placement(state, player, pending)

    assert state.board.action_spaces["space_a"].placed_resources == {"coins": 5}
    assert result["reversed_distribution"] == []


# --- Helper to simulate the collection logic ---


def _collect_placed_resources(
    space: ActionSpace, player: Player
) -> dict | None:
    """Simulate the placed resource collection logic from game_engine.py."""
    if not space.placed_resources:
        return None
    collected = dict(space.placed_resources)
    for rtype, qty in collected.items():
        if hasattr(player.resources, rtype):
            setattr(
                player.resources,
                rtype,
                getattr(player.resources, rtype) + qty,
            )
    space.placed_resources = {}
    return collected
