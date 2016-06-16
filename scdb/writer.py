output_rule = None
# write the data of object with object_name from database to file or files
def write(database, object_name, attributes_and_time_range, method):
	if not database.query_object(object_name):
		return False
	data = {}
	for field in attributes_and_time_range:
		data[field] = database.query_data(attributes_and_time_range[field][0],attributes_and_time_range[field][1],object_name, field)
	method(data)

def pilots_write(data):
	global output_rule # 1. put data to one file if homogenerous 2. force put data to one file even if it's 
	if output_rule == None:
		for field in data:
			current_file = open(field, 'w+')
			current_file.write('#'+field+'\n')
			for line in data[field]:
				times = line[0]
				timee = line[1]
				value = line[2]
				if times != timee:
					current_line = ':'+times+'~'+timee+':'+repr(value)
				else:
					current_line = ':'+times+':'+repr(value)
				current_file.write(current_line+'\n')
			current_file.flush()
			current_file.close()
