from typing import List
from Context import Context
from Decision import Decision
import math

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0 # 赢一局 + 1, 输一局 -1

    def decide(self, context: Context, decision: Decision) -> None:
        pass

class Player1(Player):

    """
        行为逻辑:
        第一次的行动: 猜测为1个1
        是否开: 计算概率
        非第一次行动: 接收k个l, 若l < 6, 则猜测为k个l+1, 否则猜测为k+1个1
    """

    def __init__(self, name: str):
        super().__init__(name)

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        if context.decisions:
            last = context.decisions[-1][1]
            total_dice_num = context.dice_num * context.player_num
            single_p = 1 / 6
            last_p = 0
            for i in range(last.dice_num, total_dice_num + 1):
                last_p += math.comb(total_dice_num, i) * (single_p**i) * ((1 - single_p)**(total_dice_num-i))

            # 这次猜测获胜的概率
            this_p = 0
            if last.dice_point < 6:
                this_p = last_p
                num = last.dice_num
                point = last.dice_point + 1
            else:
                num = last.dice_num + 1
                point = 1
                for i in range(last.dice_num + 1, total_dice_num + 1):
                    this_p += math.comb(total_dice_num, i) * (single_p**i) * ((1 - single_p)**(total_dice_num-i))

            if last_p > 0.5:
                if this_p < 0.5:
                    # 看看谁接近0.5
                    d1 = last_p - 0.5
                    d2 = 0.5 - this_p
                    if d1 > d2:
                        decision.makeGuess(num, point)
                    else:
                        decision.makeOpen(context.decisions[-1][0])
                else:
                    decision.makeGuess(num, point)
            else:
                decision.makeOpen(context.decisions[-1][0])
        else:
            decision.makeGuess(1, 1)

            