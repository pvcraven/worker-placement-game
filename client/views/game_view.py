"""Main game view: board, worker placement, resource display, game log."""

from __future__ import annotations

from pathlib import Path

import arcade
import arcade.gui

from client.ui.board_renderer import BoardRenderer
from client.ui.dialogs import (
    CardSelectionDialog,
    CardSpriteSelectionDialog,
    PlayerTargetDialog,
    QuestCompletionDialog,
    ResourceChoiceDialog,
)
from client.ui.resource_bar import ResourceBar
from client.ui.tabbed_panel import TabbedPanel
from shared.constants import RESOURCE_SYMBOLS


class GameView(arcade.View):
    """Primary gameplay screen — worker placement and game interaction."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = arcade.gui.UIManager()
        self.game_state: dict = {}
        self.board_renderer: BoardRenderer | None = None
        self.resource_bar: ResourceBar | None = None
        self.tabbed_panel: TabbedPanel | None = None
        self._setup_done = False
        self._status_text = ""
        self._quest_dialog: CardSelectionDialog | None = None
        self._quest_completion_dialog: QuestCompletionDialog | None = None
        self._face_up_buildings: list[dict] = []
        self._building_deck_remaining: int = 0
        self._reward_choice_dialog = None
        self._show_player_overview = False
        self._show_final_screen = False
        self._game_over_final = False
        self._final_scores: list | None = None
        self._target_dialog: PlayerTargetDialog | None = None
        self._text_cache: dict[str, arcade.Text] = {}
        self._sprite_cache: dict[str, arcade.Sprite] = {}
        self._fs_card_sprites: arcade.SpriteList | None = None
        self._fs_card_positions: list[tuple] | None = None
        self._highlight_mode: str | None = None
        self._highlighted_ids: list[str] = []
        self._cancel_sprite: arcade.Sprite | None = None
        self._cancel_sprite_list: arcade.SpriteList | None = None
        self._card_sprite_dialog: CardSpriteSelectionDialog | None = None
        self._btn_anchor: arcade.gui.UIAnchorLayout | None = None
        self._btn_scale: float = 0.0
        self._turn_sound = arcade.load_sound(
            "client/assets/sounds/sound1.mp3",
        )

    def on_show_view(self) -> None:
        self.ui.enable()
        self.game_state = getattr(self.window, "game_state", {})
        if not self._setup_done:
            self._build_ui()
            self._cancel_sprite = arcade.Sprite(
                "client/graphics/buttons/cancel.png",
                scale=0.5,
            )
            self._cancel_sprite.position = (55, 55)
            self._cancel_sprite.visible = False
            self._cancel_sprite_list = arcade.SpriteList()
            self._cancel_sprite_list.append(
                self._cancel_sprite,
            )
            self._setup_done = True
        self._sync_from_state()

    def on_hide_view(self) -> None:
        self.ui.disable()

    def _build_ui(self) -> None:
        self.board_renderer = BoardRenderer()
        self.resource_bar = ResourceBar()
        self.tabbed_panel = TabbedPanel()

        self._rebuild_buttons()

    def _refresh_board(self, board=None, players=None) -> None:
        if not self.board_renderer:
            return
        if board is None:
            board = self.game_state.get("board", {})
        if players is None:
            players = self.game_state.get("players", [])
        turn_order = self.game_state.get("turn_order", [])
        idx = self.game_state.get("current_player_index", 0)
        current_pid = None
        if turn_order and idx < len(turn_order):
            current_pid = turn_order[idx]
        self.board_renderer.update_board(
            board,
            players,
            turn_order=turn_order,
            current_player_id=current_pid,
        )

    def _rebuild_buttons(self) -> None:
        s = self.window.ui_scale
        self._btn_scale = s

        if self._btn_anchor:
            self.ui.remove(self._btn_anchor)

        btn_h = int(32 * s)
        sp = int(8 * s)
        font_sz = max(8, int(12 * s))
        style = arcade.gui.UIFlatButton.UIStyle
        btn_style = {
            k: style(font_size=font_sz)
            for k in ("normal", "hover", "press", "disabled")
        }
        btns = [
            ("Player Overview", int(140 * s), self._toggle_player_overview),
            ("Final Screen", int(120 * s), self._toggle_final_screen),
        ]

        btn_row = arcade.gui.UIBoxLayout(
            vertical=False,
            space_between=sp,
        )
        for text, width, callback in btns:
            btn = arcade.gui.UIFlatButton(
                text=text,
                width=width,
                height=btn_h,
                style=btn_style,
            )
            btn.on_click = lambda _ev, cb=callback: cb()
            btn_row.add(btn)

        self._btn_anchor = arcade.gui.UIAnchorLayout()
        self._btn_anchor.add(
            child=btn_row,
            anchor_x="left",
            anchor_y="bottom",
            align_x=int(10 * s),
            align_y=int(100 * s) + 5,
        )
        self.ui.add(self._btn_anchor)

    def _sync_from_state(self) -> None:
        """Update UI components from current game state."""
        if not self.game_state:
            return

        my_id = getattr(self.window, "player_id", None)
        players = self.game_state.get("players", [])
        board = self.game_state.get("board", {})

        my_player = self._get_my_player()
        if my_player and self.resource_bar:
            self.resource_bar.update_resources(my_player.get("resources", {}))

        self._refresh_board(board, players)

        # Extract building market from initial game state
        face_up = board.get("face_up_buildings", [])
        if face_up:
            self._face_up_buildings = face_up
            self._building_deck_remaining = board.get("building_deck_count", 0)
            if self.board_renderer:
                self.board_renderer.update_building_market(
                    self._face_up_buildings,
                    self._building_deck_remaining,
                )

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
            phase = self.game_state.get("phase", "placement")
            phase_label = (
                "Reassignment" if phase == "reassignment" else f"Round {current_round}"
            )
            is_my_turn = current_pid == my_id
            if is_my_turn:
                self._status_text = f"{phase_label} — YOUR TURN"
            else:
                self._status_text = f"{phase_label} — {current_name}'s turn"

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
        elif action == "quest_completion_prompt":
            self._on_quest_completion_prompt(msg)
        elif action == "quest_skipped":
            self._on_quest_skipped(msg)
        elif action == "contract_acquired":
            self._on_contract_acquired(msg)
        elif action == "building_constructed":
            self._on_building_constructed(msg)
        elif action == "placement_cancelled":
            self._on_placement_cancelled(msg)
        elif action == "building_market_update":
            self._on_building_market_update(msg)
        elif action == "reassignment_phase_start":
            self._on_reassignment_phase_start(msg)
        elif action == "worker_reassigned":
            self._on_worker_reassigned(msg)
        elif action == "intrigue_target_prompt":
            self._on_intrigue_target_prompt(msg)
        elif action == "intrigue_effect_resolved":
            self._on_intrigue_effect_resolved(msg)
        elif action == "round_end":
            self._on_round_end(msg)
        elif action == "bonus_workers_granted":
            self._on_bonus_workers(msg)
        elif action == "game_over":
            self._final_scores = msg.get("final_scores", [])
            self._show_final_screen = True
            self._game_over_final = True
            self._fs_card_sprites = None
        elif action == "state_sync":
            self.game_state = msg.get("game_state", {})
            self._sync_from_state()
        elif action == "player_disconnected":
            name = msg.get("player_name", "???")
            if self.tabbed_panel:
                self.tabbed_panel.add_entry(f"{name} disconnected")
        elif action == "player_reconnected":
            name = msg.get("player_name", "???")
            if self.tabbed_panel:
                self.tabbed_panel.add_entry(f"{name} reconnected")
        elif action == "turn_timeout":
            name = msg.get("player_name", "???")
            if self.tabbed_panel:
                self.tabbed_panel.add_entry(f"{name}'s turn was skipped (timeout)")
        elif action == "quest_reward_choice_prompt":
            self._on_quest_reward_choice_prompt(msg)
        elif action == "quest_reward_choice_resolved":
            self._on_quest_reward_choice_resolved(msg)
        elif action == "resource_choice_prompt":
            self._on_resource_choice_prompt(msg)
        elif action == "resource_choice_resolved":
            self._on_resource_choice_resolved(msg)
        elif action == "intrigue_play_prompt":
            self._on_intrigue_play_prompt(msg)
        elif action == "opponent_choice_prompt":
            self._on_opponent_choice_prompt(msg)
        elif action == "worker_recall_prompt":
            self._on_worker_recall_prompt(msg)
        elif action == "worker_recalled":
            self._on_worker_recalled(msg)
        elif action == "round_start_resource_choice_prompt":
            self._on_round_start_resource_choice_prompt(msg)
        elif action == "round_start_bonus":
            self._on_round_start_bonus(msg)
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
            bt = spaces[space_id].get("building_tile")
            if bt and bt.get("accumulation_type"):
                bt["accumulated_stock"] = 0

        self._refresh_board(board)

        # Update player resources and worker count
        self._apply_reward_to_player(pid, reward)
        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                p["available_workers"] = max(0, p.get("available_workers", 0) - 1)
                break

        # Check if this is a garage spot requiring quest selection
        space_data = spaces.get(space_id, {})
        my_id = getattr(self.window, "player_id", None)
        if (
            space_data.get("space_type") == "garage"
            and pid == my_id
            and space_data.get("reward_special")
            in (
                "quest_and_coins",
                "quest_and_intrigue",
                "reset_quests",
            )
        ):
            board = self.game_state.get("board", {})
            quests = board.get("face_up_quests", [])
            quest_ids = [q.get("id") for q in quests if q.get("id")]
            self._enter_highlight_mode(
                "quest_selection",
                quest_ids,
            )
            if self.tabbed_panel:
                self.tabbed_panel.add_entry("Click a quest card to select it")
            return

        # Building with draw_contract: player picks a face-up quest
        bt = space_data.get("building_tile", {})
        if (
            space_data.get("space_type") == "building"
            and bt.get("visitor_reward_special") == "draw_contract"
            and pid == my_id
        ):
            board = self.game_state.get("board", {})
            quests = board.get("face_up_quests", [])
            quest_ids = [q.get("id") for q in quests if q.get("id")]
            self._enter_highlight_mode(
                "quest_selection",
                quest_ids,
            )
            if self.tabbed_panel:
                self.tabbed_panel.add_entry("Click a quest card to select it")
            return

        if (
            space_data.get("reward_special") == "purchase_building"
            and pid == my_id
            and msg.get("next_player_id") is None
        ):
            self._enter_building_highlight(pid)
            return

        # Update turn
        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.tabbed_panel:
            name = self._player_name(pid)
            space_name = space_data.get("name", space_id)
            self.tabbed_panel.add_entry(f"{name} placed worker on {space_name}")

        # Owner bonus notification
        owner_bonus = msg.get("owner_bonus", {})
        if owner_bonus:
            owner_id = owner_bonus.get("owner_id", "")
            bonus = owner_bonus.get("bonus", {})
            if owner_id and bonus:
                self._apply_reward_to_player(owner_id, bonus)
            if self.tabbed_panel:
                owner_name = owner_bonus.get("owner_name", "???")
                bonus_parts = []
                for key, sym in RESOURCE_SYMBOLS:
                    val = bonus.get(key, 0)
                    if val > 0:
                        bonus_parts.append(f"{val}{sym}")
                if bonus_parts:
                    self.tabbed_panel.add_entry(
                        f"{owner_name} earned owner bonus: {' '.join(bonus_parts)}"
                    )

        # Resource trigger plot quest bonuses
        for tb in msg.get("trigger_bonuses", []):
            if tb.get("drawn_intrigue"):
                my_id = getattr(self.window, "player_id", None)
                if pid == my_id:
                    for p in self.game_state.get("players", []):
                        if p.get("player_id") == pid:
                            p.setdefault("intrigue_hand", []).extend(
                                tb["drawn_intrigue"]
                            )
                            break
            if self.tabbed_panel:
                name = self._player_name(pid)
                parts = []
                for br in (tb.get("bonus_resources") or {}).items():
                    k, v = br
                    if v:
                        sym = next((s for rk, s in RESOURCE_SYMBOLS if rk == k), k)
                        parts.append(f"{v}{sym}")
                if tb.get("drawn_intrigue"):
                    parts.append(f"{len(tb['drawn_intrigue'])} intrigue")
                if tb.get("swap_pending"):
                    parts.append("swap pending")
                cname = tb.get("contract_name", "plot quest")
                if parts:
                    self.tabbed_panel.add_entry(
                        f"{name} triggered {cname}: {' '.join(parts)}"
                    )

    def _on_worker_placed_backstage(self, msg: dict) -> None:
        slot_num = msg.get("slot_number", 0)
        pid = msg.get("player_id", "")
        card = msg.get("intrigue_card", {})
        card_id = card.get("id", "")

        # Update backstage slot state
        board = self.game_state.get("board", {})
        for s in board.get("backstage_slots", []):
            if s.get("slot_number") == slot_num:
                s["occupied_by"] = pid
                break

        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                p["available_workers"] = max(0, p.get("available_workers", 0) - 1)
                hand = p.get("intrigue_hand", [])
                p["intrigue_hand"] = [c for c in hand if c.get("id") != card_id]
                break

        # Apply intrigue effect rewards to player resources
        effect = msg.get("intrigue_effect", {})
        details = effect.get("details", {})
        if details:
            reward = {
                k: details.get(k, 0)
                for k in (
                    "guitarists",
                    "bass_players",
                    "drummers",
                    "singers",
                    "coins",
                )
            }
            all_gained = details.get("all_gained", {})
            if all_gained:
                for p in self.game_state.get("players", []):
                    self._apply_reward_to_player(
                        p.get("player_id", ""),
                        all_gained,
                    )
            elif any(reward.values()):
                self._apply_reward_to_player(pid, reward)
            vp = details.get("victory_points", 0)
            if vp:
                for p in self.game_state.get("players", []):
                    if p.get("player_id") == pid:
                        p["victory_points"] = p.get("victory_points", 0) + vp
                        break

            drawn = details.get("drawn", [])
            if drawn:
                etype = effect.get("type", "")
                my_id = getattr(self.window, "player_id", None)
                for p in self.game_state.get("players", []):
                    if p.get("player_id") == pid:
                        if pid == my_id:
                            if etype == "draw_intrigue":
                                p.setdefault("intrigue_hand", []).extend(drawn)
                            elif etype == "draw_contracts":
                                p.setdefault("contract_hand", []).extend(drawn)
                        else:
                            key = "intrigue_hand_count"
                            if etype == "draw_contracts":
                                key = "contract_hand_count"
                            if etype in (
                                "draw_intrigue",
                                "draw_contracts",
                            ):
                                p[key] = p.get(key, 0) + len(drawn)
                        break

        # Apply plot quest bonus VP for playing an intrigue card
        plot_bonus = msg.get("plot_quest_bonus_vp", 0)
        if plot_bonus:
            for p in self.game_state.get("players", []):
                if p.get("player_id") == pid:
                    p["victory_points"] = p.get("victory_points", 0) + plot_bonus
                    break

        self._refresh_board(board)

        if self.tabbed_panel:
            name = self._player_name(pid)
            card_name = card.get("name", "?")
            bonus_str = f" (+{plot_bonus} VP plot bonus)" if plot_bonus else ""
            self.tabbed_panel.add_entry(
                f"{name} placed worker on Backstage"
                f" slot {slot_num}, played {card_name}{bonus_str}"
            )
            effect = msg.get("intrigue_effect", {})
            effect_type = effect.get("type", "")
            details = effect.get("details", {})
            effect_str = self._format_intrigue_effect(effect_type, details)
            if effect_str:
                self.tabbed_panel.add_entry(f"  Effect: {effect_str}")

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

    def _on_intrigue_target_prompt(self, msg: dict) -> None:
        effect_type = msg.get("effect_type", "")
        effect_value = msg.get("effect_value", {})
        targets = msg.get("eligible_targets", [])

        parts = []
        for k, sym in RESOURCE_SYMBOLS:
            v = effect_value.get(k, 0)
            if v:
                parts.append(f"{v}{sym}")
        val_str = " ".join(parts) if parts else ""

        if effect_type == "steal_resources":
            desc = f"Steal {val_str} from an opponent"
        else:
            desc = f"Opponent loses {val_str}"

        def on_select(player_id: str) -> None:
            self._target_dialog = None
            self.window.network.send(
                {
                    "action": "choose_intrigue_target",
                    "target_player_id": player_id,
                }
            )

        def on_cancel() -> None:
            self._target_dialog = None
            self.window.network.send(
                {
                    "action": "cancel_intrigue_target",
                }
            )

        self._target_dialog = PlayerTargetDialog(
            title="Choose Target",
            effect_description=desc,
            eligible_targets=targets,
            on_select=on_select,
            on_cancel=on_cancel,
            ui_manager=self.ui,
        )
        self._target_dialog.show(
            self.window.width,
            self.window.height,
            scale=self.window.ui_scale,
        )

    def _on_intrigue_effect_resolved(
        self,
        msg: dict,
    ) -> None:
        pid = msg.get("player_id", "")
        target_pid = msg.get("target_player_id", "")
        effect_type = msg.get("effect_type", "")
        affected = msg.get("resources_affected", {})

        keys = (
            "guitarists",
            "bass_players",
            "drummers",
            "singers",
            "coins",
        )
        for k in keys:
            amt = affected.get(k, 0)
            if amt <= 0:
                continue
            # Target loses
            for p in self.game_state.get("players", []):
                if p.get("player_id") == target_pid:
                    res = p.get("resources", {})
                    res[k] = max(0, res.get(k, 0) - amt)
                    break
            # Attacker gains (steal only)
            if effect_type == "steal_resources":
                for p in self.game_state.get("players", []):
                    if p.get("player_id") == pid:
                        res = p.get("resources", {})
                        res[k] = res.get(k, 0) + amt
                        break

        # Update resource bar if local player is involved
        my_id = getattr(self.window, "player_id", None)
        if my_id in (pid, target_pid) and self.resource_bar:
            for p in self.game_state.get("players", []):
                if p.get("player_id") == my_id:
                    self.resource_bar.update_resources(
                        p.get("resources", {}),
                    )
                    break

        if self.tabbed_panel:
            name = self._player_name(pid)
            tname = self._player_name(target_pid)
            parts = []
            for k, sym in RESOURCE_SYMBOLS:
                v = affected.get(k, 0)
                if v:
                    parts.append(f"{v}{sym}")
            res_str = " ".join(parts)
            if effect_type == "steal_resources":
                self.tabbed_panel.add_entry(f"{name} stole {res_str} from {tname}")
            else:
                self.tabbed_panel.add_entry(f"{tname} lost {res_str}")

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
                    p.setdefault("contract_hand", []).append(selected_card)
                    break

        # Apply bonus to local state
        if bonus.get("coins"):
            self._apply_reward_to_player(pid, {"coins": bonus["coins"]})
        if bonus.get("intrigue_card"):
            my_id = getattr(self.window, "player_id", None)
            if pid == my_id:
                for p in self.game_state.get("players", []):
                    if p.get("player_id") == pid:
                        p.setdefault("intrigue_hand", []).append(bonus["intrigue_card"])
                        break

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.tabbed_panel:
            name = self._player_name(pid)
            bonus_str = ""
            if bonus.get("coins"):
                bonus_str = f" (+{bonus['coins']} coins)"
            elif bonus.get("intrigue_card"):
                bonus_str = " (+1 intrigue card)"
            self.tabbed_panel.add_entry(f"{name} selected a quest{bonus_str}")

    def _on_quests_reset(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        reshuffled = msg.get("deck_reshuffled", False)

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.tabbed_panel:
            name = self._player_name(pid)
            extra = " (deck reshuffled)" if reshuffled else ""
            self.tabbed_panel.add_entry(f"{name} reset the quest display{extra}")

    def _on_face_up_quests_updated(self, msg: dict) -> None:
        quests = msg.get("face_up_quests", [])
        board = self.game_state.get("board", {})
        board["face_up_quests"] = quests
        self._refresh_board(board)

    def _on_quest_completed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        cname = msg.get("contract_name", "?")
        cid = msg.get("contract_id", "")
        vp = msg.get("victory_points_earned", 0)
        plot_bonus = msg.get("plot_quest_bonus_vp", 0)
        showcase_bonus = msg.get("showcase_bonus_vp", 0)
        spent = msg.get("resources_spent", {})
        bonus = msg.get("bonus_resources", {})
        drawn_intr = msg.get("drawn_intrigue", [])
        drawn_q = msg.get("drawn_quests", [])
        building = msg.get("building_granted")
        my_id = getattr(self.window, "player_id", None)

        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                p["victory_points"] = (
                    p.get("victory_points", 0) + vp + plot_bonus + showcase_bonus
                )
                hand = p.get("contract_hand", [])
                completed_card = {"id": cid, "name": cname, "victory_points": vp}
                for c in hand:
                    if c.get("id") == cid:
                        completed_card["genre"] = c.get("genre", "")
                        break
                p["contract_hand"] = [c for c in hand if c.get("id") != cid]
                p.setdefault("completed_contracts", []).append(completed_card)
                res = p.get("resources", {})
                for k in (
                    "guitarists",
                    "bass_players",
                    "drummers",
                    "singers",
                    "coins",
                ):
                    res[k] = max(0, res.get(k, 0) - spent.get(k, 0) + bonus.get(k, 0))
                if pid == my_id:
                    if drawn_intr:
                        p.setdefault(
                            "intrigue_hand",
                            [],
                        ).extend(drawn_intr)
                    if drawn_q:
                        p.setdefault(
                            "contract_hand",
                            [],
                        ).extend(drawn_q)
                else:
                    if drawn_intr:
                        p["intrigue_hand_count"] = p.get(
                            "intrigue_hand_count", 0
                        ) + len(drawn_intr)
                    if drawn_q:
                        p["contract_hand_count"] = p.get(
                            "contract_hand_count", 0
                        ) + len(drawn_q)
                if pid == my_id and self.resource_bar:
                    self.resource_bar.update_resources(
                        res,
                    )
                break

        if building:
            board = self.game_state.get("board", {})
            sid = building.get("space_id", "")
            if sid:
                board.setdefault(
                    "constructed_buildings",
                    [],
                ).append(sid)
                spaces = board.get("action_spaces", {})
                if sid not in spaces:
                    spaces[sid] = {
                        "name": building.get(
                            "building_name",
                            "?",
                        ),
                        "space_type": "building",
                        "owner_id": pid,
                        "reward": building.get(
                            "visitor_reward",
                            {},
                        ),
                        "owner_bonus": building.get(
                            "owner_bonus",
                            {},
                        ),
                        "building_tile": {
                            "id": building.get("building_id", ""),
                        },
                        "occupied_by": None,
                    }
            self._refresh_board(board)

        extra_workers = msg.get("extra_workers_granted", 0)
        if extra_workers > 0:
            for p in self.game_state.get("players", []):
                if p.get("player_id") == pid:
                    p["total_workers"] = p.get("total_workers", 0) + extra_workers
                    break

        opp_coins = msg.get("opponent_coins_granted")
        if opp_coins:
            opp_pid = opp_coins.get("player_id", "")
            opp_coins_amt = opp_coins.get("coins", 0)
            for p in self.game_state.get("players", []):
                if p.get("player_id") == opp_pid:
                    res = p.get("resources", {})
                    res["coins"] = res.get("coins", 0) + opp_coins_amt
                    if opp_pid == my_id and self.resource_bar:
                        self.resource_bar.update_resources(res)
                    break

        if self.tabbed_panel:
            name = self._player_name(pid)
            total_bonus = plot_bonus + showcase_bonus
            vp_str = f"{vp} VP" if not total_bonus else f"{vp}+{total_bonus} VP"
            parts = [vp_str]
            for k, sym in RESOURCE_SYMBOLS:
                v = bonus.get(k, 0)
                if v:
                    parts.append(f"+{v}{sym}")
            if drawn_intr:
                parts.append(f"drew {len(drawn_intr)} intrigue")
            if drawn_q:
                parts.append(f"drew {len(drawn_q)} quest(s)")
            if building:
                bname = building.get("building_name", "?")
                parts.append(f"building: {bname}")
            if extra_workers:
                parts.append(f"+{extra_workers} worker(s)")
            if opp_coins:
                oname = opp_coins.get("player_name", "?")
                parts.append(f"{oname} got {opp_coins.get('coins', 0)} coins")
            reward_str = ", ".join(parts)
            self.tabbed_panel.add_entry(
                f"{name} completed '{cname}'" f" ({reward_str})"
            )

        next_pid = msg.get("next_player_id")
        if next_pid:
            self._update_current_player(next_pid)

    def _on_quest_reward_choice_prompt(
        self,
        msg: dict,
    ) -> None:
        reward_type = msg.get("reward_type", "")
        choices = msg.get("available_choices", [])
        quest_name = msg.get("quest_name", "")

        if reward_type == "choose_quest":
            from client.ui.dialogs import RewardChoiceDialog

            self._reward_choice_dialog = RewardChoiceDialog(
                title=f"Quest Reward: {quest_name}",
                description="Choose a quest card:",
                choices=choices,
                label_key="name",
                on_select=self._on_reward_quest_selected,
                ui_manager=self.ui,
            )
            self._reward_choice_dialog.show(
                self.window.width,
                self.window.height,
                scale=self.window.ui_scale,
            )
        elif reward_type == "choose_building":
            bld_ids = [b.get("id") for b in self._face_up_buildings if b.get("id")]
            self._enter_highlight_mode(
                "building_reward",
                bld_ids,
            )
            self._status_text = "Pick a building as your quest reward"

    def _on_reward_quest_selected(
        self,
        choice_id: str,
    ) -> None:
        self._reward_choice_dialog = None
        self.window.network.send(
            {
                "action": "quest_reward_choice",
                "choice_id": choice_id,
            }
        )

    def _on_quest_reward_choice_resolved(
        self,
        msg: dict,
    ) -> None:
        pid = msg.get("player_id", "")
        reward_type = msg.get("reward_type", "")
        choice = msg.get("choice", {})
        quest_name = msg.get("quest_name", "")
        my_id = getattr(self.window, "player_id", None)

        if reward_type == "choose_quest":
            for p in self.game_state.get("players", []):
                if p.get("player_id") == pid:
                    if pid == my_id:
                        p.setdefault(
                            "contract_hand",
                            [],
                        ).append(choice)
                    else:
                        p["contract_hand_count"] = p.get("contract_hand_count", 0) + 1
                    break
            face_up = self.game_state.get(
                "board",
                {},
            ).get("face_up_quests", [])
            cid = choice.get("id")
            board = self.game_state.setdefault("board", {})
            board["face_up_quests"] = [q for q in face_up if q.get("id") != cid]
            self._refresh_board(board)
        elif reward_type == "choose_building":
            board = self.game_state.get("board", {})
            sid = choice.get("space_id", "")
            if sid:
                board.setdefault(
                    "constructed_buildings",
                    [],
                ).append(sid)
                spaces = board.get(
                    "action_spaces",
                    {},
                )
                if sid not in spaces:
                    spaces[sid] = {
                        "name": choice.get(
                            "building_name",
                            "?",
                        ),
                        "space_type": "building",
                        "owner_id": pid,
                        "reward": choice.get(
                            "visitor_reward",
                            {},
                        ),
                        "owner_bonus": choice.get(
                            "owner_bonus",
                            {},
                        ),
                        "occupied_by": None,
                        "building_tile": {"id": choice.get("building_id", "")},
                    }
                bid = choice.get("building_id")
                if bid:
                    fub = board.get(
                        "face_up_buildings",
                        [],
                    )
                    board["face_up_buildings"] = [b for b in fub if b.get("id") != bid]
                self._refresh_board(board)

        if self.tabbed_panel:
            name = self._player_name(pid)
            if reward_type == "choose_quest":
                qn = choice.get("name", "?")
                self.tabbed_panel.add_entry(
                    f"{name} chose quest '{qn}'" f" as reward for '{quest_name}'"
                )
            elif reward_type == "choose_building":
                bn = choice.get(
                    "building_name",
                    choice.get("name", "?"),
                )
                self.tabbed_panel.add_entry(
                    f"{name} chose building '{bn}'" f" as reward for '{quest_name}'"
                )

        next_pid = msg.get("next_player_id")
        if next_pid:
            self._update_current_player(next_pid)

    def _on_resource_choice_prompt(
        self,
        msg: dict,
    ) -> None:
        pid = msg.get("player_id", "")
        my_id = getattr(self.window, "player_id", None)
        if pid != my_id:
            name = self._player_name(pid)
            title = msg.get("title", "choosing resources")
            self._status_text = f"Waiting on {name}: {title}"
            if self.tabbed_panel:
                self.tabbed_panel.add_entry(f"Waiting on {name}: {title}")
            return

        prompt_id = msg.get("prompt_id", "")

        def on_select(p_id: str, chosen: dict) -> None:
            self.window.network.send(
                {
                    "action": "resource_choice",
                    "prompt_id": p_id,
                    "chosen_resources": chosen,
                }
            )

        dialog = ResourceChoiceDialog(
            prompt_id=prompt_id,
            title=msg.get("title", "Choose Resources"),
            description=msg.get("description", ""),
            choice_type=msg.get("choice_type", "pick"),
            allowed_types=msg.get("allowed_types", []),
            pick_count=msg.get("pick_count", 1),
            total=msg.get("total", 0),
            bundles=msg.get("bundles", []),
            is_spend=msg.get("is_spend", False),
            on_select=on_select,
            ui_manager=self.ui,
        )
        dialog.show(
            self.window.width,
            self.window.height,
            scale=self.window.ui_scale,
        )

    def _on_resource_choice_resolved(
        self,
        msg: dict,
    ) -> None:
        pid = msg.get("player_id", "")
        chosen = msg.get("chosen_resources", {})
        is_spend = msg.get("is_spend", False)
        source = msg.get("source_description", "")
        my_id = getattr(self.window, "player_id", None)

        if pid == my_id:
            my_player = self._get_my_player()
            if my_player:
                res = my_player.get("resources", {})
                for key, val in chosen.items():
                    if key in res:
                        if is_spend:
                            res[key] = res.get(key, 0) - val
                        else:
                            res[key] = res.get(key, 0) + val
                if self.resource_bar:
                    self.resource_bar.update_resources(res)

        if self.tabbed_panel:
            name = self._player_name(pid)
            parts = []
            for k, v in chosen.items():
                if v > 0:
                    parts.append(f"{v} {k}")
            res_str = ", ".join(parts) if parts else "none"
            verb = "turned in" if is_spend else "gained"
            self.tabbed_panel.add_entry(f"{name} {verb} {res_str} from {source}")

        next_pid = msg.get("next_player_id")
        if next_pid:
            self._update_current_player(next_pid)

    def _on_intrigue_play_prompt(self, msg: dict) -> None:
        cards = msg.get("intrigue_hand", [])
        if not cards:
            return

        def on_select(card_id: str) -> None:
            self._card_sprite_dialog = None
            self.window.network.send(
                {
                    "action": "play_intrigue_from_quest",
                    "intrigue_card_id": card_id,
                }
            )

        self._card_sprite_dialog = CardSpriteSelectionDialog(
            title="Play an Intrigue Card (Quest Reward)",
            cards=cards,
            card_type="intrigue",
            on_select=on_select,
            on_cancel=None,
            cancel_label="",
        )

    def _on_opponent_choice_prompt(self, msg: dict) -> None:
        opponents = msg.get("opponents", [])
        coins = msg.get("coins_amount", 0)

        def on_select(player_id: str) -> None:
            self._target_dialog = None
            self.window.network.send(
                {
                    "action": "choose_opponent",
                    "target_player_id": player_id,
                }
            )

        self._target_dialog = PlayerTargetDialog(
            title="Choose Opponent",
            effect_description=f"Choose an opponent to receive {coins} coins",
            eligible_targets=[
                {
                    "player_id": o.get("player_id"),
                    "player_name": o.get("player_name"),
                }
                for o in opponents
            ],
            on_select=on_select,
            on_cancel=None,
            ui_manager=self.ui,
        )
        self._target_dialog.show(
            self.window.width,
            self.window.height,
            scale=self.window.ui_scale,
        )

    def _on_worker_recall_prompt(self, msg: dict) -> None:
        spaces = msg.get("occupied_spaces", [])
        if not spaces:
            return
        space_ids = [s.get("space_id", "") for s in spaces]
        self._enter_highlight_mode("worker_recall", space_ids)
        self._status_text = "Select a worker to recall"

    def _on_worker_recalled(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        space_id = msg.get("space_id", "")
        space_name = msg.get("space_name", "?")
        my_id = getattr(self.window, "player_id", None)

        board = self.game_state.get("board", {})
        spaces = board.get("action_spaces", {})
        if space_id in spaces:
            spaces[space_id]["occupied_by"] = None

        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                p["available_workers"] = p.get("available_workers", 0) + 1
                break

        if pid == my_id:
            self._exit_highlight_mode()

        if self.tabbed_panel:
            name = self._player_name(pid)
            self.tabbed_panel.add_entry(f"{name} recalled worker from {space_name}")

    def _on_round_start_resource_choice_prompt(self, msg: dict) -> None:
        player_id = msg.get("player_id", "")
        contract_name = msg.get("contract_name", "")
        my_id = getattr(self.window, "player_id", None)

        if player_id != my_id:
            name = self._player_name(player_id)
            self._status_text = f"Waiting on {name}: round-start resource choice"
            return

        options = [
            {"label": "Guitarist", "value": "guitarists"},
            {"label": "Bass Player", "value": "bass_players"},
            {"label": "Drummer", "value": "drummers"},
            {"label": "Singer", "value": "singers"},
        ]

        s = self.window.ui_scale
        anchor = arcade.gui.UIAnchorLayout()
        v_box = arcade.gui.UIBoxLayout(space_between=int(8 * s))

        title = arcade.gui.UILabel(
            text=f"Choose a resource ({contract_name})",
            font_size=max(8, int(16 * s)),
            text_color=arcade.color.WHITE,
            bold=True,
        )
        v_box.add(title)

        widget_ref = [None]

        for opt in options:
            btn = arcade.gui.UIFlatButton(
                text=opt["label"],
                width=int(200 * s),
                height=int(36 * s),
            )
            resource_type = opt["value"]

            def make_handler(rt):
                def handler(_event=None):
                    if widget_ref[0]:
                        self.ui.remove(widget_ref[0])
                    self.window.network.send(
                        {
                            "action": "round_start_resource_choice",
                            "resource_type": rt,
                        }
                    )

                return handler

            btn.on_click = make_handler(resource_type)
            v_box.add(btn)

        bg = v_box.with_padding(all=int(20 * s)).with_background(color=(0, 0, 0, 230))
        anchor.add(child=bg, anchor_x="center", anchor_y="center")
        widget_ref[0] = self.ui.add(anchor)

    def _on_round_start_bonus(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        resource_type = msg.get("resource_type", "")
        contract_name = msg.get("contract_name", "")

        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                res = p.get("resources", {})
                res[resource_type] = res.get(resource_type, 0) + 1
                my_id = getattr(self.window, "player_id", None)
                if pid == my_id and self.resource_bar:
                    self.resource_bar.update_resources(res)
                break

        if self.tabbed_panel:
            name = self._player_name(pid)
            self.tabbed_panel.add_entry(
                f"{name} gained 1 {resource_type} from {contract_name}"
            )

    def _on_quest_completion_prompt(
        self,
        msg: dict,
    ) -> None:
        quests = msg.get("completable_quests", [])
        if not quests:
            return

        def on_select(contract_id: str) -> None:
            self._quest_completion_dialog = None
            self.window.network.send(
                {
                    "action": "complete_quest",
                    "contract_id": contract_id,
                }
            )

        def on_skip() -> None:
            self._quest_completion_dialog = None
            self.window.network.send(
                {
                    "action": "skip_quest_completion",
                }
            )

        self._quest_completion_dialog = QuestCompletionDialog(
            quests=quests,
            on_select=on_select,
            on_skip=on_skip,
            bonus_quest_id=msg.get("bonus_quest_id"),
            bonus_vp=msg.get("bonus_vp", 0),
        )
        self._quest_completion_dialog.show(
            self.window.width,
            self.window.height,
        )

    def _on_quest_skipped(self, msg: dict) -> None:
        next_pid = msg.get("next_player_id")
        if next_pid:
            self._update_current_player(next_pid)

    def _on_contract_acquired(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        if self.tabbed_panel:
            name = self._player_name(pid)
            self.tabbed_panel.add_entry(
                f"{name} acquired a contract",
            )

    def _on_placement_cancelled(self, msg: dict) -> None:
        """Handle placement cancellation — free space, return worker."""
        space_id = msg.get("space_id", "")
        pid = msg.get("player_id", "")

        board = self.game_state.get("board", {})

        if space_id.startswith("backstage_slot_"):
            slot_num = int(space_id.split("_")[-1])
            for s in board.get("backstage_slots", []):
                if s.get("slot_number") == slot_num:
                    s["occupied_by"] = None
                    s["intrigue_card_played"] = None
                    break
        else:
            spaces = board.get("action_spaces", {})
            if space_id in spaces:
                spaces[space_id]["occupied_by"] = None

        returned_card = msg.get("returned_card", {})
        reversed_bonus = msg.get("plot_quest_bonus_vp", 0)
        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                p["available_workers"] = p.get("available_workers", 0) + 1
                if returned_card:
                    p.setdefault("intrigue_hand", []).append(
                        returned_card,
                    )
                if reversed_bonus:
                    p["victory_points"] = p.get("victory_points", 0) - reversed_bonus
                break

        self._refresh_board(board)

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.tabbed_panel:
            name = self._player_name(pid)
            if space_id.startswith("backstage_slot_"):
                self.tabbed_panel.add_entry(f"{name} cancelled intrigue targeting")
            else:
                self.tabbed_panel.add_entry(f"{name} cancelled placement")

    def _on_building_market_update(self, msg: dict) -> None:
        """Handle building market state update from server."""
        self._face_up_buildings = msg.get("face_up_buildings", [])
        self._building_deck_remaining = msg.get("deck_remaining", 0)
        if self.board_renderer:
            self.board_renderer.update_building_market(
                self._face_up_buildings,
                self._building_deck_remaining,
            )

    def _on_building_constructed(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        bname = msg.get("building_name", "?")
        new_space_id = msg.get("new_space_id", "")
        cost = msg.get("cost_coins", 0)
        accum_vp = msg.get("accumulated_vp", 0)
        plot_bonus = msg.get("plot_quest_bonus_vp", 0)
        total_vp = accum_vp + plot_bonus

        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                if cost:
                    res = p.get("resources", {})
                    res["coins"] = max(0, res.get("coins", 0) - cost)
                    my_id = getattr(self.window, "player_id", None)
                    if pid == my_id and self.resource_bar:
                        self.resource_bar.update_resources(res)
                if total_vp:
                    p["victory_points"] = p.get("victory_points", 0) + total_vp
                break

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
                "owner_bonus": msg.get("owner_bonus", {}),
                "occupied_by": None,
                "building_tile": msg.get(
                    "building_tile", {"id": msg.get("building_id", "")}
                ),
            }

        self._refresh_board(board)

        next_pid = msg.get("next_player_id")
        self._update_current_player(next_pid)

        if self.tabbed_panel:
            name = self._player_name(pid)
            if total_vp:
                if plot_bonus:
                    vp_str = f" (+{accum_vp}+{plot_bonus} VP)"
                else:
                    vp_str = f" (+{accum_vp} VP)"
            else:
                vp_str = ""
            self.tabbed_panel.add_entry(
                f"{name} built {bname}{vp_str}",
            )

    def _on_reassignment_phase_start(self, msg: dict) -> None:
        slots = msg.get("backstage_slots", [])
        self.game_state["phase"] = "reassignment"
        self.game_state["reassignment_queue"] = [s["slot_number"] for s in slots]

        my_id = getattr(self.window, "player_id", None)
        if slots:
            first_owner = slots[0].get("player_id") or slots[0].get("occupied_by")
            if first_owner == my_id:
                self._status_text = "Reassignment — YOUR TURN"
            else:
                name = self._player_name(first_owner)
                self._status_text = f"Reassignment — {name}'s turn"
        else:
            self._status_text = "Reassignment Phase"

        if self.tabbed_panel:
            self.tabbed_panel.add_entry("--- Reassignment Phase ---")
        self._play_reassignment_sound_if_my_turn()

    def _on_worker_reassigned(self, msg: dict) -> None:
        pid = msg.get("player_id", "")
        from_slot = msg.get("from_slot", 0)
        to_space = msg.get("to_space_id", "")
        reward = msg.get("reward_granted", {})

        board = self.game_state.get("board", {})

        # Clear the backstage slot
        for s in board.get("backstage_slots", []):
            if s.get("slot_number") == from_slot:
                s["occupied_by"] = None
                s["intrigue_card_played"] = None
                break

        # Mark target space as occupied
        spaces = board.get("action_spaces", {})
        if to_space in spaces:
            spaces[to_space]["occupied_by"] = pid

        # Apply reward
        self._apply_reward_to_player(pid, reward)

        # Pop from reassignment queue
        queue = self.game_state.get("reassignment_queue", [])
        if queue and queue[0] == from_slot:
            queue.pop(0)

        self._refresh_board(board)

        if self.tabbed_panel:
            name = self._player_name(pid)
            space_name = to_space
            space_data = spaces.get(to_space, {})
            if space_data.get("name"):
                space_name = space_data["name"]
            self.tabbed_panel.add_entry(
                f"{name} reassigned from Backstage" f" {from_slot} to {space_name}"
            )

        # Owner bonus notification
        owner_bonus = msg.get("owner_bonus", {})
        if owner_bonus:
            owner_id = owner_bonus.get("owner_id", "")
            bonus = owner_bonus.get("bonus", {})
            if owner_id and bonus:
                self._apply_reward_to_player(owner_id, bonus)
            if self.tabbed_panel:
                owner_name = owner_bonus.get("owner_name", "???")
                bonus_parts = []
                for key, sym in RESOURCE_SYMBOLS:
                    val = bonus.get(key, 0)
                    if val > 0:
                        bonus_parts.append(f"{val}{sym}")
                if bonus_parts:
                    self.tabbed_panel.add_entry(
                        f"{owner_name} earned owner bonus:" f" {' '.join(bonus_parts)}"
                    )

        # Resource trigger plot quest bonuses
        for tb in msg.get("trigger_bonuses", []):
            if tb.get("drawn_intrigue"):
                if pid == getattr(self.window, "player_id", None):
                    for p in self.game_state.get("players", []):
                        if p.get("player_id") == pid:
                            p.setdefault("intrigue_hand", []).extend(
                                tb["drawn_intrigue"]
                            )
                            break
            if self.tabbed_panel:
                name = self._player_name(pid)
                parts = []
                for k, v in (tb.get("bonus_resources") or {}).items():
                    if v:
                        sym = next((s for rk, s in RESOURCE_SYMBOLS if rk == k), k)
                        parts.append(f"{v}{sym}")
                if tb.get("drawn_intrigue"):
                    parts.append(f"{len(tb['drawn_intrigue'])} intrigue")
                if tb.get("swap_pending"):
                    parts.append("swap pending")
                cname = tb.get("contract_name", "plot quest")
                if parts:
                    self.tabbed_panel.add_entry(
                        f"{name} triggered {cname}: {' '.join(parts)}"
                    )

        my_id = getattr(self.window, "player_id", None)
        space_data = spaces.get(to_space, {})

        self._play_reassignment_sound_if_my_turn()

        # Building purchase during reassignment
        if space_data.get("reward_special") == "purchase_building" and pid == my_id:
            self._enter_building_highlight(pid)
            return

        # Garage quest selection during reassignment
        if (
            space_data.get("space_type") == "garage"
            and pid == my_id
            and space_data.get("reward_special")
            in (
                "quest_and_coins",
                "quest_and_intrigue",
                "reset_quests",
            )
        ):
            board_data = self.game_state.get("board", {})
            quests = board_data.get(
                "face_up_quests",
                [],
            )
            quest_ids = [q.get("id") for q in quests if q.get("id")]
            self._enter_highlight_mode(
                "quest_selection",
                quest_ids,
            )
            if self.tabbed_panel:
                self.tabbed_panel.add_entry("Click a quest card to select it")
            return

        # Building with draw_contract during reassignment
        bt = space_data.get("building_tile", {})
        if (
            space_data.get("space_type") == "building"
            and bt.get("visitor_reward_special") == "draw_contract"
            and pid == my_id
        ):
            board_data = self.game_state.get("board", {})
            quests = board_data.get("face_up_quests", [])
            quest_ids = [q.get("id") for q in quests if q.get("id")]
            self._enter_highlight_mode(
                "quest_selection",
                quest_ids,
            )
            if self.tabbed_panel:
                self.tabbed_panel.add_entry("Click a quest card to select it")

    def _on_round_end(self, msg: dict) -> None:
        next_round = msg.get("next_round", 0)
        bonus = msg.get("bonus_worker_granted", False)
        turn_order = msg.get("turn_order", [])

        self.game_state["current_round"] = next_round
        self.game_state["current_player_index"] = 0
        self.game_state["phase"] = "placement"
        self.game_state.pop("reassignment_queue", None)
        if turn_order:
            self.game_state["turn_order"] = turn_order

        # Reset workers and clear board
        for p in self.game_state.get("players", []):
            total = p.get("total_workers", 0)
            if bonus:
                total += 1
                p["total_workers"] = total
            p["available_workers"] = total
            p["completed_quest_this_turn"] = False

        board = self.game_state.get("board", {})
        for space in board.get("action_spaces", {}).values():
            space["occupied_by"] = None
        for slot in board.get("backstage_slots", []):
            slot["occupied_by"] = None
            slot["intrigue_card_played"] = None

        accum_stocks = msg.get("accumulated_stocks", {})
        spaces = board.get("action_spaces", {})
        for space_id, stock in accum_stocks.items():
            bt = spaces.get(space_id, {}).get("building_tile")
            if bt:
                bt["accumulated_stock"] = stock

        self._refresh_board(board)

        my_id = getattr(self.window, "player_id", None)
        if self.resource_bar:
            for p in self.game_state.get("players", []):
                if p.get("player_id") == my_id:
                    self.resource_bar.update_resources(p.get("resources", {}))
                    break

        # Update turn indicator
        if turn_order:
            first_pid = turn_order[0]
            if first_pid == my_id:
                self._status_text = f"Round {next_round} — YOUR TURN"
                arcade.play_sound(self._turn_sound)
            else:
                name = self._player_name(first_pid)
                self._status_text = f"Round {next_round} — {name}'s turn"
        else:
            self._status_text = f"Round {next_round}"

        if self.tabbed_panel:
            self.tabbed_panel.add_entry(f"--- Round {next_round} ---")
            if bonus:
                self.tabbed_panel.add_entry("All players gained a bonus worker!")

    def _on_bonus_workers(self, msg: dict) -> None:
        new_count = msg.get("new_worker_count", 0)
        if self.tabbed_panel:
            self.tabbed_panel.add_entry(
                f"Round 5: All players now have {new_count} workers!"
            )

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def on_mouse_scroll(
        self,
        x: int,
        y: int,
        scroll_x: int,
        scroll_y: int,
    ) -> None:
        if not self.tabbed_panel:
            return
        s = self.window.ui_scale
        cw = self.window.content_width
        ch = self.window.content_height
        bar_h = int(100 * s)
        status_h = int(50 * s)
        log_w = int(450 * s)
        log_x = cw - log_w
        log_y = bar_h
        log_h = ch - bar_h - status_h
        if log_x <= x <= log_x + log_w and log_y <= y <= log_y + log_h:
            if self.tabbed_panel.active_tab == "game_log":
                self.tabbed_panel.scroll(-int(scroll_y))

    def on_mouse_press(
        self,
        x: int,
        y: int,
        button: int,
        modifiers: int,
    ) -> None:
        """Handle clicks on the board to place or reassign workers."""
        if self._show_final_screen:
            rect = getattr(self, "_fs_close_rect", None)
            if rect:
                rx, ry, rw, rh = rect
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    if self._game_over_final:
                        self.window.network.disconnect()
                        self.window.show_lobby()
                    else:
                        self._show_final_screen = False
            return

        if self.tabbed_panel and self.tabbed_panel.on_click(x, y):
            return

        if self._card_sprite_dialog:
            if self._card_sprite_dialog.on_click(x, y):
                return

        if self._quest_completion_dialog:
            if self._quest_completion_dialog.handle_click(
                x,
                y,
            ):
                return

        if self._highlight_mode:
            self._handle_highlight_click(x, y)
            return

        if not self.board_renderer:
            return

        phase = self.game_state.get("phase", "")
        my_id = getattr(self.window, "player_id", None)

        if phase == "reassignment":
            self._handle_reassignment_click(x, y)
            return

        turn_order = self.game_state.get("turn_order", [])
        idx = self.game_state.get("current_player_index", 0)
        if not turn_order or idx >= len(turn_order):
            return
        if turn_order[idx] != my_id:
            return  # Not my turn

        space_id = self.board_renderer.get_space_at(x, y)
        if space_id:
            if space_id.startswith("backstage_slot_"):
                self._handle_backstage_click(space_id)
            else:
                self.window.network.send(
                    {
                        "action": "place_worker",
                        "space_id": space_id,
                    }
                )

    def _handle_reassignment_click(
        self,
        x: int,
        y: int,
    ) -> None:
        """During reassignment, click an action space to reassign."""
        my_id = getattr(self.window, "player_id", None)
        queue = self.game_state.get("reassignment_queue", [])
        if not queue:
            return

        current_slot = queue[0]

        # Check this slot belongs to me
        board = self.game_state.get("board", {})
        slot_owner = None
        for s in board.get("backstage_slots", []):
            if s.get("slot_number") == current_slot:
                slot_owner = s.get("occupied_by")
                break
        if slot_owner != my_id:
            self._status_text = "Waiting for another player to reassign"
            return

        space_id = self.board_renderer.get_space_at(x, y)
        if not space_id:
            return

        if space_id.startswith("backstage_slot_"):
            self._status_text = "Cannot reassign to a Backstage slot"
            return

        self.window.network.send(
            {
                "action": "reassign_worker",
                "slot_number": current_slot,
                "target_space_id": space_id,
            }
        )

    def _handle_backstage_click(self, space_id: str) -> None:
        """Handle click on a backstage slot — show intrigue card selection."""
        slot_number = int(space_id.split("_")[-1])

        my_player = self._get_my_player()
        if not my_player:
            return

        board = self.game_state.get("board", {})
        backstage = board.get("backstage_slots", [])
        for s in backstage:
            if s.get("slot_number") == slot_number and s.get("occupied_by") is not None:
                self._status_text = "That Backstage slot is occupied"
                return

        intrigue_cards = my_player.get("intrigue_hand", [])
        if not intrigue_cards:
            self._status_text = "You need an intrigue card" " to place here"
            return

        for s in backstage:
            if s.get("slot_number", 0) < slot_number and s.get("occupied_by") is None:
                self._status_text = f"Backstage {s['slot_number']} must be filled first"
                return

        def on_select(card_id: str) -> None:
            self._card_sprite_dialog = None
            self.window.network.send(
                {
                    "action": "place_worker_backstage",
                    "slot_number": slot_number,
                    "intrigue_card_id": card_id,
                }
            )

        def on_cancel() -> None:
            self._card_sprite_dialog = None

        self._card_sprite_dialog = CardSpriteSelectionDialog(
            title="Select an Intrigue Card",
            cards=intrigue_cards,
            card_type="intrigue",
            on_select=on_select,
            on_cancel=on_cancel,
        )

    def _enter_building_highlight(
        self,
        pid: str,
    ) -> None:
        player_coins = 0
        for p in self.game_state.get("players", []):
            if p.get("player_id") == pid:
                player_coins = p.get(
                    "resources",
                    {},
                ).get("coins", 0)
                break
        affordable = [
            b.get("id")
            for b in self._face_up_buildings
            if b.get("cost_coins", 999) <= player_coins and b.get("id")
        ]
        if not affordable:
            self._status_text = "You can't afford any buildings"
            self._show_info_dialog(
                "You don't have enough coins" " to buy any buildings.",
            )
            self.window.network.send(
                {
                    "action": "cancel_purchase_building",
                }
            )
            return
        self._enter_highlight_mode(
            "building_purchase",
            affordable,
        )
        if self.tabbed_panel:
            self.tabbed_panel.add_entry("Click a building to purchase it")

    def _handle_highlight_click(
        self,
        x: int,
        y: int,
    ) -> None:
        # Check cancel button
        if self._cancel_sprite and self._cancel_sprite.visible:
            sx = self._cancel_sprite.center_x
            sy = self._cancel_sprite.center_y
            hw = self._cancel_sprite.width / 2
            hh = self._cancel_sprite.height / 2
            if sx - hw <= x <= sx + hw and sy - hh <= y <= sy + hh:
                if self._highlight_mode == "quest_selection":
                    self.window.network.send(
                        {
                            "action": "cancel_quest_selection",
                        }
                    )
                    if self.tabbed_panel:
                        self.tabbed_panel.add_entry("Quest selection cancelled")
                elif self._highlight_mode == "building_purchase":
                    self.window.network.send(
                        {
                            "action": "cancel_purchase_building",
                        }
                    )
                    if self.tabbed_panel:
                        self.tabbed_panel.add_entry("Building purchase cancelled")
                self._exit_highlight_mode()
                return

        if not self.board_renderer:
            return

        clicked = self.board_renderer.get_space_at(x, y)
        if not clicked:
            return

        if self._highlight_mode == "quest_selection":
            if clicked.startswith("quest_card_"):
                qid = clicked[len("quest_card_") :]
                if qid in self._highlighted_ids:
                    self.window.network.send(
                        {
                            "action": "select_quest_card",
                            "card_id": qid,
                        }
                    )
                    self._exit_highlight_mode()
        elif self._highlight_mode == "building_purchase":
            if clicked.startswith("building_card_"):
                bid = clicked[len("building_card_") :]
                if bid in self._highlighted_ids:
                    self.window.network.send(
                        {
                            "action": "purchase_building",
                            "building_id": bid,
                        }
                    )
                    self._exit_highlight_mode()
                else:
                    self._status_text = "You can't afford that building"
                    self._show_info_dialog(
                        "You don't have enough coins" " for that building.",
                    )
        elif self._highlight_mode == "building_reward":
            if clicked.startswith("building_card_"):
                bid = clicked[len("building_card_") :]
                if bid in self._highlighted_ids:
                    self.window.network.send(
                        {
                            "action": "quest_reward_choice",
                            "choice_id": bid,
                        }
                    )
                    self._exit_highlight_mode()
        elif self._highlight_mode == "worker_recall":
            if clicked in self._highlighted_ids:
                self.window.network.send(
                    {
                        "action": "recall_worker",
                        "space_id": clicked,
                    }
                )
                self._exit_highlight_mode()

    def _enter_highlight_mode(
        self,
        mode: str,
        ids: list[str],
    ) -> None:
        self._highlight_mode = mode
        self._highlighted_ids = ids
        if self._cancel_sprite:
            self._cancel_sprite.visible = True

    def _exit_highlight_mode(self) -> None:
        self._highlight_mode = None
        self._highlighted_ids = []
        if self._cancel_sprite:
            self._cancel_sprite.visible = False

    def _show_info_dialog(self, message: str) -> None:
        s = self.window.ui_scale
        v_box = arcade.gui.UIBoxLayout(
            space_between=int(10 * s),
        )
        label = arcade.gui.UILabel(
            text=message,
            font_size=max(8, int(14 * s)),
            text_color=arcade.color.WHITE,
            multiline=True,
            width=int(300 * s),
        )
        v_box.add(label)

        ok_btn = arcade.gui.UIFlatButton(
            text="OK",
            width=int(120 * s),
            height=int(40 * s),
        )

        anchor = arcade.gui.UIAnchorLayout()
        widget = self.ui.add(anchor)

        def dismiss(_event=None):
            self.ui.remove(widget)

        ok_btn.on_click = dismiss
        v_box.add(ok_btn)
        bg_box = v_box.with_padding(
            all=int(20 * s),
        ).with_background(color=(0, 0, 0))
        anchor.add(
            child=bg_box,
            anchor_x="center",
            anchor_y="center",
        )

    def _toggle_player_overview(self) -> None:
        self._show_player_overview = not self._show_player_overview

    def _toggle_final_screen(self) -> None:
        if self._game_over_final:
            return
        self._show_final_screen = not self._show_final_screen
        self._fs_card_sprites = None

    def _calculate_scores_from_state(self) -> list[dict]:
        players = self.game_state.get("players", [])
        my_id = getattr(self.window, "player_id", None)
        scores = []
        for p in players:
            game_vp = p.get("victory_points", 0)
            res = p.get("resources", {})
            resource_vp = (
                res.get("guitarists", 0)
                + res.get("bass_players", 0)
                + res.get("drummers", 0)
                + res.get("singers", 0)
                + res.get("coins", 0) // 2
            )
            genre_bonus_vp = 0
            is_me = p.get("player_id") == my_id
            pc = p.get("producer_card")
            if pc and is_me:
                bonus_genres = pc.get("bonus_genres", [])
                bvp = pc.get("bonus_vp_per_contract", 4)
                for c in p.get("completed_contracts", []):
                    if c.get("genre") in bonus_genres:
                        genre_bonus_vp += bvp
            genre_known = is_me or False
            scores.append(
                {
                    "player_id": p.get("player_id", ""),
                    "player_name": p.get("display_name", "???"),
                    "game_vp": game_vp,
                    "genre_bonus_vp": genre_bonus_vp,
                    "genre_known": genre_known,
                    "resource_vp": resource_vp,
                    "total_vp": game_vp + genre_bonus_vp + resource_vp,
                    "producer_card": pc or {},
                }
            )
        scores.sort(key=lambda x: x["total_vp"], reverse=True)
        return scores

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def on_draw(self) -> None:
        self.clear()

        s = self.window.ui_scale
        cw = self.window.content_width
        ch = self.window.content_height

        bar_h = int(100 * s)
        status_h = int(50 * s)
        log_w = int(450 * s)
        board_w = cw - log_w
        board_h = ch - bar_h - status_h

        if s != self._btn_scale:
            self._rebuild_buttons()
        elif self._btn_anchor and self._btn_anchor._children:
            self._btn_anchor._children[0].data["align_y"] = bar_h + 5

        if self.board_renderer:
            self.board_renderer.draw(
                0,
                bar_h,
                board_w,
                board_h,
                highlighted_ids=self._highlighted_ids,
                scale=s,
            )

        if self.resource_bar:
            my_id = getattr(self.window, "player_id", None)
            workers_left = 0
            vp = 0
            intrigue_count = 0
            quests_open = 0
            quests_closed = 0
            player_color = ""
            for p in self.game_state.get("players", []):
                if p.get("player_id") == my_id:
                    workers_left = p.get("available_workers", 0)
                    vp = p.get("victory_points", 0)
                    intrigue_count = len(p.get("intrigue_hand", []))
                    quests_open = len(p.get("contract_hand", []))
                    quests_closed = len(p.get("completed_contracts", []))
                    if self.board_renderer:
                        player_color = self.board_renderer._player_color_name(my_id)
                    break
            self.resource_bar.draw(
                0,
                0,
                cw,
                bar_h,
                workers_left,
                vp,
                intrigue_count=intrigue_count,
                quests_open=quests_open,
                quests_closed=quests_closed,
                scale=s,
                player_color=player_color,
            )

        if self.tabbed_panel:
            self.tabbed_panel.draw(
                cw - log_w,
                bar_h,
                log_w,
                board_h,
                player_data=self._get_my_player(),
                scale=s,
            )

        if self._show_player_overview:
            self._draw_player_overview_panel(cw, ch, s)

        if self._show_final_screen:
            self._draw_final_screen(cw, ch, s)

        # Cancel button for highlight mode
        if (
            self._highlight_mode
            and self._cancel_sprite
            and self._cancel_sprite.visible
            and self._cancel_sprite_list
        ):
            self._cancel_sprite.scale = 0.5 * s
            self._cancel_sprite.position = (55 * s, 55 * s)
            self._cancel_sprite_list.draw()

        # Quest completion card dialog
        if self._quest_completion_dialog:
            self._quest_completion_dialog.draw(cw, ch, scale=s)

        # Card sprite selection dialog
        if self._card_sprite_dialog:
            self._card_sprite_dialog.draw(cw, ch, scale=s)

        # Status bar
        status_y = ch - status_h / 2
        arcade.draw_rect_filled(
            arcade.rect.XYWH(cw / 2, status_y, cw, status_h),
            arcade.color.BLACK,
        )
        self._text(
            "status",
            self._status_text,
            cw / 2,
            status_y,
            arcade.color.WHITE,
            max(8, int(16 * s)),
            anchor_x="center",
            anchor_y="center",
        ).draw()

        self._draw_player_list(ch, status_h, s)

        self.ui.draw()

    def _draw_player_overview_panel(
        self,
        w: float,
        h: float,
        s: float = 1.0,
    ) -> None:
        players = self.game_state.get("players", [])
        my_id = getattr(self.window, "player_id", None)

        panel_w = min(w - 40 * s, 1300 * s)
        row_count = len(players) + 1
        row_h = int(36 * s)
        panel_h = min(
            h - 80 * s,
            70 * s + row_count * row_h,
        )
        panel_x = w / 2
        panel_y = h / 2

        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                panel_x,
                panel_y,
                panel_w,
                panel_h,
            ),
            (0, 0, 0),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(
                panel_x,
                panel_y,
                panel_w,
                panel_h,
            ),
            arcade.color.WHITE,
            border_width=2,
        )

        self._text(
            "po_title",
            "Player Overview",
            panel_x,
            panel_y + panel_h / 2 - 22 * s,
            arcade.color.WHITE,
            max(8, int(20 * s)),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

        headers = [
            "#",
            "Name",
            "Workers",
            "Guitarists",
            "Bass",
            "Drummers",
            "Singers",
            "Coins",
            "Intrigue",
            "Quests",
            "Completed",
            "VP",
        ]
        base_col_widths = [
            35,
            200,
            90,
            105,
            85,
            100,
            90,
            80,
            90,
            85,
            105,
            65,
        ]
        col_widths = [int(cw * s) for cw in base_col_widths]
        total_w = sum(col_widths)
        start_x = panel_x - total_w / 2
        header_y = panel_y + panel_h / 2 - 52 * s
        font_tbl = max(8, int(14 * s))

        cx = start_x
        for i, hdr in enumerate(headers):
            self._text(
                f"po_h_{i}",
                hdr,
                cx + col_widths[i] / 2,
                header_y,
                arcade.color.GOLD,
                font_tbl,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            ).draw()
            cx += col_widths[i]

        turn_order = self.game_state.get("turn_order", [])
        cp_idx = self.game_state.get(
            "current_player_index",
            0,
        )
        current_pid = (
            turn_order[cp_idx] if turn_order and cp_idx < len(turn_order) else None
        )

        for row, p in enumerate(players):
            pid = p.get("player_id", "")
            is_me = pid == my_id
            row_y = header_y - row_h - row * row_h

            if pid == current_pid:
                ax = start_x - 14 * s
                ar = 6 * s
                arcade.draw_triangle_filled(
                    ax,
                    row_y + ar,
                    ax,
                    row_y - ar,
                    ax + ar * 1.4,
                    row_y,
                    arcade.color.GOLD,
                )

            if is_me:
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(
                        panel_x,
                        row_y,
                        total_w + 10,
                        row_h - 4,
                    ),
                    (40, 40, 80),
                )

            res = p.get("resources", {})
            name = p.get("display_name", "???")
            workers = p.get("available_workers", 0)

            if is_me:
                intr = len(p.get("intrigue_hand", []))
                quests = len(p.get("contract_hand", []))
            else:
                intr = p.get(
                    "intrigue_hand_count",
                    len(p.get("intrigue_hand", [])),
                )
                quests = p.get(
                    "contract_hand_count",
                    len(p.get("contract_hand", [])),
                )

            done = len(p.get("completed_contracts", []))
            vp = p.get("victory_points", 0)

            order = p.get("slot_index", 0) + 1

            vals = [
                str(order),
                name,
                str(workers),
                str(res.get("guitarists", 0)),
                str(res.get("bass_players", 0)),
                str(res.get("drummers", 0)),
                str(res.get("singers", 0)),
                str(res.get("coins", 0)),
                str(intr),
                str(quests),
                str(done),
                str(vp),
            ]

            color = arcade.color.WHITE if is_me else arcade.color.LIGHT_GRAY
            cx = start_x
            for i, val in enumerate(vals):
                self._text(
                    f"po_{row}_{i}",
                    val,
                    cx + col_widths[i] / 2,
                    row_y,
                    color,
                    font_tbl,
                    anchor_x="center",
                    anchor_y="center",
                ).draw()
                cx += col_widths[i]

    def _draw_final_screen(
        self,
        w: float,
        h: float,
        s: float = 1.0,
    ) -> None:
        if self._final_scores is not None:
            scores = [
                {
                    **fs,
                    "genre_known": True,
                }
                for fs in self._final_scores
            ]
            scores.sort(key=lambda x: x.get("total_vp", 0), reverse=True)
        else:
            scores = self._calculate_scores_from_state()

        if not scores:
            return

        n = len(scores)
        panel_w = min(w - 40 * s, (280 * n + 60) * s)
        panel_h = min(h - 60 * s, 520 * s)
        px = w / 2
        py = h / 2

        arcade.draw_rect_filled(
            arcade.rect.XYWH(w / 2, h / 2, w, h),
            (0, 0, 0, 160),
        )
        arcade.draw_rect_filled(
            arcade.rect.XYWH(px, py, panel_w, panel_h),
            (20, 20, 30),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(px, py, panel_w, panel_h),
            arcade.color.WHITE,
            border_width=2,
        )

        title = (
            "Final Scores" if not self._game_over_final else "Game Over - Final Scores"
        )
        self._text(
            "fs_title",
            title,
            px,
            py + panel_h / 2 - 25 * s,
            arcade.color.GOLD,
            max(10, int(22 * s)),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        ).draw()

        max_vp = max(sc.get("total_vp", 0) for sc in scores)
        col_w = panel_w / max(n, 1)
        card_h = int(230 * s)
        top_y = py + panel_h / 2 - 55 * s
        val_font = max(8, int(14 * s))
        small_font = max(7, int(11 * s))

        if self._fs_card_sprites is None:
            self._fs_card_sprites = arcade.SpriteList()
            for sc in scores:
                pc = sc.get("producer_card") or {}
                card_id = pc.get("id", "")
                png = Path(f"client/assets/card_images/producers/{card_id}.png")
                if pc.get("name") and png.exists():
                    sp = arcade.Sprite(str(png))
                    sp.visible = True
                    self._fs_card_sprites.append(sp)

        sprite_idx = 0
        for i, sc in enumerate(scores):
            cx = px - panel_w / 2 + col_w * i + col_w / 2
            cur_y = top_y

            if sc.get("total_vp", 0) == max_vp:
                self._text(
                    f"fs_win_{i}",
                    "WINNER",
                    cx,
                    cur_y,
                    arcade.color.GOLD,
                    max(9, int(16 * s)),
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                ).draw()
            cur_y -= 20 * s

            pc = sc.get("producer_card") or {}
            pc_name = pc.get("name", "")
            card_id = pc.get("id", "")
            png = Path(f"client/assets/card_images/producers/{card_id}.png")
            if pc_name and png.exists() and sprite_idx < len(self._fs_card_sprites):
                sp = self._fs_card_sprites[sprite_idx]
                sp.scale = card_h / max(sp.texture.height, 1)
                sp.position = (cx, cur_y - card_h / 2)
                sprite_idx += 1
            elif pc_name:
                self._text(
                    f"fs_nocard_{i}",
                    "No Producer",
                    cx,
                    cur_y - card_h / 2,
                    arcade.color.DARK_GRAY,
                    small_font,
                    anchor_x="center",
                    anchor_y="center",
                ).draw()
            cur_y -= card_h + 10 * s

            self._text(
                f"fs_name_{i}",
                sc.get("player_name", "???"),
                cx,
                cur_y,
                arcade.color.WHITE,
                val_font,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            ).draw()
            cur_y -= 22 * s

            rows = [
                ("Game VP", str(sc.get("game_vp", 0))),
            ]
            if sc.get("genre_known", False):
                rows.append(("Genre Bonus", str(sc.get("genre_bonus_vp", 0))))
            else:
                rows.append(("Genre Bonus", "?"))
            rows.append(("Resource VP", str(sc.get("resource_vp", 0))))

            for label, val in rows:
                self._text(
                    f"fs_l_{i}_{label}",
                    label + ":",
                    cx - 5 * s,
                    cur_y,
                    arcade.color.LIGHT_GRAY,
                    small_font,
                    anchor_x="right",
                    anchor_y="center",
                ).draw()
                self._text(
                    f"fs_v_{i}_{label}",
                    val,
                    cx + 5 * s,
                    cur_y,
                    arcade.color.WHITE,
                    small_font,
                    anchor_x="left",
                    anchor_y="center",
                ).draw()
                cur_y -= 18 * s

            cur_y -= 4 * s
            self._text(
                f"fs_tl_{i}",
                "Total:",
                cx - 5 * s,
                cur_y,
                arcade.color.GOLD,
                val_font,
                anchor_x="right",
                anchor_y="center",
                bold=True,
            ).draw()
            self._text(
                f"fs_tv_{i}",
                str(sc.get("total_vp", 0)),
                cx + 5 * s,
                cur_y,
                arcade.color.GOLD,
                val_font,
                anchor_x="left",
                anchor_y="center",
                bold=True,
            ).draw()

        if self._fs_card_sprites:
            self._fs_card_sprites.draw()

        btn_w = int(100 * s)
        btn_h = int(32 * s)
        btn_x = px
        btn_y = py - panel_h / 2 + 30 * s
        arcade.draw_rect_filled(
            arcade.rect.XYWH(btn_x, btn_y, btn_w, btn_h),
            (80, 80, 100),
        )
        arcade.draw_rect_outline(
            arcade.rect.XYWH(btn_x, btn_y, btn_w, btn_h),
            arcade.color.WHITE,
            border_width=1,
        )
        self._text(
            "fs_close_btn",
            "Close",
            btn_x,
            btn_y,
            arcade.color.WHITE,
            max(8, int(14 * s)),
            anchor_x="center",
            anchor_y="center",
        ).draw()
        self._fs_close_rect = (
            btn_x - btn_w / 2,
            btn_y - btn_h / 2,
            btn_w,
            btn_h,
        )

    @staticmethod
    def _resource_str(res: dict) -> str:
        parts = []
        for key, sym in RESOURCE_SYMBOLS:
            val = res.get(key, 0)
            if val > 0:
                parts.append(f"{val}{sym}")
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Player turn-order list (drawn on the status bar)
    # ------------------------------------------------------------------

    def _draw_player_list(
        self,
        ch: float,
        status_h: float,
        s: float,
    ) -> None:
        if not self.board_renderer:
            return
        turn_order = self.game_state.get("turn_order", [])
        players = self.game_state.get("players", [])
        if not turn_order or not players:
            return

        player_map = {p["player_id"]: p for p in players}
        idx = self.game_state.get("current_player_index", 0)
        current_pid = turn_order[idx] if idx < len(turn_order) else None

        font_sz = max(10, int(14 * s))
        vp_font_sz = max(8, int(11 * s))
        circle_r = max(4, int(7 * s))
        gap = int(8 * s)
        bar_bot = ch - status_h
        row_top = bar_bot + status_h * 0.65
        row_bot = bar_bot + status_h * 0.28
        list_x = int(10 * s)

        for i, pid in enumerate(turn_order):
            p = player_map.get(pid)
            if not p:
                continue
            color = self.board_renderer._player_color(pid)
            is_current = pid == current_pid
            cx = list_x + circle_r
            arcade.draw_circle_filled(cx, row_top, circle_r, color)
            name = p.get("display_name", "???")
            if is_current:
                name = f"> {name}"
            txt = self._text(
                f"plist_{i}",
                name,
                cx + circle_r + gap,
                row_top,
                arcade.color.WHITE,
                font_sz,
                bold=is_current,
                anchor_x="left",
                anchor_y="center",
            )
            txt.bold = is_current
            txt.draw()
            vp = p.get("victory_points", 0)
            vp_txt = self._text(
                f"plist_vp_{i}",
                f"{vp} VP",
                cx + circle_r + gap,
                row_bot,
                arcade.color.LIGHT_GRAY,
                vp_font_sz,
                anchor_x="left",
                anchor_y="center",
            )
            vp_txt.draw()
            list_x = int(cx + circle_r + gap + txt.content_width + int(30 * s))

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
            t.font_size = font_size
            return t
        t = arcade.Text(
            text,
            x,
            y,
            color,
            font_size=font_size,
            font_name="Tahoma",
            **kwargs,
        )
        self._text_cache[key] = t
        return t

    def _get_my_player(self) -> dict | None:
        """Return the local player's data dict, or None."""
        my_id = getattr(self.window, "player_id", None)
        for p in self.game_state.get("players", []):
            if p.get("player_id") == my_id:
                return p
        return None

    def _player_name(self, player_id: str) -> str:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                return p.get("display_name", "???")
        return "???"

    @staticmethod
    def _format_intrigue_effect(
        effect_type: str,
        details: dict,
    ) -> str:
        if effect_type in ("gain_resources", "all_players_gain"):
            parts = []
            for k, sym in RESOURCE_SYMBOLS:
                v = details.get(k, 0)
                if v:
                    parts.append(f"+{v}{sym}")
            gained = details.get("all_gained", {})
            for k, sym in RESOURCE_SYMBOLS:
                v = gained.get(k, 0)
                if v:
                    parts.append(f"+{v}{sym} (all)")
            return " ".join(parts)
        if effect_type == "gain_coins":
            c = details.get("coins", 0)
            return f"+{c}$" if c else ""
        if effect_type == "vp_bonus":
            vp = details.get("victory_points", 0)
            return f"+{vp} VP" if vp else ""
        if effect_type == "draw_contracts":
            n = len(details.get("drawn", []))
            return f"Drew {n} quest(s)"
        if effect_type == "draw_intrigue":
            n = len(details.get("drawn", []))
            return f"Drew {n} intrigue card(s)"
        return ""

    def _apply_reward_to_player(self, player_id: str, reward: dict) -> None:
        for p in self.game_state.get("players", []):
            if p.get("player_id") == player_id:
                res = p.get("resources", {})
                keys = (
                    "guitarists",
                    "bass_players",
                    "drummers",
                    "singers",
                    "coins",
                )
                for key in keys:
                    amt = reward.get(key, 0)
                    res[key] = res.get(key, 0) + amt
                vp = reward.get("victory_points", 0)
                if vp:
                    p["victory_points"] = p.get("victory_points", 0) + vp
                my_id = getattr(self.window, "player_id", None)
                if player_id == my_id and self.resource_bar:
                    self.resource_bar.update_resources(res)
                break

    def _play_reassignment_sound_if_my_turn(self) -> None:
        queue = self.game_state.get("reassignment_queue", [])
        if not queue:
            return
        my_id = getattr(self.window, "player_id", None)
        board = self.game_state.get("board", {})
        for s in board.get("backstage_slots", []):
            if s.get("slot_number") == queue[0]:
                if s.get("occupied_by") == my_id:
                    arcade.play_sound(self._turn_sound)
                return

    def _update_current_player(self, next_pid: str | None) -> None:
        if next_pid is None:
            return
        turn_order = self.game_state.get("turn_order", [])
        if next_pid in turn_order:
            idx = turn_order.index(next_pid)
            self.game_state["current_player_index"] = idx
        if self.board_renderer:
            self.board_renderer._current_player_id = next_pid
        my_id = getattr(self.window, "player_id", None)
        rnd = self.game_state.get("current_round", "?")
        phase = self.game_state.get("phase", "placement")
        phase_label = "Reassignment" if phase == "reassignment" else f"Round {rnd}"
        if next_pid == my_id:
            self._status_text = f"{phase_label} — YOUR TURN"
            arcade.play_sound(self._turn_sound)
        else:
            name = self._player_name(next_pid)
            self._status_text = f"{phase_label} — {name}'s turn"
