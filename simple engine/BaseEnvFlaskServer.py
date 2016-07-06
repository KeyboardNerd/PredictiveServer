from BaseEnv import *
from flask import Flask
from flask import request
import numpy as np
file_name = "test.estimator"
app = Flask(__name__)

ESTIMATOR = {}
LAMBDA_CALCULATOR = {}
SCHEMA = {}
CONSTANT = {}
estimator, features, constant = load_estimator(file_name)
ESTIMATOR['0'] = (estimator, features, constant)
CONSTANT['0'] = {'s':61.0}
def accept_schema(request, model, estimator_dict, schema_dict, lambda_dict):
    estimator, features,constant = estimator_dict[model]
    to_parse = False
    if model in schema_dict and schema_dict[model]['name'] != request.args['name']:
        to_parse = True
    elif model not in schema_dict:
        schema_dict[model] = {}
        schema_dict[model]['name'] = request.args['name']
        to_parse = True
    if to_parse:
        current_schema = {}
        name = map(lambda(x): x.strip(), request.args['name'].split(',')) # parse to schema
        for i in xrange(len(name)):
            current_schema[name[i]] = {'index': i}
        schema_dict[model]['schema'] = current_schema
        schema_dict[model]['name'] = request.args['name']
        lambda_dict[model] = BaseEnv.generate_transformer(features, schema_dict[model]['schema'], constant)
        print "lambda expression updated!"
@app.route("/")
def hello():
    model = request.args['model']
    estimator, features,constant = ESTIMATOR[model] # retrieve model
    data = [map(lambda(x): float(x.strip()), request.args['value'].split(','))] # parse to data
    accept_schema(request, model, ESTIMATOR, SCHEMA, LAMBDA_CALCULATOR)
    feature_transformer = LAMBDA_CALCULATOR[model]
    X = np.apply_along_axis(feature_transformer, 1, data)
    return str(estimator.predict(X))[2:-2]