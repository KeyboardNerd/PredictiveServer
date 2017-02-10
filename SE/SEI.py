'''
Serializer Interface
'''
from abc import ABCMeta, abstractmethod
class SEI(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def Serialize(self):
        pass

    @abstractmethod
    def Deserialize(self):
        pass