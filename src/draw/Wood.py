from math import sqrt, radians, sin, cos
import Chains
from Sand import *
from dialog import *

from random import random, seed
    
class Sander( Sandable ):
    """
### Randomly generate something that looks like a wood board

#### Hints

Drawing random wood boards requires a lot of compute time. Be patient.

#### Parameters

* **Number of Knots** - number of knots that the piece of wood should have.
* **Maximum Knot Radius** - largest radius (in inches) of a random knot.
* **Random seed** - used to generate random drawings.  Different seeds generate different locations
  and sizes for the knots. The *Random* button will create new seeds automatically.
* **X Lines per Inch** - The straightness/curviness of the wood grain lines.
* **Y Lines per Inch** - The density of wood grain per inch.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    SPIRAL_LPI = 4.0

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "knots",           "Number of Knots",          default = 5, min = 0, max = 100 ),
            DialogFloat( "rKnot",           "Maximum Knot Radius",      units = "inches", default = 5.0, min = 1.0, max = 10.0 ),
            DialogInt(   "seed",            "Random Seed",              default = 1, min = 0, max = 10000, rbutton = True ),
            DialogFloat( "xLinesPerInch",   "X Lines per Inch",         default = 10.0, min = 0.001, max = 60.0 ),
            DialogFloat( "yLinesPerInch",   "Y Lines per Inch",         default = 2.0, min = 0.001, max = 10.0 ),
            DialogBreak(),
            DialogFloat( "xOffset",         "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width (x)",                units = "inches", default = width ),
            DialogFloat( "length",          "Length (y)",               units = "inches", default = length ),
        ]

    def generate( self, params ):
        seed( params.seed )
        knots = []
        attempts = 200
        while len( knots ) < params.knots and attempts > 0:
            x = params.xOffset + 1.0 + random()*(params.width-2.0)
            y = params.yOffset + 1.0 + random()*(params.length-2.0)
            r = int(self.SPIRAL_LPI * max(1.0,random() * params.rKnot))
            # Check for circular overlap
            for knot in knots:
                if self._overlap( x, y, r, knot ):
                    attempts -= 1
                    break
            else:
                knots.append( ((x,y), r) )
        knots.sort( key = lambda chain: chain[0][0] )

        chains = self._grid( params )
        for c, s in knots:
            self._knot( chains, c, s )
            chains.insert( 0, self._transform( self._spiral( 1.0 / self.SPIRAL_LPI, 0.0, s ), c))
        chains.insert( len( knots ), [ (params.xOffset+params.width, params.yOffset) ] )
        return chains
    
    def _grid( self, params ):
        xCount = int( params.width * params.xLinesPerInch )
        yCount = int( params.length * params.yLinesPerInch )
        xSpacing = params.width / xCount
        ySpacing = params.length / yCount
        
        chains = []
        for y in range( yCount + 1 ):
            yp = params.yOffset + y * ySpacing
            chain = [ [params.xOffset + x * xSpacing, yp] for x in range( xCount + 1 ) ]
            if y % 2:
                chain.reverse()
            chains.append( chain )
        return chains
    
    def _knot( self, chains, knotCenter, knotRadius ):
        for chain in chains:
            for point in chain:
                distance = sqrt( (knotCenter[0]-point[0]) ** 2 + (knotCenter[1]-point[1]) ** 2 )
                if distance > 0.001:
                    point[0] += knotRadius/self.SPIRAL_LPI * ((point[0] - knotCenter[0]) / distance)
                    point[1] += knotRadius/self.SPIRAL_LPI * ((point[1] - knotCenter[1]) / distance)

    def _spiral( self, lineWidth, innerRadius, rotations, angleRate = 15.0 ):
        chain = []
        points = int((360.0 / angleRate) * rotations )
        radiusFactor = (rotations * lineWidth) / points
        for point in range(int(points)):
            angle = radians( point * angleRate )
            radius = innerRadius + point * radiusFactor 
            chain.append( [cos( angle ) * radius, sin( angle ) * radius])
        return chain

    def _transform( self, chain, offset ):
        return [ [x + offset[0], y + offset[1]] for (x,y) in chain ]

    def _overlap( self, x1, y1, r1, rock ):
        ((x2, y2), r2) = rock
        dx, dy = x2 - x1, y2 - y1
        return sqrt( dx**2 + dy**2 ) < (r1 + r2)
