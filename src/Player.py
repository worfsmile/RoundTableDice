from typing import List
from Context import Context
from Decision import Decision
import math
import random
from LLMsDriven import LLMsResponse, prompter
from system_message import system_message

class Player:
    def __init__(self, name: str):
        self.name = name
        self.dices = []
        self.score = 0 # 赢一局 + 1, 输一局 -1
        self.dicedict = None
    
    def dice_dict(self):
        if self.dice_dict is None:
            return self.dicedict
        else:
            return self.count_dice_dict()

    def count_dice_dict(self):
        return None

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

class Player2(Player1):
    
    """
        行为逻辑:
        第一次的行动: 猜测为1个1
        是否开: 计算概率
        非第一次行动: 两种策略
        在计算概率时考虑自己手中的骰子
    """

    def __init__(self, name: str):
        super().__init__(name)

    def count_dice_dict(self):
        """计算骰子的频数"""
        dice_dict = {}
        for dice in self.dices:
            if dice in dice_dict:
                dice_dict[dice] += 1
            else:
                dice_dict[dice] = 1
        return dice_dict

    def get_num_point_plyer2(self, dice_dict, last, context):
        num = 0
        point = 0

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
        
        return num, point, this_p

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        if context.decisions:
            dice_dict = self.dice_dict()
            last = context.decisions[-1][1]

            tmp = dice_dict.get(last.dice_point, 0)
            total_dice_num = context.dice_num * context.player_num - tmp
            last_p = self.count_p(last.dice_num - tmp, total_dice_num - tmp)

            num, point, this_p = self.get_num_point_plyer2(dice_dict, last, context)

            self.action(decision, context, last_p, this_p, num, point)

        else:
            decision.makeGuess(1, 1)

class Player3(Player2):
    
    """
        行为逻辑:
        第一次的行动: 根据手中的骰子做出最极端的决策
        是否开: 计算概率
        非第一次行动: 两种策略
        在计算概率时考虑自己手中的骰子, 做出的决策为最极端的策略
    """

    def __init__(self, name: str, threshold: float = None):
        super().__init__(name)
        self.threshold = threshold

    def get_num_point_plyer3(self, dice_dict, last, context, threshold):
        this_p = 0
        num = None
        point = None
        this_p1 = 0

        if last.dice_point < 6:
            num1 = None
            point1 = None
            tmpnum = last.dice_num
            for pointi in range(last.dice_point + 1, 7):
                tmp = dice_dict.get(pointi, 0)
                total_dice_numi = context.dice_num * context.player_num - tmp
                pi = self.count_p(tmpnum - tmp, total_dice_numi - tmp)
                if pi > threshold:
                    if pi < this_p1 or this_p1 == 0:
                        this_p1 = pi
                        point1 = pointi
                        num1 = tmpnum
        
        this_p2 = 0
        flag = 1
        num2 = None
        point2 = None
        tmpnum = last.dice_num + 1
        while flag:
            flag = 0
            for pointi in range(1, 7):
                tmp = dice_dict.get(pointi, 0)
                total_dice_numi = context.dice_num * context.player_num - tmp
                pi = self.count_p(tmpnum - tmp, total_dice_numi - tmp)
                if pi > threshold:
                    if pi < this_p2 or this_p2 == 0:
                        this_p2 = pi
                        flag = 1
                        num2 = tmpnum
                        point2 = pointi
            tmpnum += 1
        
        if this_p1 < this_p2 and this_p1 > threshold:
            this_p = this_p1
            num = num1
            point = point1
        
        elif this_p2 > threshold:
            this_p = this_p2
            num = num2
            point = point2
        
        if num == None:
            num, point, this_p = self.get_num_point_plyer2(dice_dict, last, context)
        
        return num, point, this_p

    def decide(self, context: Context, decision: Decision, threshold: float = 0.5) -> None:
        """玩家进行决策"""
        dice_dict = self.count_dice_dict()
        if self.threshold:
            threshold = self.threshold
        if context.decisions:
            dice_dict = self.dice_dict()
            last = context.decisions[-1][1]
            total_dice_num = context.dice_num * context.player_num
            last_p = self.count_p(last.dice_num, total_dice_num)

            num, point, this_p = self.get_num_point_plyer3(dice_dict, last, context, threshold)
            
            self.action(decision, context, last_p, this_p, num, point)

        else:
            point = 1
            num = 0
            for i in range(1, 7):
                n = dice_dict.get(i, 0)
                if n > num:
                    point = i
                    num = n
            decision.makeGuess(num, point)

class Player4(Player3):
    """
        行为逻辑:
        通过大模型驱动的决策机器人
    """
    def __init__(self, name: str, add_prefix: bool = False):
        super().__init__(name)
        self.add_prefix = add_prefix

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        dice_dict = self.count_dice_dict()
        if context.decisions:
            
            message = [
                {
                    "role": "system",
                    "content": system_message(self.dices, self.name)
                }
            ]

            prefix = ""

            if self.add_prefix:
                for i in range(len(context.decisions)):
                    tmp = context.decisions[i][1]
                    player_name = context.decisions[i][0]
                    tmp_num = tmp.dice_num
                    tmp_point = tmp.dice_point
                    prefix += f"in {i+1} turn, " + f"{player_name} call {tmp_num} dices with {tmp_point}\n"

            message.append({
                "role": "user",
                "content": prompter(context, self.dices, prefix)
            })

            last = context.decisions[-1][1]
            flag = 1
            try_time = 0
            while flag != 0 and try_time < 3:
                flag, strategy = LLMsResponse(context, message, self.dices, 1)
                if flag:
                    print(flag, strategy)
                try_time += 1
            
            if flag != 0:
                num, point, this_p = self.get_num_point_plyer3(dice_dict, last, context, 0.5)
                tmp = self.dice_dict().get(point, 0)
                last_p = self.count_p(num - tmp, context.dice_num * context.player_num - tmp)

            else:
                num, point = strategy
                if num == 0:
                    last_p = 0
                    this_p = 0
                    
                else:
                    tmp = self.dice_dict().get(point, 0)
                    this_p = self.count_p(num, context.dice_num * context.player_num)
                    last_p = self.count_p(num - tmp, context.dice_num * context.player_num - tmp)

            self.action(decision, context, last_p, this_p, num, point)
        else:
            point = 1
            num = 0
            for i in range(1, 7):
                n = dice_dict.get(i, 0)
                if n > num:
                    point = i
                    num = n
            decision.makeGuess(num, point)
