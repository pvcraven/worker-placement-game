from enum import StrEnum


class ResourceType(StrEnum):
    GUITARIST = "guitarist"
    BASS_PLAYER = "bass_player"
    DRUMMER = "drummer"
    SINGER = "singer"


class Genre(StrEnum):
    JAZZ = "jazz"
    POP = "pop"
    SOUL = "soul"
    FUNK = "funk"
    ROCK = "rock"


class GamePhase(StrEnum):
    LOBBY = "lobby"
    PLACEMENT = "placement"
    REASSIGNMENT = "reassignment"
    ROUND_END = "round_end"
    GAME_OVER = "game_over"


RESOURCE_COLORS: dict[ResourceType, str] = {
    ResourceType.GUITARIST: "red",
    ResourceType.BASS_PLAYER: "black",
    ResourceType.DRUMMER: "white",
    ResourceType.SINGER: "purple",
}
COIN_COLOR = "gold"

MIN_PLAYERS = 1
MAX_PLAYERS = 5
TOTAL_ROUNDS = 8
BONUS_WORKER_ROUND = 5
TURN_TIMEOUT_SECONDS = 60
GAME_PRESERVE_TIMEOUT_SECONDS = 1800  # 30 minutes
FACE_UP_QUEST_COUNT = 4
FACE_UP_BUILDING_COUNT = 3
BACKSTAGE_SLOTS = 3

STARTING_WORKERS: dict[int, int] = {1: 4, 2: 4, 3: 3, 4: 2, 5: 2}
STARTING_INTRIGUE_CARDS = 2
STARTING_COINS_BASE = 4
STARTING_COINS_INCREMENT = 2

CARD_WIDTH = 190
CARD_HEIGHT = 230
BUILDING_CARD_HEIGHT = 170
SPACE_CARD_HEIGHT = 100

# Short labels for resource types, used in card rendering and UI
RESOURCE_SYMBOLS: list[tuple[str, str]] = [
    ("guitarists", "G"),
    ("bass_players", "B"),
    ("drummers", "D"),
    ("singers", "S"),
    ("coins", "$"),
]
