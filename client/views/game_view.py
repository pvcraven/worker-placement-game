"""Main game view: board, worker placement, resource display, game log."""

from __future__ import annotations

import arcade
import arcade.gui

from client.ui.board_renderer import BoardRenderer
from client.ui.game_log import GameLogPanel
from client.ui.resource_bar import ResourceBar


class GameView(arcade.View):
    """Primary gameplay screen — worker placement and game interaction."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = arcade.gui.UIManager()
        self.game_state: dict = {}
        self.board_renderer: BoardRenderer | None = None
        self.resource_bar: ResourceBar | None = None
        self.game_log_panel: GameLogPanel | None = None
        self._setup_done = False
        self._status_text = ""

    def on_show_view(self) -> None:
        self.ui.enable()
        self.game_state = getattr(self.window, "game_state", {})
        if not self._setup_done:
            self._build_ui()
            self._setup_done = True
        self._sync_from_state()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def _build_ui(self) -> None:
        self.board_renderer = BoardRenderer()
        self.resource_bar = ResourceBar()
        self.game_log_panel = GameLogPanel()

    def _sync_from_state(self) -> None:
        """Update UI components from current game state."""
        if not self.game_state:
            return

        my_id = getattr(self.window, "player_id", None)
        players = self.game_state.get("players", [])
        board = self.game_state.get("board", {})

        # Find my player data
        my_player = None
        for p in players:
            if p.get("player_id") == my_id:
                my_player = p
                break

        if my_player and self.resource_bar:
            self.resource_bar.update_resources(my_player.get("resources", {}))

        if self.board_renderer:
            self.board_renderer.update_board(board, players)

        # Update turn indicator
        turn_order = self.game_state.get("turn_order", [])
        idx = self.game_state.get("current_player_index", 0)
        current_round = self.game_state.get("current_round", 0)
        if turn_order and idx < len(turn_order):
            current_pid = turn_order[idx]
            current_name = "Unknown"
            for p in players:
                if p.get("player_id") == current_pid:
                    current_name = p.get("display_name", "Unknown")
            is_my_turn = current_pid == my_id
            if is_my_turn:
                self._status_text = f"Round {current_round} — YOUR TURN"
            else:
                self._status_text = f"Round {current_round} — {current_name}'s turn"

    def on_update(self, delta_time: float) -> None:
        """Poll network and process messages."""
        network = self.window.network
        for msg in network.poll():
            self._handle_message(msg)

    def _handle_message(self, msg: dict) -> None:
        action = msg.get("action")

        if action == "worker_placed":
            self._on_worker_placed(msg)
        elif action == "worker_placed_garage":
            self._on_worker_placed_garage(msg)
        elif action == "quest_completed":
            self._on_quest_completed(msg)
        elif action == "contract_acquired":
            self._on_contract_acquired(msg)
        elif action == "building_constructed":
            self._on_building_constructed(msg)
        elif action == "reassignment_phase_start":
            self._status_text = "Reassignment Phase"
        elif action == "worker_reassigned":
            self._on_worker_reassigned(msg)
        elif action == "round_end":
            self._on_round_end(msg)
        elif action == "bonus_workers_granted":
            self._on_bonus_workers(msg)
        elif action == "game_over":
            self.window.final_scores = msg.get("final_scores", [])
            self.window.tiebreaker = msg.get("tiebreaker_applied", False)
            self.window.show_results()
        elif action == "state_sync":
            self.game_state = msg.get("game_state", {})
            self._sync_from_state()
        elif action == "player_disconnected":
            name = msg.get("player_name", "???")
            if self.game_log_panel:
                self.game_log_panel.add_entry(f"{name} disconnected")
        elif action == "player_reconnected":
            name = msg.get("player_name", "???")
            if self.game_log_panel:
                self.game_log_panel.add_entry(f"{name} reconnected")
        elif action == "turn_timeout":
            name = msg.get("player_name", "???")
            if self.game_log_panel:
                self.game_log_panel.add_entry(f"{name}'s turn was skipped (timeout)")
        elif action == "error":
            self._status_text = msg.get("message", "Error")

    def _on_worker_placed(self, msg: dict) -> None:
        space_id = msg.get("space_id", "")
        pid = msg.get("player_id", "")
        reward = msg.get("reward_granted", {})

        # Update local state
        board = self.game_state.get("board", {})
        spaces = board.get("action_spaces", {})
        if space_id in spaces:
            spaces[space_id]["occupied_by"] = pid

        # Update player resources
        self._apply_reward_to_player(pid, reward)

        # Update turn
        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.game_log_panel:
            name = self._player_name(pid)
            space_name = spaces.get(space_id, {}).get("name", space_id)
            self.game_log_panel.add_entry(f"{name} placed worker on {space_name}")

    def _on_worker_placed_garage(self, msg: dict) -> None:
        slot = msg.get("slot_number", 0)
        pid = msg.get("player_id", "")
        card = msg.get("intrigue_card", {})

        if self.game_log_panel:
            name = self._player_name(pid)
            card_name = card.get("name", "?")
            self.game_log_panel.add_entry(
                f"{name} placed worker on Garage slot {slot}, played {card_name}"
            )

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

    def _on_quest_completed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        cname = msg.get("contract_name", "?")
        vp = msg.get("victory_points_earned", 0)

        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(f"{name} completed '{cname}' for {vp} VP")

    def _on_contract_acquired(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(f"{name} acquired a contract")

    def _on_building_constructed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        bname = msg.get("building_name", "?")
        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(f"{name} built {bname}")

    def _on_worker_reassigned(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        slot = msg.get("from_slot", 0)
        to_space = msg.get("to_space_id", "")
        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(
                f"{name} reassigned from Garage slot {slot} to {to_space}"
            )

    def _on_round_end(self, msg: dict) -> None:
        next_round = msg.get("next_round", 0)
        bonus = msg.get("bonus_worker_granted", False)
        self.game_state["current_round"] = next_round
        self.game_state["current_player_index"] = 0
        self._status_text = f"Round {next_round}"
        if self.game_log_panel:
            self.game_log_panel.add_entry(f"--- Round {next_round} ---")
            if bonus:
                self.game_log_panel.add_entry("All players gained a bonus worker!")

    def _on_bonus_workers(self, msg: dict) -> None:
        new_count = msg.get("new_worker_count", 0)
        if self.game_log_panel:
            self.game_log_panel.add_entry(
                f"Round 5: All players now have {new_count} workers!"
            )

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Handle clicks on the board to place workers."""
        if not self.board_renderer:
            return

        my_id = getattr(self.window, "player_id", None)
        turn_order = self.game_state.get("turn_order", [])
        idx = self.game_state.get("current_player_index", 0)
        if not turn_order or idx >= len(turn_order):
            return
        if turn_order[idx] != my_id:
            return  # Not my turn

        space_id = self.board_renderer.get_space_at(x, y)
        if space_id:
            self.window.network.send({
                "action": "place_worker",
                "space_id": space_id,
            })

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def on_draw(self) -> None:
        self.clear()

        w, h = self.window.width, self.window.height

        if self.board_renderer:
            self.board_renderer.draw(0, 100, w, h - 160)

        if self.resource_bar:
            self.resource_bar.draw(0, 0, w, 100)

        if self.game_log_panel:
            self.game_log_panel.draw(w - 300, 100, 300, h - 160)

        # Status bar
        arcade.draw_rect_filled(
            arcade.rect.XYWH(w / 2, h - 25, w, 50),
            arcade.color.BLACK,
        )
        arcade.draw_text(
            self._status_text,
            w / 2, h - 25,
            arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
        )

        self.ui.draw()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _player_name(self, player_id: str) -> str:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                return p.get("display_name", "???")
        return "???"

    def _apply_reward_to_player(self, player_id: str, reward: dict) -> None:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                res = p.get("resources", {})
                for key in ("guitarists", "bass_players", "drummers", "singers", "coins"):
                    res[key] = res.get(key, 0) + reward.get(key, 0)
                my_id = getattr(self.window, "player_id", None)
                if player_id == my_id and self.resource_bar:
                    self.resource_bar.update_resources(res)
                break

    def _update_current_player(self, next_pid: str | None) -> None:
        if next_pid is None:
            return
        turn_order = self.game_state.get("turn_order", [])
        if next_pid in turn_order:
            self.game_state["current_player_index"] = turn_order.index(next_pid)
        my_id = getattr(self.window, "player_id", None)
        if next_pid == my_id:
            self._status_text = f"Round {self.game_state.get('current_round', '?')} — YOUR TURN"
        else:
            name = self._player_name(next_pid)
            self._status_text = f"Round {self.game_state.get('current_round', '?')} — {name}'s turn"
