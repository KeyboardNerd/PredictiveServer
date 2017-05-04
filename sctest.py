import pandas as pd
from sklearn.pipeline import make_pipeline
from sctransformer import UnitTransformer, FormulaTransformer
from sklearn.linear_model import LinearRegression
from sclearn import StreamPipeline

import unittest

class Test(unittest.TestCase):
    """
    Simple Testing suit
    """

    def test_train():
        # define input streams
        names = ['v', 'p', 't', 'w', 'a']
        # define first transformation
        units = ["knot","in_Hg","celsius","force_pound","degree"]
        tounits = ["m/s", "pascal", "kelvin", "newton", "radian"]
        tuple_units = []
        for i, unit in enumerate(units):
            tuple_units.append((unit, tounits[i]))
        s1 = UnitTransformer(tuple_units)
        # second layer of transformation
        constants = {"s": 61.0, "R": 286.9}
        labels = ["2*w/(v**2*(p/R/t)*s)"]
        s2 = FormulaTransformer(labels, names, constants)
        # sink ( any sink transformation could be used to predict )
        # no fit_transform rule, can only predict
        features = ["a"]
        s3 = make_pipeline(FormulaTransformer(features, names), LinearRegression())
        # train the shit outof it
        with (open("data/training.csv")) as f:
            df = pd.read_csv(f, names=names, header=0)
            # awkward transformation from dataframe to numpy matrix
            # could use panda sklearn to solve
            ndarray = df.as_matrix(names)
            rawX = s1.fit_transform(ndarray)
            y = s2.fit_transform(rawX)
            X = rawX
            s3.fit(X, y)
            y_ = s3.predict(X)
            print X.shape, y_.shape
            #plt.scatter(FormulaTransformer(features, names).fit_transform(X), y_)
            #plt.show()
        # wrap the process as StreamPipeline for learning machine
        sp = StreamPipeline(names, s3)
        sp.predict(v=1.0, p=2.0, t=3.0, w=4.0, a=5.0)