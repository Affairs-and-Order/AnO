import random
import sqlite3


class Attack:
    def __init__(self, Nat1, Nat2):
        for roll in range(0, 3):
            self.nat1_roll = random.randint(1, Nat1)
            self.nat2_roll = random.randint(1, Nat2)
            self.difference = abs(self.nat1_roll - self.nat2_roll)

        if self.nat1_roll > self.nat2_roll:
            self.nat1_roll_wins += 1
            Nat2 -= self.difference # water attacks are weaker than land attacks
        else:
            self.nat2_roll_wins += 1
            Nat1 -= self.difference

        self.calculateWin(Nat1, Nat2)

    def calculateWin(self, Nat1, Nat2):
        if self.nat1_roll_wins > self.nat2_roll_wins:
            return [Nat1, ]

