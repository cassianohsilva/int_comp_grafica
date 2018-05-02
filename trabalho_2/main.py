#!/usr/bin/python3

from OpenGL.GLUT import *

from tree import *
from camera import PerspectiveCamera

# import traceback

# ############################################
# ############ Utility functions #############
# ############################################

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

	# global fboSelection

	names = tree.drawPicking()
	
	# glBindFramebuffer(GL_READ_FRAMEBUFFER, fboSelection)
	glBindFramebuffer(GL_READ_FRAMEBUFFER, tree.fboSelection)
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

tree = None

startPoint = None
endPoint = None

collisionEdge = None

window = None

orthoMatrix = None
perspectiveMatrix = None

perspective = False

camera = None

extrusionObject = None

# ############################################
# ############ OpenGL callbacks ##############
# ############################################

def mousePressedOrReleased(button, state, x, y):

	global startPoint, endPoint, collisionEdge, extrusionObject

	if button == GLUT_LEFT_BUTTON:

		if state == GLUT_DOWN:
			startPoint = [clamp(x, WIDTH), clamp(y, HEIGHT)]
			endPoint = [clamp(x, WIDTH), clamp(y, HEIGHT)]

			if perspective:
				extrusionObject = pickElements((x, y))

		else:

			if not perspective and (endPoint != None) and (startPoint != endPoint):
				tree.recalculateBSP(convertWindowToOpenGL(startPoint), convertWindowToOpenGL(endPoint))

			startPoint = None
			endPoint = None
			collisionEdge = None
			extrusionObject = None

def mouseDragged(x, y):

	global startPoint, endPoint, collisionEdge

	if startPoint != None:

		factor = 7.5

		if perspective:
			if not extrusionObject:
				camera.rotate( (endPoint[0] - clamp(x, WIDTH)) * factor / WIDTH, (clamp(y, HEIGHT) - endPoint[1]) * factor / HEIGHT)
			else:
				dz = tuple(map(float.__sub__, gluUnProject(endPoint[0], endPoint[1], 0.0), gluUnProject(x, y, 0.0) ))[2]

				# TODO Check this constant
				extrusionObject.extrude(dz * 2)

		endPoint[0], endPoint[1] = clamp(x, WIDTH), clamp(y, HEIGHT)

	# glutWarpPointer(0, 0)

def specialKeyPressed(key, x, y):

	# global perspective

	# if perspective:

	# 	if (key == GLUT_KEY_UP) or (key == GLUT_KEY_DOWN):
	# 		el = pickElements((x, y))

	# 		if el != None:

	# 			if key == GLUT_KEY_UP:
	# 				el.extrude(0.025)
	# 			else:
	# 				el.extrude(-0.025)
	pass

def keyPressed(key, x, y):

	global perspective

	key = key.decode().lower()

	if key == 'o':
		perspective = not perspective

	elif key == 'r':
		if perspective:
			camera.reset()

	# ESC key
	elif key == '\x1b':
		glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
		glutLeaveMainLoop()

def draw():

	global perspective

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

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

	global window, perspectiveMatrix, orthoMatrix, camera

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
		(0.0, 1.0, 0.0),
		WIDTH, HEIGHT)

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

	# #####################################################################

	# glGetDouble(GL_PROJECTION_MATRIX, perspectiveMatrix)
	# glLoadMatrix(perspectiveMatrix)

	# print(perspectiveMatrix, orthoMatrix)

	glLineWidth(2)

def main():

	global tree
	
	setup()

	tree = Tree(WIDTH, HEIGHT)
	
	glutDisplayFunc(draw)
	glutIdleFunc(draw)
	glutMouseFunc(mousePressedOrReleased)
	glutMotionFunc(mouseDragged)
	glutKeyboardFunc(keyPressed)
	glutSpecialFunc(specialKeyPressed)
	glutMainLoop()


if __name__ == '__main__':
	main()