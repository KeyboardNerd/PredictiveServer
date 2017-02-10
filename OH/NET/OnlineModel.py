import numpy as np


class OnlineModel(object):
	""" OnlineModel is a class specifically designed for ServerInterface, it may be changed later on"""
	def __init__(self, model, translation={}):
		self.model = model
		self.translation = translation

	def predictSingleValue(self, feature_dict):
		# translate the feature dict
		self.translate(feature_dict)
		feature_dict.update(self.model.constants) # inject environment to the dictionary
		mx = map(lambda(feature): eval(feature.format(**feature_dict)), self.model.features)
		return self.model.predict(np.asmatrix(mx))

	def translate(self, feature_dict):
		for i in feature_dict:
			if i in self.translation:
				feature_dict[self.translation[i]] = feature_dict[i]
				del feature_dict[i]
	def save(self,filename):
		self.model.save(filename)