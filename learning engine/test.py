from sclearning import *
from scp import *
from scparser import *
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

db = ScDBController("b.db")
db.connect()
db.parse(ScDBParser(csvFileParser), "data/bayes_training.txt", "", "bayes")
db.setColumnInfo(tableName="bayes", fileName="bayes.ini")
db.close()