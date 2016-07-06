import compiler
import pickle
import json
from sclearning import *
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
import pickle

MODELS = {}
TRAINERS = {}
ESTIMATORS = {}
DBNAME = 'b.db'

class Transformer():
    # transformer take in a equation and evaluate
    def __init__(self, transformation_equation=None, json_object=None):
        self.equation_list = transformation_equation
        self.regex = re.compile('\{[0-9A-Za-z]+\}')
        if json_object:
            self.fromJSONObject(json_object)
    def get_features(self):
        features = []
        for equation in self.equation_list:
            for i in self.regex.findall(equation):
                features.append(i[1:-1])
        return list(set(features))
    def eval(self, argument_dict):
        return np.asmatrix(map(lambda(equation): eval(equation.format(**argument_dict)), self.equation_list))
    def toString(self):
        return json.dumps({'equation_list':self.equation_list})
    def fromJSONObject(self, json_object):
        self.equation_list = json_object['equation_list']

class Estimator():
    def __init__(self, predictor, transformer):
        self.predictor = predictor
        self.transformer = transformer
    def predict(self, argument_dict):
        # make data
        return self.predictor.predict(self.transformer.eval(argument_dict))

class Trainer():
    def __init__(self, preprocessor, learningmodel, feature_transformation, label_transformation):
        self.p = preprocessor
        self.feature = feature_transformation
        self.label = label_transformation
        self.l = learningmodel
    def fit(self, obj, values, constraint_formula, constraint_vars, size):
        self.p.load(ScDBController(DBNAME), obj, values, constraint_formula, constraint_vars, size)
        self.l.fit(self.p.feature, self.p.label)
        return Estimator(self.l, self.feature)

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        try:
            int(string)
            return True
        except ValueError:
            return False
        return False

# use object to refactor, now just for experiment
def parse_equation(string):
    # simple equation parsing... for this special equation
    string = string.split(',')
    formula = string[0]; variables = string[1:]
    variable_dict = {}
    for i in variables:
        pair = map(lambda(x): x.strip(), i.split('='))
        value_unit = map(lambda(x): x.strip(), pair[1].split('('))
        if (len(value_unit) == 1):
            value = value_unit[0]
            unit = ""
        elif len(value_unit) == 2:
            value = value_unit[0]
            unit = value_unit[1][:-1]
        isnumber = is_number(value)
        variable_dict[pair[0].strip()] = {'value': value, 'unit': unit, 'isnumber': isnumber}
    return (formula, variable_dict)
    
def parse_predict_equation(string):
    pairs = map(lambda(x): x.split('='), string.split(','))
    variable_dict = {}
    for i in pairs:
        name_unit = map(lambda(x): x.strip(), i[0].split('('))
        if len(name_unit) == 1:
            name = name_unit[0]
            unit = ""
        elif len(name_unit) == 2:
            name = name_unit[0]
            unit = name_unit[1][:-1]
        else:
            raise Error("Parsing Error")
        value = i[1].strip()
        isnumber = is_number(value)
        variable_dict[name.strip()] = {'unit':unit,'value':value, 'isnumber': isnumber}
    return variable_dict

def parse_training_query(string):
    pairs = map(lambda(x):x.split('='), string.split(','))
    result = {}
    for pair in pairs:
        value_unit = map(lambda(x): x.strip(), pair[1].split('('))
        if (len(value_unit) == 1):
            value = value_unit[0]
            unit = ""
        elif len(value_unit) == 2:
            value = value_unit[0]
            unit = value_unit[1][:-1]
        isnumber = is_number(value)
        result[pair[0].strip()] = {'unit': unit, 'value': value, 'isnumber': isnumber}
    return result

def parse_values(string):
    pairs = map(lambda(x):x.split('='), string.split(','))
    result = {}
    for pair in pairs:
        result[pair[0].strip()] = float(pair[1])
    return result

def parse(json_string):
    global MODELS, TRAINERS
    json_dict = json.loads(json_string)
    if json_dict['MODE'] == 0: # define a new instance of learning pipeline
        model = MODELS[json_dict["MODEL"]]
        feature_equation = (json_dict["FEATURE"])
        label_equation = (json_dict["LABEL"])
        preprocessor = LearnPreprocessor()
        preprocessor.setfeature(feature_equation)
        preprocessor.setlabel(label_equation)
        wrapper = Trainer(preprocessor, model, Transformer(feature_equation), Transformer(label_equation))
        TRAINERS[json_dict['ID']] = wrapper
    elif json_dict['MODE'] == 1:
        pipeline = TRAINERS[json_dict['ID']]
        obj_name = json_dict['OBJECT']
        values = parse_training_query(json_dict['DATA'])
        constraint = parse_equation(json_dict['CONSTRAINT'])
        size = json_dict['size']
        ESTIMATORS[json_dict['ID']] = pipeline.fit( obj_name, values, constraint[0], constraint[1], size)
    elif json_dict['MODE'] == 2:
        estimator = ESTIMATORS[json_dict['ID']]
        return estimator.predict(parse_values(json_dict["VALUES"]))

def register_model(name, model):
    global MODELS
    MODELS[name] = model

def histo_plot( data):
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib
    from scipy.stats import norm
    from matplotlib.legend_handler import HandlerLine2D
    (mu, sigma) = norm.fit(data)
    # the histogram of the data
    n, bins, patches = plt.hist(data, 30, normed=1, facecolor='green', alpha=0.75)
    # add a 'best fit' line
    y = mlab.normpdf( bins, mu, sigma)
    l = plt.plot(bins, y, 'r--', linewidth=2)

import os
def save_estimator(dir_name):
    requested_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir_name)
    if not os.path.exists(requested_dir):
        os.mkdir(requested_dir)
    header = open(os.path.join(requested_dir, "header"), "w+")
    header_dict = {}
    for i in ESTIMATORS:
        f = open(os.path.join(requested_dir, str(i)+'.predictor'), 'w+b')
        g = open(os.path.join(requested_dir, str(i)+'.transformer'), 'w+')
        pickle.dump(ESTIMATORS[i].predictor, f)
        header_dict[i] = str(i)
        g.write((ESTIMATORS[i].transformer.toString()))
        f.close()
        g.close()
    header.write(json.dumps(header_dict))
    header.close()

def find_feature(id):
    return ESTIMATORS[id].transformer.get_features()

def load_estimator(dir_name):
    requested_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir_name)
    if not os.path.exists(requested_dir):
        raise Exception("requested directory is not found")
    # read header
    header_dict = json.load(open(os.path.join(requested_dir, "header")))
    for i in header_dict:
        predictor = pickle.load(open(os.path.join(requested_dir, header_dict[i]+'.predictor'), 'rb'))
        print "loaded predictor: " + str(predictor)
        transformer = Transformer(json_object=json.load(open(os.path.join(requested_dir, header_dict[i]+'.transformer'), 'r')))
        ESTIMATORS[int(i)] = Estimator(predictor, transformer)
        
    return ESTIMATORS

# need to refactor that it's MVC structure
if __name__ == '__main__':
    register_model("My regression 1", LinearRegression())
    register_model("Bayesian", GaussianNB())
    # every instance of learning model can only have one model, feature and label definition
    model_define_string = '{"MODE": 0, "ID":0, "MODEL":"My regression 1", "FEATURE":["{aoa}"], "LABEL":"2*{W}/({V}**2*{S}*(4.174794718087996e-11*(288.14-0.00649*{H})**4.256))"}'
    training_string_db = '{"MODE": 1, "ID": 0, "OBJECT":"example", "size":1000,"DATA":"aoa=angle of attack(radian),  W=current weight(N), V=true air speed(m/s), S=61.0(m^2), H=altitude msl(m)","CONSTRAINT": "abs({b}-{a})/{a}<0.05, b=lift(N), a = current weight(N)"}'
    predict_string = '{"MODE": 2, "ID": 0, "VALUES":"aoa=0.02234021"}'
    parse(model_define_string)
    parse(training_string_db)
    parse(predict_string)
    model_define_string2 = '{"MODE": 0, "ID":1, "MODEL":"Bayesian", "FEATURE":["{b}/{a}"], "LABEL":"{c}"}'
    training_string_db2 = '{"MODE": 1, "ID": 1, "OBJECT":"bayes", "size":3000,"DATA":"b=b,  a=a, c=c","CONSTRAINT": ""}'
    predict_string2 = '{"MODE": 2, "ID": 1, "VALUES":"b=2,a=1"}'
    parse(model_define_string2)
    parse(training_string_db2)
    model = MODELS["My regression 1"]
    model.coef_ = 6.27203070470782986234
    model.intercept_ = 0.35713086960224765809
    save_estimator("test")
    load_estimator("test")
    print parse(predict_string2)
    print parse(predict_string)
#    query.append(json.dumps({'MODE':2, 'ID':1, 'VALUES':X1}))
