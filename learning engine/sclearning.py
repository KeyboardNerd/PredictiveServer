import numpy as np
import sklearn as sk
import sqlite3
import csv
import time
import datetime
import ConfigParser

from sclearning import *
import sys
import sqlite3
import time
import datetime
import sklearn.svm
import matplotlib.pyplot as plt
import re
from pint import UnitRegistry

def _convert(matrix, inputUnit, outputUnit):
    ureg = UnitRegistry()
    q = ureg.Quantity
    return q(matrix, inputUnit).to(outputUnit).magnitude

def unitConvert(dataSet, inputUnits, outputUnits):
    if len(inputUnits) != len(outputUnits):
        raise Exception("Units List should match")
    for i in xrange(len(inputUnits)):
        if (inputUnits[i] and inputUnits[i] != outputUnits[i]):
            dataSet[:,i] = _convert(dataSet[:,i], inputUnits[i], outputUnits[i])

class LearnPreprocessor():
    # load file/database/etc to memory for learning model to run
    def __init__(self):
        self.feature_equation = None
        self.label_equation = None
        self.feature_var = []
        self.label_var = {}
        self.feature = None
        self.label = None
        self.cols = {}
        self.regex = re.compile('\{[0-9A-Za-z]+\}')
    def setfeature(self, equation_list):
        self.feature_equation = equation_list
        for equation in equation_list:
            current_obj = {}
            for i in self.regex.findall(equation):
                current_obj[i[1:-1]] = ""
            self.feature_var.append(current_obj)
        
    def setlabel(self, equation):
        self.label_equation = equation
        for i in self.regex.findall(equation):
            self.label_var[i[1:-1]] = ""
    
    def load(self, database, table, requested_values, constraint_formula, constraint_values, size):
        database.connect()
        col_names = []
        col_units = []
        requested_units = []
        constraint_pairs = {}
        for i in requested_values:
            item = requested_values[i]
            if not item['isnumber']:
                info = database.queryColumnInfoByName(item['value'], True)[0]
                col_names.append(info[0])
                col_units.append(info[2])
                item['value'] = info[0]
                requested_units.append(item['unit'])
        for i in constraint_values:
            item = constraint_values[i]
            if not item['isnumber']:
                info = database.queryColumnInfoByName(item['value'], True)[0]
                col_names.append(info[0])
                item['value'] = info[0]
            constraint_pairs[i] = '"' + item['value'] + '"'
        data = np.array(database.queryDataByConstraintAndOrder(table, col_names, "%s"%(constraint_formula.format(**constraint_pairs)), None, limit=size))
        database.close()
        unitConvert(data, col_units, requested_units)
        for i in xrange(len(col_names)):
            self.cols[col_names[i]] = i
        self.dataset = data
        # make feature 
        self.feature = np.ones((self.dataset.shape[0], len(self.feature_var)))
        for one_feature_index in xrange(len(self.feature_var)):
            one_feature = self.feature_var[one_feature_index]
            for i in one_feature:
                if requested_values[i]['isnumber']:
                    one_feature[i] = requested_values[i]['value']
                else:
                    one_feature[i] = 'self.dataset[:,%d]'%self.cols[requested_values[i]['value']]                
            self.feature[:,one_feature_index] = eval(self.feature_equation[one_feature_index].format(**one_feature)) # it's dangerous to do this, use ast manipulation to revise this later
        # make label
        for i in self.label_var:
            if requested_values[i]['isnumber']:
                self.label_var[i] = requested_values[i]['value']
            else:
                self.label_var[i] = 'self.dataset[:,%d]'%self.cols[requested_values[i]['value']]
        self.label = eval(self.label_equation.format(**self.label_var)) # it's dangerous to do this, use ast manipulation to revise this later
        np.savetxt("feature.csv",self.feature, delimiter=',')
        np.savetxt("label.csv",self.label, delimiter=',')

class ScDBController(object):
    DEBUG = False
    def __init__(self, dbName):
        self.dbName = dbName
        self.connection = None
    def connect(self):
        self.connection = sqlite3.connect(self.dbName)
    def close(self):
        self.connection.close()
    def parse_with_line_function(self, filename, table, function, title=None, title_parse=None):
        f = open(filename)
    def parse(self, parser, fileName, delimiter, tableName):
        parser.parse(fileName, delimiter, tableName, self.dbName, self.connection)
    def write(self, writer, tableName, constraint):
        writer.write(self, tableName, constraint)
    def setColumnInfo(self, tableName, fileName):
        # set column information
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND  name='COL_INFO'")
        result = cursor.fetchall()
        # create table if it's not here
        cursor.execute("CREATE TABLE IF NOT EXISTS COL_INFO (\'column\' TEXT NOT NULL, \'unit\' TEXT, \'type\' TEXT, \'name\' TEXT, \'belong\' TEXT NOT NULL, CONSTRAINT \'ID\' PRIMARY KEY (\'column\',\'belong\'))")
        # update the rows, first delete all the rows belonging to tableName
        try:
            cursor.execute("DELETE FROM COL_INFO WHERE belong=\""+tableName+"\"")        
        except sqlite3.OperationalError as e:
            print "COL_INFO DELETE ERR: " + str(e)
            pass
        result = self._readConf(fileName,tableName)
        cursor.executemany("INSERT INTO COL_INFO values (?,?,?,?,?)",result)
        self.connection.commit()
    def queryColumnInfoByName(self,name, distinctCheck=False):
        cursor = self.connection.cursor()
        query = "SELECT COLUMN, NAME, UNIT, TYPE FROM COL_INFO WHERE NAME='%s'"%name;
        if self.DEBUG:
            print query
        cursor.execute(query)
        result = cursor.fetchall()
        if distinctCheck:
            if len(result) == 0:
                raise Exception("No column name is found:" + name)
            elif len(result) > 1:
                raise Exception("Confusing column name %d columns are found:" + str(result))
        return result
    def execute(self, q):
        result = self.connection.cursor().execute(q)
        self.connection.commit()
        return result
    def queryDataByConstraintAndOrder(self, table, columns, constraint=None, order=None, limit=None):
        if type(columns) is list:
            select = ""
            for i in columns:
                select += '"%s",'%i
            select = select[:-1]
        s = 'SELECT %s '%(select)
        f = 'FROM %s '%(table)
        w = ""
        o = ""
        if (constraint):
            w = 'WHERE %s '%(constraint)
        if (order):
            o = 'ORDER BY %s '%(order)
        if (limit):
            l = 'limit %d '%limit
        query = s + f + w + o + l
        if self.DEBUG:
            print query
        result = None
        try:
            result = self.connection.cursor().execute(query).fetchall()
            return result
        except sqlite3.OperationalError as e:
            raise type(e)(e.message + "\nError Query: " + query)

    def _readConf(self, fileName, tableName):
        reader = csv.reader(filter(lambda(x): bool(x.strip()) and (bool(x.strip()) and x[0] != ';'), open(fileName,"rU").readlines()), delimiter='|')
        result = []
        for i in reader:
            result.append(map(str.strip, i) + [tableName])
        return result

class ScDBParser(object):
    DEBUG = False
    def __init__(self, parser=None):
        self.connection = None
        self.parser = parser
    def setParserFunction(self, function):
        self.parser = function
    def parse(self, fileName, delimiter, tableName, dbName, externalConnection=None):
        if externalConnection != None:
            connection = externalConnection
        else:
            connection = sqlite3.connect(dbName)

        heading, toInsert, rowLength = self.parser(fileName, delimiter)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND  name=\"%s\""%(tableName))
        if len(cursor.fetchall()) == 0: # if there's no table named <tableName>
            if self.DEBUG:
                print "CREATING NEW TABLE...:"
            createTableQuery = "CREATE TABLE IF NOT EXISTS " + tableName + " (ROWINDEX INTEGER PRIMARY KEY AUTOINCREMENT,"
            for i in xrange(len(heading)):
                if heading[i].strip(): # if the heading is not empty
                    createTableQuery += ( '\"'+heading[i].strip() + '\"' + " DOUBLE,")
            createTableQuery = createTableQuery[:-1] + ")" # remove the last comma
            if self.DEBUG:
                print createTableQuery
            cursor.execute(createTableQuery)
        # insert data:
        query = "insert into " + tableName + " values (null,"
        for i in xrange(rowLength):
            query += "?,"
        query = query[:-1] + ")"
        cursor.executemany(query, toInsert)
        connection.commit()
        if externalConnection == None:
            connection.close()
    
class PILOTSFileWriter(object):
    """docstring for PILOTSDataWriter"""
    DEBUG = False
    def __init__(self, outputFiles, name, unit, timeColumn=None, baseTime=time.time()):
        super(PILOTSFileWriter, self).__init__()
        self.fileNames = outputFiles
        self.timeColumn = timeColumn
        self.name = name
        self.unit = unit
        self.baseTime = baseTime
    def toPILOTSTIME(self, basetime, elapsedtime):
        currenttime = basetime+elapsedtime # second
        return datetime.datetime.fromtimestamp(currenttime).strftime(':%Y-%m-%d %H%M%S%f')[:-3]+'-0500:'
            
    def write(self, database, dbTable, constraint=""):
        connection = database.connection
        cursor = connection.cursor()
        if self.timeColumn != None:
            timeColumn = "\""+database.queryColumnInfoByName(self.timeColumn)[0][0]+"\"" + "," # for query
        else:
            timeColumn = ""
        for fileName in self.fileNames:
            # query
            queryFields = ""
            length = len(self.fileNames[fileName])
            headline = "#"
            units = []
            tounits = []
            for index in xrange(length):
                columnInfo = database.queryColumnInfoByName(self.fileNames[fileName][index])
                units.append(columnInfo[0][2])
                tounits.append(self.unit[self.fileNames[fileName][index]])
                queryFields += "\""+ columnInfo[0][0] +"\","
                if self.fileNames[fileName][index] in self.name:
                    headline += self.name[self.fileNames[fileName][index]]
                else:
                    headline += self.fileNames[fileName][index]
                headline += ","
            queryFields = queryFields[:-1]
            query = "SELECT "+timeColumn+queryFields+" FROM "+ dbTable + " " + constraint
            cursor.execute(query);
            result = np.matrix(cursor.fetchall())
            unitConvert(result, units, tounits)
            # save to file
            resultFile = open(fileName,"w+")
            resultFile.write(headline[:-1]+"\n")
            if self.timeColumn != None:                
                for i in result:
                    line = self.toPILOTSTIME(self.baseTime, i[:,0]) + str(i.tolist()[0][1:])[1:-1] +"\n"
                    resultFile.write(line)
            else:
                elapsedTime = 0
                for i in result:
                    line = self.toPILOTSTIME(self.baseTime, i[:,0]) + str(i.tolist()[0][:])[1:-1] +"\n"
                    resultFile.write(line)
                    elapsedTime += 1
            resultFile.close()
