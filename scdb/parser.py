attribute = None
units = None
delimiter = None
time_column = None
_object_name = None
_database = None
def parse(file_name, database, object_name, method):
	global _database, _object_name
	_object_name = _object_name
	_database = database
	result = method(file_name)
	if not database.query_object(object_name):
		database.insert_object(object_name, "")
	for i in result:
		if not database.query_field(i):
			if i in units:
				database.insert_field(i,units[i])
			else:
				database.insert_field(i,'null')
	for i in result:
		for j in result[i]:
			database.insert_data(j[0],j[1],object_name,i,j[2])

def pilots_parse(file_name):
	global attribute
	reader = filter(lambda(x): bool(x.strip()), open(file_name,"rU").readlines())
	headline = reader[0]
	if headline[0] != '#':
		raise Exception("Not a valid PILOTS file")
	if attribute == None:
		heading = headline[1:].split(',')
	else:
		heading = attribute[:]
		if len(heading) != headline[1:].split(','):
			raise Exception("Not a valid attribute setting")
	r = {}
	for i in heading:
		r[i] = []
	length = len(heading)
	line = 0
	for row in reader[1:]:
		d = row.split(":")
		location = d[0]
		if '~' in d[1]:
			time_start,time_end = d[1].split('~')
		else:
			time_start = time_end = d[1]
		data = map(float, d[2].split(','))
		col = 0
		for i in heading:
			r[i].append([time_start, time_end, data[col]])
			col+=1
	return r
