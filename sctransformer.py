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
import scutil

class UnitTransformer(TransformerMixin):
    """
    Transform X to X' with different units, the size and position of input is enforced
    """
    def __init__(self, list_tuple_units):
        self.units = list_tuple_units
        self.ureg_q = UnitRegistry().Quantity
    def fit(self, X, y=None):
        if X.shape[1] != len(self.units):
            raise Exception("Input matrix's size (%d) doesn't match with size of units (%d)"%(X.shape[1], len(self.units)))
        return self
    def transform(self, X):
        X = X.copy()
        for i, pair_unit in enumerate(self.units):
            X[:,i] = self.ureg_q(X[:,i], pair_unit[0]).to(pair_unit[1]).magnitude
        return X

class FormulaTransformer(TransformerMixin):
    def __init__(self, listst_featureformula, listst, constants={}):
        # compile the expressions
        self.l_expr = [ScEvalExpr(st_feature) for st_feature in listst_featureformula]
        self.listst = listst
        self.constants = constants
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        # parse X:
        raw_ = {}
        raw_.update(self.constants)
        for i, stfeature in enumerate(self.listst):
            raw_[stfeature] = X[:,i]
        features_ = []
        for expr in self.l_expr:
            col = expr.eval(**raw_)
            col = np.reshape(col, (col.shape[0], 1)) # reshape the matrix
            features_.append(col)
        # what's the shape of feature?
        return np.concatenate(features_, axis=1)