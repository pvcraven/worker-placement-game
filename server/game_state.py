"""Game session management: create, find, and clean up game sessions."""

from __future__ import annotations

import logging
import random
import time

from server.models.game import GameState

logger = logging.getLogger(__name__)

_CODE_LENGTH = 3
_CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def _generate_game_code() -> str:
    return "".join(random.choices(_CODE_CHARS, k=_CODE_LENGTH))


class SessionManager:
    """Manages all active game sessions."""

    def __init__(self) -> None:
        self.sessions: dict[str, GameState] = {}  # game_code -> GameState

    def create_session(self, max_players: int) -> GameState:
        """Create a new game session with a unique game code."""
        while True:
            code = _generate_game_code()
            if code not in self.sessions:
                break

        game_id = f"game_{code}_{int(time.time())}"
        state = GameState(
            game_id=game_id,
            game_code=code,
            max_players=max_players,
            created_at=time.time(),
            last_activity=time.time(),
        )
        self.sessions[code] = state
        logger.info(
            "Created session %s (code: %s, max: %d)", game_id, code, max_players
        )
        return state

    def get_session(self, game_code: str) -> GameState | None:
        return self.sessions.get(game_code)

    def remove_session(self, game_code: str) -> None:
        removed = self.sessions.pop(game_code, None)
        if removed:
            logger.info("Removed session %s", removed.game_id)

    def cleanup_expired(self, timeout_seconds: int) -> list[str]:
        """Remove sessions that have been inactive past the timeout.

        Returns list of removed game codes.
        """
        now = time.time()
        expired = []
        for code, state in list(self.sessions.items()):
            if now - state.last_activity > timeout_seconds:
                all_disconnected = all(not p.is_connected for p in state.players)
                if all_disconnected or not state.players:
                    expired.append(code)
                    self.remove_session(code)
        return expired

    @property
    def active_count(self) -> int:
        return len(self.sessions)
