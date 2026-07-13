"""Tests for the building market — buying a building should not reshuffle
the other face-up buildings' positions."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from server.game_engine import (
    handle_cancel_purchase_building,
    handle_place_worker,
    handle_purchase_building,
)
from server.models.game import (
    ActionSpace,
    BackstageSlot,
    GameState,
    Player,
    PlayerResources,
)
from shared.card_models import BuildingTile
from shared.constants import GamePhase


def _make_server(state: GameState) -> MagicMock:
    server = MagicMock()
    server.session_manager.get_session.return_value = state
    server.broadcast_to_game = AsyncMock()
    server.send_to_player = AsyncMock()
    return server


def _make_conn(player_id: str, game_code: str = "test") -> MagicMock:
    conn = MagicMock()
    conn.player_id = player_id
    conn.game_code = game_code
    conn.send_error = AsyncMock()
    return conn


def _make_building(building_id: str, cost: int = 2) -> BuildingTile:
    return BuildingTile(
        id=building_id,
        name=building_id,
        description="test",
        cost_coins=cost,
    )


def _make_state() -> GameState:
    state = GameState(game_code="test", game_id="test-id")
    player = Player(
        player_id="p1",
        display_name="Player p1",
        slot_index=0,
        resources=PlayerResources(coins=10),
    )
    state.players = [player]

    state.board.face_up_buildings = [
        _make_building("bld_a"),
        _make_building("bld_b"),
        _make_building("bld_c"),
        _make_building("bld_d"),
    ]
    state.board.building_deck = [_make_building("bld_new")]
    state.board.building_lots = ["lot_0"]

    return state


def test_purchased_building_replaced_in_place():
    """Regression: buying the leftmost building must slot the replacement
    into that same spot, leaving the other buildings' order untouched
    (previously the purchased tile was removed and the replacement was
    appended at the end, shifting everything else left)."""
    state = _make_state()
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.building_id = "bld_a"

    asyncio.run(handle_purchase_building(server, conn, msg))

    ids = [b.id for b in state.board.face_up_buildings]
    assert ids == ["bld_new", "bld_b", "bld_c", "bld_d"]


def test_purchased_building_with_empty_deck_leaves_gap_removed():
    """When the deck is empty, the slot is simply removed rather than
    leaving a stale entry or reshuffling the rest."""
    state = _make_state()
    state.board.building_deck = []
    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()
    msg.building_id = "bld_b"

    asyncio.run(handle_purchase_building(server, conn, msg))

    ids = [b.id for b in state.board.face_up_buildings]
    assert ids == ["bld_a", "bld_c", "bld_d"]


def test_cancel_purchase_during_reassignment_reverses_collected_resources():
    """Regression: cancelling a Realtor (purchase_building) visit during the
    reassignment phase must reverse any resources collected from the space
    (e.g. guitarists placed there by 'The Riff Network') instead of letting
    the player keep them for free, and must return the worker to its
    backstage slot rather than silently ending its reassignment."""
    state = GameState(game_code="test", game_id="test-id")
    state.phase = GamePhase.REASSIGNMENT
    player = Player(
        player_id="p1",
        display_name="Player p1",
        slot_index=0,
        resources=PlayerResources(guitarists=3),
        available_workers=2,
    )
    state.players = [player]

    state.board.action_spaces["realtor"] = ActionSpace(
        space_id="realtor",
        name="Realtor",
        space_type="permanent",
        occupied_by="p1",
        reward_special="purchase_building",
    )
    state.board.backstage_slots = [BackstageSlot(slot_number=1, occupied_by=None)]
    state.reassignment_active_player_id = "p1"
    state.reassignment_queue = []

    state.pending_placement = {
        "player_id": "p1",
        "space_id": "realtor",
        "granted_resources": {"guitarists": 3},
        "granted_vp": 0,
        "accumulated_stock_consumed": 0,
        "accumulation_type": None,
        "owner_bonus_info": {},
        "trigger_bonuses": [],
        "is_reassignment": True,
        "from_slot": 1,
    }

    server = _make_server(state)
    conn = _make_conn("p1")
    msg = MagicMock()

    asyncio.run(handle_cancel_purchase_building(server, conn, msg))

    assert player.resources.guitarists == 0
    assert player.available_workers == 2
    assert state.pending_placement is None
    assert state.board.action_spaces["realtor"].occupied_by is None
    assert state.board.backstage_slots[0].occupied_by == "p1"
    assert state.reassignment_queue == [1]
    assert state.reassignment_active_player_id is None

    server.broadcast_to_game.assert_called_once()
    _, response = server.broadcast_to_game.call_args[0]
    assert response.action == "placement_cancelled"
    assert response.reversed_rewards == {"guitarists": 3}
    assert response.restored_slot == 1


def test_cancel_purchase_building_restores_placed_resources_to_space():
    """Regression: coins placed on Realtor by a distribution building (e.g.
    The Bankroll) must NOT be kept by a player who lands there and cancels
    the purchase — they must go back onto Realtor for the next visitor,
    rather than vanishing or staying with the canceller."""
    state = GameState(game_code="test", game_id="test-id")
    state.phase = GamePhase.PLACEMENT
    player = Player(
        player_id="p1",
        display_name="Player p1",
        slot_index=0,
        resources=PlayerResources(coins=1),
        available_workers=2,
    )
    state.players = [player]
    state.turn_order = ["p1"]
    state.current_player_index = 0

    realtor = ActionSpace(
        space_id="realtor",
        name="Realtor",
        space_type="permanent",
        reward_special="purchase_building",
    )
    realtor.placed_resources = {"coins": 2}
    state.board.action_spaces["realtor"] = realtor

    server = _make_server(state)
    conn = _make_conn("p1")
    place_msg = MagicMock()
    place_msg.space_id = "realtor"

    asyncio.run(handle_place_worker(server, conn, place_msg))

    # Landing collects the placed coins immediately and clears the space...
    assert player.resources.coins == 3
    assert realtor.placed_resources == {}
    placed_call = next(
        c
        for c in server.broadcast_to_game.call_args_list
        if c.args[1].action == "worker_placed"
    )
    assert placed_call.args[1].collected_placed_resources == {"coins": 2}

    # ...but cancelling must give the coins back to the space, not the player.
    server.broadcast_to_game.reset_mock()
    cancel_conn = _make_conn("p1")
    cancel_msg = MagicMock()
    asyncio.run(handle_cancel_purchase_building(server, cancel_conn, cancel_msg))

    assert player.resources.coins == 1
    assert realtor.placed_resources == {"coins": 2}

    server.broadcast_to_game.assert_called_once()
    _, response = server.broadcast_to_game.call_args[0]
    assert response.action == "placement_cancelled"
    assert response.restored_placed_resources == {"coins": 2}
