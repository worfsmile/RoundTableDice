

class Context:
    """玩家能看到的信息"""
    def __init__(self):
        self.player_num: int # 玩家数量
        self.dice_num: int # 骰子数量
        self.dices: DicePoints # 该玩家的骰子点数
        self.decisions: List[Tuple[str, Decision]] # 之前的决策