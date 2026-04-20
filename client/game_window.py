"""Base Arcade window with resize, fullscreen, and minimum size support."""

from __future__ import annotations

import arcade

# Design resolution — all layout is defined relative to this
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080
MIN_WIDTH = 1024
MIN_HEIGHT = 768
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080


class GameWindow(arcade.Window):
    """Main application window.  Manages view switching and scaling."""

    def __init__(
        self,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        fullscreen: bool = False,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            title="Record Label - Worker Placement Game",
            resizable=True,
            fullscreen=fullscreen,
            antialiasing=False,
            pixel_perfect=True,
        )
        self.scale_x: float = width / DESIGN_WIDTH
        self.scale_y: float = height / DESIGN_HEIGHT
        self.ui_scale: float = min(self.scale_x, self.scale_y)
        self.content_width: float = DESIGN_WIDTH * self.ui_scale
        self.content_height: float = DESIGN_HEIGHT * self.ui_scale
        self._too_small = False
        self.background_color = arcade.color.DARK_SLATE_GRAY

    # ------------------------------------------------------------------
    # Resize handling
    # ------------------------------------------------------------------

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._too_small = width < MIN_WIDTH or height < MIN_HEIGHT
        self.scale_x = width / DESIGN_WIDTH
        self.scale_y = height / DESIGN_HEIGHT
        self.ui_scale = min(self.scale_x, self.scale_y)
        self.content_width = DESIGN_WIDTH * self.ui_scale
        self.content_height = DESIGN_HEIGHT * self.ui_scale

    def on_draw(self) -> None:
        self.clear()
        if self._too_small:
            self._draw_too_small_overlay()
            return
        # Delegate to current view
        if self.current_view:
            self.current_view.on_draw()

    def _draw_too_small_overlay(self) -> None:
        """Show a message when the window is below minimum size."""
        arcade.draw_text(
            "Window too small.\nPlease resize to at least 1024x768.",
            self.width / 2,
            self.height / 2,
            arcade.color.WHITE,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=self.width - 40,
            align="center",
        )

    # ------------------------------------------------------------------
    # View management
    # ------------------------------------------------------------------

    def show_menu(self) -> None:
        from client.views.menu_view import MenuView
        self.show_view(MenuView())

    def show_lobby(self) -> None:
        from client.views.lobby_view import LobbyView
        self.show_view(LobbyView())

    def show_game(self) -> None:
        from client.views.game_view import GameView
        self.show_view(GameView())

    def show_results(self) -> None:
        from client.views.results_view import ResultsView
        self.show_view(ResultsView())
