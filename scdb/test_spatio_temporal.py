import temporal as t
import sqlite3
import datetime
t.dbController = sqlite3
t.connect("a.db")
t.close()
t.connect("a.db")
t.insert_object("name","information")
t.insert_field("height", "meter")
current_time = str(datetime.datetime.now())
t.insert_data(None, None, "name", "height", 1.1)
t.commit()
print t.query_object("name")
print t.query_data(None,u'2016-06-15 21:43:30.197295',"name","height")
print t.query_field("height")
t.close()
