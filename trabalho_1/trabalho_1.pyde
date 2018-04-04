from random import randint

# ############################################
# ############# Data structures ##############
# ############################################
class Node(object):
  
  def __init__(self, vertices, color=None):
    super(Node, self).__init__()

    self.__color = color if ( (color != None) and (len(color) == 3) ) else randColor()
    self.__vertices = vertices
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
        pq = PVector(p1[0] - v1[0], p1[1] - v1[1])

        r = PVector(v2[0] - v1[0], v2[1] - v1[1])
        s = PVector(p2[0] - p1[0], p2[1] - p1[1])

        # If p1 and v1 are the same point
        if (p1[0] == v1[0]) and (p1[1] == v1[1]):
          pq = PVector(p2[0] - v1[0], p2[1] - v1[1])

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

  def draw(self):
    
    if self.__left != None:
      self.__left.draw()

    if self.__right != None:
      self.__right.draw()

    if (self.__left == None) and (self.__right == None):

      beginShape()
      fill(self.__color[0], self.__color[1], self.__color[2])

      for p in self.__vertices:
        vertex(p[0], p[1])

      endShape(CLOSE)

class Tree(object):
  
  def __init__(self, width, height):
    super(Tree, self).__init__()
    self.__root = Node([(0, 0), (width, 0), (width, height), (0, height)], None)

  def draw(self):
    self.__root.draw()

  def recalculateBSP(self, p1, p2):
    self.__root.recalculateBSP(p1, p2)

  def checkCollison(self, p1, p2):
    return self.__root.checkCollison(p1, p2)

# ############################################
# ############ Utility functions #############
# ############################################

def randColor():
  return (randint(0, 255), randint(0, 255), randint(0, 255))

def signal(v):

  if v > 0:
    return 1
  elif v < 0:
    return -1
  else:
    return 0

# ############################################
# ############ Global variables ##############
# ############################################

WIDTH = 800
HEIGHT = 600

tree = Tree(WIDTH, HEIGHT)

startPoint = None
endPoint = None

collisionEdge = None

# ############################################
# ########## Processing functions ############
# ############################################

def setup():
  size(WIDTH + 1, HEIGHT + 1)


def mousePressed():

  global startPoint

  startPoint = (mouseX, mouseY)


def mouseDragged():

  global startPoint, endPoint, collisionEdge

  endPoint = (mouseX, mouseY)

  collisionEdge = tree.checkCollison(startPoint, endPoint)


def mouseReleased():

  global startPoint, endPoint, collisionEdge

  if startPoint != endPoint:
    tree.recalculateBSP(startPoint, endPoint)

  startPoint = None
  endPoint = None
  collisionEdge = None


def draw():

  global startPoint, collisionEdge

  tree.draw()

  if collisionEdge:

    stroke(255)
    strokeWeight(2)
    line(collisionEdge[0][0], collisionEdge[0][1], collisionEdge[1][0], collisionEdge[1][1])
    strokeWeight(1)
    stroke(0)

  if startPoint != None:
    line(startPoint[0], startPoint[1], mouseX, mouseY)
