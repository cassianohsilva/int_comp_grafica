#!/usr/bin/python3

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from random import uniform
from numbers import Number
from math import sqrt, sin, cos

import traceback

# ############################################
# ############# Data structures ##############
# ############################################
class Node(object):

	def __init__(self, vertices, color=None, editableVertices=None):
		super(Node, self).__init__()

		self.__color = color if ( (color != None) and (len(color) == 3) ) else randColor()
		self.__vertices = [ (v[0], v[1], 0) for v in vertices ]
		self.__editableVertices = [ [v[0], v[1], BSP_DEPTH] for v in vertices ]
		self.__equation = None
		self.__intersectionPoints = None

		self.__left = None
		self.__right = None

	def hasChildren(self):
		return not ((self.__equation == None) or (self.__left == None) or (self.__right == None))

	"""
		Subdivide or merge node elements
	""" 
	def recalculateBSP(self, p1, p2, markedForMerge=False):

		# Same point?
		# Do nothing
		if p1 == p2:
			return

		# Not a leaf node?
		# Let's check for any collision or subdivision
		if self.hasChildren():
			signal1 = signal(self.__equation(p1[0], p1[1]))
			signal2 = signal(self.__equation(p2[0], p2[1]))

			# Points are not at the same side (collision)
			# or a collision was previously detected
			if (signal1 != signal2) or markedForMerge:

				child = self.__left if signal1 < 0 else self.__right

				# Not a leaf node?
				if child.hasChildren():
					child.recalculateBSP(p1, p2, True)

				# Merge the leaves children nodes
				else:

					if signal1 < 0:
						self.__color = self.__right.__color
					else:
						self.__color = self.__left.__color

					self.__equation = None
					self.__left = None
					self.__right = None
					self.__intersectionPoints = None

			# No collision or subdivision?
			# Try again
			else:

				if signal1 < 0:
					self.__left.recalculateBSP(p1, p2)

				else:
					self.__right.recalculateBSP(p1, p2)

				pass

		else:

			# Implicit equation coefficients
			a = p2[1] - p1[1]
			b = p1[0] - p2[0]
			c = (p2[0] * p1[1]) - (p1[0] * p2[1])

			self.__equation = lambda x, y : a*x + b*y + c

			new_vertices = [ [], [] ]
			intersectionPoints = []

			for i in range(len(self.__vertices)):

				v1 = self.__vertices[i]
				v2 = self.__vertices[(i + 1) % len(self.__vertices)]

				# Vector between first mouse point and first bound vertex
				pq = Vector(p1[0] - v1[0], p1[1] - v1[1])

				r = Vector(v2[0] - v1[0], v2[1] - v1[1])
				s = Vector(p2[0] - p1[0], p2[1] - p1[1])

				# If p1 and v1 are the same point
				if (p1[0] == v1[0]) and (p1[1] == v1[1]):
					pq = Vector(p2[0] - v1[0], p2[1] - v1[1])

				numerator1 = pq.x * s.y - pq.y * s.x
				numerator2 = pq.x * r.y - pq.y * r.x

				denominator = r.x * s.y - r.y * s.x

				intersection = None

				if (numerator1 != 0) or (numerator2 != 0):

					if denominator != 0:
						t = numerator1 / denominator
						u = numerator2 / denominator

						if (t >= 0) and (t <= 1):
							intersection = ( v1[0] + t*r.x, v1[1] + t*r.y )


					side = self.__equation(v1[0], v1[1])

					if side < 0:
						new_vertices[0].append(v1)

					elif side > 0:
						new_vertices[1].append(v1)

					else:
						new_vertices[0].append(v1)
						new_vertices[1].append(v1)


					if (intersection != None) and (intersection != v1) and (intersection != v2):
						new_vertices[0].append(intersection)
						new_vertices[1].append(intersection)

						intersectionPoints.append(intersection)

					pass

				pass

			self.__left = Node(new_vertices[0], self.__color)
			self.__right = Node(new_vertices[1])

			self.__intersectionPoints = intersectionPoints

			pass
		pass

	"""
		Check if the line segment between p1 and p2 collide with some edge
	"""
	def checkCollison(self, p1, p2, collision=False):

		if p1 == p2:
			return None

		if self.hasChildren():
			signal1 = signal(self.__equation(p1[0], p1[1]))
			signal2 = signal(self.__equation(p2[0], p2[1]))

			if (signal1 != signal2) or collision:

				child = self.__left if signal1 < 0 else self.__right

				if child.hasChildren():
					return child.checkCollison(p1, p2, True)

				else:
					return self.__intersectionPoints

			else:

				if signal1 < 0:
					return self.__left.checkCollison(p1, p2)

				else:
					return self.__right.checkCollison(p1, p2)

				pass

		else:
			return None

	def extrude(self, de):

		# print("before", self.__editableVertices)

		for i in range(len(self.__editableVertices)):

			self.__editableVertices[i][2] = max(self.__editableVertices[i][2] + de, BSP_DEPTH)

			# if self.__editableVertices[i][2] > -BSP_DEPTH:
			# 	self.__editableVertices[i][2] = -BSP_DEPTH

		# print("after", self.__editableVertices)

	def __draw3D(self, selectMode, names):
		# glEnable(GL_LIGHTING)
		# glEnable(GL_COLOR_MATERIAL)
		# glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

		glEnable(GL_DEPTH_TEST)

		if selectMode:

			names.append(self)

			l = len(names)

			r = l // 65025
			g = (l % 65025) // 255
			b = l % 255

			glColor3ub(r, g, b)

		else:
			glColor(self.__color[0], self.__color[1], self.__color[2])

		# Borders
		glBegin(GL_QUAD_STRIP)

		for v in range(len(self.__vertices) + 1):

			i = (v + 1) % len(self.__vertices)

			glVertex(self.__vertices[i][0], self.__vertices[i][1], self.__vertices[i][2])
			glVertex(self.__editableVertices[i][0], self.__editableVertices[i][1], self.__editableVertices[i][2])
			# glVertex(self.__vertices[nextI][0], self.__vertices[nextI][1], self.__vertices[nextI][2])
			# glVertex(self.__editableVertices[nextI][0], self.__editableVertices[nextI][1], self.__editableVertices[nextI][2])

		glEnd()

		# glDisable(GL_LIGHTING)

		# Front and back face
		# Back face has inversed vertices orientations
		for p in (self.__vertices, self.__editableVertices[::-1]):

			glBegin(GL_POLYGON)

			for v in p:
				glVertex(v[0], v[1], v[2])

			glEnd()

		glDisable(GL_DEPTH_TEST)

	def draw(self, perspective, selectMode=False, names=[]):

		if self.__left != None:
			self.__left.draw(perspective, selectMode, names)

		if self.__right != None:
			self.__right.draw(perspective, selectMode, names)

		if (self.__left == None) and (self.__right == None):

			if perspective or selectMode:

				self.__draw3D(selectMode, names)

			else:

				glDisable(GL_LIGHTING)

				# Draw polygon
				glColor(self.__color[0], self.__color[1], self.__color[2])
				glBegin(GL_POLYGON)

				for p in self.__vertices:
					glVertex(p[0], p[1], p[2])
				glEnd()

				# Draw border
				glColor(0, 0, 0)
				glBegin(GL_LINE_LOOP)

				for p in self.__vertices:
					glVertex(p[0], p[1], p[2])
				glEnd()

class Tree(object):

	def __init__(self):
		super(Tree, self).__init__()
		# self.__root = Node([(0, 0), (width, 0), (width, height), (0, height)], None)
		# self.__root = Node([(0, 0), (0, 1), (1, 1), (1, 0)], None)
		self.__root = Node([(0, 0), (0, 1), (1, 1), (1, 0)], None)

	def draw(self, perspective=False):
		self.__root.draw(perspective)

	def recalculateBSP(self, p1, p2):
		self.__root.recalculateBSP(p1, p2)

	def checkCollison(self, p1, p2):
		return self.__root.checkCollison(p1, p2)

	def drawPicking(self):

		global fboSelection, texSelection

		names = []

		glEnable(GL_TEXTURE_2D)

		glBindFramebuffer(GL_FRAMEBUFFER, fboSelection)
		glBindTexture(GL_TEXTURE_2D, texSelection)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texSelection, 0)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		self.__root.draw(perspective, selectMode=True, names=names)

		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		glBindTexture(GL_TEXTURE_2D, 0)
		glDisable(GL_TEXTURE_2D)

		return names

# ############################################
# ############# Utiliry classes ##############
# ############################################

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

class PerspectiveCamera(object):

	def __init__(self, position, direction, up):
		super(PerspectiveCamera, self).__init__()
		self.__position = Vector(*position)
		self.__direction = Vector(*direction)
		self.__up = Vector(*up)

		# Copy passed parameters
		self.__initialPosition = position
		self.__initialDirection = direction
		self.__initialUp = up

	def apply(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		gluPerspective(40.0, WIDTH / HEIGHT, 1.0, 10.0)

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

	def move(self, dx, dy):

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

# ############################################
# ############ Utility functions #############
# ############################################

def clamp(val, vmax, vmin=0):
	return max(vmin, min(val, vmax))

def randColor():
	# Not too black or too white
	return (uniform(0.1, 0.9), uniform(0.1, 0.9), uniform(0.1, 0.9))

def signal(v):

	if v > 0:
		return 1
	elif v < 0:
		return -1
	else:
		return 0

def convertWindowToOpenGL(point):

	global WIDTH, HEIGHT

	return (float(point[0]) / WIDTH, 1.0 - (float(point[1]) / HEIGHT))

def convertOpenGLToWindow(point):

	global WIDTH, HEIGHT

	return (point[0] * WIDTH, (1 - point[1]) * HEIGHT)

def applyCurrentMatrix():

	if perspective:
		# return perspectiveMatrix
		camera.apply()
	else:
		glLoadMatrixd(orthoMatrix)
		# return orthoMatrix

def pickElements(point):

	global fboSelection

	names = tree.drawPicking()
	
	glBindFramebuffer(GL_READ_FRAMEBUFFER, fboSelection)
	glReadBuffer(GL_COLOR_ATTACHMENT0)

	pixels = glReadPixels(point[0], HEIGHT - point[1], 1, 1, GL_RGB, GL_UNSIGNED_BYTE)

	glReadBuffer(GL_NONE)
	glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)

	# R + G + B
	index = (pixels[0] * 65025) + (pixels[1] * 255) + (pixels[2] - 1)

	return names[index] if index >= 0 else None

# ############################################
# ############ Global variables ##############
# ############################################

WIDTH, HEIGHT = 800, 600
BSP_DEPTH = 0.1

tree = Tree()

startPoint = None
endPoint = None

collisionEdge = None

window = None

orthoMatrix = None
perspectiveMatrix = None

perspective = False

camera = None

fboSelection = None
texSelection = None

# ############################################
# ############ OpenGL callbacks ##############
# ############################################

def mousePressedOrReleased(button, state, x, y):

	global startPoint, endPoint, collisionEdge

	if button == GLUT_LEFT_BUTTON:

		if state == GLUT_DOWN:
			startPoint = (clamp(x, WIDTH), clamp(y, HEIGHT))

		else:

			if not perspective and (endPoint != None) and (startPoint != endPoint):
				tree.recalculateBSP(convertWindowToOpenGL(startPoint), convertWindowToOpenGL(endPoint))

			startPoint = None
			endPoint = None
			collisionEdge = None

def mouseDragged(x, y):

	global startPoint, endPoint, collisionEdge

	if startPoint != None:
		endPoint = (clamp(x, WIDTH), clamp(y, HEIGHT))

		# collisionEdge = tree.checkCollison(convertWindowToOpenGL(startPoint), convertWindowToOpenGL(endPoint))
	# print(convertWindowToOpenGL((x, y)))
	# glutWarpPointer(0, 0)

def specialKeyPressed(key, x, y):

	global perspective

	if perspective:

		if (key == GLUT_KEY_UP) or (key == GLUT_KEY_DOWN):
			el = pickElements((x, y))

			if el != None:

				if key == GLUT_KEY_UP:
					el.extrude(0.025)
				else:
					el.extrude(-0.025)

def keyPressed(key, x, y):

	global perspective

	if key == b'o':
		perspective = not perspective

	elif key == b'd':
		camera.move(0.05, 0)

	elif key == b'a':
		camera.move(-0.05, 0)

	elif key == b'w':
		camera.move(0, 0.05)

	elif key == b's':
		camera.move(0, -0.05)

	elif key == b'r':
		if perspective:
			camera.reset()

	# ESC key
	elif key == b'\x1b':
		glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
		glutLeaveMainLoop()

def draw():

	# global perspectiveMatrix, orthoMatrix, startPoint, endPoint, tree
	# print(perspectiveMatrix)
	global perspective

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

	# glLoadMatrixd(getCurrentMatrix())
	applyCurrentMatrix()

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	tree.draw(perspective)

	if not perspective:
		if (startPoint != None) and (endPoint != None):

			glColor(0, 0, 0)

			glBegin(GL_LINE_STRIP)

			glVertex(*convertWindowToOpenGL(startPoint))
			glVertex(*convertWindowToOpenGL(endPoint))

			glEnd()

	else:
		# 3D view
		pass

	glutSwapBuffers()

def setup():

	global window, perspectiveMatrix, orthoMatrix, camera, fboSelection, texSelection

	glutInit()
	glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(WIDTH + 1, HEIGHT + 1)
	# glutInitWindowPosition(0, 0)
	window = glutCreateWindow("Trabalho 2")

	# gluLookAt(
	# 		0.0, 0.0, -1.0,
	# 		0.5, 0.5, 0.0,
	# 		0.0, 1.0, 0.0)

	camera = PerspectiveCamera(
		(0.5, 0.5, 2.5),
		# (0.5, 0.5, 0.0),
		(0.0, 0.0, -2.5),
		(0.0, 1.0, 0.0))

	glMatrixMode(GL_PROJECTION)

	# Save first perspective matrix
	# glLoadIdentity()
	# gluPerspective(40.0, WIDTH / HEIGHT, 1.0, 10.0)
	# perspectiveMatrix = glGetDouble(GL_PROJECTION_MATRIX)

	# Save first ortho matrix
	glLoadIdentity()
	glOrtho(0.0, 1.0, 0.0, 1.0, -0.5, 0.5)
	orthoMatrix = glGetDouble(GL_PROJECTION_MATRIX)

	glMatrixMode(GL_MODELVIEW)

	# #####################################################################

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)

	glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
	glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
	glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
	glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, -4.0, 1.0])

	glDisable(GL_LIGHTING)

	fboSelection = glGenFramebuffers(1)
	texSelection = glGenTextures(1)

	# #####################################################################

	# glGetDouble(GL_PROJECTION_MATRIX, perspectiveMatrix)
	# glLoadMatrix(perspectiveMatrix)

	# print(perspectiveMatrix, orthoMatrix)

	glLineWidth(2)

def main():
	
	setup()
	
	glutDisplayFunc(draw)
	glutIdleFunc(draw)
	glutMouseFunc(mousePressedOrReleased)
	glutMotionFunc(mouseDragged)
	glutKeyboardFunc(keyPressed)
	glutSpecialFunc(specialKeyPressed)
	glutMainLoop()


if __name__ == '__main__':
	main()