"""
Reads training definitions, run pipeline and generate the .estimator file
load_ prefix means change the inner states of the current object
stat_ prefix: static
step_ prefix: one step in transformation pipeline
"""

from scdecoder import ScDecoder
import types
class DataDef(ScDecoder):
    def _required(self):
        return [
            ("file", types.StringType),
            ("filetype", types.StringType),
            ("schema", types.DictionaryType),
            ("constants", types.DictionaryType)
        ]
    def _optional(self):
        return []

class PreprocessDef(ScDecoder):
    def _required(self):
        return [
            ("steps", type.ListType)
        ]
    def _optional(self):
        return []


class ModelDef(object):
    """
    Definition of Model field as major learning model in training pipeline
    """
    _stat_st_features = "features"
    _stat_st_labels = "labels"
    _stat_st_algo = "algorithm"
    def __init__(self, dict_def=None):
        self.step_model = None
        self.list_features = None
        self.list_labels = None
        if dict_def is not None:
            self.load_dict(dict_def)

    def load_dict(self, dict_def):
        """
        load dictionary into local fields.
        """
        self.step_model = dict_def.get(ModelDef._stat_st_algo)
        self.list_features = dict_def.get(ModelDef._stat_st_features)
        self.list_labels = dict_def.get(ModelDef._stat_st_labels)

    def st_pathalgo(self):
        """
        get path to the output estimator
        """
        return self.step_model.get('save_file')

class TrainDef(object):
    """
    Data structure containing training definition
    """
    _stat_st_data = "data"
    _stat_st_preproc = "preprocessing"
    _stat_st_model = "model"
    def __init__(self, dict_def=None):
        self.datadef = None
        self.preprocessdef = None
        self.modeldef = None
        if dict_def is not None:
            self.load_dict(dict_def)

    def load_dict(self, dict_def):
        """
        load diction into local fields
        """
        self.datadef = DataDef(dict_def.get(TrainDef._stat_st_data))
        self.preprocessdef = PreprocessDef(dict_def.get(TrainDef._stat_st_preproc))
        self.modeldef = ModelDef(dict_def.get(TrainDef._stat_st_model))
