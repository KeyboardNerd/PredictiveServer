"""
Contains custom learning algorithms 
"""

import math
import numpy as np
import operator
import sys
import pandas as pd
from scipy.stats import norm
from sklearn.pipeline import make_pipeline
from sklearn.utils.estimator_checks import check_estimator
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import euclidean_distances
from sklearn.linear_model import LinearRegression
from pint import UnitRegistry
from utils.sceval import ScEvalExpr
import scalgoutil
import matplotlib.pyplot as plt

# TODO: Improve the algorithm
class DynamicBayesianClassifier(BaseEstimator):
    def __init__(self, num_sigma=2, num_threshold=100, num_mode_max = 1000):
        self.num_sigma = num_sigma
        self.num_threshold = num_threshold
        self.num_mode_max = num_mode_max
        self.dbayesmode_major_ = {}
        self.dbayesmode_minor_ = {}
        self.size_ = 0

    def _get_next_id(self):
        """
        Get the next available state id
        """
        for i in xrange(1, self.num_mode_max):
            if i not in self.classes_:
                yield i
            else:
                continue
        raise Exception("No available ID, Maximum Number of modes: " + str(self.num_mode_max))

    def create_minor_mode(self, x):
        id_mode = next(self._get_next_id())
        self.dbayesmode_minor_[id_mode] = scalgoutil.DBayesMode(id_mode)
        self.dbayesmode_minor_[id_mode].update(x)
        self.classes_ = np.append(self.classes_, id_mode)
        return id_mode

    def update_priors(self):
        for mode_major in self.dbayesmode_major_.values():
            mode_major.prior = (1.0*mode_major.n)/self.size_

    def _predict(self, X):
        output_type = []
        for x in X:
            if (self.in_major_states(x)):
                self.size_ += 1
                id_mode = self.get_id_mode(x)
                self.dbayesmode_major_[id_mode].update(x)
                self.update_priors()
                output_type.append(id_mode)
            else:
                id_mode = self.get_minor_mode(x)
                if (id_mode is not None):
                    self.dbayesmode_minor_[id_mode].update(x)
                    output_type.append(id_mode)
                    # If item number in a minor state > 1000, change it to a major state.
                    if (self.dbayesmode_minor_[id_mode].n >= self.num_threshold):
                        self.dbayesmode_major_[id_mode] = self.dbayesmode_minor_[id_mode]
                        del(self.dbayesmode_minor_[id_mode])
                        self.size_ += self.dbayesmode_major_[id_mode].n
                        self.update_priors()
                else:
                    id_mode = self.create_minor_mode(x)
                    output_type.append(id_mode)
        return np.asarray(output_type)

    def get_id_mode(self, x):
        post_prob = {}
        evidence = 0.0
        for state in self.dbayesmode_major_.values():
            evidence += norm.pdf(x, state.mean, state.std) * state.prior
        for i in self.dbayesmode_major_:
            post_prob[i] = norm.pdf(x, self.dbayesmode_major_[i].mean, self.dbayesmode_major_[i].std) * self.dbayesmode_major_[i].prior / evidence
        # Get the state of the highest post prob.
        return max(post_prob.iteritems(), key=operator.itemgetter(1))[0]

    def in_major_states(self, item):
        for mode in self.dbayesmode_major_.values():
            if item >= mode.mean - self.num_sigma * mode.std and item <= mode.mean + self.num_sigma * mode.std:
                return True
        return False

    # Get average value of std divided by mean
    def avg_std(self):
        result = 0.0
        for state in self.dbayesmode_major_.values():
            result += state.std
        return result / len(self.dbayesmode_major_)

    # Check if the item is within mean +- 3 sigma of any minor state
    def get_minor_mode(self, x):
        for mode in self.dbayesmode_minor_.values():
            est_std = mode.std
            # If item in a minor state < 100, use estimated std
            if mode.n < 100: # wtf?
                est_std = self.avg_std()
            if x >= mode.mean - self.num_sigma * est_std and x <= mode.mean + self.num_sigma * est_std:
                return mode.id
        return None

    @staticmethod
    def _first_col(X):
        return X[:,0]

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        self.classes_ = unique_labels(y)
        self.X_ = DynamicBayesianClassifier._first_col(X)
        self.y_ = y
        self.size_ = self.X_.size
        for i in range(self.X_.size):
            if y[i] not in self.dbayesmode_major_.keys():
                self.dbayesmode_major_[y[i]] = scalgoutil.DBayesMode(y[i])
            self.dbayesmode_major_[y[i]].update(self.X_[i])
            self.update_priors()
        return self

    def predict(self, X):
        check_is_fitted(self, ['X_', 'y_'])
        X = check_array(X)
        X = DynamicBayesianClassifier._first_col(X)
        return self._predict(X)

if __name__ == '__main__':
    main()