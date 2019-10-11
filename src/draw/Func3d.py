from Sand import *
from dialog import *
from Chains import *
from math import *
    
class Func3d( Sandable ):
    """
        <h3>Graph 3D functions of the form z = f(x,y)</h3>

        <ul>
         <li><i>Expression</i> - mathematical formula that returns a number and can use any of the functions, constants,
             and variables that are explained in more detail below.  The function shouldn't include "z=" because it is implied.
         <li><i>X Start, End, Points</i> - defines the range of <i>x</i> points being given to the <i>Expression</i> and
             subsequently graphed.
         <li><i>Y Start, End, Points</i> - defines the range of <i>y</i> points.
         <li><i>Z Scale</i> - amount to multiply the z values by.  Z values are automatically scaled between -1.0 and 1.0.
             A <i>Z Scale</i> factor of 1.0 leaves the high alone. Smaller values reduce the size of the "bumps" in the graph
             while larger values exagerate them.
         <li><i>Horizontal Rotation</i> - angle to horizontally rotate the graph. The graph can be rotated up to 45 degrees.
         <li><i>Vertical Tilt</i> - angle to tilt the graph down. The highest angle is 90 degrees - looking at the graph from the side.
             An angle of 0 degrees looks down from the top and isn't very interesting because there is no way to see the z values.
         <li><i>Zoom</i> - the graph is automatically resized to fit the drawing area. To create drawings that take up the entire
             space you can "zoom in" by increasing this value.
         <li><i>Top Down</i> - direction for drawing the chart. The default is set to Trueto draw with correct hidden-lines.
             Switching this to False can create some interesting inversion effects.
         <li><i>X and Y Origin</i> - lower left corner of the drawing. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the figure should be. Probably not worth changing.
        </ul>

        Some interesting functions:<br>
        <blockquote>
         <table>
          <tr><th>Description</th><th>Expression</th><th>Ranges</th></tr>
          <tr><td>Waves</td><td>x**3-3*x+y**3-3*y</td><td>X and Y (-1, 1, 45)</td></tr>
          <tr><td>Rosenbrock Function</td><td>-((1-x)**2 + 100*(y-x**2)**2)</td><td>X and Y (-2, 2, 45)</td></tr>
          <tr><td>Reverse Dish</td><td>-x**2-y**2</td><td>X and Y (-2, 2, 45)</td></tr>
          <tr><td>Exponential Bumps</td><td>-x*exp(-x**2-y**2)</td><td>X and Y (-2, 2, 45)</td></tr>
         </table>
        </blockquote>

        List of supported functions (from the Python math module):<br>
        <blockquote>abs, acos, asin, atan, atan2, ceil, cos, cosh, degrees, exp, fabs, floor, fmod,
        frexp, hypot, ldexp, log, log10, modf, pow, radians, sin, sinh, sqrt, tan, tanh</blockquote>

        List of supported constants:<br>
        <blockquote>e, pi</blockquote>

        List of supported variables:<br>
        <blockquote>x, y</blockquote>
        """

    def __init__( self, width, length ):
        self.editor = [
            DialogStr(   "expression",      "Expression",           default = 'cos( 3.*radians( sqrt(x*x+y*y )))', length=45 ),
            DialogFloat( "xStart",          "X Start",              default = -180.0 ),
            DialogFloat( "xEnd",            "X End",                default = 180.0 ),
            DialogInt(   "xPoints",         "X Points",             default = 45, min = 2, max = 180 ),
            DialogFloat( "yStart",          "Y Start",              default = -180.0 ),
            DialogFloat( "yEnd",            "Y End",                default = 180.0 ),
            DialogInt(   "yPoints",         "Y Points",             default = 45, min = 2, max = 180 ),
            DialogFloat( "zScale",          "Z Scale",              default = 1.0, min = 0.01, max = 10.0 ),
            DialogFloat( "xyAngle",         "Horizontal Rotation",  units = "degrees", default = 45.0, min = 0.0, max = 45.0 ),
            DialogFloat( "yzAngle",         "Vertical Tilt",        units = "degrees", default = 45.0, min = 0.0, max = 90.0 ),
            DialogFloat( "zoom",            "Zoom",                 default = 1.0, min = 0.25, max = 10.0 ),
            DialogYesNo( "topDown",         "Top Down",             default = True ),
            DialogBreak(),
            DialogFloat( "xOffset",         "X Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width",                units = "inches", default = width, min = 1.0, max = 1000.0 ),
            DialogFloat( "length",          "Length",               units = "inches", default = length, min = 1.0, max = 1000.0 ),
        ]

    def generate( self, params ):
        xPoints = params.xPoints
        yPoints = params.yPoints
        xOffset = params.xOffset
        yOffset = params.yOffset
        xStart = params.xStart
        yStart = params.yStart
        xyAngle = params.xyAngle
        yzAngle = params.yzAngle

        xScale = params.width / (xPoints - 1)
        yScale = params.length / (yPoints - 1)
        
        yAScale = (params.yEnd - yStart) / (yPoints - 1)
        xAScale = (params.xEnd - xStart) / (xPoints - 1)

        # Calculate the zValues
        try:
            self._initCallFunc( params.expression )
            zMin, zMax = 1E100, -1E100
            zValues = [[ 0.0 ] * xPoints for y in range( yPoints )]
            for y in range( yPoints ):
                yr = y * yAScale + yStart
                for x in range( xPoints ):
                    xr = x * xAScale + xStart
                    z = self._callFunc( xr, yr )
                    zMin, zMax = min(z,zMin), max(z,zMax)
                    zValues[ y ][ x ] = z
        except Exception as e:
            raise SandException( "Expression failed: %s" % e )

        if type(zMin) != float or type(zMax) != float or zMin == zMax:
            raise SandException( "The function didn't return proper numbers for the Z calculation" )

        # Generate the chains (NEW WAY)
        xScale = 2.0 / xPoints
        xOffset = -1.0
        yScale = 2.0 / yPoints
        yOffset = -1.0
        zScale = 2.0 / (zMax - zMin)
        zOffset = zMin
        chain = []
        for y in range( yPoints ):
            points = []
            yp = yOffset + yScale * y
            for x in range( xPoints ):
                xp = xOffset + xScale * x
                zp = params.zScale * (zValues[y][x] - zOffset) * zScale
                xpr, ypr, zpr = self._rotate((xp,yp,zp),xyAngle,yzAngle)
                points.append( (xpr,ypr) )
            if y % 2:
                points.reverse()
            chain += points

        if params.topDown:
            chain.reverse()
        chains = Chains.autoScaleCenter( [chain], [(params.xOffset,params.yOffset),(params.xOffset+params.width,params.yOffset+params.length)], params.zoom )
        return chains

    def _initCallFunc( self, expression ):
        self.expression = expression
        from math import acos,asin,atan,atan2,ceil,cos,cosh,degrees,e,exp,fabs,floor,fmod,frexp,hypot,ldexp,log,log10,modf,pi,pow,radians,sin,sinh,sqrt,tan,tanh

        safe_list = [
            'math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh','degrees',
            'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 
            'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh',
            ]
        self.safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        self.safe_dict['abs'] = abs
    
    def _callFunc( self, x, y ):
        self.safe_dict['x'] = self.safe_dict['X'] = x
        self.safe_dict['y'] = self.safe_dict['Y'] = y
        z = eval( self.expression, {"__builtins__":None}, self.safe_dict )
        return z

    def _rotate( self, p, xyAngle, yzAngle ):
        x, y, z = p
        x1 = x * cos( radians( xyAngle )) - y * sin( radians( xyAngle ))
        y1 = x * sin( radians( xyAngle )) + y * cos( radians( xyAngle ))
        y2 = y1 * cos( radians( yzAngle )) - z * sin( radians( yzAngle ))
        z2 = y1 * sin( radians( yzAngle )) + z * sin( radians( yzAngle ))
        return (x1,y2,z2)
