import sclogger as sclogger
import sys
import json
import os
import inspect
import numpy as np
import sctransformer
import scestimator
from sclearndef import TrainDef
from sclogger import SCLOG
from scimporter import ScImporterCSV
import pandas as pd
import pandas

class LearningWrapper(object):
    """
    Initialized with an training definition and train the model based on the training definition
    """
    def __init__(self, traindef):
        self.traindef = traindef
        # load the existing modules from sctransformer and scalgo
        self.d_transformer = {}
        self.d_estimator = {}
        self.importer  = None
        self.preproc_x = []
        self.preproc_y = []
        self.pipeline = None
        # load implemented estimator and transformer
        for t in inspect.getmembers(sctransformer, predicate=LearningWrapper.transformer_predicate):
            self.d_transformer[t[0]] = t[1]
        for t in inspect.getmembers(scestimator, predicate=LearningWrapper.estimator_predicate):
            self.d_estimator[t[0]] = t[1]

    @staticmethod
    def transformer_predicate(value):
        return (inspect.isclass(value) and value.__module__ == 'sctransformer' and hasattr(value, 'fit') and hasattr(value, 'transform'))
    
    @staticmethod
    def estimator_predicate(value):
        return (inspect.isclass(value) and value.__module__ == 'scestimator' and hasattr(value, 'fit') and hasattr(value, 'predict'))
    
    @staticmethod
    def makedict(list1, list2):
        """
        make dictionary with items in list1 as keys and those in list2 as values
        """
        result = {}
        if len(list1) != len(list2):
            return {}
        for i in xrange(len(list1)):
            result[list1[i]] = list2[i]
        return result

    def train(self):
        """ use training definition to train the model"""
        
        print ("engineIO: Finished Training")

    def setup(self):
        # setup data importer
        ddef = self.traindef.datadef
        pdef = self.traindef.preprocessdef
        mdef = self.traindef.modeldef
        # setup importer
        if len(ddef.list_file) != 1:
            raise Exception("currently allows only one input data file")
        if ddef.str_type.lower() != 'csv':
            raise Exception("currently allows only csv")
        self.importer = ScImporterCSV(ddef.list_file[0])
        # setup preprocessor
        list_tuple_units = []
        # load schema definition TODO: integrate into sclearndef
        with (open(ddef.str_path_sch)) as f:
            json_dict = json.load(f)
            sch_names = json_dict["names"]
            sch_units = json_dict["units"]
        for i, name in sch_names:
            list_tuple_units.append((sch_units[i], pdef.step_preproc[name]))
        params = {"list_tuple_units": list_tuple_units}
        self.preproc_x.append()

# TODO: add complex model support
class StreamPipeline():
    def __init__(self, names, pipeline):
        self.mpname_idx = {}
        for i, n in enumerate(names):
            self.mpname_idx[n] = i
        self.pipeline = pipeline
        self.input_matrix = np.zeros((1, len(names)))

    def predict(self, **streamname_value):
        for name, value in self.mpname_idx.iteritems():
            self.input_matrix[0, value] = streamname_value[name]
        return self.pipeline.predict(self.input_matrix)

def main():
    """
    Read first argument as the training definition file
    train the model, save the output estimator
    """
    sclogger.init()
    sclogger.SCLOG.info("LearningEngine started\n")
    if len(sys.argv) != 2:
        sclogger.SCLOG.error("training definition path is not provided")
        return
    st_pathtraindef = os.path.join(sys.argv[1])
    learningengine = LearningEngine(st_pathtraindef)
    learningengine.train()

if __name__ == '__main__':
    main()
