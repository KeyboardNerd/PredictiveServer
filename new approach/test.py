from sclearning import *
import sys
import sqlite3
import time
import datetime
import sklearn.linear_model
import matplotlib.pyplot as plt
def TestParse():
    # read XPlaneFile to database
    XPlaneFileParser.DEBUG = True
    parser = XPlaneFileParser("a.db","ATR72","converter", "conf.ini")
    parser.connect()
    parser.parse("zxcv.txt", "|")
    parser.close()

def testWrite():
    # output to PILOTS format
    writer = PILOTSFileWriter("a.db","ATR72")
    writer.write(filenames = {"aktas.txt":["____A_ktas"], "all.txt":["___cltotal", "____A_ktas"]})

# learning model
def queryDataSet(dbNameFile, query):
    con = sqlite3.connect(dbNameFile)
    cursor = con.cursor()
    cursor.execute(query)
    units = []
    return (np.matrix(cursor.fetchall()), units)
def convertUnit(A, units):
    A[:,4] *= 4.44822
    A[:,3] = A[:,3]*0.0174533
    A[:,2] = A[:,2]+273.15
    A[:,1] = A[:,1]*3386.39
    A[:,0] = A[:,0]*0.514444
def makeTrainingData(A):
    N = np.ones((A[:,3].shape[0],2))
    N[:,0:1] = A[:,3]
    return N
def makeTargetValue(A):
    W = A[:,4]
    V = A[:,0]
    P = A[:,1]
    T = A[:,2]
    N = 2*W/(P/1000/(0.2869*T))/np.power(V,2)/61.0
    return N
def train(model, X,Y):
    model.fit(X,Y)
def predict(model, X):
    return model.predict(X)

# make training set
query = "SELECT [Vtrue,_ktas],[AMprs,_inHG],[AMtmp,_degC],[alpha,__deg],[curnt,___lb] FROM ATR72 WHERE abs([curnt,___lb]-[_lift,___lb])/[curnt,___lb]<0.02 ORDER BY [_totl,_time] limit 1000 "
A,units = queryDataSet("a.db", query)
convertUnit(A,units)
X = makeTrainingData(A)
Y = makeTargetValue(A)
model = sklearn.linear_model.LinearRegression()
train(model, X,Y)
Cl_predicted = predict(model, X)
# predict weight:
W = A[:,4]
V = A[:,0]
P = A[:,1]
T = A[:,2]
W_predicted = 0.5*np.multiply(np.multiply(Cl_predicted,(P/1000/(0.2869*T))),np.power(V,2))*61.0
# show result
plt.plot(np.linspace(0,W_predicted.shape[0],W_predicted.shape[0]), (W_predicted).tolist())
plt.plot(np.linspace(0,W_predicted.shape[0],W_predicted.shape[0]), (W).tolist())
plt.show()
