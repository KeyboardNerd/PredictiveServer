import compiler 
import json
from sclearning import *
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
MODELS = {}
INSTANCE = {}
DBNAME = 'b.db'

class LearnWrapper():
    def __init__(self, preprocessor, learningmodel):
        self.p = preprocessor
        self.l = learningmodel
    def fit(self, obj, values, constraint_formula, constraint_vars, size):
        self.p.load(ScDBController(DBNAME), obj, values, constraint_formula, constraint_vars, size)
        self.l.fit(self.p.feature, self.p.label)
    def predict(self, point):
        return self.l.predict(np.matrix(point))

# first support single instance of learning model running
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


def parse(json_string):
    global MODELS, INSTANCE
    json_dict = json.loads(json_string)
    if json_dict['MODE'] == 0: # define a new instance of learning pipeline
        model = MODELS[json_dict["MODEL"]]
        feature_equation = (json_dict["FEATURE"])
        label_equation = (json_dict["LABEL"])
        preprocessor = LearnPreprocessor()
        preprocessor.setfeature(feature_equation)
        preprocessor.setlabel(label_equation)
        wrapper = LearnWrapper(preprocessor, model)
        INSTANCE[json_dict['ID']] = wrapper
    elif json_dict['MODE'] == 1:
        pipeline = INSTANCE[json_dict['ID']]
        obj_name = json_dict['OBJECT']
        values = parse_training_query(json_dict['DATA'])
        constraint = parse_equation(json_dict['CONSTRAINT'])
        size = json_dict['size']        
        pipeline.fit( obj_name, values, constraint[0], constraint[1], size)
        
    elif json_dict['MODE'] == 2:
        pipeline = INSTANCE[json_dict['ID']]
        #print pipeline.predict(parse_predict_equation(json_dict["VALUES"]))
        return pipeline.predict(json_dict["VALUES"])

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
if __name__ == '__main__':
    register_model("My regression 1", LinearRegression())
    register_model("Bayesian", GaussianNB())
    # every instance of learning model can only have one model, feature and label definition
    model_define_string = '{"MODE": 0, "ID":0, "MODEL":"My regression 1", "FEATURE":["{aoa}"], "LABEL":"2*{W}/({V}**2*{S}*(4.174794718087996e-11*(288.14-0.00649*{H})**4.256))"}'
    training_string_db = '{"MODE": 1, "ID": 0, "OBJECT":"example", "size":1000,"DATA":"aoa=angle of attack(radian),  W=current weight(N), V=true air speed(m/s), S=61.0(m^2), H=altitude msl(m)","CONSTRAINT": "abs({b}-{a})/{a}<0.01, b=lift(N), a = current weight(N)"}'
    predict_string = '{"MODE": 2, "ID": 0, "VALUES":[0.02234021]}'
    parse(model_define_string)
    parse(training_string_db)
    parse(predict_string)
    model_define_string2 = '{"MODE": 0, "ID":1, "MODEL":"Bayesian", "FEATURE":["{b}/{a}"], "LABEL":"{c}"}'
    training_string_db2 = '{"MODE": 1, "ID": 1, "OBJECT":"bayes", "size":3000,"DATA":"b=b,  a=a, c=c","CONSTRAINT": ""}'
    predict_string2 = '{"MODE": 2, "ID": 1, "VALUES":[2]}'
    parse(model_define_string2)
    parse(training_string_db2)
    parse(predict_string2)

#    query.append(json.dumps({'MODE':2, 'ID':1, 'VALUES':X1}))