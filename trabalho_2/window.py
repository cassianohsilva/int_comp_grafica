from OpenGL.GLUT import *

from tree import *
from camera import PerspectiveCamera

class Window(object):
	"""docstring for Window"""
	def __init__(self, width, height):
		super(Window, self).__init__()

		# Pass dimensions by reference
		self.__dimension = [width, height]

		self.__GLInit()

		self.__camera = PerspectiveCamera(
					(0.5, 0.5, 2.5),
					# (0.5, 0.5, 0.0),
					(0.0, 0.0, -2.5),
					(0.0, 1.0, 0.0),
					self.__dimension)

		self.__tree = Tree(self.__dimension)

		self.__startPoint = None
		self.__endPoint = None

		self.__perspective = False

		self.__selectedObject = None

		self.__collisionEdge = None

	def convertWindowToOpenGL(self, point):

		return (float(point[0]) / self.__dimension[0], 1.0 - (float(point[1]) / self.__dimension[1]))

	def convertOpenGLToWindow(self, point):

		return (point[0] * self.__dimension[0], (1 - point[1]) * self.__dimension[1])

	def applyCurrentMatrix(self):

		if self.__perspective:
			self.__camera.apply()
			
		else:
			glViewport(0, 0, self.__dimension[0] + 1, self.__dimension[1] + 1)
			glOrtho(0.0, 1.0, 0.0, 1.0, -0.5, 0.5)

	def __GLInit(self):

		glutInitWindowSize(self.__dimension[0] + 1, self.__dimension[1] + 1)
		self.__id = glutCreateWindow("Trabalho 2")

		glMatrixMode(GL_PROJECTION)

		# Save ortho matrix
		glLoadIdentity()
		glOrtho(0.0, 1.0, 0.0, 1.0, -0.5, 0.5)

		glMatrixMode(GL_MODELVIEW)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
		glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
		glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
		glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, -4.0, 1.0])

		glDisable(GL_LIGHTING)

		glLineWidth(2)

	def specialKeyPressed(self, key, x, y):
		pass

	def resize(self, w, h):
		self.__dimension[0] = w - 1
		self.__dimension[1] = h - 1

	def keyPressed(self, key, x, y):

		key = key.decode().lower()

		if key == 'o':
			self.__perspective = not self.__perspective

		elif key == 'r':
			if self.__perspective:
				self.__camera.reset()

		# ESC key
		elif key == '\x1b':
			glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
			glutLeaveMainLoop()

	def pickElements(self, point):

		names = self.__tree.drawPicking()
		
		glBindFramebuffer(GL_READ_FRAMEBUFFER, self.__tree.fbo)
		glReadBuffer(GL_COLOR_ATTACHMENT0)

		pixels = glReadPixels(point[0], self.__dimension[1] - point[1], 1, 1, GL_RGB, GL_UNSIGNED_BYTE)

		glReadBuffer(GL_NONE)
		glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)

		# R + G + B
		index = (pixels[0] * 65025) + (pixels[1] * 255) + (pixels[2] - 1)

		return names[index] if (index >= 0 and index < len(names)) else None

	def draw(self):

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		self.applyCurrentMatrix()

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self.__tree.draw(self.__perspective)

		if not self.__perspective:
			if (self.__startPoint != None) and (self.__endPoint != None):

				glColor(0, 0, 0)

				glBegin(GL_LINE_STRIP)

				glVertex(*self.convertWindowToOpenGL(self.__startPoint))
				glVertex(*self.convertWindowToOpenGL(self.__endPoint))

				glEnd()

		else:
			# 3D view
			pass

		glutSwapBuffers()

	def mouseDragged(self, x, y):

		if self.__startPoint != None:

			factor = 7.5

			if self.__perspective:
				if not self.__selectedObject:
					self.__camera.rotate(
								(self.__endPoint[0] - clamp(x, self.__dimension[0])) * factor / self.__dimension[0],
								(clamp(y, self.__dimension[1]) - self.__endPoint[1]) * factor / self.__dimension[1])
				else:
					dz = tuple(map(float.__sub__, gluUnProject(self.__endPoint[0], self.__endPoint[1], 0.0), gluUnProject(x, y, 0.0) ))[2]

					# TODO Check this constant
					self.__selectedObject.extrude(dz * 2)

			self.__endPoint[0], self.__endPoint[1] = clamp(x, self.__dimension[0]), clamp(y, self.__dimension[1])

	def mousePressedOrReleased(self, button, state, x, y):

		if button == GLUT_LEFT_BUTTON:

			if state == GLUT_DOWN:
				self.__startPoint = [clamp(x, self.__dimension[0]), clamp(y, self.__dimension[1])]
				self.__endPoint = [clamp(x, self.__dimension[0]), clamp(y, self.__dimension[1])]

				if self.__perspective:
					self.__selectedObject = self.pickElements((x, y))

			else:

				if not self.__perspective and (self.__endPoint != None) and (self.__startPoint != self.__endPoint):
					self.__tree.recalculateBSP(self.convertWindowToOpenGL(self.__startPoint), self.convertWindowToOpenGL(self.__endPoint))

				self.__startPoint = None
				self.__endPoint = None
				self.__collisionEdge = None
				self.__selectedObject = None
