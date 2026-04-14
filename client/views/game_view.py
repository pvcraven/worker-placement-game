"""Main game view: board, worker placement, resource display, game log."""

from __future__ import annotations

import arcade
import arcade.gui

from client.ui.board_renderer import BoardRenderer
from client.ui.card_renderer import CardRenderer
from client.ui.dialogs import BuildingPurchaseDialog, CardSelectionDialog
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
        self._quest_dialog: CardSelectionDialog | None = None
        self._building_dialog: BuildingPurchaseDialog | None = None
        self._face_up_buildings: list[dict] = []
        self._building_deck_remaining: int = 0
        self._show_quests_hand = False
        self._show_intrigue_hand = False
        self._text_cache: dict[str, arcade.Text] = {}

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

        # Hand toggle buttons
        quests_btn = arcade.gui.UIFlatButton(
            text="My Quests", width=120, height=32,
        )
        quests_btn.on_click = lambda _: self._toggle_quests()
        intrigue_btn = arcade.gui.UIFlatButton(
            text="My Intrigue", width=120, height=32,
        )
        intrigue_btn.on_click = lambda _: self._toggle_intrigue()

        btn_row = arcade.gui.UIBoxLayout(
            vertical=False, space_between=8,
        )
        btn_row.add(quests_btn)
        btn_row.add(intrigue_btn)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(
            child=btn_row,
            anchor_x="left",
            anchor_y="bottom",
            align_x=10,
            align_y=105,
        )
        self.ui.add(anchor)

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
                self._status_text = (
                    f"Round {current_round}"
                    f" — {current_name}'s turn"
                )

    def on_update(self, delta_time: float) -> None:
        """Poll network and process messages."""
        network = self.window.network
        for msg in network.poll():
            self._handle_message(msg)

    def _handle_message(self, msg: dict) -> None:
        action = msg.get("action")

        if action == "worker_placed":
            self._on_worker_placed(msg)
        elif action == "worker_placed_backstage":
            self._on_worker_placed_backstage(msg)
        elif action == "face_up_quests_updated":
            self._on_face_up_quests_updated(msg)
        elif action == "quest_card_selected":
            self._on_quest_card_selected(msg)
        elif action == "quests_reset":
            self._on_quests_reset(msg)
        elif action == "quest_completed":
            self._on_quest_completed(msg)
        elif action == "contract_acquired":
            self._on_contract_acquired(msg)
        elif action == "building_constructed":
            self._on_building_constructed(msg)
        elif action == "building_market_update":
            self._on_building_market_update(msg)
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
                self.game_log_panel.add_entry(
                    f"{name}'s turn was skipped (timeout)"
                )
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

        # Check if this is a garage spot requiring quest selection
        space_data = spaces.get(space_id, {})
        my_id = getattr(self.window, "player_id", None)
        if (
            space_data.get("space_type") == "garage"
            and pid == my_id
            and space_data.get("reward_special") in (
                "quest_and_coins", "quest_and_intrigue"
            )
        ):
            self._show_quest_selection_dialog()
            if self.game_log_panel:
                self.game_log_panel.add_entry(
                    "Select a quest card from the display"
                )
            return

        # Check if this is the Real Estate Listings spot for building purchase
        if (
            space_data.get("reward_special") == "purchase_building"
            and pid == my_id
        ):
            self._show_building_purchase_dialog()
            return

        # Update turn
        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.game_log_panel:
            name = self._player_name(pid)
            space_name = space_data.get("name", space_id)
            self.game_log_panel.add_entry(
                f"{name} placed worker on {space_name}"
            )

        # Owner bonus notification
        owner_bonus = msg.get("owner_bonus", {})
        if owner_bonus and self.game_log_panel:
            owner_name = owner_bonus.get("owner_name", "???")
            bonus = owner_bonus.get("bonus", {})
            bonus_parts = []
            for key, sym in [("guitarists", "G"), ("bass_players", "B"),
                             ("drummers", "D"), ("singers", "S"), ("coins", "$")]:
                val = bonus.get(key, 0)
                if val > 0:
                    bonus_parts.append(f"{val}{sym}")
            if bonus_parts:
                self.game_log_panel.add_entry(
                    f"{owner_name} earned owner bonus: {' '.join(bonus_parts)}"
                )

    def _on_worker_placed_backstage(self, msg: dict) -> None:
        slot = msg.get("slot_number", 0)
        pid = msg.get("player_id", "")
        card = msg.get("intrigue_card", {})

        if self.game_log_panel:
            name = self._player_name(pid)
            card_name = card.get("name", "?")
            self.game_log_panel.add_entry(
                f"{name} placed worker on Backstage"
                f" slot {slot}, played {card_name}"
            )

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

    def _show_quest_selection_dialog(self) -> None:
        """Show dialog for selecting a face-up quest card."""
        board = self.game_state.get("board", {})
        quests = board.get("face_up_quests", [])
        if not quests:
            return

        def on_select(card_id: str) -> None:
            self._quest_dialog = None
            self.window.network.send({
                "action": "select_quest_card",
                "card_id": card_id,
            })

        self._quest_dialog = CardSelectionDialog(
            title="Select a Quest Card",
            cards=quests,
            on_select=on_select,
            ui_manager=self.ui,
        )
        self._quest_dialog.show(
            self.window.width, self.window.height
        )

    def _show_building_purchase_dialog(self) -> None:
        """Show dialog for purchasing a face-up building."""
        # Get player's current coins
        my_id = getattr(self.window, "player_id", None)
        player_coins = 0
        for p in self.game_state.get("players", []):
            if p.get("player_id") == my_id:
                player_coins = p.get("resources", {}).get("coins", 0)
                break

        def on_purchase(building_id: str) -> None:
            self._building_dialog = None
            self.window.network.send({
                "action": "purchase_building",
                "building_id": building_id,
            })

        def on_cancel() -> None:
            self._building_dialog = None
            if self.game_log_panel:
                self.game_log_panel.add_entry("Building purchase cancelled")

        self._building_dialog = BuildingPurchaseDialog(
            buildings=self._face_up_buildings,
            player_coins=player_coins,
            on_purchase=on_purchase,
            on_cancel=on_cancel,
            ui_manager=self.ui,
        )
        self._building_dialog.show(
            self.window.width, self.window.height,
        )

    def _on_quest_card_selected(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        card_id = msg.get("card_id", "")
        bonus = msg.get("bonus_reward", {})

        # Move the card from face-up quests into the player's hand
        board = self.game_state.get("board", {})
        face_up = board.get("face_up_quests", [])
        selected_card = None
        for q in face_up:
            if q.get("id") == card_id:
                selected_card = q
                break
        if selected_card:
            for p in self.game_state.get("players", []):
                if p.get("player_id") == pid:
                    p.setdefault("contract_hand", []).append(
                        selected_card
                    )
                    break

        # Apply bonus to local state
        if bonus.get("coins"):
            self._apply_reward_to_player(
                pid, {"coins": bonus["coins"]}
            )
        if bonus.get("intrigue_card"):
            my_id = getattr(self.window, "player_id", None)
            if pid == my_id:
                for p in self.game_state.get("players", []):
                    if p.get("player_id") == pid:
                        p.setdefault(
                            "intrigue_hand", []
                        ).append(bonus["intrigue_card"])
                        break

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.game_log_panel:
            name = self._player_name(pid)
            bonus_str = ""
            if bonus.get("coins"):
                bonus_str = f" (+{bonus['coins']} coins)"
            elif bonus.get("intrigue_card"):
                bonus_str = " (+1 intrigue card)"
            self.game_log_panel.add_entry(
                f"{name} selected a quest{bonus_str}"
            )

    def _on_quests_reset(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        reshuffled = msg.get("deck_reshuffled", False)

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.game_log_panel:
            name = self._player_name(pid)
            extra = " (deck reshuffled)" if reshuffled else ""
            self.game_log_panel.add_entry(
                f"{name} reset the quest display{extra}"
            )

    def _on_face_up_quests_updated(self, msg: dict) -> None:
        quests = msg.get("face_up_quests", [])
        board = self.game_state.get("board", {})
        board["face_up_quests"] = quests
        if self.board_renderer:
            self.board_renderer.update_board(
                board, self.game_state.get("players", [])
            )

    def _on_quest_completed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        cname = msg.get("contract_name", "?")
        vp = msg.get("victory_points_earned", 0)

        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(
                f"{name} completed '{cname}'"
                f" for {vp} VP"
            )

    def _on_contract_acquired(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        if self.game_log_panel:
            name = self._player_name(pid)
            self.game_log_panel.add_entry(f"{name} acquired a contract")

    def _on_building_market_update(self, msg: dict) -> None:
        """Handle building market state update from server."""
        self._face_up_buildings = msg.get("face_up_buildings", [])
        self._building_deck_remaining = msg.get("deck_remaining", 0)
        if self.board_renderer:
            self.board_renderer.update_building_market(
                self._face_up_buildings, self._building_deck_remaining,
            )

    def _on_building_constructed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        bname = msg.get("building_name", "?")
        new_space_id = msg.get("new_space_id", "")

        # Update local board state
        board = self.game_state.get("board", {})
        constructed = board.get("constructed_buildings", [])
        if new_space_id and new_space_id not in constructed:
            constructed.append(new_space_id)

        # Add building to local action_spaces so it renders
        spaces = board.get("action_spaces", {})
        if new_space_id and new_space_id not in spaces:
            spaces[new_space_id] = {
                "name": bname,
                "space_type": "building",
                "owner_id": msg.get("owner_id", ""),
                "reward": msg.get("visitor_reward", {}),
                "occupied_by": None,
            }

        if self.board_renderer:
            self.board_renderer.update_board(
                board, self.game_state.get("players", []),
            )

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
                f"{name} reassigned from Backstage slot {slot} to {to_space}"
            )

        # Owner bonus notification
        owner_bonus = msg.get("owner_bonus", {})
        if owner_bonus and self.game_log_panel:
            owner_name = owner_bonus.get("owner_name", "???")
            bonus = owner_bonus.get("bonus", {})
            bonus_parts = []
            for key, sym in [("guitarists", "G"), ("bass_players", "B"),
                             ("drummers", "D"), ("singers", "S"), ("coins", "$")]:
                val = bonus.get(key, 0)
                if val > 0:
                    bonus_parts.append(f"{val}{sym}")
            if bonus_parts:
                self.game_log_panel.add_entry(
                    f"{owner_name} earned owner bonus: {' '.join(bonus_parts)}"
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
                self.game_log_panel.add_entry(
                    "All players gained a bonus worker!"
                )

    def _on_bonus_workers(self, msg: dict) -> None:
        new_count = msg.get("new_worker_count", 0)
        if self.game_log_panel:
            self.game_log_panel.add_entry(
                f"Round 5: All players now have {new_count} workers!"
            )

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int,
    ) -> None:
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

    def _toggle_quests(self) -> None:
        self._show_quests_hand = not self._show_quests_hand
        self._show_intrigue_hand = False

    def _toggle_intrigue(self) -> None:
        self._show_intrigue_hand = not self._show_intrigue_hand
        self._show_quests_hand = False

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

        # Hand overlay panels
        if self._show_quests_hand or self._show_intrigue_hand:
            self._draw_hand_panel(w, h)

        # Status bar
        arcade.draw_rect_filled(
            arcade.rect.XYWH(w / 2, h - 25, w, 50),
            arcade.color.BLACK,
        )
        self._text(
            "status", self._status_text,
            w / 2, h - 25,
            arcade.color.WHITE, 16,
            anchor_x="center", anchor_y="center",
        ).draw()

        self.ui.draw()

    def _draw_hand_panel(self, w: float, h: float) -> None:
        """Draw the quest or intrigue hand overlay."""
        my_id = getattr(self.window, "player_id", None)
        my_player = None
        for p in self.game_state.get("players", []):
            if p.get("player_id") == my_id:
                my_player = p
                break
        if not my_player:
            return

        if self._show_quests_hand:
            cards = my_player.get("contract_hand", [])
            title = "My Quests"
            draw_fn = CardRenderer.draw_contract
            hand_prefix = "hand_quest"
        else:
            cards = my_player.get("intrigue_hand", [])
            title = "My Intrigue"
            draw_fn = CardRenderer.draw_intrigue
            hand_prefix = "hand_intrigue"

        # Semi-transparent background
        panel_w = min(w - 40, 700)
        panel_h = 260
        panel_x = w / 2
        panel_y = h / 2
        arcade.draw_rect_filled(
            arcade.rect.XYWH(panel_x, panel_y, panel_w, panel_h),
            (0, 0, 0, 200),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(panel_x, panel_y, panel_w, panel_h),
            arcade.color.WHITE,
            border_width=2,
        )

        self._text(
            "hand_title", title,
            panel_x, panel_y + panel_h / 2 - 20,
            arcade.color.WHITE, 16,
            anchor_x="center", anchor_y="center", bold=True,
        ).draw()

        if not cards:
            self._text(
                "hand_empty", "No cards",
                panel_x, panel_y,
                arcade.color.LIGHT_GRAY, 14,
                anchor_x="center", anchor_y="center",
            ).draw()
            return

        card_spacing = 150
        total = len(cards) * card_spacing
        start_x = panel_x - total / 2 + card_spacing / 2
        for i, card in enumerate(cards[:4]):
            cx = start_x + i * card_spacing
            draw_fn(cx, panel_y - 10, card, cache_key=f"{hand_prefix}_{i}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _text(
        self,
        key: str,
        text: str,
        x: float,
        y: float,
        color,
        font_size: int,
        **kwargs,
    ) -> arcade.Text:
        """Get or create a cached Text object."""
        if key in self._text_cache:
            t = self._text_cache[key]
            t.text = text
            t.x = x
            t.y = y
            t.color = color
            return t
        t = arcade.Text(
            text, x, y, color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def _player_name(self, player_id: str) -> str:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                return p.get("display_name", "???")
        return "???"

    def _apply_reward_to_player(self, player_id: str, reward: dict) -> None:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                res = p.get("resources", {})
                keys = (
                    "guitarists", "bass_players",
                    "drummers", "singers", "coins",
                )
                for key in keys:
                    amt = reward.get(key, 0)
                    res[key] = res.get(key, 0) + amt
                my_id = getattr(self.window, "player_id", None)
                if player_id == my_id and self.resource_bar:
                    self.resource_bar.update_resources(res)
                break

    def _update_current_player(self, next_pid: str | None) -> None:
        if next_pid is None:
            return
        turn_order = self.game_state.get("turn_order", [])
        if next_pid in turn_order:
            idx = turn_order.index(next_pid)
            self.game_state["current_player_index"] = idx
        my_id = getattr(self.window, "player_id", None)
        rnd = self.game_state.get("current_round", "?")
        if next_pid == my_id:
            self._status_text = (
                f"Round {rnd} — YOUR TURN"
            )
        else:
            name = self._player_name(next_pid)
            self._status_text = (
                f"Round {rnd} — {name}'s turn"
            )
