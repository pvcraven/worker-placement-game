"""Reusable sprite animation manager using arcade easing functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import arcade
from arcade.anim import Easing, ease


@dataclass
class EaseAnimation:
    sprite: arcade.Sprite
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    start_time: float
    duration: float
    easing: Easing = Easing.SINE
    start_scale: float | None = None
    end_scale: float | None = None
    sound: arcade.Sound | None = None
    on_complete: Callable[[], None] | None = None
    _sound_played: bool = field(default=False, repr=False)


class AnimationManager:
    """Manages a collection of active sprite animations."""

    def __init__(self) -> None:
        self._animations: list[EaseAnimation] = []
        self._sprite_list: arcade.SpriteList = arcade.SpriteList()
        self._elapsed: float = 0.0

    def animate(
        self,
        sprite: arcade.Sprite,
        start: tuple[float, float],
        end: tuple[float, float],
        duration: float = 1.0,
        easing: Easing = Easing.SINE,
        start_scale: float | None = None,
        end_scale: float | None = None,
        sound: arcade.Sound | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        sprite.position = start
        if start_scale is not None:
            sprite.scale = start_scale
        anim = EaseAnimation(
            sprite=sprite,
            start_x=start[0],
            start_y=start[1],
            end_x=end[0],
            end_y=end[1],
            start_time=self._elapsed,
            duration=duration,
            easing=easing,
            start_scale=start_scale,
            end_scale=end_scale,
            sound=sound,
            on_complete=on_complete,
        )
        self._animations.append(anim)
        self._sprite_list.append(sprite)
        if sound:
            arcade.play_sound(sound)
            anim._sound_played = True

    def update(self, delta_time: float) -> None:
        self._elapsed += delta_time
        completed: list[EaseAnimation] = []
        for anim in self._animations:
            end_time = anim.start_time + anim.duration
            if self._elapsed >= end_time:
                anim.sprite.position = (anim.end_x, anim.end_y)
                if anim.end_scale is not None:
                    anim.sprite.scale = anim.end_scale
                completed.append(anim)
            else:
                x = ease(
                    anim.start_x,
                    anim.end_x,
                    anim.start_time,
                    end_time,
                    self._elapsed,
                    func=anim.easing,
                )
                y = ease(
                    anim.start_y,
                    anim.end_y,
                    anim.start_time,
                    end_time,
                    self._elapsed,
                    func=anim.easing,
                )
                anim.sprite.position = (x, y)
                if anim.start_scale is not None and anim.end_scale is not None:
                    anim.sprite.scale = ease(
                        anim.start_scale,
                        anim.end_scale,
                        anim.start_time,
                        end_time,
                        self._elapsed,
                        func=anim.easing,
                    )

        for anim in completed:
            anim.sprite.remove_from_sprite_lists()
            self._animations.remove(anim)
            if anim.on_complete:
                anim.on_complete()

    def draw(self) -> None:
        self._sprite_list.draw()

    def clear(self) -> None:
        for anim in self._animations:
            anim.sprite.remove_from_sprite_lists()
        self._animations.clear()
