from typing import List
from Context import Context
from Decision import Decision
import math
import random

class Player:
    def __init__(self, name: str):
        self.name = name
        self.dices = []
        self.score = 0 # 赢一局 + 1, 输一局 -1

    def count_p(self, num, total):
        if num > total:
            return 0
        if num < 0:
            return 1
        single_p = 1 / 6
        p = 0
        for i in range(num, total + 1):
            p += math.comb(total, i) * (single_p**i) * ((1 - single_p)**(total - i))
        return p

    def decide(self, context: Context, decision: Decision) -> None:
        pass

    def action(self, decision: Decision, context: Context, last_p: float, this_p: float, num: int, point: int) -> None:
        coin = random.random()
        if last_p > coin:
            coin = random.random()
            if this_p < coin:
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
            last_p = self.count_p(last.dice_num, total_dice_num)

            # 这次猜测获胜的概率
            this_p = 0
            if last.dice_point < 6:
                this_p = last_p
                num = last.dice_num
                point = last.dice_point + 1
            else:
                num = last.dice_num + 1
                point = 1
                this_p = self.count_p(num, total_dice_num)

            self.action(decision, context, last_p, this_p, num, point)

        else:
            decision.makeGuess(1, 1)

class Player2(Player):
    
    """
        行为逻辑:
        第一次的行动: 猜测为1个1
        是否开: 计算概率
        非第一次行动: 两种策略
        在计算概率时考虑自己手中的骰子
    """

    def __init__(self, name: str):
        super().__init__(name)

    def dice_dict(self):
        """计算骰子的频数"""
        dice_dict = {}
        for dice in self.dices:
            if dice in dice_dict:
                dice_dict[dice] += 1
            else:
                dice_dict[dice] = 1
        return dice_dict

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        if context.decisions:
            dice_dict = self.dice_dict()
            last = context.decisions[-1][1]

            tmp = dice_dict.get(last.dice_point, 0)
            total_dice_num = context.dice_num * context.player_num - tmp
            last_p = self.count_p(last.dice_num - tmp, total_dice_num - tmp)

            this_p = 0
            this_p1 = 0
            this_p2 = 0
            if last.dice_point < 6:
                num1 = last.dice_num
                point1 = last.dice_point + 1
                for pointi in range(last.dice_point + 1, 7):
                    tmp = dice_dict.get(pointi, 0)
                    total_dice_numi = context.dice_num * context.player_num - tmp
                    pi = self.count_p(num1 - tmp, total_dice_numi - tmp)
                    if pi > this_p1:
                        this_p1 = pi
                        point1 = pointi
            

            num2 = last.dice_num + 1
            for pointi in range(1, 7):
                tmp = dice_dict.get(pointi, 0)
                total_dice_numi = context.dice_num * context.player_num - tmp
                pi = self.count_p(num2 - tmp, total_dice_numi - tmp)
                if pi > this_p2:
                    this_p2 = pi
                    point2 = pointi

            if this_p1 > this_p2:
                this_p = this_p1
                num = num1
                point = point1
            else:
                this_p = this_p2
                num = num2
                point = point2

            self.action(decision, context, last_p, this_p, num, point)

        else:
            decision.makeGuess(1, 1)

class Player3(Player):
    
    """
        行为逻辑:
        第一次的行动: 根据手中的骰子做出最极端的决策
        是否开: 计算概率
        非第一次行动: 两种策略
        在计算概率时考虑自己手中的骰子, 做出的决策为最极端的策略
    """

    def __init__(self, name: str):
        super().__init__(name)

    def dice_dict(self):
        """计算骰子的频数"""
        dice_dict = {}
        for dice in self.dices:
            if dice in dice_dict:
                dice_dict[dice] += 1
            else:
                dice_dict[dice] = 1
        return dice_dict

    def decide(self, context: Context, decision: Decision) -> None:
        pass

            
