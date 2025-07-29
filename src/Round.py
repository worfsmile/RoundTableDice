from typing import Dict, List, Tuple, Optional
from Context import Context
from Decision import Decision
from DicePoints import DicePoints
from Player import Player

class Round:
    """一轮游戏"""
    def __init__(self, dices: Dict[str, DicePoints]):
        self.dices = dices # 记录每个人的骰子点数
        self.decisions: List[Tuple[str, Decision]] = [] # 记录所有的决策
        self.loser: Optional[Player] = None # 输家

    def makeDecision(self, player: str, decision: Decision) -> bool:
        # 1. 报的点数是否正确
        if not decision.open and self.decisions:
            last = self.decisions[-1][1]
            if not (decision.dice_num > last.dice_num or
                    (decision.dice_num == last.dice_num and
                     decision.dice_point > last.dice_point)):
                print(f"{player} 报点无效: "
                      f"({last.dice_point}有{last.dice_num}个)"
                      f" -> ({decision.dice_point}有{decision.dice_num}个)")
                return False

        # 2. 开的玩家是否正确
        if decision.open:
            find_player = False
            for d in self.decisions:
                player_name = d[0]
                if player_name == decision.opened_player:
                    find_player = True
                    break

            if not find_player:
                print(f"玩家 {decision.opened_player} 还未报过点数")
                return False

        self.decisions.append((player, decision))
        return True

    def check(self, dice_num: int, dice_point: int) -> bool:
        """检查场上的骰子点数是否满足个数"""
        s = 0
        for points in self.dices.values():
            for p in points:
                if p == dice_point:
                    s += 1
        return s >= dice_num

    def getContext(self, player: str, game: "Game") -> Context:
        ret = Context()
        ret.player_num = len(game.players)
        ret.dice_num = game.dice_num
        ret.dices = self.dices[player]
        ret.decisions = self.decisions
        return ret
