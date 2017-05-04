"""
Sc Data Loader represents the interface to load data to Panda DataFrame using Data Loader definition
"""

class ScImporter(object):
    TYPE = None
    def __init__(self, filename, names=[], headerrow=None):
        self.filename = filename
        self.headerrow = None
        self.names = names
    def load(self):
        raise NotImplementedError()

# maybe it's not a good idea to do polymorphism
class ScImporterCSV(ScImporter):
    TYPE = "csv" # use decorator
    def load(self):
        with (open(self.filename)) as f:
            return pd.read_csv(f, self.names, self.headerrow).as_matrx()
