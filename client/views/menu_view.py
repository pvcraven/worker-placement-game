"""Main menu view: Create Game / Join Game."""

from __future__ import annotations

import arcade
import arcade.gui

_BTN_STYLE = {
    "normal": arcade.gui.UIFlatButton.UIStyle(
        font_size=18,
        font_name=("Arial",),
        font_color=arcade.color.WHITE,
        bg=(44, 62, 80, 255),
        border=None,
        border_width=0,
    ),
    "hover": arcade.gui.UIFlatButton.UIStyle(
        font_size=18,
        font_name=("Arial",),
        font_color=arcade.color.WHITE,
        bg=(52, 73, 94, 255),
        border=(149, 165, 166, 255),
        border_width=2,
    ),
    "press": arcade.gui.UIFlatButton.UIStyle(
        font_size=18,
        font_name=("Arial",),
        font_color=(44, 62, 80, 255),
        bg=(236, 240, 241, 255),
        border=(149, 165, 166, 255),
        border_width=2,
    ),
    "disabled": arcade.gui.UIFlatButton.UIStyle(
        font_size=18,
        font_name=("Arial",),
        font_color=(189, 195, 199, 255),
        bg=(127, 140, 141, 255),
        border=None,
        border_width=0,
    ),
}


class MenuView(arcade.View):
    """Main menu with Create Game and Join Game options."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = arcade.gui.UIManager()
        self._setup_done = False

    def on_show_view(self) -> None:
        self.ui.enable()
        if not self._setup_done:
            self._build_ui()
            self._setup_done = True

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.RETURN or key == arcade.key.ENTER:
            if self.code_input.text.strip():
                self._on_join(None)

    def on_hide_view(self) -> None:
        self.ui.disable()

    def _build_ui(self) -> None:
        self.ui.clear()

        v_box = arcade.gui.UIBoxLayout(space_between=15)

        # Title
        title = arcade.gui.UILabel(
            text="Record Label",
            font_size=48,
            text_color=arcade.color.WHITE,
            bold=True,
            align="center",
        )
        v_box.add(title)

        subtitle = arcade.gui.UILabel(
            text="A Worker Placement Game",
            font_size=20,
            text_color=arcade.color.LIGHT_GRAY,
            bold=True,
            align="center",
        )
        v_box.add(subtitle)

        spacer = arcade.gui.UISpace(height=30)
        v_box.add(spacer)

        # Player name input
        name_label = arcade.gui.UILabel(
            text="Your Label Name:",
            font_size=18,
            text_color=arcade.color.WHITE,
            bold=True,
        )
        v_box.add(name_label)

        _input_s = arcade.gui.UIInputText.UIStyle(
            bg=arcade.color.WHITE,
            border=arcade.color.WHITE,
            border_width=2,
        )
        input_style = {
            "normal": _input_s,
            "hover": _input_s,
            "press": _input_s,
            "disabled": _input_s,
        }
        self.name_input = arcade.gui.UIInputText(
            text=getattr(self.window, "player_name", "") or "",
            width=350,
            height=45,
            font_size=16,
            text_color=arcade.color.BLACK,
            caret_color=arcade.color.BLACK,
            style=input_style,
        )
        v_box.add(self.name_input)

        spacer2 = arcade.gui.UISpace(height=15)
        v_box.add(spacer2)

        # Create Game button
        create_btn = arcade.gui.UIFlatButton(
            text="Create Game", width=350, height=55, style=_BTN_STYLE
        )
        create_btn.on_click = self._on_create
        v_box.add(create_btn)

        # Join Game section
        code_label = arcade.gui.UILabel(
            text="Game Code:",
            font_size=18,
            text_color=arcade.color.WHITE,
            bold=True,
        )
        v_box.add(code_label)

        self.code_input = arcade.gui.UIInputText(
            text="",
            width=350,
            height=45,
            font_size=16,
            text_color=arcade.color.BLACK,
            caret_color=arcade.color.BLACK,
            style=input_style,
        )
        v_box.add(self.code_input)

        join_btn = arcade.gui.UIFlatButton(
            text="Join Game", width=350, height=55, style=_BTN_STYLE
        )
        join_btn.on_click = self._on_join
        v_box.add(join_btn)

        # Server address
        server_label = arcade.gui.UILabel(
            text="Server:",
            font_size=14,
            text_color=arcade.color.GRAY,
            bold=True,
        )
        v_box.add(server_label)

        _server_s = arcade.gui.UIInputText.UIStyle(
            bg=arcade.color.WHITE_SMOKE,
            border=arcade.color.WHITE_SMOKE,
            border_width=2,
        )
        server_style = {
            "normal": _server_s,
            "hover": _server_s,
            "press": _server_s,
            "disabled": _server_s,
        }
        self.server_input = arcade.gui.UIInputText(
            text=getattr(self.window, "network", None)
            and self.window.network.server_url
            or "ws://localhost:8765",
            width=350,
            height=35,
            font_size=14,
            text_color=arcade.color.BLACK,
            caret_color=arcade.color.BLACK,
            style=server_style,
        )
        v_box.add(self.server_input)

        self.status_label = arcade.gui.UILabel(
            text="",
            font_size=14,
            text_color=arcade.color.YELLOW,
            bold=True,
        )
        v_box.add(self.status_label)

        anchor = self.ui.add(arcade.gui.UIAnchorLayout())
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")

    def _on_create(self, event) -> None:
        name = self.name_input.text.strip()
        if not name:
            self.status_label.text = "Please enter a label name."
            return

        server = self.server_input.text.strip()
        self.window.player_name = name
        network = self.window.network
        network.server_url = server
        network.connect()

        from client.user_config import save_config

        save_config(name=name, server=server)
        network.send(
            {
                "action": "create_game",
                "player_name": name,
                "max_players": 4,
            }
        )
        self.status_label.text = "Creating game..."

    def _on_join(self, event) -> None:
        name = self.name_input.text.strip()
        code = self.code_input.text.strip().upper()
        if not name:
            self.status_label.text = "Please enter a label name."
            return
        if not code:
            self.status_label.text = "Please enter a game code."
            return

        server = self.server_input.text.strip()
        self.window.player_name = name
        self.window.game_code = code
        network = self.window.network
        network.server_url = server
        network.connect()

        from client.user_config import save_config

        save_config(name=name, server=server)
        network.send(
            {
                "action": "join_game",
                "game_code": code,
                "player_name": name,
            }
        )
        self.status_label.text = "Joining game..."

    def on_update(self, delta_time: float) -> None:
        """Poll network for responses."""
        network = self.window.network
        for msg in network.poll():
            action = msg.get("action")
            if action == "game_created":
                self.window.player_id = msg["player_id"]
                self.window.game_code = msg["game_code"]
                self.window.show_lobby()
            elif action == "player_joined":
                self.window.show_lobby()
            elif action == "error":
                self.status_label.text = msg.get("message", "Error")

    def on_draw(self) -> None:
        self.clear()
        self.ui.draw()
