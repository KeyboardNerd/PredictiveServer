import numpy as np
import sklearn as sk
import sqlite3
import csv
import abc
import time
import datetime
class FileParser(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, dbName, tableName, unitConverter, configFileName):
        self.configFileName = configFileName
        self.dbName = dbName # file parser parse the csv file and store result into sqlite database by calling
        self.tableName = tableName
        self.columns = []
        self.connection = None
        self.unitConverter = unitConverter
    def connect(self):
        self.connection = sqlite3.connect(self.dbName)
    def close(self):
        self.connection.close()
    @abc.abstractmethod
    def parse(self, filename):
        pass

class XPlaneFileParser(FileParser):
    def setColumnInfo(self, dictionary):
        columns = getColumns()
        for i in columns:
            if i in dictionary:
                t = (dictionary[i]["UNIT"], dictionary[i]["NAME"])
                query = "UPDATE COL_INFO SET UNIT=" + t[0] +",NAME="+t[1]+" WHERE COL_IND=" + i

    def getColumns():
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info("+self.tableName+")")
        return map(lambda(t): t[1],cursor.fetchall())[1:]

    def parse(self, filename, delimiter):
        reader = csv.reader(filter(lambda(x): bool(x.strip()), open(filename,"rU").readlines()), delimiter=delimiter)
        heading = next(reader)
        header = []
        append = False
        r = ""
        for i in xrange(len(heading)):
            if i % 2 == 0 and i != 0:
                header.append(r)
                r = ""
            r += heading[i].strip().replace("/","")
        createTableQuery = "CREATE TABLE IF NOT EXISTS " + self.tableName + " (ROWINDEX INTEGER PRIMARY KEY,"
        for i in xrange(len(header)):
            createTableQuery += ( header[i] + " DOUBLE")
            if i != len(header) - 1:
                createTableQuery += ","
        # read the csv file to database
        # set columns if it's not here
        createTableQuery = createTableQuery + ")"
        self.columns = header
        cursor = self.connection.cursor()
        cursor.execute(createTableQuery)
        toInsert = []
        length = -1
        for row in reader:
            result = map(float, map(str.strip, row[:-1]))
            if length == -1:
                length = len(result)
            if length != len(result):
                raise Exception("data is not aligned")
            toInsert.append(result)
        query = "insert into " + self.tableName + " values (null,"
        for i in xrange(length):
            query += "?"
            if (i != length - 1):
                query += ","
        query += ")"
        cursor.executemany(query, toInsert)
        self.connection.commit()
        # create column information
        cursor = self.connection.cursor()
        # check if table exists:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND  name='COL_INFO'")
        result = cursor.fetchall()
        # if it's not created then:
        print result
        if len(result) == 0:
            # get column names:
            cursor.execute("PRAGMA table_info("+self.tableName+")")
            columns = map(lambda(t): t[1],cursor.fetchall())[1:]
            t = map(lambda(c): (c,c), columns)
            cursor.execute("CREATE TABLE IF NOT EXISTS COL_INFO (COL_IND TEXT PRIMARY KEY, UNIT TEXT, NAME TEXT)")
            cursor.executemany("INSERT INTO COL_INFO values (?,null,?)", t)
            self.connection.commit()

class PILOTSFileWriter(object):
    """docstring for PILOTSDataWriter"""
    def __init__(self, dbName, dbTable):
        super(PILOTSFileWriter, self).__init__()
        self.dbName = dbName
        self.dbTable = dbTable

    def toPILOTSTIME(self, basetime, elapsedtime):
        currenttime = basetime+elapsedtime # second
        return datetime.datetime.fromtimestamp(currenttime).strftime(':%Y-%m-%d %H%M%S%f')[:-3]+'-0500:'

    def write(self, filenames, rowRange=None, timeColumnName="", baseTime=time.time()):
        connection = sqlite3.connect(self.dbName)
        cursor = connection.cursor()
        if timeColumnName != "":
            timeColumnName = timeColumnName + "," # for query
        debug = open("DEBUG","w+")
        for filename in filenames:
            # make query
            queryFields = ""
            length = len(filenames[filename])
            for index in xrange(length):
                queryFields += filenames[filename][index]
                if (index != length - 1):
                    queryFields += ","
            if rowRange:
                print rowRange
                query = "SELECT "+timeColumnName+queryFields+" FROM "+self.dbTable+" WHERE ROWINDEX BETWEEN "+str(rowRange[0])+" AND "+str(rowRange[1])
            else:
                query = "SELECT "+timeColumnName+queryFields+" FROM "+self.dbTable
            print query
            cursor.execute(query);
            resultFile = open(filename,"w+")
            resultFile.write("#"+queryFields +"\n")
            if timeColumnName != "":
                for i in cursor:
                    debug.write(str(i)+"\n")
                    resultFile.write(self.toPILOTSTIME(baseTime, i[0]) + str(i[1:])[1:-1] +"\n")
            else:
                elapsedTime = 0
                for i in cursor:
                    resultFile.write(self.toPILOTSTIME(baseTime, elapsedTime) + str(i)[1:-1]+"\n")
                    elapsedTime += 1
            resultFile.close()
        debug.close()
        connection.close()

class Preprocessor(object):
    def __init__(self, arg):
        super(Preprocessor, self).__init__()
        self.arg = arg

class LearningModel(object):
    """docstring for LearningModel"""
    def __init__(self, arg):
        super(LearningModel, self).__init__()
        self.arg = arg

class PostProcessor(object):
    """docstring for PostProcessor"""
    def __init__(self, arg):
        super(PostProcessor, self).__init__()
        self.arg = arg
