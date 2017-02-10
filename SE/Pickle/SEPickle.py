import SE.SEI as SEI
import pickle


class SEPickle(SEI.SEI):
    def __init__(self, model=None, path=None):
        self.model = model
        self.path = path

    def Serialize(self):
        with open(self.path, 'w+') as f:
            pickle.dump(self.model, f)

    def Deserialize(self):
        with open(self.path, 'rb') as f:
            return pickle.load(f)