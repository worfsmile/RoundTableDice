import tkinter as tk
from tkinter import messagebox, simpledialog
from Game import Game
from Player import Player1, Player2, Player3, Player4
from Decision import Decision
import random

class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Liar Dice Game")
        self.root.geometry("600x500")

        self.num_dice = 4
        self.num_per_round = 10

        self.players = [Player1("Peter"), Player1("Lois"), Player1("Brian"), Player1("Stewie")]
        self.player_types = {"Player1": Player1, "Player2": Player2, "Player3": Player3, "Player4": Player4}

        self.main_menu()

    def start_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.game = Game(self.num_dice, self.players)
        self.current_round_index = 1
        self.message_history = []

        # 标题
        title_label = tk.Label(self.root, text="🎮 游戏进行中", font=("Helvetica", 20))
        title_label.pack(pady=10)

        # 模式选择：单步 or 一次到底
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)
        self.auto_mode = tk.BooleanVar(value=False)
        tk.Radiobutton(mode_frame, text="显示历史", variable=self.auto_mode, value=True).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="隐藏历史", variable=self.auto_mode, value=False).pack(side=tk.LEFT)

        # 控制按钮
        ctl_frame = tk.Frame(self.root)
        ctl_frame.pack(pady=5)
        self.step_button = tk.Button(ctl_frame, text="下一步", command=self.on_step)
        self.step_button.pack(side=tk.LEFT, padx=5)
        self.run_button  = tk.Button(ctl_frame, text="运行到结束", command=self.on_run)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 14))
        self.status_label.pack()

        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.text_widget = tk.Text(self.text_frame, state="disabled", wrap="word")
        self.text_widget.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_widget.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self.game.roundStart()

        status_button = tk.Button(self.root, text="🎲 当前状态", font=("Helvetica", 12), command=self.show_status)
        status_button.place(x=480, y=10)

        back_button = tk.Button(self.root, text="返回", font=("Helvetica", 12), command=self.main_menu)
        back_button.place(x=480, y=50)

        first = self.game._getNextPlayer().name
        self.status_var.set(f"第 1 轮／共 {self.num_per_round} 轮    当前玩家：{first}")

    def on_step(self):
        """单步执行一次 next_turn"""
        finished = self.next_turn()
        if finished:
            # 回合结束后禁用按钮
            self.step_button.config(state="disabled")
            self.run_button .config(state="disabled")

    def on_run(self):
        """一次性跑完整场（所有回合）"""
        # 禁用“下一步”按钮
        self.step_button.config(state="disabled")
        self.run_button .config(state="disabled")
        # 当 next_turn 返回 False 时不断循环
        def loop():
            if not self.next_turn():
                # 继续下一次
                self.root.after(50, loop)
        loop()

    def next_turn(self):
        """
        执行一个决策回合，返回 True 表示本局（所有回合）已结束，
        返回 False 则表示本轮（单回合）尚未结束，需要继续循环。
        """
        finished = self.game.turn(print_out=False)
        ret = False
        msg = ""
        if not finished:
            # 本回合还在进行，展示最新一次的决策
            # 注意：此时 self.game.current_round 一定不为 None
            name, decision = self.game.current_round.decisions[-1]
            msg += f"👉 {name} 叫了 {decision.dice_num} 个 {decision.dice_point}"

            # 更新状态栏：当前回合、当前玩家
            next_player = self.game._getNextPlayer().name
            self.status_var.set(
                f"第 {self.current_round_index} 轮／共 {self.num_per_round} 轮    当前玩家：{next_player}"
            )
           

        else:
            msg += f"👉 {finished[0]} 选择开 {finished[1].opened_player}\n"
            # 本回合结束
            last_round = self.game.rounds[-1]
            loser = last_round.loser.name
            msg += f"❌ 第 {self.current_round_index} 轮 结束，{loser} 输了!\n"
            # 显示所有玩家的骰子
            for pname, dices in last_round.dices.items():
                msg += f"{pname} 的骰子: {dices}\n"
            # 显示最新比分
            for p in self.players:
                msg += f"{p.name} 分数: {p.score}\n"

            # 判断是否全部回合结束
            if self.current_round_index >= self.num_per_round:
                # 整场比赛结束
                self.end_game()
                ret = True
            else:
                # 进入下一回合
                self.current_round_index += 1
                msg += f"\n📢 开始第 {self.current_round_index} 轮！"
                self.game.roundStart()
                # 更新状态栏为下一回合首个玩家
                first_player = self.game._getNextPlayer().name
                self.status_var.set(
                    f"第 {self.current_round_index} 轮／共 {self.num_per_round} 轮    当前玩家：{first_player}"
                )

        self.message_history.append(msg)
        if self.auto_mode.get():
            message = "\n".join(self.message_history)
            self.append_message(message)

        return ret

    def show_status(self):
        status_win = tk.Toplevel(self.root)
        status_win.title("当前状态")
        status_win.geometry("300x300")

        for player in self.players:
            dices = player.dices if hasattr(player, 'dices') else []
            label = tk.Label(status_win, text=f"{player.name}: 🎲 {dices}   分数: {player.score}")
            label.pack(anchor="w", padx=10, pady=5)

    def append_message(self, msg):
        if hasattr(self, 'text_widget') and self.text_widget.winfo_exists():
            self.text_widget.config(state="normal")
            # 清空所有内容
            self.text_widget.delete("1.0", tk.END)
            # 插入新内容
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see("end")
            self.text_widget.config(state="disabled")

    def end_game(self):
        self.append_message("🏁 游戏结束！最终得分：")
        scores = [(p.name, p.score) for p in self.players]
        for name, score in scores:
            self.append_message(f"{name}: {score}")

        tk.messagebox.showinfo("游戏结束", "\n".join([f"{n}: {s}" for n, s in scores]))
        self.main_menu()

    def main_menu(self):
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()

        # 主标题
        title_label = tk.Label(self.root, text="🎲 Liar Dice Game 🎲", font=("Helvetica", 20))
        title_label.pack(pady=50)

        dice_label = tk.Label(self.root, text="🎲", font=("Helvetica", 100))
        dice_label.pack(pady=30)

        self.animate_dice(dice_label)  # 启动动画

        start_button = tk.Button(self.root, text="开始游戏", font=("Helvetica", 14), command=self.start_game)
        start_button.pack(side="bottom", pady=20)

        # 设置按钮
        setting_button = tk.Button(self.root, text="设置", font=("Helvetica", 12), command=self.setting)
        setting_button.place(x=480, y=10)

        # 帮助按钮
        help_button = tk.Button(self.root, text="帮助", font=("Helvetica", 12), command=self.help)
        help_button.place(x=480, y=50)

        # 退出按钮
        quit_button = tk.Button(self.root, text="退出", font=("Helvetica", 12), command=self.root.quit)
        quit_button.place(x=480, y=90)
    
    def setting(self):
        setting_window = tk.Toplevel(self.root)
        setting_window.title("游戏设置")

        tk.Label(setting_window, text="选择玩家数量:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(setting_window, text="选择每局骰子数:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(setting_window, text="每局的round数:").grid(row=2, column=0, padx=5, pady=5)

        player_count_var = tk.IntVar(value=4)
        num_dice_var = tk.IntVar(value=4)
        num_rounds_var = tk.IntVar(value=10)

        spinbox = tk.Spinbox(setting_window, from_=3, to=6, textvariable=player_count_var, width=5)
        spinbox.grid(row=0, column=1, padx=5, pady=5)

        spinbox = tk.Spinbox(setting_window, from_=1, to=20, textvariable=num_dice_var, width=5)
        spinbox.grid(row=1, column=1, padx=5, pady=5)

        spinbox = tk.Spinbox(setting_window, from_=10, to=1000, textvariable=num_rounds_var, width=5)
        spinbox.grid(row=2, column=1, padx=5, pady=5)

        player_frame = tk.Frame(setting_window)
        player_frame.grid(row=4, column=0, columnspan=2, pady=10)

        player_type_vars = []
        player_name_vars = []

        def refresh_player_settings():
            for widget in player_frame.winfo_children():
                widget.destroy()
            player_type_vars.clear()
            player_name_vars.clear()

            num_players = player_count_var.get()
            for i in range(num_players):
                tk.Label(player_frame, text=f"玩家{i+1} 类型:").grid(row=i, column=0, padx=5, pady=2, sticky='e')
                type_var = tk.StringVar(value="Player1")
                type_menu = tk.OptionMenu(player_frame, type_var, "Player1", "Player2", "Player3", "Player4")
                type_menu.grid(row=i, column=1, padx=5, pady=2)
                player_type_vars.append(type_var)

                tk.Label(player_frame, text="名字:").grid(row=i, column=2, padx=5, pady=2, sticky='e')
                name_var = tk.StringVar(value=f"Player{i+1}")
                name_entry = tk.Entry(player_frame, textvariable=name_var)
                name_entry.grid(row=i, column=3, padx=5, pady=2)
                player_name_vars.append(name_var)

        refresh_player_settings()

        refresh_button = tk.Button(setting_window, text="确定", command=refresh_player_settings)
        refresh_button.grid(row=3, column=0, columnspan=2, pady=5)

        def apply_settings():
            num_players = player_count_var.get()
            self.num_dice = num_dice_var.get()
            self.num_per_round = num_rounds_var.get()
            selected_players = []

            for i in range(num_players):
                cls_name = player_type_vars[i].get()
                player_cls = self.player_types[cls_name]
                player_name = player_name_vars[i].get()
                selected_players.append(player_cls(player_name))

            self.players = selected_players
            self.game = Game(num_players, self.players)
            messagebox.showinfo("设置完成", f"已设置 {num_players} 位玩家。")
            setting_window.destroy()

        apply_button = tk.Button(setting_window, text="应用设置", command=apply_settings)
        apply_button.grid(row=5, column=0, columnspan=2, pady=10)

    def help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("游戏说明 / Help")
        help_window.geometry("600x500")

        help_text = (
            "📋 Overview\n\n"
            "RoundTableDice is a turn-based multiplayer dice game that blends hidden information, bluffing, and challenging mechanics.\n"
            "Each player rolls dice in secret and takes turns making claims about the total dice values. Others can choose to believe or challenge the claim — at their own risk.\n\n"
            "👥 Players and Setup\n"
            "* Players: n players, labeled p1, p2, ..., pn\n"
            "* Dice: Each player has m standard 6-sided dice\n"
            "* Visibility: Players can only see their own dice\n\n"
            "🔁 Game Loop\n\n"
            "🧍 1. Starting the Game\n"
            "* The player who lost the previous round goes first.\n"
            "* If it's the first round, player p1 starts.\n\n"
            "🗣️ 2. Making a Claim\n"
            "* On a player's turn, they claim: “There are at least l dice showing value k.”\n"
            "* l ≥ 1, k ∈ {1..6}\n"
            "* This includes all players’ dice.\n\n"
            "🤔 3. Other Players Decide\n"
            "* Each other player can Pass (accept) or Challenge (dispute the claim).\n\n"
            "❓ Challenge Resolution\n"
            "* If someone challenges:\n"
            "  1. Reveal all dice\n"
            "  2. Count dice showing value k (or +1s if Wild Ones enabled)\n"
            "  3. If actual ≥ claim → challenger loses, else → claimer loses\n"
            "* Loser starts next round\n\n"
            "🔂 If No One Challenges:\n"
            "* Turn passes to next player\n"
            "* New claim must be stronger (l' > l or same l and higher k)\n\n"
            "🏁 Ending a Round\n"
            "* Round ends after a challenge\n"
            "* Loser starts next round\n\n"
            "🧮 Optional Scoring\n"
            "* +1 point for winning challenge\n"
            "* –1 point for losing\n"
            "* First to threshold wins\n\n"
            "📌 Example:\n"
            "* Player 1: “At least 4 dice showing 3”\n"
            "* Player 2 passes\n"
            "* Player 3 challenges\n"
            "* Revealed dice show 5 threes \n"
            "* Player 3 loses and starts next round"
        )

        text_widget = tk.Text(help_window, wrap="word", font=("Helvetica", 11))
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

    def animate_dice(self, dice_label):
        dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        new_face = random.choice(dice_emojis)
        if dice_label.winfo_exists():
            dice_label.config(text=new_face)
            self.root.after(1000, self.animate_dice, dice_label)

    def quit(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game_ui = GameUI(root)
    root.mainloop()
