

class Decision:
    """一次决策: 开人 or 报点"""
    def __init__(self):
        self.open: bool = False # 是否开人

        self.opened_player: str = None
        self.dice_num: int = 1      # 骰子个数
        self.dice_point: int = 1    # # 骰子点数

    def makeOpen(self, player_name: str) -> None:
        self.open = True
        self.opened_player = player_name

    def makeGuess(self, dice_num: int, dict_point: int) -> None:
        self.open = False
        self.dice_num = dice_num
        self.dice_point = dict_point

    def __repr__(self):
        if self.open:
            return f"开 {self.opened_player}"
        else:
            return f"{self.dice_point} 有 {self.dice_num} 个"