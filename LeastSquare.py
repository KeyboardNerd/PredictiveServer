import LearningModel as lm
import numpy as np
import math
class LeastSquare(lm.SupervisedLearningModel):
	# X[:,0]: air speed, X[:,1]: pressure, X[:,2]: temperature, X[:,3]: angle of attack
	# Y: weight
	def _error(self,x,y,param):
		r = y - self._eval(x,param)
		se = np.dot(r.transpose(), r)
		rmse = math.sqrt(se/y.shape[0])
		return {'RMSE': rmse, 'SE': se}

	def _train(self,x,y):
		W = y[:,0]; T = x[:,2]; P = x[:,1]; V = x[:,0]; AOA = x[:,3]
		rho = P/1000/(0.2869*T)
		Cl_estimated = 2*W/rho/np.power(V,2)/61.0
		A = np.ones((AOA.shape[0],2))
		A[:,0] = AOA
		w = np.linalg.lstsq(A, Cl_estimated)[0]
		q, r = np.linalg.qr(A)
		b = np.dot(q.transpose(),Cl_estimated)
		weight = np.linalg.lstsq(r[:2,:2],b[:2])
		np.savetxt("y.csv",Cl_estimated,delimiter=",")
		np.savetxt("x.csv",A,delimiter=",")
		return weight[0]

	def _eval(self, x, param):
		T = x[:,2]; P = x[:,1]; V = x[:,0]; AOA = x[:,3]
		rho = P/1000/(0.2869*T)
		A = np.ones((AOA.shape[0],2))
		A[:,0] = AOA
		y = 0.5*np.dot(A,param)*rho*np.power(V,2)*61.0
		return np.asmatrix(y).transpose()

# special case of the linear transformation ( for this test... )
class SpecialLinearTransformation(lm.DataTransformer):
	def setWeight(self, weight):
		self.w = weight;
	def _YTrans(self, Y):
		r = np.array([Y[:,:].sum(axis=1) + self.w]).transpose()
		return r
	def _XTrans(self, X):
		# place holder
		x1 = np.divide(np.multiply(np.power(X[:,0],2), X[:,1]),X[:,2]);
		x2 = np.multiply(x1,X[:,3])
		x3 = np.multiply(x2, X[:,3])
		A = np.ones((X.shape[0],3))
		A[:,1] = x1
		A[:,2] = x2
		return A

class SpecialLinearTransformationP(lm.DataTransformer):
	def setWeight(self, weight):
		self.w = weight;
	def _YTrans(self, Y):
		r = np.array([Y[:,:].sum(axis=1) + self.w]).transpose()
		return r
	def _XTrans(self, X):
		return X[:,:]
