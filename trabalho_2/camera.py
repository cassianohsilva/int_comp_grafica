from OpenGL.GL import glMatrixMode, glLoadIdentity, glMatrixMode, GL_PROJECTION, GL_MODELVIEW
from OpenGL.GLU import gluPerspective, gluLookAt

from vector import Vector

class PerspectiveCamera(object):

	# def __init__(self, position, direction, up, width, height):
	def __init__(self, position, direction, up, dimension):
		super(PerspectiveCamera, self).__init__()
		self.__position = Vector(*position)
		self.__direction = Vector(*direction)
		self.__up = Vector(*up)

		self.__dimension = dimension

		# Copy passed parameters
		self.__initialPosition = position
		self.__initialDirection = direction
		self.__initialUp = up

	def apply(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		gluPerspective(40.0, self.__dimension[0] / self.__dimension[1], 1.0, 10.0)

		gluLookAt(*self.__position, *(self.__position + self.__direction), *self.__up)

		glMatrixMode(GL_MODELVIEW)

	def reset(self):
		self.__position = Vector(*self.__initialPosition)
		self.__direction = Vector(*self.__initialDirection)
		self.__up = Vector(*self.__initialUp)

	@property
	def position(self):
		return self.__position

	@property
	def center(self):
		return (self.__position + self.__direction)

	@property
	def up(self):
		return self.__up

	def rotate(self, dx, dy):

		radius = self.__direction.magnitude

		left = self.__direction.cross(self.__up).normalized
		center = self.__position + self.__direction

		# New position and direction
		tempPosition = self.__position + (left * dx) + (self.__up * dy)
		tempDirection = radius * (center - tempPosition).normalized

		# Correct vectors
		left = tempDirection.cross(self.__up).normalized
		up = left.cross(tempDirection).normalized

		self.__direction = tempDirection

		self.__position = center - self.__direction

		self.__up = up
