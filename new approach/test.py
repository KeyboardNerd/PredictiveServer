from sclearning import *
import numpy as np
import os.path

def XPlaneFileParser(fileName, delimiter):
    reader = csv.reader(filter(lambda(x): bool(x.strip()), open(fileName,"rU").readlines()), delimiter=delimiter)
    heading = next(reader)
    data = []
    length = -1
    for row in reader:
        result = map(float, map(str.strip, row[:-1]))
        if length == -1:
            length = len(result)
        elif length != len(result):
            raise Exception("data is not filled")
        data.append(result)
    return (heading, data, length)

def toX(A):
    N = np.ones((A[:,3].shape[0],2))
    N[:,0:1] = A[:,3]
    return N

def toY(A):
    W = A[:,4]
    V = A[:,0]
    P = A[:,1]
    T = A[:,2]
    N = 2*W/(P/1000/(0.2869*T))/np.power(V,2)/61.0
    return N

def transform(A):
    V = A[:,0]
    P = A[:,1]
    T = A[:,2]
    W = A[:,4]
    return (W,V,P,T)

def estimateW(A):
    V = A[:,0]
    P = A[:,1]
    T = A[:,2]
    W = A[:,4]
    return 0.5*np.multiply(P/1000/(0.2869*T),np.power(V,2))*61.0

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

def testLearning():
    db = ScDBController("a.db")
    proc = ScLearningPreprocessor()
    cols = ["true air speed", "ambient pressure", "ambient temperature", "angle of attack", "current weight"]
    constraint = "abs({b}-{a})/{b}<0.01"
    constraintVar = {'a':"lift", 'b':"current weight"}
    orderandlimit = "{a}"
    orderandlimitVar = {'a':'total time'}
    units = ["m/s","pascal","kelvin","radian","newton"]
    proc.loadDataSet(db, "example", cols, constraint, constraintVar, orderandlimit, orderandlimitVar,units)
    X = proc.makeTrainingData(toX)
    Y = proc.makeTargetValue(toY)
    model = sklearn.linear_model.LinearRegression()
    model.fit(X,Y)
    Cl_predicted = model.predict(X)
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (Cl_predicted - Y).tolist())
    plt.show()
    W_predicted = np.multiply(Cl_predicted, proc.execute(estimateW))
    W = proc.execute(transform)[0]
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (W_predicted).tolist())
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (W).tolist())
    plt.show()

testDBRead()
testDBWrite()
testLearning()