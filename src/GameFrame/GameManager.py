
from Player import Player
from Judge import Judge

class GameManager:
    def __init__(self, n_players, m_dice):
        players = [Player(i) for i in range(n_players)]
        dice_set = []
        for player in players:
            player.initialize_hand(m_dice)
            dice_set.extend(player.hand)
        self.players = players
        self.current_player_index = 0
        self.records = []
        self.score = 10
        self.judge = Judge(dice_set)
    
    def each_round(self):
        if len(self.records) == 0:
            record = current_player.browse()
        else:
            record = current_player.browse(self.records[-1])
            while not record:
                record = current_player.browse(self.records[-1])
        self.records.append(record)

        for player_i in range(len(self.players)):
            if player_i != self.current_player_index:
                if player_i != (self.current_player_index + 1) % len(self.players):
                    score = self.score * 2
                else:
                    score = self.score
                playeri = self.players[player_i]
                if playeri.question():
                    if self.judge.judge_question(playeri, record):
                        playeri.score += score
                        self.players[self.current_player_index].score -= score
                    else:
                        playeri.score -= score
                        self.players[self.current_player_index].score += score
                        self.current_player_index = player_i
                    return 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return 0


def main():
    n = 3
    m = 5
    game_manager = GameManager(n, m)
    flag = 1
    while flag:
        while not game_manager.each_round():
            pass
        print("Game Over")


