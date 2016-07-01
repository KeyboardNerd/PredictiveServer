class Transformer():
    # transformer take in a equation and evaluate
    def __init__(self, transformation_equation):
        self.transformation_equation = transformation_equation
    def eval(self, argument_dict):
        return map(lambda(equation): eval(equation.format(**argument_dict)), self.transformation_equation)
    def __str__(self):
        return str(self.transformation_equation)
class Estimator():
    def __init__(self, predictor, transformer):
        self.p = predictor
        self.t = transformer
    def predict(self, argument_dict):
        # make data
        return self.p.predict(transformer.eval(argument_dict))

t = Transformer(["{a}","{a}/{b}"])
print t.eval({'a':10.0,'b':20})