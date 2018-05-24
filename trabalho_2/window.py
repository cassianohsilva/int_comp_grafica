from OpenGL.GLUT import *

from utils import signal
from tree import *
from camera import PerspectiveCamera

class Window(object):

	def __init__(self, width, height):
		super(Window, self).__init__()

		# Pass dimensions by reference
		self.__dimension = [width, height]

		self.__GLInit()

		self.__camera = PerspectiveCamera(
					(0.5, 0.5, 2.5),
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


	def extrude(self, x, y, direction):

		if self.__perspective:

			self.__selectedObject = self.pickElements((x, y))

			if self.__selectedObject:
				self.__selectedObject.extrude(0.025 * signal(direction))


	def specialKeyPressed(self, key, x, y):
		if key == GLUT_KEY_UP:
			self.extrude(x, y, 1)
		elif key == GLUT_KEY_DOWN:
			self.extrude(x, y, -1)


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

				glBegin(GL_LINES)

				glVertex(*self.convertWindowToOpenGL(self.__startPoint))
				glVertex(*self.convertWindowToOpenGL(self.__endPoint))

				if self.__collisionEdge != None:

					glColor(1.0, 1.0, 1.0)

					glVertex(*self.__collisionEdge[0])
					glVertex(*self.__collisionEdge[1])

				glEnd()

		glutSwapBuffers()


	def mouseDragged(self, x, y):

		if self.__startPoint != None:

			factor = 7.5

			if self.__perspective:

				self.__camera.rotate(
							(self.__endPoint[0] - clamp(x, self.__dimension[0])) * factor / self.__dimension[0],
							(clamp(y, self.__dimension[1]) - self.__endPoint[1]) * factor / self.__dimension[1])

			elif self.__collisionEdge == None:

				self.__collisionEdge = self.__tree.checkCollison(
										self.convertWindowToOpenGL(self.__startPoint),
										self.convertWindowToOpenGL(self.__endPoint))

			self.__endPoint[0], self.__endPoint[1] = clamp(x, self.__dimension[0]), clamp(y, self.__dimension[1])


	def mouseButton(self, button, state, x, y):

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

		# Mouse wheel
		elif (button == 3) or (button == 4):

			self.extrude(x, y, -button + 3.5)