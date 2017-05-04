"""
Strong typed decoder, useful for importing configuration files
"""
import types
class ScDecoder(object):
    def __init__(self, obj_dict):
        self._decode(obj_dict)

    def _required(self):
        raise NotImplementedError()

    def _optional(self):
        raise NotImplementedError()

    def _decode(self, obj_dict):
        obj_dict = obj_dict.copy()
        for fieldtype in self._required():
            if (fieldtype[0] not in obj_dict ):
                raise Exception("Required Field is missing: " + fieldtype[0])
            if (type(obj_dict[fieldtype[0]]) is not fieldtype[1]):
                raise Exception("Required Field's type mismatched: expected %s, get %s"%(str(fieldtype[1]), str(type(obj_dict[fieldtype[0]]))))
        for field in self._optional():
            if (field not in obj_dict):
                obj_dict[field] = None
        self.__dict__.update(obj_dict)