
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.hand = []

    def add_to_score(self, score):
        self.score += score

    def initialize_hand(self, m = 5):
        for i in range(m):
            self.hand.append(random.randint(1, 6))
        return self.hand

    def question(self):
        is_question = False
        return is_question

    def browse(self, record = None):
        k = 0
        l = 0
        if record is not None:
            if k > record[0] or (k == record[0] and l > record[1]):
                return [k, l]
            else:
                return None
        else:
            return [k, l]
