import compiler 
import json
from sclearning import *
from sklearn.linear_model import LinearRegression
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
        print self.l.coef_, self.l.intercept_
    def predict(self, point):
        return self.l.predict(point)

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
        value, unit = map(lambda(x): x.strip(), pair[1].split('('))
        isnumber = is_number(value)
        unit = unit[:-1]
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
    for i in pairs:
        value, unit = i[1].split('(')
        unit = unit[:-1]
        isnumber = is_number(value)
        result[i[0].strip()] = {'unit': unit, 'value': value, 'isnumber': isnumber}
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
        print pipeline.predict(json_dict["VALUES"])

def register_model(name, model):
    global MODELS
    MODELS[name] = model

register_model("My regression 1", LinearRegression())
# every instance of learning model can only have one model, feature and label definition
model_define_string = '{"MODE": 0, "ID":0, "MODEL":"My regression 1", "FEATURE":["{aoa}"], "LABEL":"2*{W}/({V}**2*{S}*(4.174794718087996e-11*(288.14-0.00649*{H})**4.256))"}'
training_string_db = '{"MODE": 1, "ID": 0, "OBJECT":"example", "size":1000,"DATA":"aoa=angle of attack(radian),  W=current weight(N), V=true air speed(m/s), S=61.0(m^2), H=altitude msl(m)","CONSTRAINT": "abs({b}-{a})/{a}<0.01, b=lift(N), a = current weight(N)"}'
predict_string = '{"MODE": 2, "ID": 0, "VALUES":[0.02234021]}'
parse(model_define_string)
parse(training_string_db)
parse(predict_string)