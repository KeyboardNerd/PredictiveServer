from sclearning import *
from sklearn.naive_bayes import GaussianNB
import json
import scp
import numpy as np
import os.path

def testDBRead():
    db = ScDBController("a.db")
    if not os.path.isfile("a.db"):
        db.connect()
        db.parse(parser=XPlaneFileParser(), fileName="xplane_sample.txt", delimiter="|", tableName="example")
        db.setColumnInfo(tableName="example",fileName="conf.ini")
        db.close()

def testDBWrite():
    db = ScDBController("a.db")
    db.connect()
    files = {"speed.txt":["true air speed", "ambient pressure"], "weight":["current weight"]}
    name = {"true air speed":"speed", "ambient pressure":"pressure", "current weight":"weight"}
    unit = {"true air speed":"m/s","ambient pressure":"pascal","current weight":"newton"}
    time_col = "total time"
    db.write(PILOTSFileWriter(files, name, unit), "example", " WHERE ROWINDEX BETWEEN 100 AND 200")

def testBayesian():
    # make model
    scp.register_model("Bayesian", GaussianNB())
    model_define_string2 = '{"MODE": 0, "ID":1, "MODEL":"Bayesian", "FEATURE":["{b}/{a}"], "LABEL":"{c}"}'
    training_string_db2 = '{"MODE": 1, "ID": 1, "OBJECT":"bayes", "size":3000,"DATA":"b=b,  a=a, c=c","CONSTRAINT": ""}'
    scp.parse(model_define_string2)
    scp.parse(training_string_db2)

    # test Bayesian
    c = np.random.normal(2, 0.2, 300)
    d = np.append(np.random.normal(4, 0.4, 100), np.random.normal(6, 1, 100))
    d = np.append(d, np.random.normal(8, 1, 100))
    X1 = d/c
    # query result
    Y1 = map(lambda a: scp.parse(json.dumps({'MODE':2,'ID':1,'VALUES':a})), X1)
    # plot result
    scp.histo_plot(X1[:100])
    scp.histo_plot(X1[100:200])
    scp.histo_plot(X1[200:300])
    plt.xlabel('d/c')
    plt.ylabel('Probability')
    plt.title('Histogram of the testing set d/c')
    plt.grid(True)
    plt.show()

    # Plot d/c
    plt.plot(X1)
    plt.plot(Y1, marker='o', markersize=5, label='Type')
    plt.legend()
    plt.title("Testing Set d/c, and types")
    plt.ylabel("d/c")
    plt.xlabel("time (s)")
    plt.show()
if __name__ == '__main__':
    testBayesian()