from OpenGL.GL import *
from OpenGL.GLU import *

from vector import Vector
from random import uniform

def randColor():
	# Not too black or too white
	return (uniform(0.1, 0.9), uniform(0.1, 0.9), uniform(0.1, 0.9))

def clamp(val, vmax, vmin=0):
	return max(vmin, min(val, vmax))

def signal(v):

	if v > 0:
		return 1
	elif v < 0:
		return -1
	else:
		return 0

# ############################################
# ############# Data structures ##############
# ############################################
class Node(object):

	def __init__(self, vertices, color=None, editableVertices=None):
		super(Node, self).__init__()

		self.__color = color if ( (color != None) and (len(color) == 3) ) else randColor()
		self.__vertices = [ (v[0], v[1], 0) for v in vertices ]
		self.__editableVertices = [ [v[0], v[1], Tree.BSP_MIN_DEPTH] for v in vertices ] if editableVertices == None else editableVertices
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

			newVertices = [ [], [] ]
			newEditableVertices = [ [], [] ]

			intersectionPoints = []

			for i in range(len(self.__vertices)):

				v1 = self.__vertices[i]
				v2 = self.__vertices[(i + 1) % len(self.__vertices)]

				ev1 = self.__editableVertices[i]
				ev2 = self.__editableVertices[(i + 1) % len(self.__vertices)]

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
						newVertices[0].append(v1)
						newEditableVertices[0].append(ev1)

					elif side > 0:
						newVertices[1].append(v1)
						newEditableVertices[1].append(ev1)

					else:
						newVertices[0].append(v1)
						newVertices[1].append(v1)

						newEditableVertices[0].append(ev1)
						# Duplicate the reference
						newEditableVertices[1].append(ev1[:])


					if (intersection != None) and (intersection != v1) and (intersection != v2):

						# Compute editable intersection from (x, y) of the base intersection
						er = ( ev2[0] - ev1[0], ev2[1] - ev1[1], ev2[2] - ev1[2] )
						t = 0

						if er[0] != 0:
							t = (intersection[0] - ev1[0]) / er[0]
						else:
							t = (intersection[1] - ev1[1]) / er[1]

						eiv = [intersection[0], intersection[1], ev1[2] + t * er[2]]

						newVertices[0].append(intersection)
						newVertices[1].append(intersection)

						newEditableVertices[0].append(eiv)
						# Duplicate the reference
						newEditableVertices[1].append(eiv[:])

						intersectionPoints.append(intersection)

					pass

				pass

			self.__left = Node(newVertices[0], self.__color, editableVertices=newEditableVertices[0])
			self.__right = Node(newVertices[1], editableVertices=newEditableVertices[1])

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


			self.__editableVertices[i][2] = max(self.__editableVertices[i][2] + de, Tree.BSP_MIN_DEPTH)


			# if self.__editableVertices[i][2] > -BSP_MIN_DEPTH:
			# 	self.__editableVertices[i][2] = -BSP_MIN_DEPTH

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

	BSP_MIN_DEPTH = 0.1

	def __init__(self, width, height):

		super(Tree, self).__init__()
		# self.__root = Node([(0, 0), (width, 0), (width, height), (0, height)], None)
		# self.__root = Node([(0, 0), (0, 1), (1, 1), (1, 0)], None)
		self.__root = Node([(0, 0), (0, 1), (1, 1), (1, 0)], None)
		self.__width = width
		self.__height = height

		self.fboSelection = glGenFramebuffers(1)
		self.texSelection = glGenTextures(1)
		self.depthSelection = glGenRenderbuffers(1)

	def draw(self, perspective=False):
		self.__root.draw(perspective)

	def recalculateBSP(self, p1, p2):
		self.__root.recalculateBSP(p1, p2)

	def checkCollison(self, p1, p2):
		return self.__root.checkCollison(p1, p2)

	def drawPicking(self):

		# global fboSelection, texSelection, depthSelection

		names = []

		glEnable(GL_TEXTURE_2D)

		# Attach buffers and texture
		glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fboSelection)
		glBindTexture(GL_TEXTURE_2D, self.texSelection)
		glBindRenderbuffer(GL_RENDERBUFFER, self.depthSelection)

		glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.__width, self.__height)
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depthSelection)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.__width, self.__height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
		glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texSelection, 0)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# self.__root.draw(perspective, selectMode=True, names=names)
		self.__root.draw(True, selectMode=True, names=names)

		glBindRenderbuffer(GL_RENDERBUFFER, 0)
		glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
		glBindTexture(GL_TEXTURE_2D, 0)
		glDisable(GL_TEXTURE_2D)

		return names
