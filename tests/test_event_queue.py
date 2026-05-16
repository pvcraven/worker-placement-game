"""Unit tests for EventQueue sequential processing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from client.ui.event_queue import (
    AnimationEvent,
    DialogEvent,
    EventQueue,
    QueuedEvent,
    SoundEvent,
)


def _make_game_view() -> MagicMock:
    return MagicMock()


class TestQueuedEvent:
    def test_starts_not_started(self) -> None:
        event = QueuedEvent()
        assert not event.started

    def test_start_sets_started(self) -> None:
        gv = _make_game_view()
        event = QueuedEvent()
        event.start(gv)
        assert event.started

    def test_is_complete_returns_false(self) -> None:
        event = QueuedEvent()
        assert not event.is_complete()


class TestAnimationEvent:
    def test_start_calls_setup_fn(self) -> None:
        gv = _make_game_view()
        called = []
        event = AnimationEvent(setup_fn=lambda g: called.append(True))
        event.start(gv)
        assert called == [True]

    def test_not_complete_until_done(self) -> None:
        event = AnimationEvent(setup_fn=lambda g: None)
        assert not event.is_complete()
        event.done = True
        assert event.is_complete()


class TestDialogEvent:
    def test_start_calls_show_fn(self) -> None:
        gv = _make_game_view()
        called = []
        event = DialogEvent(show_fn=lambda g: called.append(True))
        event.start(gv)
        assert called == [True]

    def test_not_complete_until_done(self) -> None:
        event = DialogEvent(show_fn=lambda g: None)
        assert not event.is_complete()
        event.done = True
        assert event.is_complete()

    def test_sound_plays_on_start(self) -> None:
        gv = _make_game_view()
        sound = MagicMock()
        event = DialogEvent(show_fn=lambda g: None, sound=sound)
        mock_arcade = MagicMock()
        with patch.dict("sys.modules", {"arcade": mock_arcade}):
            event.start(gv)
        mock_arcade.play_sound.assert_called_once_with(sound)


class TestSoundEvent:
    def test_completes_after_duration(self) -> None:
        sound = MagicMock()
        event = SoundEvent(sound=sound, duration=1.0)
        gv = _make_game_view()
        mock_arcade = MagicMock()
        with patch.dict("sys.modules", {"arcade": mock_arcade}):
            event.start(gv)
        mock_arcade.play_sound.assert_called_once_with(sound)
        assert not event.is_complete()
        event.update(0.5)
        assert not event.is_complete()
        event.update(0.6)
        assert event.is_complete()


class TestEventQueue:
    def test_enqueue_starts_immediately_when_idle(self) -> None:
        gv = _make_game_view()
        queue = EventQueue()
        called = []
        event = AnimationEvent(setup_fn=lambda g: called.append(True))
        queue.enqueue(event, gv)
        assert called == [True]
        assert queue.is_busy()

    def test_sequential_processing(self) -> None:
        gv = _make_game_view()
        queue = EventQueue()
        order = []
        e1 = AnimationEvent(setup_fn=lambda g: order.append("e1"))
        e2 = AnimationEvent(setup_fn=lambda g: order.append("e2"))
        e3 = AnimationEvent(setup_fn=lambda g: order.append("e3"))
        queue.enqueue(e1, gv)
        queue.enqueue(e2, gv)
        queue.enqueue(e3, gv)
        assert order == ["e1"]
        e1.done = True
        queue.update(0.016, gv)
        assert order == ["e1", "e2"]
        e2.done = True
        queue.update(0.016, gv)
        assert order == ["e1", "e2", "e3"]
        e3.done = True
        queue.update(0.016, gv)
        assert not queue.is_busy()

    def test_is_busy_false_when_empty(self) -> None:
        queue = EventQueue()
        assert not queue.is_busy()

    def test_is_busy_true_with_current(self) -> None:
        gv = _make_game_view()
        queue = EventQueue()
        event = AnimationEvent(setup_fn=lambda g: None)
        queue.enqueue(event, gv)
        assert queue.is_busy()

    def test_is_busy_true_with_pending(self) -> None:
        gv = _make_game_view()
        queue = EventQueue()
        e1 = AnimationEvent(setup_fn=lambda g: None)
        e2 = AnimationEvent(setup_fn=lambda g: None)
        queue.enqueue(e1, gv)
        queue.enqueue(e2, gv)
        assert queue.is_busy()

    def test_update_noop_when_idle(self) -> None:
        gv = _make_game_view()
        queue = EventQueue()
        queue.update(0.016, gv)
        assert not queue.is_busy()
