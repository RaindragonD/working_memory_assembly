
import numpy as np
from numpy.random import binomial
from brain import *

class ConvergenceLogger():
    def __init__(self):
        self.support = set()
        self.winners_hist = []
        self.support_sizes = []
        self.num_new_winners = []
        self.step = 0
    
    def update(self, new_winners):
        self.step += 1
        self.winners_hist.append(new_winners)
        for i in new_winners:
            self.support.add(i)
        self.support_sizes.append(len(self.support))
        if self.step >= 2:
            num_new_winners = self.support_sizes[-1]-self.support_sizes[-2]
            self.num_new_winners.append(num_new_winners)