from sclearning import *
import sys
import sqlite3
import time
import datetime

# translate XPlane file to database
# x = XPlaneFileParser("test.db", "ATR72")
# x.connect()
# x.parse("Data.txt")
# x.close()
# print x.columns
#connection.commit()
# save as PILOTS form
# FileDict = {"aktas.txt":["____A_ktas"], "all.txt":["___cltotal", "____A_ktas"]}
# writer = PILOTSFileWriter("test.db", "ATR72")
# writer.write(FileDict, timeColumnName = "_totl_time")

# read file to database
parser = XPlaneFileParser("a.db","ATR72","")
parser.connect()
parser.parse("zxcv.txt","conf.", "|")
parser.close()

# output to PILOTS format
writer = PILOTSFileWriter("a.db","ATR72")
