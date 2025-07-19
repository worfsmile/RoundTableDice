from typing import List, Tuple, Dict, Optional
import random


DicePoints = List[int] # 骰子点数

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

class Context:
    """玩家能看到的信息"""
    def __init__(self, dices: DicePoints, decisions: List[Tuple[str, Decision]]):
        self.dices = dices
        self.decisions = decisions

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
                if p >= dice_point:
                    s += 1
        return s >= dice_num

    def getContext(self, player: str) -> Context:
        return Context(self.dices[player], self.decisions)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0 # 赢一局 + 1, 输一局 -1

    def decide(self, context: Context, decision: Decision) -> None:
        """玩家进行决策"""
        if context.decisions:
            last = context.decisions[-1][1]
            decision.makeGuess(last.dice_num, last.dice_point + 1)
            if last.dice_point == 6:
                decision.makeOpen(context.decisions[-1][0])
        else:
            decision.makeGuess(4, 1)

class Game:
    def __init__(self, dice_num: int, players: List[Player]):
        self.dice_num = dice_num
        self.players = players
        self.players_map = {p.name: p for p in players}

        self.rounds: List[Round] = []
        self.current_round: Optional[Round] = None

    def roundStart(self) -> None:
        """开一局游戏"""
        dices = {}
        # 为每个玩家摇骰子
        for player in self.players:
            dices[player.name] = [random.randint(1, 6) for _ in range(self.dice_num)]
        self.current_round = Round(dices)

    def _getNextPlayer(self) -> Player:
        """选择下一个需要决策的玩家"""
        if self.current_round.decisions:
            last_player_name = self.current_round.decisions[-1][0]

            if self.players_map.get(last_player_name) is None:
                print(f"错误: 未找到玩家: {last_player_name}")
                return

            i = self.players.index(self.players_map[last_player_name])
            return self.players[(i + 1) % len(self.players)]

        # 这一轮还没开始
        if self.rounds: # 从上一轮寻找输家
            last_round = self.rounds[-1]

            if self.players_map.get(last_round.loser.name) is None:
                print(f"错误: 未找到玩家: {last_player_name}")
                return

            i = self.players.index(self.players_map[last_round.loser.name])
            return self.players[(i + 1) % len(self.players)]

        # 游戏刚开始
        return self.players[0]

    def turn(self) -> bool:
        """继续一轮, 返回本轮是否结束"""
        if self.current_round is None:
            print("游戏未开始")
            return True

        # 让玩家进行决策
        decision = Decision()
        player = self._getNextPlayer()
        player.decide(self.current_round.getContext(player.name), decision)
        if not self.current_round.makeDecision(player.name, decision):
            return True # 不合法的猜测结束

        # 判断输赢
        if decision.open:
            for d in self.current_round.decisions[::-1]:
                player_name, player_d = d
                if player_name == decision.opened_player:
                    if self.current_round.check(player_d.dice_num, player_d.dice_point):
                        # 被开的赢
                        self.players_map[decision.opened_player].score += 1
                        player.score -= 1
                        winner = decision.opened_player
                        loser = player.name
                    else:
                        # 开的赢
                        player.score += 1
                        self.players_map[decision.opened_player].score -= 1
                        winner = player.name
                        loser = decision.opened_player
                    print(
                        f"本轮结束: 赢家 {winner}, 输家 {loser}\n"
                        f"{player.name} 开 {decision.opened_player}\n"
                        f"{decision.opened_player} 报 {player_d.dice_num} 个 {player_d.dice_point}\n"
                        f"场上点数:"
                    )
                    break
            # 结束本轮
            for name, dices in self.current_round.dices.items():
                print(f"{name}: {dices}")
            self.rounds.append(self.current_round)
            self.current_round = None
            return True
        return False

if __name__ == "__main__":
    players = [
        Player("Peter"),
        Player("Lois"),
        Player("Brain"),
        Player("Stewie"),
    ]
    g = Game(4, players)
    g.roundStart()
    while not g.turn():
        pass