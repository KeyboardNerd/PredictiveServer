import parser
import writer
import temporal as t
import sqlite3
t.dbController = sqlite3
t.connect("a.db")
t.init()
#parser.units = {"speed":"knot","pressure":"pascal"}
#parser.parse("speed.txt", t, "The ATR Family", parser.pilots_parse)
#writer.output_rule = None
#writer.write(t, "The ATR Family", {"speed":[None,None], "pressure":[None,None]}, writer.pilots_write)
t.commit()
t.close()
