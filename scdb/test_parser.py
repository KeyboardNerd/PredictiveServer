import parser
import temporal as t
import sqlite3
t.dbController = sqlite3
t.connect("a.db")
parser.units = {"speed":"knot","pressure":"pascal"}
parser.parse("speed.txt", t, "The ATR Family", parser.pilots_parse)
t.commit()
t.close()
