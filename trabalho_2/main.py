#!/usr/bin/python3

import sys
from window import *

def printUsage():
	print('Usage:\n')
	print('\tO\t\t\tSwitch between 2D and 3D view')
	print('\tESC\t\t\tFinish program\n')

	print('On 3D view:\n')
	print('\tR\t\t\tReset camera position')
	print('\tMouse wheel or')
	print('\tUp/Down key\t\tExtrude polygon (mouse need to be over the polygon)')
	print('\tClick and move to rotate the camera')

def main(argv):

	glutInit(argv)
	glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)

	window = Window(800, 600)
	
	glutDisplayFunc(window.draw)
	glutIdleFunc(window.draw)
	glutReshapeFunc(window.resize)
	glutMouseFunc(window.mouseButton)
	glutMotionFunc(window.mouseDragged)
	glutKeyboardFunc(window.keyPressed)
	glutSpecialFunc(window.specialKeyPressed)

	printUsage()

	glutMainLoop()

if __name__ == '__main__':
	main(sys.argv)