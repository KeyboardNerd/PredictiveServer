import csv

def XPlaneFileParser(fileName, delimiter):
    reader = csv.reader(filter(lambda(x): bool(x.strip()), open(fileName,"rU").readlines()), delimiter=delimiter)
    heading = next(reader)
    data = []
    length = -1
    for row in reader:
        result = map(float, map(str.strip, row[:-1]))
        if length == -1:
            length = len(result)
        elif length != len(result):
            raise Exception("data is not filled")
        data.append(result)
    return (heading, data, length)

def csvFileParser(fileName, delimiter):
    reader = csv.reader(filter(lambda(x): bool(x.strip()), open(fileName, "rU").readlines()))
    heading = next(reader)
    data = []
    length = -1
    for row in reader:
        result = map(float, map(str.strip, row))
        if length == -1:
            length = len(result)
        elif length != len(result):
            raise Exception("data is not filled")
        data.append(result)
    return (heading, data, length)

def PILOTSFileParser(fileName, delimiter):
    # example file parser without considering time
    reader = filter(lambda(x): bool(x.strip()), open(fileName,"rU").readlines())
    headline = reader[0]
    if headline[0] != '#':
        raise Exception("Not a valid PILOTS file")
    heading = headline[1:].split(',')
    data = []
    length = len(heading)
    for row in reader[1:]:
        d = row.split(":")
        location = d[0]
        time = d[1]
        other = map(float, d[2].split(','))        
        if len(other) != length:
            raise Exception("data is not filled, aborted")
        data.append(other)
    return (heading, data, length)