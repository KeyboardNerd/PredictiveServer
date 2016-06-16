'''
Temporal Database is a subset of database using generic database interface defined in
PEP 249 -- Python Database API Specification v2.0
Every data point is associated with a object, time range stamp
'''

dbController = None
dbConnection = None
def connect(database):
	global dbConnection
	dbConnection = dbController.connect(database)

def close():
	dbConnection.close()
def commit():
	dbConnection.commit()

def query_object( object_name):
	cursor = dbConnection.cursor()
	cursor.execute('SELECT "__INDEX","NAME","INFO" FROM "OBJECTS" WHERE NAME=?',(object_name,))
	indexes = cursor.fetchall()
	if len(indexes) != 1:
		if len(indexes) > 1:
			raise Exception("More than one object with name %s"%(object_name))
	if len(indexes) == 0:
		return None
	else:
		return indexes[0]

def query_data( time_start, time_end, object_name, data_name):
	# example implementation of this class
	cursor = dbConnection.cursor()
	object_index = query_object(object_name)[0]
	select_clause = 'SELECT TIMES,TIMEE,VALUE FROM %s '%data_name
	where_clause = 'WHERE OBJECT=%d'%object_index
	t = []
	if time_start:
		where_clause += ' AND TIMES >= ? '
		t.append(time_start)
	if time_end:
		where_clause += ' AND TIMEE <= ? '
		t.append(time_end)
	cursor.execute(select_clause+where_clause+" ORDER BY TIMES",t)
	r = cursor.fetchall()
	return r
def query_field( name ):
	cursor = dbConnection.cursor()
	cursor.execute('SELECT NAME, UNIT FROM COL_INFO WHERE NAME=?',(name,))
	indexes = cursor.fetchall()
	if len(indexes) != 1:
		if len(indexes) > 1:
			raise Exception("More than one object with name %s"%(object_name))
	if len(indexes) == 0:
		return None
	else:
		return indexes[0]
def insert_object( name, info, overwrite=False):
	cursor = dbConnection.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS "OBJECTS" (__INDEX INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT UNIQUE, INFO TEXT)')
	if overwrite:
		cursor.execute('INSERT OR REPLACE INTO OBJECTS (NAME, INFO) VALUES (?,?)',(name, info))
	else:
		cursor.execute('INSERT OR IGNORE INTO OBJECTS (NAME, INFO) VALUES (?,?)',(name, info))

def insert_field( data_field, unit):
	cursor = dbConnection.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS COL_INFO (__INDEX INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT UNIQUE, UNIT TEXT)')
	cursor.execute('CREATE TABLE IF NOT EXISTS %s (__INDEX INTEGER PRIMARY KEY AUTOINCREMENT, TIMES datetime, TIMEE datetime, VALUE FLOAT, OBJECT INTEGER)'%data_field)
	cursor.execute('INSERT OR IGNORE INTO COL_INFO (NAME, UNIT) VALUES (?,?)',(data_field, unit))

def insert_data( time_start, time_end, object_name, data_name, data):
	cursor = dbConnection.cursor()
	object_index = query_object(object_name)[0]
	# example implementation of this class using one table for each dataType
	cursor.execute('INSERT INTO %s values (null,?,?,?,?)'%data_name,(time_start, time_end, data,object_index))
