import math


class PolyLine:
    def __init__(self, points=[]):
        self.points = points
        self.stack = []
        self.x = 0.0
        self.y = 0.0
        self.a = 0.0

    def __setitem__(self, i, v):
        self.points[i] = v

    def __getitem__(self, i):
        return self.points[i]

    def __delitem__(self, i):
        del self.points[i]

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return repr(self.points)

    def __add__(self, v):
        return self.points.__add__(v)

    def append(self, i):
        self.points.append(i)

    def extend(self, vs):
        self.points.extend(vs)

    def reverse(self):
        self.points.reverse()

#
#   Specific polyline methods
#
    def extents(self, ext=[(1E100, 1E100), (-1E100, -1E100)]):
        """Calculate the lower left and upper right corners"""
        xp, yp = list(zip(*self.points))
        return [(min(ext[0][0], min(xp)), min(ext[0][1], min(yp))), (max(ext[1][0], max(xp)), max(ext[1][1], max(yp)))]

    def scale(self, scale):
        """Multiply each point by the scale factors"""
        self.points = [(p[0] * scale[0], p[1] * scale[1]) for p in self.points]
        return self

    def translate(self, offset):
        """Translate (move) all of the points by offset"""
        self.points = [(p[0] + offset[0], p[1] + offset[1]) for p in self.points]
        return self

    def rotate(self, angle):
        """Rotate all of the points by angle around 0,0"""
        sin = math.sin(math.radians(angle))
        cos = math.cos(math.radians(angle))
        self.points = [(p[0] * cos - p[1] * sin, p[0] * sin + p[1] * cos) for p in self.points]
        return self

#
#   Turtle operations
#
    def forward(self, distance):
        """Move the turtle forward by distance"""
        if not len(self):
            self.points = [(0.0, 0.0)]
        x, y = self.points[-1]
        newX = x + math.cos(math.radians(self.a)) * distance
        newY = y + math.sin(math.radians(self.a)) * distance
        self.points.append((newX, newY))

    def turn(self, degrees):
        """Turn the turtle by degrees"""
        self.a += degrees

    def push(self):
        """Save the current position of the turtle on a stack"""
        if not len(self):
            self.points = [(0.0, 0.0)]
        self.stack.append((self.a, len(self.points)-1))

    def _pop(self):
        self.a, oldPos = self.stack.pop()
        # reverse course over the pushed path
        if oldPos == 0:
            self.points.extend(self.points[::-1])
        else:
            self.points.extend(self.points[len(self.points)-1:oldPos-1:-1])

    def pop(self):
        """Move back (in an efficient and non-destructive manner) to a previous position"""
        self.a, oldPos = self.stack.pop()
        if oldPos == 0:
            points = self.points[::-1]
        else:
            points = self.points[len(self.points)-1:oldPos-1:-1]

        # Remove extra paths when popping the location (and hence path)
        # off the stack.

        # Create a dictionary of rouded duplicate points in the path
        def round(n): return math.floor(n * 100000.0 + 0.5) * .00001
        segs = {}
        for i, p in enumerate(points):
            p = (round(p[0]), round(p[1]))
            if p in segs:
                segs[p].append(i)
            else:
                segs[p] = [i]

        # Create ranges of points based on the first and last time a point was found
        delRange = []
        for seg in list(segs.values()):
            lo, hi = min(seg), max(seg)
            if lo != hi:
                delRange.append((hi-lo, (lo, hi)))

        # Create a list of final ranges of points to delete by looking for the largest
        # ranges first and eliminating enclosed or overlapping smaller ranges
        if len(delRange):
            delRange.sort()
            delRange.reverse()
            bigRanges = []
            for dist, (lo, hi) in delRange:
                for i in range(len(bigRanges)):
                    l, h = bigRanges[i]
                    if lo >= l and hi <= h:
                        break
                    elif hi < l or lo > h:
                        continue
                    elif dist <= h-l:
                        break
                    bigRanges[i] = (hi, lo)
                    break
                else:
                    bigRanges.append((lo, hi))

            bigRanges.sort()
            bigRanges.reverse()
            for lo, hi in bigRanges:
                del points[lo:hi]

        self.points.extend(points)
