import math
from sandable import Sandable, SandException
from dialog import DialogStr, DialogFloat, DialogInt, DialogYesNo, DialogBreak
from Chains import Chains


class Sander(Sandable):
    """
### Graph 3D functions of the form z = f(x,y)

#### Parameters

* **Expression** - mathematical formula that returns a number and can use any of the functions, constants,
  and variables that are explained in more detail below.  The function shouldn't include "z=" because it is implied.
* **X Start, End, Points** - defines the range of **x** points being given to the **Expression** and
  subsequently graphed.
* **Y Start, End, Points** - defines the range of **y** points.
* **Z Scale** - amount to multiply the z values by.  Z values are automatically scaled between -1.0 and 1.0.
  A **Z Scale** factor of 1.0 leaves the high alone. Smaller values reduce the size of the "bumps" in the graph
  while larger values exagerate them.
* **Horizontal Rotation** - angle to horizontally rotate the graph. The graph can be rotated up to 45 degrees.
* **Vertical Tilt** - angle to tilt the graph down. The highest angle is 90 degrees - looking at the graph from the side.
  An angle of 0 degrees looks down from the top and isn't very interesting because there is no way to see the z values.
* **Zoom** - the graph is automatically resized to fit the drawing area. To create drawings that take up the entire
  space you can "zoom in" by increasing this value.
* **Top Down** - direction for drawing the chart. The default is set to True to draw with correct hidden-lines.
  Switching this to False can create some interesting inversion effects.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.

#### Available functions, constants, and variables

##### Functions (from the Python math module)

    abs, acos, asin, atan, atan2, ceil, cos, cosh, degrees,
    exp, fabs, float, floor, fmod, frexp, hypot, int, ldexp,
    log, log10, modf, pow, radians, sin, sinh, sqrt, tan, tanh

##### Constants

    e, pi

##### Variables

    x, y

#### Examples

  Description | Expression | Ranges
  --- | --- | ---
  Waves | x**3-3*x+y**3-3*y | X and Y (-1, 1, 45)
  Rosenbrock Function | -((1-x)**2 + 100*(y-x**2)**2) | X and Y (-2, 2, 45)
  Reverse Dish | -x**2-y**2 | X and Y (-2, 2, 45)
  Exponential Bumps | -x*exp(-x**2-y**2) | X and Y (-2, 2, 45)
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogStr("expression",      "Expression",           default='cos( 3.*radians( sqrt(x*x+y*y )))', length=45),
            DialogFloat("xStart",          "X Start",              default=-180.0),
            DialogFloat("xEnd",            "X End",                default=180.0),
            DialogInt("xPoints",         "X Points",             default=45, min=2, max=180),
            DialogFloat("yStart",          "Y Start",              default=-180.0),
            DialogFloat("yEnd",            "Y End",                default=180.0),
            DialogInt("yPoints",         "Y Points",             default=45, min=2, max=180),
            DialogFloat("zScale",          "Z Scale",              default=1.0, min=0.01, max=10.0),
            DialogFloat("xyAngle",         "Horizontal Rotation",  units="degrees", default=45.0, min=-45.0, max=45.0),
            DialogFloat("yzAngle",         "Vertical Tilt",        units="degrees", default=45.0, min=0.0, max=90.0),
            DialogFloat("zoom",            "Zoom",                 default=1.0, min=0.25, max=10.0),
            DialogYesNo("topDown",         "Top Down",             default=True),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",             units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",             units=units, default=0.0),
            DialogFloat("width",           "Width",                units=units, default=width, min=1.0, max=width*4),
            DialogFloat("length",          "Length",               units=units, default=length, min=1.0, max=length*4),
        ]

    def generate(self, params):
        xPoints = params.xPoints
        yPoints = params.yPoints
        xOffset = params.xOffset
        yOffset = params.yOffset
        xStart = params.xStart
        yStart = params.yStart
        xyAngle = math.radians(params.xyAngle)
        yzAngle = math.radians(params.yzAngle)

        xScale = params.width / (xPoints - 1)
        yScale = params.length / (yPoints - 1)

        yAScale = (params.yEnd - yStart) / (yPoints - 1)
        xAScale = (params.xEnd - xStart) / (xPoints - 1)

        # Calculate the zValues
        try:
            self._initCallFunc(params.expression)
            zMin, zMax = 1E100, -1E100
            zValues = [[0.0] * xPoints for y in range(yPoints)]
            for y in range(yPoints):
                yr = y * yAScale + yStart
                for x in range(xPoints):
                    xr = x * xAScale + xStart
                    z = self._callFunc(xr, yr)
                    zMin, zMax = min(z, zMin), max(z, zMax)
                    zValues[y][x] = z
        except Exception as e:
            raise SandException("Expression failed: %s" % e)

        if type(zMin) not in (int, float) or type(zMax) not in (int, float):
            raise SandException("The function didn't return proper numbers for the Z calculation")

        # Generate the chains
        xScale = 2.0 / xPoints
        xOffset = -1.0
        yScale = 2.0 / yPoints
        yOffset = -1.0
        zScale = 2.0 / (zMax - zMin) if zMax != zMin else 1.
        zOffset = zMin
        chain = []
        for y in range(yPoints):
            points = []
            yp = yOffset + yScale * y
            for x in range(xPoints):
                xp = xOffset + xScale * x
                zp = params.zScale * (zValues[y][x] - zOffset) * zScale
                xpr, ypr, zpr = self._rotate((xp, yp, zp), xyAngle, yzAngle)
                points.append((xpr, ypr))
            if y % 2:
                points.reverse()
            chain += points

        if params.topDown:
            chain.reverse()
        chains = Chains.autoScaleCenter([chain], [(params.xOffset, params.yOffset), (params.xOffset+params.width, params.yOffset+params.length)], params.zoom)
        return chains

    def _initCallFunc(self, expression):
        math_safe_list = [
            'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees',
            'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',
            'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan',
            'tanh',
        ]
        norm_safe_list = ['min', 'max', 'abs', 'float', 'int']
        self.safe_dict = dict([(k, eval('math.'+k)) for k in math_safe_list])
        for k in norm_safe_list:
            self.safe_dict[k] = eval(k)
        self.expression = compile(expression, 'Expression', 'eval')

    def _callFunc(self, x, y):
        self.safe_dict['x'] = self.safe_dict['X'] = x
        self.safe_dict['y'] = self.safe_dict['Y'] = y
        # Only allow a small subset of builtin functions
        z = eval(self.expression, {'__builtins__': {}}, self.safe_dict)
        return z

    def _rotate(self, p, xyR, yzR):
        x, y, z = p
        x1 = x * math.cos(xyR) - y * math.sin(xyR)
        y1 = x * math.sin(xyR) + y * math.cos(xyR)
        y2 = y1 * math.cos(yzR) - z * math.sin(yzR)
        z2 = y1 * math.sin(yzR) + z * math.sin(yzR)
        return (x1, y2, z2)
