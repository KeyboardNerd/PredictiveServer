import numpy as np
from pint import UnitRegistry
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import re
import bayes
import pickle

class BaseEnv():
    def __init__(self):
        self.constant_dict = {}
        self.variable_dict = {}
        self.data = None
        self.feature = None
        self.label = None
        self.cached_data = None

    def load_file(self, file_name, map_method, header_method=None, header=None):
        raw = open(file_name,'rU').readlines()
        head = None
        start = 0
        if header_method:
            start = 1
            head = header_method(raw[0])
        body = raw[start:]
        raw_data = np.asmatrix(map(map_method, body))
        if header:
            head = header
        for i in xrange(len(head)):
            self.variable_dict[head[i]] = {'index': i}
        return raw_data

    def append_data(self, data):
        if self.data:
            self.data = self.data.vstack(data)
        else:
            self.data = data.copy()
    def set_data(self, data):
        self.data = data.copy()

    def set_constant(self, **constants):
        self.constant_dict.update(constants)

    def update_variable_info(self, **info):
        for key in info:
            self.variable_dict[key].update(info[key])
    def get_constant(self):
        return self.constant_dict.copy()
    def get_schema_info(self, *columns):
        if not columns:
            return self.variable_dict.copy()
        else:
            result = {}
            for key in self.variable_dict:
                result[key] = {}
                for value_key in columns:
                    result[key][value_key] = self.variable_dict[key][value_key]
            return result
    def get_columns_info(self, *columns):
        result = [0]*len(self.variable_dict)
        for key in self.variable_dict:
            if not columns:
                # return all values if columns is not defined
                value = self.variable_dict[key].copy()
                value.update({'name': key})
                result[self.variable_dict[key]['index']] = value
            else:
                items = {}
                for i in columns:
                    if i == 'name':
                        item[i] = key
                    else:
                        items[i] = self.variable_dict[key][i]
                result[self.variable_dict[key]['index']] = items
        return result

    def transform(self, transformer, **parameters):
        # a transformer is a function transform and return modified data
        return transformer(self.data, **parameters)
    @staticmethod
    def unit_transformer(npmatrix, **parameters):
        schema = parameters['schema']
        tounits = parameters['units']
        data = npmatrix.copy()
        ureg = UnitRegistry()
        Q_ = ureg.Quantity
        for i in schema:
            index = schema[i]['index']
            unit = schema[i]['unit']
            tounit = tounits[i]
            data[:,index] = Q_(data[:,index], unit).to(tounit).magnitude
        return data
    @staticmethod
    def generate_transformer(feature_list, schema, constant):
        def position_lookup(requested_name, schema, constant, matrix_name):
            if requested_name in schema:
                return {requested_name: "%s[%d]"%(matrix_name, schema[requested_name]['index'])}
            elif requested_name in constant:
                return {requested_name: str(constant[requested_name])}
            else:
                raise Exception("position lookup failed" + requested_name)
        regex = re.compile('\{[0-9A-Za-z]+\}')
        indexes = {}
        find_var_function = lambda(string): map(lambda(requested_name): position_lookup(requested_name, schema, constant, 'x'), map(lambda(word):word[1:-1], regex.findall(i)))
        string_vars = map(lambda(one): (reduce(lambda a,b: dict(a,**b), one)), [ find_var_function(i) for i in feature_list])
        string = []
        for i in xrange(len(feature_list)):
            string.append(feature_list[i].format(**string_vars[i]))
        transformer = eval('lambda(x): np.asarray(['+reduce(lambda a,b: a+','+b, string)+'])')
        return transformer
    @staticmethod
    def feature_label_transformer(npmatrix, **parameters):
        schema = parameters['schema']; constant = parameters['constant']; features=parameters['features']; labels=parameters['labels']
        feature_transformer = BaseEnv.generate_transformer(features, schema, constant)
        label_transformer = BaseEnv.generate_transformer(labels, schema, constant)
        X = np.apply_along_axis(feature_transformer, 1, npmatrix)
        Y = np.apply_along_axis(label_transformer, 1, npmatrix)
        return {'label': Y, 'feature': X}
    def train_estimator(self,estimator):
        estimator.fit(self.feature, self.label)
        return estimator


def save_estimator(filename, estimator, features, constants):
    pickle.dump((estimator, features, constants),open(filename, 'w+b'))

def load_estimator(filename):
    estimator, features,constants = pickle.load(open(filename, 'rb'))
    return (estimator, features, constants)

def save_bayes(filename, estimator, features, constants):
    estimator_json = estimator.to_json()
    pickle.dump((estimator_json, features, constants), open(filename, 'w+b'))
def load_bayes(filename):
    estimator_json, features, constants = pickle.load(open(filename, 'rb'))
    estimator = bayes.Bayes()
    estimator.load_json(estimator_json)
    return (estimator, features, constants)
def generate_linearRegression():
    units = ['knot', 'in_Hg', 'celsius', 'degree', 'force_pound']
    tounits = ['m/s', 'pascal', 'kelvin', 'radian', 'newton']
    name = ['v','p','t','a','w']
    env = BaseEnv()
    csvfile = lambda(row): map( float, row.split(','))
    csvfile_header = lambda(row): map( lambda(word): word.strip(), row.split(','))
    pilotfile = lambda(row): map(float, row.split(':')[-1].split(','))
    pilot_header = lambda(row): map(lambda(word): word.strip(), row[1:].split(','))
    env.load_file("thetrain.csv", csvfile, csvfile_header, header=['v','p','t','a','w'])
    env.append_cached_data()
    env.set_constant(s=61.0)
    env.update_variable_info(v={'unit': 'knot'}, p={'unit': 'in_Hg'}, t={'unit': 'celsius'}, a={'unit': 'degree'}, w={'unit': 'force_pound'})
    cached_data = env.transform(env.unit_transformer, schema=env.get_schema_info(), units=dict(v='m/s',a='radian',w='newton',t='kelvin',p='pascal'))
    env.data = cached_data.copy()
    cached_data = env.transform(env.feature_label_transformer, schema=env.get_schema_info(), constant=env.get_constant(), features=["{a}"], labels=["2*{w}/({v}**2*({p}/286.9/{t})*{s})"])
    env.label = cached_data['label']
    env.feature = cached_data['feature']
    estimator = env.train_estimator(LinearRegression())
    # for estimation, the input should be: schematic meaning of the matrix columns, feature transformation method
    input_data = np.ones((100,1))
    schema = {'aoa': {'index': 0}}
    features = ['{aoa}']
    for i in xrange(1):
        estimator.predict(np.apply_along_axis(BaseEnv.generate_transformer(features, schema, {}), 1, input_data))
    save_estimator("linearRegression.estimator", estimator, features, env.constant_dict)
    load_estimator("linearRegression.estimator")

def generate_Bayes():
    name = ['a','b','type']
    env = BaseEnv()
    pilotfile = lambda(row): map(float, row.split(':')[-1].split(','))
    pilot_header = lambda(row): map(lambda(word): word.strip(), row[1:].split(','))
    data = env.load_file("data/bayes_training.txt", pilotfile, pilot_header, header=name)
    env.append_data(data)
    cached_data = env.transform(env.feature_label_transformer, schema=env.get_schema_info(), constant=env.get_constant(), features=['{b}/{a}'], labels=["{type}"])
    env.label = cached_data['label']
    env.feature = cached_data['feature']
    estimator = env.train_estimator(bayes.Bayes())
    data = env.load_file('data/bayes_testing.txt', pilotfile, pilot_header, header=name)
    transformer = BaseEnv.generate_transformer(feature_list=['{b}/{a}'], schema=env.get_schema_info(), constant=env.get_constant())
    save_bayes("bayes.estimator", estimator, ['{b}/{a}'], env.constant_dict)
    (estimator, features, constants) = load_bayes("bayes.estimator")
    print estimator.predict(np.asmatrix(np.apply_along_axis(transformer, 1, data)))
if __name__ == '__main__':
    generate_Bayes()