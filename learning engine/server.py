import scp
import numpy
from flask import Flask
from flask import request
app = Flask(__name__)
scp.load_estimator("test")
@app.route("/")
def hello():
    values = request.args['id']
    print '{"MODE": 2, "ID": 0, "VALUES":%s}'%str(values)
    return str(scp.parse('{"MODE": 2, "ID": 0, "VALUES":%s}'%str(values)))
