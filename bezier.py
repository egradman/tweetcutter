import numpy
import math
from cairosvg.surface.helpers import normalize
from cairosvg.surface.path import PATH_LETTERS

class Bezier(object):
  """construct a reparameterized bezier compound curve
     from a collection of control points
     every fourth point is the reused as the first point of the next curve
     [0 1 2 (3] 4 5 [6) 7 8 (9] ...
  """
  def __init__(self, points):

    # separate out the 4-tuple bezier curves
    curves = []
    i = 0
    while i+3 < len(points):
      curves.append(points[i:i+4])
      i += 3

    # for each curve, precompute parallel arrays of length -> (x, y, angle)
    p0 = self.bezierPoint(*curves[0], t=0)
    self.lengths = [0.0] # have to preadd (0.0)?
    self.xs = [p0[0]]
    self.ys = [p0[1]]
    self.angles = [0] # placeholder; this will be set properly at the end
    self.total_length = 0 # total length of this bezier compound
    for a,b,c,d in curves:
      resolution = 64
      for i in range(resolution):
        t0 = (i+0)*1.0/resolution
        t1 = (i+1)*1.0/resolution
        p0 = self.bezierPoint(a,b,c,d, t0)
        p1 = self.bezierPoint(a,b,c,d, t1)
        v = p1-p0
        self.total_length += numpy.sqrt(numpy.sum(numpy.square(v)))
        self.lengths.append(self.total_length)
        self.xs.append(p1[0])
        self.ys.append(p1[1])
        self.angles.append(math.atan2(v[1], v[0]))
    self.lengths /= self.total_length
    # set the initial angle properly
    self.angles[0] = self.angles[1]

  def point_at(self, t):
    """
    for a given t[0..1] return the x,y,th of the curve
    this result is reparameterized in the length of the curve
    which means that the relationship between any interval in t
    and the corresponding interval in distance is fixed
    """
    _xs = numpy.interp(t, self.lengths, self.xs)
    _ys = numpy.interp(t, self.lengths, self.ys)
    _angle = numpy.interp(t, self.lengths, self.angles)
    return list(numpy.vstack([_xs, _ys, _angle]).T)

  @classmethod
  def bezierPoint(cls, a, b, c, d, t):
    """return the xy coordinate on a 4-point bezier curve for a given value of t"""
    t1 = 1-t
    return a*t1*t1*t1 + 3*b*t*t1*t1 + 3*c*t*t*t1 + d*t*t*t
    
  @classmethod
  def parse_svg(cls, string):
    """the thing you're parsing better be a relative continuous bezier curve!"""
    for letter in PATH_LETTERS:
      string = string.replace(letter, "|%s " % letter)
    string = normalize(string)
    commands = string.split("|")[1:]
    c = []
    for command in commands:
      args = command.split()
      letter = args.pop(0)
      args = map(float, args)
      print letter, args
      if letter == "M":
        x1, y1 = args
        c.append(numpy.array((x1, y1)))
      elif letter == "c":
        x1, y1, x2, y2, x3, y3 = args

        top = c[-1]
        c.append(top+numpy.array((x1, y1)))
        c.append(top+numpy.array((x2, y2)))
        c.append(top+numpy.array((x3, y3)))

      elif letter == "s":
        x1 = x3 - x2 # from previous
        y1 = y3 - y2 # from previous

        x2, y2, x3, y3 = args

        top = c[-1]
        c.append(top+numpy.array((x1, y1)))
        c.append(top+numpy.array((x2, y2)))
        c.append(top+numpy.array((x3, y3)))

    return c

