from typing import List, Optional
import random
from Player import Player, Player1, Player2, Player3, Player4
from Round import Round
from Decision import Decision
from Context import Context
from DicePoints import DicePoints

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
            player.dices = dices[player.name]

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
        return self.players[random.randint(0, len(self.players)-1)]

    def turn(self, print_out: bool) -> bool:
        """继续一轮, 返回本轮是否结束"""
        if self.current_round is None:
            print("游戏未开始")
            return True

        # 让玩家进行决策
        decision = Decision()
        player = self._getNextPlayer()
        player.decide(self.current_round.getContext(player.name, self), decision)
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
                    if print_out:
                        print(
                            f"本轮结束: 赢家 {winner}, 输家 {loser}\n"
                            f"{player.name} 开 {decision.opened_player}\n"
                            f"{decision.opened_player} 报 {player_d.dice_num} 个 {player_d.dice_point}\n"
                            f"场上点数:"
                        )
                    break

            self.current_round.loser = self.players_map[loser]
            # 结束本轮
            for name, dices in self.current_round.dices.items():
                if print_out:
                    print(f"{name}: {dices}")
            self.rounds.append(self.current_round)
            self.current_round = None
            return (player.name, decision)
        return False

if __name__ == "__main__":
    players = [
        Player1("Peter"),
        Player1("Lois"),
        Player1("Brain"),
        Player4("Stewie"),
    ]
    g = Game(4, players)
    for i in range(10):
        g.roundStart()
        while not g.turn(False):
            pass
    print("最终得分:")
    for player in players:
        print(player.name, player.score)
