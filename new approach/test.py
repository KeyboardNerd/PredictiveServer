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

def csvFileParser(fileName, delimiter):
    reader = csv.reader(fileter(lambda(x): bool(x.strip())), open(fileName, "rU").readlines())
    heading = next(reader)
    data = []
    length = -1
    for row in reader:
        result = map(float, map(str.strip, row))
        if length == -1:
            length = len(result)
        elif length != len(result):
            raise Exception("data is not filled")
        data.append(result)
    return (heading, data, length)
def PILOTSFileParser(fileName, delimiter):
    # example file parser without considering time
    reader = filter(lambda(x): bool(x.strip()), open(fileName,"rU").readlines())
    headline = reader[0]
    if headline[0] != '#':
        raise Exception("Not a valid PILOTS file")
    heading = headline[1:].split(',')
    data = []
    length = len(heading)
    for row in reader[1:]:
        d = row.split(":")
        location = d[0]
        time = d[1]
        other = map(float, d[2].split(','))        
        if len(other) != length:
            raise Exception("data is not filled, aborted")
        data.append(other)
    return (heading, data, length)

def toX(A):
    N = np.ones((A[:,2].shape[0],2))
    N[:,0:1] = A[:,2]
    return N

def toY(A):
    W = A[:,3]
    V = A[:,0]
    H = A[:,1]
    rho = 4.174794718087996e-11*np.power((288.14-0.00649*H),4.256)
    np.savetxt("ssh.txt",H)
    np.savetxt("ssa.txt", 288.14-0.00649*H)
    np.savetxt("sss.txt", rho)
    Cl = np.divide(2*W,np.multiply(rho, np.multiply(np.power(V,2), 61.0)))
    return Cl

def toW(A):
    W = A[:,3]
    V = A[:,0]
    H = A[:,1]
    AoA = A[:,2]
    return (V,H,AoA,W)
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
    print model.coef_[0][0],model.coef_[0][1]
    Cl_predicted = model.predict(X)
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (Cl_predicted - Y).tolist())
    plt.show()
    W_predicted = np.multiply(Cl_predicted, proc.execute(estimateW))
    W = proc.execute(transform)[0]
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (W_predicted).tolist())
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), (W).tolist())
    plt.show()

def t1():
    db = ScDBController("b.db")
    proc = ScLearningPreprocessor()
    cols = ["true air speed","altitude msl", "angle of attack", "current weight"]
    units = ["m/s","meter","radian","newton"]
    constraint = "abs({b}-{a})/{b} < 0.02"
    constraintVar = {'a':"lift","b":"current weight"}
    orderandlimit = "{a}"
    orderandlimitVar = {'a':'total time'}
    proc.loadDataSet(db, "example", cols, constraint, constraintVar, orderandlimit, orderandlimitVar, units)
    X = proc.makeTrainingData(toX)
    Y = proc.makeTargetValue(toY)
    model = sklearn.linear_model.LinearRegression(normalize=True)
    model.fit(X,Y)
    print model.score(X,Y)
    Cl = model.predict(X)
    plt.plot(np.linspace(0, Y.shape[0], Y.shape[0]), Y.tolist())
    plt.plot(np.linspace(0, Y.shape[0], Y.shape[0]), Cl.tolist())
    plt.show()
    V,H,A,W = proc.execute(toW)
    rho = 4.174794718087996e-11*np.power((288.14-0.00649*H),4.256)
    L = 0.5*np.multiply(np.multiply(rho,np.power(V,2)),Cl)*61
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), L.tolist())
    plt.plot(np.linspace(0,Y.shape[0],Y.shape[0]), W.tolist())
    plt.show()
# # load testing data
# db = ScDBController("c.db")
# db.connect()
# db.parse(parser=ScDBParser(csvFileParser), fileName="testingdata.csv", delimiter=",", tableName="example")
# db.setColumnInfo(tableName="example",fileName="conf.ini")
# db.close()
t1()
