class ScGPSLocation():
	def __init__(self, latitude, longitude, elevation):
		self.longitude = longitude; self.latitude = latitude; self.elevation = altitude
	def __str__(self):
		return "%d,%d,%d"%(self.latitude,self.longitude,self.elevation)
	def __unicode__(self):
		return u"%d,%d,%d"%(self.latitude,self.longitude,self.elevation)
	def __repr__(self):
		return str(self)

def connect(self):
	self.dbConnection = self.dbController.connect(database)

def close(self):
	self.dbConnection.close()

def insert_object(self, name, info):
	cursor = self.dbConnection.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS "OBJECTS" (__INDEX PRIMARY KEY INTEGER AUTOINCREMENT, NAME TEXT UNIQUE, INFO TEXT)')

def query_object(self, object_name):
	cursor = self.dbConnection.cursor()
cursor.execute('SELECT "__INDEX" FROM "OBJECTS" WHERE NAME=?',(data_name))
	indexes = cursor.fetchall()
	if len(indexes) != 1:
		if len(indexes) == 0:
			raise Exception("No object with name %s"%(object_name))
		if len(indexes) > 1:
			raise Exception("More than one object with name %s"%(object_name))
	return indexes[0]

def create_data_table(self, data_field):
	cursor = self.dbConnection.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS {tableName}(__INDEX PRIMARY KEY INTEGER AUTOINCREMENT, TIMES datetime, TIMEE datetime, LOCS TEXT, LOCE TEXT, VALUE FLOAT, OBJECT INTEGER)'.format({"tableName": data_name}))
def insert_data(self, timeRange, locationRange, object_name, data_name, data, unit):
	""" timeRange = (startTime, endTime), locationRange = (startLocation, endLocation), object_name = what object the data belongs to, data_name = what table should data be inserted, data = the number/string/..."""
	cursor = self.dbConnection.cursor()
	# example implementation of this class using one table for each dataType
	cursor.execute('INSERT INTO ? values (?,?,?,?,?,?)',(data_name, timeRange[0], timeRange[1], str(locationRange[0]),str(locationRange[1]), object_index, data))

def query_data(self, timeRange, locationRange, object_name, data_name):
	# example implementation of this class
	cursor.execute('SELECT "__INDEX" FROM "OBJECTS" WHERE NAME=?',(object_name))
	cursor.execute('SELECT TIMES,TIMEE,VALUE FROM {field} WHERE OBJECT={index}'.format(data_name, index))
