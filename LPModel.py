import LearningModel as lm
import numpy as np
import math
import scipy.optimize as opt
class LPModel(lm.SupervisedLearningModel):
	def _error(self,x,y,param):
		r = y - np.dot(x,param)
		se = np.dot(r.transpose(), r)
		rmse = math.sqrt(se/x.shape[0])
		return {'RMSE': rmse, 'SE': se}
	def _train(self,x,y):
		# iterative method
		z0 = np.array([0,1,1])
		func = lambda z: np.array((y.transpose() - np.dot(x,z)).tolist()[0]);
		res = opt.least_squares(func, z0, loss='cauchy')
		return np.matrix(res.x).transpose()
	def _eval(self, x, param):
		return np.dot(x, param)

# special case of the linear transformation ( for this test... )
class LPModelTransformation(lm.DataTransformer):
	def setWeight(self, weight):
		self.w = weight;
	def _YTrans(self, Y):
		r = np.array([Y[:,:].sum(axis=1) + self.w]).transpose()
		return r
	def _XTrans(self, X):
		x1 = np.divide(np.multiply(np.power(X[:,0],2), X[:,1]),X[:,2]);
		x2 = np.multiply(x1,X[:,3])
		A = np.ones((X.shape[0],3))
		A[:,1] = x1
		A[:,2] = x2
		return A
