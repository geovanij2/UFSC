import json


class bob(object):
	"""docstring for bob"""
	def __init__(self, arg):
		super(bob, self).__init__()
		self.arg = arg

	def hello(self):
		print('hello', self.arg)

bo = bob('bob')

q = json.dumps(bo.__dict__)
print(q)
del bo

t = json.loads(q)
print(t)
t['arg']

a = { 't': [1,2,3] }
b = json.dumps(a)

print(b)

a = [1,2,3]
b = ['A', 'B', 'C']
print(a.__dict__)