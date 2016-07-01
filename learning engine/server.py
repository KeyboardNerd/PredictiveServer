import scp
import numpy
import json
from flask import Flask
from flask import request
app = Flask(__name__)
scp.load_estimator("test")
@app.route("/")
def hello():
    mode_ = int(request.args['MODE'])
    id_ = int(request.args['ID'])
    query = ""
    for feature_name in scp.find_feature(id_):
        query += (feature_name + '=' + request.args[feature_name] + ',')
    query = query[:-1]
    print query
    return str(scp.parse(json.dumps({'MODE':mode_, 'ID':id_,'VALUES':query})).tolist())[1:-1]