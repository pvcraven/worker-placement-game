"""Test that reassignment is blocked while waiting for quest completion."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from server.game_engine import handle_reassign_worker
from server.models.game import (
    ActionSpace,
    BackstageSlot,
    BoardState,
    GameState,
    Player,
    PlayerResources,
)
from shared.card_models import ContractCard, ResourceCost
from shared.constants import GamePhase


def _make_player(name: str, pid: str) -> Player:
    return Player(
        player_id=pid,
        display_name=name,
        slot_index=0,
        resources=PlayerResources(
            guitarists=1, bass_players=3, singers=1, coins=10
        ),
    )


def _make_state() -> GameState:
    paul = _make_player("Paul", "paul")
    pat = _make_player("Pat", "pat")

    paul.contract_hand = [
        ContractCard(
            id="quest_1",
            name="A&R Talent Scout",
            description="test",
            genre="pop",
            cost=ResourceCost(bass_players=3, singers=1, coins=2),
            victory_points=7,
        ),
    ]

    state = GameState(
        game_code="TST",
        game_id="game_TST_1",
        max_players=2,
    )
    state.phase = GamePhase.REASSIGNMENT
    state.players = [paul, pat]
    state.turn_order = ["paul", "pat"]

    state.board = BoardState(
        action_spaces={
            "talent_show": ActionSpace(
                space_id="talent_show",
                name="Talent Show",
                space_type="permanent",
                reward=ResourceCost(singers=1),
            ),
            "jam_session": ActionSpace(
                space_id="jam_session",
                name="The Jam Session",
                space_type="permanent",
                reward=ResourceCost(guitarists=1),
            ),
        },
        backstage_slots=[
            BackstageSlot(slot_number=1, occupied_by="paul"),
            BackstageSlot(slot_number=2, occupied_by="pat"),
        ],
    )
    state.reassignment_queue = [1, 2]
    return state


def _make_server(state: GameState) -> MagicMock:
    server = MagicMock()
    server.session_manager.get_session.return_value = state
    server.broadcast_to_game = AsyncMock()
    server.send_to_player = AsyncMock()
    return server


def _make_conn(pid: str, game_code: str = "TST") -> MagicMock:
    conn = MagicMock()
    conn.player_id = pid
    conn.game_code = game_code
    conn.send_model = AsyncMock()
    conn.send_error = AsyncMock()
    return conn


def _make_msg(slot: int, target: str) -> MagicMock:
    msg = MagicMock()
    msg.slot_number = slot
    msg.target_space_id = target
    return msg


def test_reassign_blocked_while_waiting_for_quest_completion():
    """Pat cannot reassign while server waits for Paul's quest completion."""
    state = _make_state()
    server = _make_server(state)
    pat_conn = _make_conn("pat")
    pat_msg = _make_msg(slot=2, target="jam_session")

    # Simulate: Paul already reassigned, quest completion prompt sent
    state.reassignment_queue = [2]  # Paul's slot already popped
    state.waiting_for_quest_completion = True
    state.reassignment_active_player_id = None

    asyncio.run(handle_reassign_worker(server, pat_conn, pat_msg))

    pat_conn.send_error.assert_called_once()
    error_code = pat_conn.send_error.call_args[0][0]
    assert error_code == "INVALID_ACTION"
    assert "quest completion" in pat_conn.send_error.call_args[0][1].lower()


def test_reassign_proceeds_after_quest_completion_resolved():
    """Pat can reassign after Paul's quest completion is resolved."""
    state = _make_state()
    server = _make_server(state)
    pat_conn = _make_conn("pat")
    pat_msg = _make_msg(slot=2, target="jam_session")

    state.reassignment_queue = [2]
    state.waiting_for_quest_completion = False
    state.reassignment_active_player_id = None

    pat = state.get_player("pat")
    guitars_before = pat.resources.guitarists

    asyncio.run(handle_reassign_worker(server, pat_conn, pat_msg))

    pat_conn.send_error.assert_not_called()
    assert pat.resources.guitarists == guitars_before + 1
