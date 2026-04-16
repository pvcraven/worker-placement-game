"""Lobby view: player list, ready toggle, start game."""

from __future__ import annotations

import arcade
import arcade.gui


_BTN_STYLE = {
    "normal": arcade.gui.UIFlatButton.UIStyle(
        font_size=18, font_name=("Arial",), font_color=arcade.color.WHITE,
        bg=(44, 62, 80, 255), border=None, border_width=0,
    ),
    "hover": arcade.gui.UIFlatButton.UIStyle(
        font_size=18, font_name=("Arial",), font_color=arcade.color.WHITE,
        bg=(52, 73, 94, 255), border=(149, 165, 166, 255), border_width=2,
    ),
    "press": arcade.gui.UIFlatButton.UIStyle(
        font_size=18, font_name=("Arial",), font_color=(44, 62, 80, 255),
        bg=(236, 240, 241, 255), border=(149, 165, 166, 255), border_width=2,
    ),
    "disabled": arcade.gui.UIFlatButton.UIStyle(
        font_size=18, font_name=("Arial",), font_color=(189, 195, 199, 255),
        bg=(127, 140, 141, 255), border=None, border_width=0,
    ),
}


class LobbyView(arcade.View):
    """Waiting room before the game starts."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = arcade.gui.UIManager()
        self.players: list[dict] = []
        self._setup_done = False

    def on_show_view(self) -> None:
        self.ui.enable()
        if not self._setup_done:
            self._build_ui()
            self._setup_done = True

    def on_hide_view(self) -> None:
        self.ui.disable()

    def _build_ui(self) -> None:
        self.ui.clear()

        v_box = arcade.gui.UIBoxLayout(space_between=10)

        # Title
        title = arcade.gui.UILabel(
            text="Game Lobby",
            font_size=40,
            text_color=arcade.color.WHITE,
            bold=True,
            align="center",
        )
        v_box.add(title)

        # Game code display
        code = getattr(self.window, "game_code", "???")
        code_label = arcade.gui.UILabel(
            text=f"Game Code: {code}",
            font_size=24,
            text_color=arcade.color.YELLOW,
            bold=True,
            align="center",
        )
        v_box.add(code_label)

        spacer = arcade.gui.UISpace(height=20)
        v_box.add(spacer)

        # Player list label
        self.player_list_label = arcade.gui.UILabel(
            text="Waiting for players...",
            font_size=18,
            text_color=arcade.color.WHITE,
            bold=True,
            multiline=True,
            width=400,
        )
        v_box.add(self.player_list_label)

        spacer2 = arcade.gui.UISpace(height=20)
        v_box.add(spacer2)

        # Ready button
        self.ready_btn = arcade.gui.UIFlatButton(text="Ready", width=300, height=55, style=_BTN_STYLE)
        self.ready_btn.on_click = self._on_ready
        v_box.add(self.ready_btn)
        self._is_ready = False

        # Start button (host only)
        self.start_btn = arcade.gui.UIFlatButton(text="Start Game", width=300, height=55, style=_BTN_STYLE)
        self.start_btn.on_click = self._on_start
        v_box.add(self.start_btn)

        # Status
        self.status_label = arcade.gui.UILabel(
            text="",
            font_size=16,
            text_color=arcade.color.YELLOW,
            bold=True,
        )
        v_box.add(self.status_label)

        anchor = self.ui.add(arcade.gui.UIAnchorLayout())
        anchor.add(child=v_box, anchor_x="center", anchor_y="center")

    def _on_ready(self, event) -> None:
        self._is_ready = not self._is_ready
        self.ready_btn.text = "Unready" if self._is_ready else "Ready"
        self.window.network.send({
            "action": "player_ready",
            "ready": self._is_ready,
        })

    def _on_start(self, event) -> None:
        self.window.network.send({"action": "start_game"})
        self.status_label.text = "Starting game..."

    def _update_player_list(self) -> None:
        if not self.players:
            self.player_list_label.text = "Waiting for players..."
            return
        lines = []
        for p in self.players:
            ready = "READY" if p.get("ready", False) else "waiting"
            lines.append(f"  {p.get('name', '???')} [{ready}]")
        self.player_list_label.text = "Players:\n" + "\n".join(lines)

    def on_update(self, delta_time: float) -> None:
        network = self.window.network
        messages = network.poll()
        for i, msg in enumerate(messages):
            action = msg.get("action")
            if action == "player_joined":
                self.players = msg.get("players", [])
                self._update_player_list()
            elif action == "player_ready_update":
                pid = msg.get("player_id")
                ready = msg.get("ready", False)
                for p in self.players:
                    if p.get("player_id") == pid:
                        p["ready"] = ready
                self._update_player_list()
            elif action == "game_started":
                self.window.game_state = msg.get("game_state", {})
                self.window.show_game()
                for remaining in messages[i + 1:]:
                    network.incoming.put(remaining)
                return
            elif action == "error":
                self.status_label.text = msg.get("message", "Error")

    def on_draw(self) -> None:
        self.clear()
        self.ui.draw()
