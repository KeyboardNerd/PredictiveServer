import numpy as np
from pint import UnitRegistry
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import re
import bayes
import pickle

class BaseEnv():
    ''' class BaseEnv provides basic access of loading,training functions for machine learning'''
    def __init__(self):
        self.constant_dict = {}
        self.variable_dict = {}
        self.data = None
        self.feature = None
        self.label = None
        self.cached_data = None

    def load_file(self, file_name, map_method, header_method=None, header=None):
        '''
            @return: returns a matrix of data contained in file with name "file_name"
            @effect: clean and set self.variable_dict to column information 
            @parameters: file_name( string, name of the file want to load )
                         map_method( function with one parameter, this will be mapped to each line in file body. It should retrun an array-like )
                         header_method( function with one parameter, this will be used for parsing first line (header) in the file. If it's None, then we assume that the file contains no header)
                         header ( list of string, header contains the semantic meaning of each column in returend matrix)
        '''
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
        self.variable_dict = {}
        for i in xrange(len(head)):
            self.variable_dict[head[i]] = {'index': i}
        return raw_data

    def append_data(self, data):
        '''
            @effect: vertically stack data to the end of self.data, if self.data is empty, then data will be copied into self.data
            @parameters: data(numpy ndarray)
            @require: self.data and data's column dimension should match
        '''
        if self.data:
            self.data = self.data.vstack(data)
        else:
            self.data = data.copy()


    def set_data(self, data):
        '''
            @effect: self.data is set to copy of data
            @param: data(numpy ndarray)
        '''
        self.data = data.copy()

    def set_constant(self, **constants):
        '''
            @effect: add constant_dict with the key value pairs defined in constants
            @param: constants(dictionary, the key value pairs to be added to self.constant_dict)
        '''
        self.constant_dict.update(constants)


    def update_variable_info(self, **info):
        '''
            @effect: update key value pairs stored in self.variable_dict
            @param: info(dictionary, key value pairs to be used to update self.variable_dict)
        '''
        for key in info:
            self.variable_dict[key].update(info[key])

    def get_constant(self):
        '''
            @return: copy of self.constant_dict
        '''
        return self.constant_dict.copy()

    def get_schema_info(self, *columns):
        '''
            @return: the requested {key: value} for each value stored in self.variable_dict[key]
            @param: columns( list of string, list of requested keys )
        '''
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
        '''
            @return: a list of dictionaries representing the semantic meaning of corresponding column in matrix
            @param: requested columns, @seealso get_schema_info
        '''
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
        '''
            @return: return value in transformer
            @param: transformer( a function with parameter(self.data), parameters )
                    parameters( a dictionary of parameters required in transformer)
        '''
        return transformer(self.data, **parameters)

    @staticmethod
    def unit_transformer(npmatrix, **parameters):
        '''
            @return: return a numpy matrix, which is the matrix with converted unit
            @param: npmatrix( a ndarray )
                    parameters (dictionary with at least fields "schema", "units", schema is schema_info defined in Env, including origin units, units is a dictionary with key in schema, representing the result unit)
        '''
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
        '''
            @return lambda expression which will transform a matrix/ndarray/array-like to np.array. Every element is defined by feature_list
            @param: feature_list(list of special string: each string contains '{var}' to identify var as a variable, and each string complies to python grammar)
                    schema ( dictionary of schematic meaning representing each column of the matrix/ndarry to be transformed)
                    constant ( dictionary of var: number, representing the constants involved in the feature_list)
        '''
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
        '''
            first it generates label, feature transformer based on parameters and apply the transformer to each row in npmatrix
            @return a dictionary with {"label": label matrix, "feature": feature matrix}        
            @param: npmatrix( ndarray, the data to be transformed )
                    parameters: ( dictionary with required fields: schema (the schema of npmatrix), constant (constant used in feature,label transformation), features (a list of string defining the transformer ), labels ( a list of string defining the transformer ) )                    
        '''
        schema = parameters['schema']; constant = parameters['constant']; features=parameters['features']; labels=parameters['labels']
        feature_transformer = BaseEnv.generate_transformer(features, schema, constant)
        label_transformer = BaseEnv.generate_transformer(labels, schema, constant)
        X = np.apply_along_axis(feature_transformer, 1, npmatrix)
        Y = np.apply_along_axis(label_transformer, 1, npmatrix)
        return {'label': Y, 'feature': X}


    def train_estimator(self,estimator):
        '''
            train a estimator, which has function fit(feature, label) for training the estimator
            @return a trained estimator
            @param: estimator(a class/module with function fit(feature, label) for training itself)
        '''
        estimator.fit(self.feature, self.label)
        return estimator


def save_estimator(filename, estimator, features, constants, to_json=False):
    '''
        save one estimator, estimator feature transformer list, constants to a pickle binary file
        @param: filename ( string, the file name)
                estimator ( scikit model, trained estimator )
                features ( list of strings, defining how to compute input matrix from raw matrix)
                constants ( dictionary of string: number pair, the values used in features if it appears as constant)
                to_json ( call to_json function in estimator to save the serialized version of estimator)
        @effect: create or replace a file named filename, containing information about estimator, features and constants, which can be retrieved by pickle.load
    '''
    if to_json:
        estimator = estimator.to_json()
    pickle.dump((estimator, features, constants),open(filename, 'w+b'))

def load_estimator(filename, to_json=False, estimator_initializer=None):
    '''
        load an estimator, estimator feature transformer, constants from file with name filename
        @param: filename (string, the file name)
                to_json (bool, is the estimator a json string?)
                estimator_initializer (function, should we initialize a instance of estimator and load json file?)
        @return: a tuple containing estimator, estimator feature transformer list, constants
    '''
    estimator_json, features,constants = pickle.load(open(filename, 'rb'))
    if to_json and estimator_initializer:
        estimator = estimator_initializer()
        estimator.load_json(estimator_json)
    else:
        estimator = estimator_json
    return (estimator, features, constants)



