class A():
	count = 0
	@staticmethod
	def test(X):
		A.count += 1
		return X.split(',')

map(A.test, ["a,b",'b,c'])
print A.count