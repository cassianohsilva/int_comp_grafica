from random import randint

class Node(object):
  
  """
    parametric list containing 2 elements with 2 coordinates (origin, vector)
  """
  # def __init__(self, parametric, vertices, color):
  def __init__(self, vertices, color):
    # super(Tree, self).__init__()

    self.__color = color if ( (color != None) and (len(color) == 3) ) else randColor()
    self.__vertices = vertices
    self.__equation = None

    # if parametric == None or len(parametric) == 0:
    self.__left = None
    self.__right = None

    # elif len(parametric) == 2:
    #   self.__origin, self.__vector = parametric

    #   bLeft, bRight = self.__calcBounds()

    #   self.__left = Node(None, bLeft, self.__color)
    #   self.__right = Node(None, bRight, randColor())

    # else:
    #   print("Parametric require 0 or 2 coordinates")

  # def __calcBounds(self):

  #   vertices1 = [ self.__vertices[0] ]
  #   vertices2 = []

  #   intersections = []

  #   for i in range(len(self.__vertices)):

  #     if len(intersections) >= 2:
  #       break

  #     else:

  #       p0 = self.__vertices[i]
  #       p1 = self.__vertices[(i + 1) % len(self.__vertices)]

  #       pq = PVector(self.__origin[0] - p0[0], self.__origin[1] - p0[1])

  #       r = PVector(p1[0] - p0[0], p1[1] - p0[1])
  #       s = PVector(self.__vector[0], self.__vector[1])
        
  #       numerator1 = pq.x * s.y - pq.y * s.x
  #       numerator2 = pq.x * r.y - pq.y * r.x

  #       denominator = r.x * s.y - r.y * s.x

  #       if numerator1 != 0:

  #         t = numerator1 / denominator
  #         u = numerator2 / denominator

  #         # if (t >= 0) and (t <= 1) and (u >= 0) and (u <= 1):
          
  #         # If intersect the bound line
  #         if (t >= 0) and (t <= 1):

  #           intersectionPoint = (t*r.x + p0[0], t*r.y + p0[1])

  #           # alreadyAdded = False

  #           # for point in intersections:

  #           #   if isClose(point, intersectionPoint):
  #           #     alreadyAdded = True
  #           #     break

  #           #   pass

  #           # if !alreadyAdded:
  #           #   intersections.append(intersectionPoint)

  #           if len(intersections) == 1:

  #             # vertices1.append(p0)
  #             # if !isclose(t, 0):
  #             vertices1.append(intersectionPoint)

  #             # if !isclose(t, 1):
  #             vertices2.append(intersectionPoint)

  #             vertices2.append(p1)

  #           elif len(intersections) == 2:

  #             vertices1.append(intersectionPoint)
  #             vertices2.append(intersectionPoint)

  #             # vertices1.append(p1)
  #         elif (len(intersections) % 2) == 0:
  #           vertices1.append(p1)
          
  #         elif (len(intersections) % 2) == 1:
  #           vertices2.append(p1)

  #   return [vertices1, vertices2]



  # def subdivide(self, parametric):

  #   if parametric != None and len(parametric) == 2:
  #     self.__origin, self.__vector = parametric

  #     bLeft, bRight = self.__calcBounds()

  #     self.__left = Node(None, bLeft, self.__color)
  #     self.__right = Node(None, bRight, randColor())

  #   else:
  #     raise "Invalid parametric function values"

  def subdivide(self, p1, p2, level=0):

    if self.__equation != None:
      signal1 = signal(self.__equation(p1[0], p1[1]))
      signal2 = signal(self.__equation(p2[0], p2[1]))

      # signal1 = signal(line_equation(p1[0], p1[1]))
      # signal2 = signal(line_equation(p2[0], p2[1]))

      if signal1 == signal2:

        if signal1 > 0:
          self.__left.subdivide(p1, p2, level+1)

        else:
          self.__right.subdivide(p1, p2, level+1)

        pass

      else:
        # Implement node remove
        pass

    else:

      # Implicit equation coefficients
      a = p2[1] - p1[1]
      b = p1[0] - p2[0]
      c = (p2[0] * p1[1]) - (p1[0] * p2[1])

      self.__equation = lambda x, y : a*x + b*y + c

      # signal1 = signal(line_equation(p1[0], p1[1]))
      # signal2 = signal(line_equation(p2[0], p2[1]))

      # if signal1 == signal2:


      # for p in polygons:

      new_vertices = [ [], [] ]

      # colors.append([randint(0, 255), randint(0, 255), randint(0, 255)])
      # colors.append([randint(0, 255), randint(0, 255), randint(0, 255)])

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

        # print(v1, v2, pq, numerator1)

        if (numerator1 != 0) or (numerator2 != 0):

          if denominator == 0.0:
            print("v1: ", v1, " v2: ", v2, " p1: ", p1, " p2: ", p2, " r: ", r, " s: ", s, " vertices: ", self.__vertices, " level: ", level)

          if denominator != 0:
            t = numerator1 / denominator
            u = numerator2 / denominator

            if (t >= 0) and (t <= 1):
              intersection = ( v1[0] + t*r.x, v1[1] + t*r.y )

          side = self.__equation(v1[0], v1[1])

          # print("\tv1: ", v1, " v2: ", v2, " side: ", side)

          if side > 0:
            new_vertices[0].append(v1)

          elif side < 0:
            new_vertices[1].append(v1)

          else:
            new_vertices[0].append(v1)
            new_vertices[1].append(v1)

          if (intersection != None) and (intersection != v1) and (intersection != v2):
            new_vertices[0].append(intersection)
            new_vertices[1].append(intersection)

          pass

        pass

      # pass

      # vertices.append(new_vertices[0])
      # vertices.append(new_vertices[1])

      # self.__left = Node(None, new_vertices[0], self.__color)
      # self.__right = Node(None, new_vertices[1], None)

      self.__left = Node(new_vertices[0], self.__color)
      self.__right = Node(new_vertices[1], None)

      print("level: ", level, " vertices: ", new_vertices)
      # print(new_vertices[1])

        #     self.__origin, self.__vector = parametric

  #     bLeft, bRight = self.__calcBounds()

  #     self.__left = Node(None, bLeft, self.__color)
  #     self.__right = Node(None, bRight, randColor())

      pass
    pass


  def draw(self):
    
    if self.__left != None:
      self.__left.draw()

    if self.__right != None:
      self.__right.draw()

    if (self.__left == None) and (self.__right == None):

      # print(self.__color)

      beginShape()
      fill(self.__color[0], self.__color[1], self.__color[2])

      for p in self.__vertices:
        vertex(p[0], p[1])

      endShape(CLOSE)

    # if self.__left == 

class Tree(object):
  
  def __init__(self, width, height):
    # super(Tree, self).__init__()
    # self.__width = width
    # self.__height = height
    self.__root = Node([(0, 0), (width, 0), (width, height), (0, height)], None)

    # self.__points = [(0, 0), (0, height), (width, height), (width, 0)]

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

# WIDTH = 800
WIDTH = 600
HEIGHT = 600

# root_vertices = [ [0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT] ]
# vertices = []
# colors = []

tree = Tree(WIDTH, HEIGHT)

def signal(v):

  if v > 0:
    return 1
  elif v < 0:
    return -1
  else:
    return 0

def setup():

  size(WIDTH + 1, HEIGHT + 1)

  # print("root:", root_vertices)
  # subdivide((0, 0), (WIDTH, HEIGHT))

  # tree.subdivide((0, 0), (100, 100))
  tree.subdivide((0, 0), (WIDTH, HEIGHT))
  tree.subdivide((90, 100), (100, 110))

  # tree.subdivide((30, 10), (WIDTH, HEIGHT))

  # subdivide((0, 0), (100, 100))
  # print("vertices", vertices)

  pass

def draw():

  tree.draw()
  # for i in range(len(vertices)):

  #   fill(colors[i][0], colors[i][1], colors[i][2])

  #   beginShape()

  #   for j in range(len(vertices[i])):

  #     v = vertices[i][j]

  #     vertex(v[0], v[1])

  #     pass

  #   endShape(CLOSE)

  #   pass

  # pass