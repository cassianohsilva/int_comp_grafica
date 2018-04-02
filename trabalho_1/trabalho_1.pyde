from random import randint

class Node(object):
  
  def __init__(self, vertices, color):
    super(Node, self).__init__()

    self.__color = color if ( (color != None) and (len(color) == 3) ) else randColor()
    self.__vertices = vertices
    self.__equation = None

    self.__left = None
    self.__right = None

  def subdivide(self, p1, p2, level=0):

    if self.__equation != None:
      signal1 = signal(self.__equation(p1[0], p1[1]))
      signal2 = signal(self.__equation(p2[0], p2[1]))

      if signal1 == signal2:

        if signal1 < 0:
          self.__left.subdivide(p1, p2, level+1)

        else:
          self.__right.subdivide(p1, p2, level+1)

      else:

        # Implement node remove
        if signal1 < 0:
          self.__color = self.__right.__color
        else:
          self.__color = self.__left.__color

        # self.__color = promovedNode.__color
        self.__equation = None
        self.__left = None
        self.__right = None

        pass

    else:

      # Implicit equation coefficients
      a = p2[1] - p1[1]
      b = p1[0] - p2[0]
      c = (p2[0] * p1[1]) - (p1[0] * p2[1])

      self.__equation = lambda x, y : a*x + b*y + c

      new_vertices = [ [], [] ]

      for i in range(len(self.__vertices)):

        v1 = self.__vertices[i]
        v2 = self.__vertices[(i + 1) % len(self.__vertices)]

        # Vector between first mouse point and first bound vertex
        pq = PVector(p1[0] - v1[0], p1[1] - v1[1])

        r = PVector(v2[0] - v1[0], v2[1] - v1[1])
        s = PVector(p2[0] - p1[0], p2[1] - p1[1])

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

          pass

        pass

      self.__left = Node(new_vertices[0], self.__color)
      self.__right = Node(new_vertices[1], None)

      pass
    pass


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

  def subdivide(self, p1, p2):
    self.__root.subdivide(p1, p2)

  @property
  def root(self):
    return self.__root

  @property
  def witdh(self):
    return self.__witdh

  @property
  def height(self):
    return self.__height

def randColor():
  return (randint(0, 255), randint(0, 255), randint(0, 255))

WIDTH = 800
# WIDTH = 600
HEIGHT = 600

tree = Tree(WIDTH, HEIGHT)

startPoint = None
endPoint = None

def signal(v):

  if v > 0:
    return 1
  elif v < 0:
    return -1
  else:
    return 0

def setup():
  size(WIDTH + 1, HEIGHT + 1)

  pass

def mousePressed():

  global startPoint

  startPoint = (mouseX, mouseY)

  pass

def mouseReleased():

  global startPoint, endPoint

  endPoint = (mouseX, mouseY)

  if startPoint != endPoint:
    tree.subdivide(startPoint, endPoint)

  startPoint = None
  endPoint = None

  pass

def draw():

  global startPoint

  tree.draw()

  if startPoint != None:
    line(startPoint[0], startPoint[1], mouseX, mouseY)
