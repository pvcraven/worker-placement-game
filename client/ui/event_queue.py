"""Sequential event queue for animations, dialogs, and sounds."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import arcade

if TYPE_CHECKING:
    from client.views.game_view import GameView


class QueuedEvent:
    """Base class for events processed by the EventQueue."""

    def __init__(self) -> None:
        self.started = False

    def start(self, game_view: GameView) -> None:
        self.started = True

    def is_complete(self) -> bool:
        return False

    def update(self, dt: float) -> None:
        pass


class AnimationEvent(QueuedEvent):
    """Plays one or more animations; completes when the final on_complete fires."""

    def __init__(self, setup_fn: Callable[[GameView], None]) -> None:
        super().__init__()
        self.setup_fn = setup_fn
        self.done = False

    def start(self, game_view: GameView) -> None:
        super().start(game_view)
        self.setup_fn(game_view)

    def is_complete(self) -> bool:
        return self.done


class DialogEvent(QueuedEvent):
    """Shows a dialog; completes when the dialog callback sets done = True."""

    def __init__(
        self,
        show_fn: Callable[[GameView], None],
        sound: arcade.Sound | None = None,
    ) -> None:
        super().__init__()
        self.show_fn = show_fn
        self.done = False
        self.sound = sound

    def start(self, game_view: GameView) -> None:
        super().start(game_view)
        if self.sound:
            arcade.play_sound(self.sound)
        self.show_fn(game_view)

    def is_complete(self) -> bool:
        return self.done


class SoundEvent(QueuedEvent):
    """Plays a sound and waits for a specified duration."""

    def __init__(self, sound: arcade.Sound, duration: float) -> None:
        super().__init__()
        self.sound = sound
        self.duration = duration
        self.elapsed = 0.0

    def start(self, game_view: GameView) -> None:
        super().start(game_view)
        arcade.play_sound(self.sound)

    def is_complete(self) -> bool:
        return self.elapsed >= self.duration

    def update(self, dt: float) -> None:
        if self.started:
            self.elapsed += dt


class EventQueue:
    """Processes queued events one at a time in FIFO order."""

    def __init__(self) -> None:
        self._queue: list[QueuedEvent] = []
        self._current: QueuedEvent | None = None

    def enqueue(self, event: QueuedEvent, game_view: GameView) -> None:
        if self._current is None:
            self._current = event
            event.start(game_view)
        else:
            self._queue.append(event)

    def update(self, dt: float, game_view: GameView) -> None:
        if self._current is None:
            return
        self._current.update(dt)
        if self._current.is_complete():
            self._current = None
            if self._queue:
                self._current = self._queue.pop(0)
                self._current.start(game_view)

    def is_busy(self) -> bool:
        return self._current is not None
