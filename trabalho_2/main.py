#!/usr/bin/python3

import sys
from window import *

# import traceback

def main(argv):

	glutInit(argv)
	glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)

	window = Window(800, 600)
	
	glutDisplayFunc(window.draw)
	glutIdleFunc(window.draw)
	glutReshapeFunc(window.resize)
	glutMouseFunc(window.mousePressedOrReleased)
	glutMotionFunc(window.mouseDragged)
	# glutKeyboardFunc(keyPressed)
	glutKeyboardFunc(window.keyPressed)
	glutSpecialFunc(window.specialKeyPressed)
	# glutMainLoop()

	glutMainLoop()

if __name__ == '__main__':
	main(sys.argv)