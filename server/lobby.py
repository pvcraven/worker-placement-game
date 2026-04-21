"""Lobby management: create, join, ready-up, start game, reconnect."""

from __future__ import annotations

import logging
import random
import time
import uuid
from typing import TYPE_CHECKING

from server.models.game import (
    ActionSpace,
    BackstageSlot,
    BoardState,
    GameLog,
    Player,
)
from shared.constants import (
    BACKSTAGE_SLOTS,
    FACE_UP_BUILDING_COUNT,
    FACE_UP_QUEST_COUNT,
    STARTING_COINS_BASE,
    STARTING_COINS_INCREMENT,
    STARTING_INTRIGUE_CARDS,
    STARTING_WORKERS,
    GamePhase,
)
from shared.messages import (
    BuildingMarketUpdateResponse,
    GameCreatedResponse,
    GameStartedResponse,
    LobbyPlayerInfo,
    PlayerJoinedResponse,
    PlayerReadyUpdateResponse,
    PlayerReconnectedResponse,
    StateSyncResponse,
)

if TYPE_CHECKING:
    from server.network import ClientConnection, GameServer

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Ready-tracking (in-memory, keyed by player_id)
# ------------------------------------------------------------------

_player_ready: dict[str, bool] = {}


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------


async def create_game(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle create_game: create session, add host player."""
    state = server.session_manager.create_session(msg.max_players)
    player_id = str(uuid.uuid4())
    player = Player(
        player_id=player_id,
        display_name=msg.player_name,
        slot_index=0,
    )
    state.players.append(player)
    state.host_player_id = player_id
    state.last_activity = time.time()

    server.register_connection(player_id, conn)
    conn.game_code = state.game_code
    _player_ready[player_id] = False

    await conn.send_model(
        GameCreatedResponse(
            game_code=state.game_code,
            player_id=player_id,
            slot_index=0,
        )
    )
    logger.info("Player '%s' created game %s", msg.player_name, state.game_code)


async def join_game(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle join_game: add player to existing session."""
    state = server.session_manager.get_session(msg.game_code)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "No game with that code.")
        return

    if state.phase != GamePhase.LOBBY:
        await conn.send_error("INVALID_ACTION", "Game already in progress.")
        return

    if len(state.players) >= state.max_players:
        await conn.send_error("LOBBY_FULL", "Game is full.")
        return

    player_id = str(uuid.uuid4())
    slot_index = len(state.players)
    player = Player(
        player_id=player_id,
        display_name=msg.player_name,
        slot_index=slot_index,
    )
    state.players.append(player)
    state.last_activity = time.time()

    server.register_connection(player_id, conn)
    conn.game_code = state.game_code
    _player_ready[player_id] = False

    # Send game_created to the joiner (with their ID)
    await conn.send_model(
        GameCreatedResponse(
            game_code=state.game_code,
            player_id=player_id,
            slot_index=slot_index,
        )
    )

    # Broadcast player_joined to everyone
    players_info = [
        LobbyPlayerInfo(
            player_id=p.player_id,
            name=p.display_name,
            slot_index=p.slot_index,
            ready=_player_ready.get(p.player_id, False),
        )
        for p in state.players
    ]
    await server.broadcast_to_game(
        state.game_code,
        PlayerJoinedResponse(
            player_name=msg.player_name,
            slot_index=slot_index,
            players=players_info,
        ),
    )
    logger.info(
        "Player '%s' joined game %s (slot %d)",
        msg.player_name,
        state.game_code,
        slot_index,
    )


async def player_ready(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle player_ready: toggle ready state."""
    if not conn.player_id or not conn.game_code:
        await conn.send_error("INVALID_ACTION", "Not in a game.")
        return

    _player_ready[conn.player_id] = msg.ready

    await server.broadcast_to_game(
        conn.game_code,
        PlayerReadyUpdateResponse(
            player_id=conn.player_id,
            ready=msg.ready,
        ),
    )


async def start_game(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle start_game: host starts the game."""
    if not conn.game_code:
        await conn.send_error("INVALID_ACTION", "Not in a game.")
        return

    state = server.session_manager.get_session(conn.game_code)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "Game not found.")
        return

    if conn.player_id != state.host_player_id:
        await conn.send_error("INVALID_ACTION", "Only the host can start the game.")
        return

    config = server.session_manager.config  # type: ignore[attr-defined]

    if len(state.players) < config.rules.min_players:
        await conn.send_error(
            "INVALID_ACTION",
            f"Need at least {config.rules.min_players} players.",
        )
        return

    # Check all players ready
    for p in state.players:
        if not _player_ready.get(p.player_id, False):
            await conn.send_error("INVALID_ACTION", "Not all players are ready.")
            return

    # --- Initialize the game ---
    _initialize_game(state, config)

    # Send game_started to each player with their filtered view
    for player in state.players:
        filtered = _filter_state_for_player(state, player.player_id)
        await server.send_to_player(
            player.player_id,
            GameStartedResponse(game_state=filtered),
        )

    # Broadcast initial building market
    await server.broadcast_to_game(
        state.game_code,
        BuildingMarketUpdateResponse(
            face_up_buildings=[b.model_dump() for b in state.board.face_up_buildings],
            deck_remaining=len(state.board.building_deck),
        ),
    )

    logger.info("Game %s started with %d players", state.game_code, len(state.players))


def _initialize_game(state, config) -> None:
    """Set up the game board, deal cards, assign workers."""
    player_count = len(state.players)
    workers = STARTING_WORKERS.get(player_count, 2)

    # Assign workers and producer cards
    producer_deck = list(config.producers)
    random.shuffle(producer_deck)
    for player in state.players:
        player.total_workers = workers
        player.available_workers = workers
        if producer_deck:
            player.producer_card = producer_deck.pop()

    state.producer_deck = producer_deck

    # Set up board from config
    board = BoardState()
    for space_cfg in config.board.permanent_spaces:
        board.action_spaces[space_cfg.space_id] = ActionSpace(
            space_id=space_cfg.space_id,
            name=space_cfg.name,
            space_type=space_cfg.space_type,
            reward=space_cfg.reward,
            reward_special=space_cfg.reward_special,
        )

    # Backstage slots
    board.backstage_slots = [
        BackstageSlot(slot_number=i) for i in range(1, BACKSTAGE_SLOTS + 1)
    ]

    # Building lots
    board.building_lots = [f"lot_{i}" for i in range(config.board.building_lot_count)]

    # Shuffle and deal quest cards (face-up quests at The Garage)
    quest_cards = list(config.contracts)
    random.shuffle(quest_cards)
    board.face_up_quests = quest_cards[:FACE_UP_QUEST_COUNT]
    board.quest_deck = quest_cards[FACE_UP_QUEST_COUNT:]

    intrigue_deck = list(config.intrigue_cards)
    random.shuffle(intrigue_deck)
    board.intrigue_deck = intrigue_deck

    all_buildings = list(config.buildings)
    random.shuffle(all_buildings)
    face_up = all_buildings[:FACE_UP_BUILDING_COUNT]
    board.face_up_buildings = face_up
    board.building_deck = all_buildings[FACE_UP_BUILDING_COUNT:]

    state.board = board

    # Deal starting intrigue cards and coins
    for i, player in enumerate(state.players):
        for _ in range(STARTING_INTRIGUE_CARDS):
            if board.intrigue_deck:
                player.intrigue_hand.append(board.intrigue_deck.pop())
        player.resources.coins = STARTING_COINS_BASE + (i * STARTING_COINS_INCREMENT)

    # First player is slot 0 by default
    state.board.first_player_id = state.players[0].player_id
    state.players[0].has_first_player_marker = True

    # Set turn order
    state.turn_order = [p.player_id for p in state.players]
    state.current_player_index = 0
    state.current_round = 1
    state.phase = GamePhase.PLACEMENT
    state.last_activity = time.time()

    state.game_log.append(
        GameLog(
            round_number=1,
            action="game_start",
            details=f"Game started with {player_count} players",
            timestamp=time.time(),
        )
    )


def _filter_state_for_player(state, player_id: str) -> dict:
    """Return a JSON-serializable dict of game state visible to this player."""
    data = state.model_dump()

    for p_data in data["players"]:
        if p_data["player_id"] != player_id:
            # Hide opponent's hand contents, show counts
            p_data["contract_hand_count"] = len(p_data["contract_hand"])
            p_data["contract_hand"] = []
            p_data["intrigue_hand_count"] = len(p_data["intrigue_hand"])
            p_data["intrigue_hand"] = []
            p_data["producer_card"] = None
        else:
            p_data["contract_hand_count"] = len(p_data["contract_hand"])
            p_data["intrigue_hand_count"] = len(p_data["intrigue_hand"])

    # Hide deck contents, show counts
    data["board"]["contract_deck_count"] = len(data["board"]["contract_deck"])
    data["board"]["contract_deck"] = []
    data["board"]["intrigue_deck_count"] = len(data["board"]["intrigue_deck"])
    data["board"]["intrigue_deck"] = []
    data["board"]["quest_deck_count"] = len(data["board"]["quest_deck"])
    data["board"]["quest_deck"] = []
    data["board"]["quest_discard"] = []
    data["board"]["building_deck_count"] = len(data["board"]["building_deck"])
    data["board"]["building_deck"] = []

    return data


async def reconnect(server: GameServer, conn: ClientConnection, msg) -> None:
    """Handle reconnect: rejoin an in-progress game."""
    state = server.session_manager.get_session(msg.game_code)
    if state is None:
        await conn.send_error("GAME_NOT_FOUND", "No game with that code.")
        return

    # Find matching player by name + slot
    player = None
    for p in state.players:
        if p.display_name == msg.player_name and p.slot_index == msg.slot_index:
            player = p
            break

    if player is None:
        await conn.send_error("INVALID_ACTION", "No matching player found.")
        return

    player.is_connected = True
    player.consecutive_timeouts = 0
    server.register_connection(player.player_id, conn)
    conn.game_code = state.game_code
    state.last_activity = time.time()

    # Send full state sync
    filtered = _filter_state_for_player(state, player.player_id)
    await conn.send_model(StateSyncResponse(game_state=filtered))

    # Notify others
    await server.broadcast_to_game(
        state.game_code,
        PlayerReconnectedResponse(
            player_id=player.player_id,
            player_name=player.display_name,
        ),
    )
    logger.info(
        "Player '%s' reconnected to game %s", player.display_name, state.game_code
    )
