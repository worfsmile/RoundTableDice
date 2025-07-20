class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0 # 赢一局 + 1, 输一局 -1

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        if context.decisions:
            last = context.decisions[-1][1]

            # 判断上一个玩家获胜的概率
            total_dice_num = context.dice_num * context.player_num
            single_p = (6 - last.dice_point + 1) / 6 # 单个骰子 >= n 的概率
            last_p = 0
            for i in range(last.dice_num, total_dice_num + 1):
                last_p += math.comb(total_dice_num, i) * (single_p**i) * ((1 - single_p)**(total_dice_num-i))

            # 这次猜测获胜的概率
            this_p = 0
            for i in range(last.dice_num + 1, total_dice_num + 1):
                last_p += math.comb(total_dice_num, i) * (single_p**i) * ((1 - single_p)**(total_dice_num-i))

            if last_p > 0.5:
                if this_p < 0.5:
                    # 看看谁接近0.5
                    d1 = last_p - 0.5
                    d2 = 0.5 - this_p
                    if d1 > d2:
                        decision.makeGuess(last.dice_num + 1, last.dice_point)
                    else:
                        decision.makeOpen(context.decisions[-1][0])
                else:
                    decision.makeGuess(last.dice_num + 1, last.dice_point)
            else:
                decision.makeOpen(context.decisions[-1][0])
        else:
            decision.makeGuess(1, 3)