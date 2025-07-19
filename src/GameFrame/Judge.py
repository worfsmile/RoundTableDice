
class Judge:
    def __init__(self, dice_set):
        self.counter = self.count(dice_set)
    
    def judge_question(self, record):
        k, l = record
        return self.counter[k] >= l

    def count(self, dice_set):
        counter = {k:0 for k in range(1, 7)}
        for dice in dice_set:
            counter[dice] += 1
        return counter
