from random import randint

WIDTH = 800
#WIDTH = 600
HEIGHT = 600

root_vertices = [ [0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT] ]
vertices = []
colors = []

def subdivide(p1, p2):

  # Implicit equation coefficients
  a = p2[1] - p1[1]
  b = p1[0] - p2[0]
  c = (p2[0] * p1[1]) - (p1[0] * p2[1])

  line_equation = lambda x, y : a*x + b*y + c

  # for p in polygons:

  new_vertices = [ [], [] ]

  colors.append([randint(0, 255), randint(0, 255), randint(0, 255)])
  colors.append([randint(0, 255), randint(0, 255), randint(0, 255)])

  for i in range(len(root_vertices)):

    v1 = root_vertices[i]
    v2 = root_vertices[(i + 1) % len(root_vertices)]

    # Vector between first mouse point and first bound vertex
    pq = PVector(p1[0] - v1[0], p1[1] - v1[1])

    r = PVector(v2[0] - v1[0], v2[1] - v1[1])
    s = PVector(p2[0] - p1[0], p2[1] - p1[1])

    numerator1 = pq.x * s.y - pq.y * s.x
    numerator2 = pq.x * r.y - pq.y * r.x

    denominator = r.x * s.y - r.y * s.x

    intersection = None

    if numerator1 != 0:

      t = numerator1 / denominator
      u = numerator2 / denominator

      if (t >= 0) and (t <= 1):
        intersection = ( v1[0] + t*r.x, v1[1] + t*r.y )

      side = line_equation(v1[0], v1[1])

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

  vertices.append(new_vertices[0])
  vertices.append(new_vertices[1])

  pass

def setup():

  size(WIDTH + 1, HEIGHT + 1)

  # print("root:", root_vertices)
  # subdivide((0, 0), (WIDTH, HEIGHT))
  subdivide((0, 0), (100, 100))
  # print("vertices", vertices)

  pass

def draw():

  for i in range(len(vertices)):

    fill(colors[i][0], colors[i][1], colors[i][2])

    beginShape()

    for j in range(len(vertices[i])):

      v = vertices[i][j]

      vertex(v[0], v[1])

      pass

    endShape(CLOSE)

    pass

  pass
