from math import sin, cos, radians, floor
from sandable import Sandable, inchesToUnits
from Chains import *
from dialog import *

from random import random, uniform, seed
    
class Sander( Sandable ):
    """
### Create a Japanese Zen rock garden

#### Hints

Press the *Random* button to automatically make new drawings.

#### Parameters

* **Number of rocks** - number of rocks in the garden.
* **Min and Max rock size** - smallest and largest possible rock sizes (radius).
* **Ball size** - size of the ball in inches for making rake lines.
* **Rake teeth** - Number of tines in the rake for cirlces around the rocks.
* **Random seed** - this is used to generate random gardens.  Different seeds generate different drawings.
    The *Random* button will create new seeds automatically.
* **Width** and **Length** - how big the maze should be. Probably not worth changing.
* **Starting locations** - where on the table the maze should be drawn. Also normally not worth changing.
"""

    def __init__( self, width, length, ballSize, units ):
        rockSize = min(width,length) / 4.0
        self.editor = [
            DialogInt(   "rocks",           "Number of rocks",          default = 5, min = 1, max = 25 ),
            DialogFloat( "minRockSize",     "Minimum rock size",        units = units, min = .25, max = rockSize, default = inchesToUnits(1.0,units)),
            DialogFloat( "maxRockSize",     "Maximum rock size",        units = units, min = .25, max = rockSize, default = inchesToUnits(1.0,units)),
            DialogInt(   "rakeSize",        "Rake teeth",               units = "tines", min = 2, max = 8, default = 4 ),
            DialogInt(   "seed",            "Random Seed",              default = 1, min = 0, max = 10000, rbutton = True ),
            DialogBreak(),
            DialogFloat( "ballSize",        "Ball size",                units = units, min = .25, default = ballSize ),
            DialogFloat( "xOffset",         "X Origin",                 units = units, default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",                 units = units, default = 0.0 ),
            DialogFloat( "width",           "Width (x)",                units = units, default = width ),
            DialogFloat( "length",          "Length (y)",               units = units, default = length ),
        ]

    def generate( self, params ):
        rockLPI     = 16.0

        seed( params.seed )
        rocks = [ (params.width * random(), params.length * random()) for n in range( params.rocks ) ]

        # Draw rocks
        chains = []
        for rock in rocks:
            rockSize = uniform( params.minRockSize, params.maxRockSize )
            # draw inside tight 16 lpi spiral
            chain = self._transform( self._spiral( 1. / rockLPI, 0.0, floor( rockSize * rockLPI ) ), rock )
            # draw outside loose ball lpi spiral ending on left side
            chain += self._transform( self._spiral( params.ballSize, rockSize, params.rakeSize ), rock )
            chains.append( chain )

        return Chains.scanalize( chains, params.xOffset, params.yOffset, params.width, params.length, 1.0 / params.ballSize )

    
    def _spiral( self, lineWidth, innerRadius, rotations, angleRate = 15.0 ):
        chain = []
        points = int(floor( (360.0 / angleRate) * rotations ))
        radiusFactor = (rotations * lineWidth) / points
        for point in range(int(points)):
            angle = radians( point * angleRate )
            radius = innerRadius + point * radiusFactor 
            chain.append( (cos( angle ) * radius, sin( angle ) * radius))
        return chain

    def _transform( self, chain, offset ):
        return [ (x + offset[0], y + offset[1]) for (x,y) in chain ]
