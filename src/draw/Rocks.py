from math import sin, cos, radians, floor
from Chains import *
from Sand import *
from dialog import *
from Sand import *

from random import random, uniform, seed
    
class Rocks( Sandable ):
    """
        <h3>Create a Japanese Zen rock garden</h3>

        Hint: Press the <i>Random</i> button to automatically make new drawings.

        <ul>
         <li><i>Number of rocks</i> - number of rocks in the garden.
         <li><i>Min and Max rock size</i> - smallest and largest possible rock sizes (radius).
         <li><i>Ball size</i> - size of the ball in inches for making rake lines.
         <li><i>Rake teeth</i> - Number of tines in the rake for cirlces around the rocks.
         <li><i>Random seed</i> - this is used to generate random gardens.  Different seeds generate different drawings.
             The <i>Random</i> button will create new seeds automatically.
         <li><i>Width</i> and <i>Length</i> - how big the maze should be. Probably not worth changing.
         <li><i>Starting locations</i> - where on the table the maze should be drawn. Also normally not worth changing.
        </ul>"""

    def __init__( self, width, length ):
        rockSize = min(width,length) / 4.0
        cfg = LoadConfig()
        self.editor = [
            DialogInt(   "rocks",           "Number of rocks",          default = 5, min = 1, max = 25 ),
            DialogFloat( "minRockSize",     "Minimum rock size",        units = "inches", min = .25, max = rockSize, default = 1.0 ),
            DialogFloat( "maxRockSize",     "Maximum rock size",        units = "inches", min = .25, max = rockSize, default = 1.0 ),
            DialogInt(   "rakeSize",        "Rake teeth",               units = "tines", min = 2, max = 8, default = 4 ),
            DialogInt(   "seed",            "Random Seed",              default = 1, min = 0, max = 10000, rbutton = True ),
            DialogBreak(),
            DialogFloat( "ballSize",        "Ball size",                units = "inches", min = .25, default = cfg.ballSize ),
            DialogFloat( "xOffset",         "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width (x)",                units = "inches", default = width ),
            DialogFloat( "length",          "Length (y)",               units = "inches", default = length ),
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
