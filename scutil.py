import math

class DBayesMode(object):
    """
    Dynamic Bayesian classifier Mode
    """
    def __init__(self, id_mode):
        self.id = id_mode
        self.n = 0
        self.mean = 0.0
        self.std = 0.0
        self.sum = 0.0
        self.sqsum = 0.0
        self.prior = 0.0

    def update(self, x):
        self.n += 1
        self.sum += x
        self.sqsum += x ** 2
        self.mean = self.sum/self.n
        self.std = math.sqrt(float(self.sqsum)/self.n - (float(self.sum)/self.n) ** 2)