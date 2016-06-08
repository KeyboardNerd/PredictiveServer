# ScLearning
This is learning application can be used to
1. DataBase: store data in SQLite, extract dataset, providing X-Plane format parser, PILOTS format writer, all data is stored with specific units defined in column information table.
2. Learning Model: Use Sci-kit to train the model by different technics. [TODO]
3. Visualization: Use Matplotlib to visualize the training result and the database. [TODO]

## Usage
### Database
to parse an X-Plane data file into SQLite database:
~~~python
parser = XPlaneFileParser("Database FileName", "Table Name", UnitConverter, "Configuration File")
parser.connect()
parser.parse("X-Plane File 1", "Delimiter")
parser.parse("X-Plane File 2", "Delimiter")
...
parser.close()
~~~
1. "Database FileName" is the sqlite databse you want to connect to, this will call sqlite3.connect("Database FileName").
2. [TO BE REVISED] "Table Name" is the table you want to parse the data into, this will affect the insertion query "INSERT INTO Table Name ..."
3. [TODO] UnitConverter is the unit converter component to be used for conversion.
4. [TODO] Configuration file is the configuration of database column information

to write data to PILOTS format:
~~~python
writer = PILOTSFileWriter("Database FileName","Table Name")
filenames = {"PILOTS FILE 1":["Column name 1",...], "PILOTS FILE 2":["Column name 1", "Column name 2",...],...}
rowRange = [100,200]
timeColumnName = "Timer"
baseTime = time.time()
writer.write(filenames, rowRange, timeColumnName, baseTime)
~~~
1. "Database FileName" is the sqlite databse you want to connect to, this will call sqlite3.connect("Database FileName").
2. [TO BE REVISED] "Table Name" is the table you want to output the data into, this will affect the selection query "SELECT ... FROM Table Name ..."
3. row range is the row numbers you want to store in the files
4. time column name specifies which column represents time (UNIX TIME)
5. base time specifies the starting time of the time column if it's not available (UNIX TIME)
6. File Names is the bunch of files and columns for each file you want to write to, e.g. "PILOTS FILE 1":["COLUMN NAME 1"] will write the column data with column name "COLUMN NAME 1" to PILOTS FILE. 
