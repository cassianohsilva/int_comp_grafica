from numbers import Number
from math import sqrt, sin, cos

class Vector(object):
	"""docstring for Vector"""
	def __init__(self, x=0, y=0, z=0):
		super(Vector, self).__init__()
		self.x, self.y, self.z = x, y, z

	def __mul__(self, val):

		if isinstance(val, Vector):
			return Vector(self.x * val.x, self.y * val.y, self.z * val.z)
		elif isinstance(val, Number):
			return Vector(self.x * val, self.y * val, self.z * val)
		else:
			raise TypeError('Invalid operator types')

	def __neg__(self):
		return Vector(-self.x, -self.y, -self.z)

	def __imul__(self, val):

		if isinstance(val, Vector):
			self.x *= val.x
			self.y *= val.y
			self.z *= val.z

			return self

		elif isinstance(val, Number):
			self.x *= val
			self.y *= val
			self.z *= val

			return self

		else:
			raise TypeError('Invalid operator types')

	def __rmul__(self, val):

		if isinstance(val, Vector):
			return self
		elif isinstance(val, Number):
			return Vector(self.x * val, self.y * val, self.z * val)
		else:
			raise TypeError('Invalid operator types')

	def __add__(self, val):

		if isinstance(val, Vector):
			return Vector(self.x + val.x, self.y + val.y, self.z + val.z)
		else:
			raise TypeError('Invalid operator types')

	def __iadd__(self, val):

		if isinstance(val, Vector):
			self.x += val.x
			self.y += val.y
			self.z += val.z

			return self

		else:
			raise TypeError('Invalid operator types')

	def __sub__(self, val):

		if isinstance(val, Vector):
			return Vector(self.x - val.x, self.y - val.y, self.z - val.z)
		else:
			raise TypeError('Invalid operator types')

	def __isub__(self, val):

		if isinstance(val, Vector):
			self.x -= val.x
			self.y -= val.y
			self.z -= val.z

			return self

		else:
			raise TypeError('Invalid operator types')

	def __len__(self):
		return 3

	def cross(self, val):

		if isinstance(val, Vector):
			return Vector(
				(self.y * val.z) - (self.z * val.y),
				(self.z * val.x) - (self.x * val.z),
				(self.x * val.y) - (self.y * val.x))
		else:
			raise TypeError('Invalid operator types')

	@property
	def magnitude(self):
		return sqrt(pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2))

	@property
	def normalized(self):

		m = self.magnitude

		return Vector(self.x / m, self.y / m, self.z / m)

	def __repr__(self):
		return str((self.x, self.y, self.z))

	def __getitem__(self, key):

		if (key >= 0) and (key < 3):
			return (self.x, self.y, self.z)[key]
		else:
			raise IndexError()
