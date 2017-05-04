"""
Interface to Parse formula expression
Notation: 
st: string
"""
import parser


class ScEvalExpr(object):
    """
    Used to parse, store and eval an python expression
    """
    import math
    from math import * # math is used in creating inner scope for the eval
    # initialize allowed inner scope
    RGST_FNSAFE = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', \
     'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', \
     'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
    MPST_FNSAFE = dict([(k, locals().get(k, None)) for k in RGST_FNSAFE])
    MPST_FNSAFE['abs'] = abs

    def __init__(self, st_exp):
        # parse the expression
        self.exp = ScEvalExpr.parse(st_exp)
        self.st_exp = st_exp

    @staticmethod
    def parse(st_exp):
        """Parse expression"""
        return parser.expr(st_exp).compile()

    def eval(self, **kwargs):
        """
        Evaluate the formula
        """
        # put into restricted code execution environment
        # inject argv to inner scope of current scope
        return eval(self.exp, ScEvalExpr.MPST_FNSAFE, kwargs)

if __name__ == '__main__':
    E = ScEvalExpr("vg - sqrt(va*va + vw*vw + 2*va*vw*cos((pi/180)*(aw-aa)))")
    print E.eval(vg=1, va=1, vw=1, aw=1, aa=1)