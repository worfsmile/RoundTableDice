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

        self.players = [Player1("Peter"), Player2("Lois"), Player3("Brian"), Player4("Stewie")]
        self.player_types = {"Player1": Player1, "Player2": Player2, "Player3": Player3, "Player4": Player4}

        self.main_menu()

    def main_menu(self):
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()

        # 主标题
        title_label = tk.Label(self.root, text="🎲 Liar Dice Game 🎲", font=("Helvetica", 20))
        title_label.pack(pady=50)

        self.dice_label = tk.Label(self.root, text="🎲", font=("Helvetica", 100))
        self.dice_label.pack(pady=30)

        self.animate_dice()  # 启动动画

        # 开始游戏按钮
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

    def start_game(self):
        pass

    def next_turn(self):
        pass

    def setting(self):
        setting_window = tk.Toplevel(self.root)
        setting_window.title("游戏设置")

        tk.Label(setting_window, text="选择玩家数量:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(setting_window, text="选择每局骰子数:").grid(row=1, column=0, padx=5, pady=5)

        player_count_var = tk.IntVar(value=4)
        num_dice_var = tk.IntVar(value=4)

        spinbox = tk.Spinbox(setting_window, from_=3, to=6, textvariable=player_count_var, width=5)
        spinbox.grid(row=0, column=1, padx=5, pady=5)

        spinbox = tk.Spinbox(setting_window, from_=1, to=20, textvariable=num_dice_var, width=5)
        spinbox.grid(row=1, column=1, padx=5, pady=5)

        player_frame = tk.Frame(setting_window)
        player_frame.grid(row=2, column=0, columnspan=2, pady=10)

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
        refresh_button.grid(row=1, column=2, columnspan=2, pady=5)

        def apply_settings():
            num_players = player_count_var.get()
            self.num_dice = num_dice_var.get()
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
        apply_button.grid(row=3, column=0, columnspan=2, pady=10)

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

    def animate_dice(self):
        dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        new_face = random.choice(dice_emojis)
        self.dice_label.config(text=new_face)
        self.root.after(1000, self.animate_dice)

    def quit(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game_ui = GameUI(root)
    root.mainloop()