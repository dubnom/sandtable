from math import sqrt, radians, sin, cos, pi
from Sand import *
from dialog import *
from Chains import *

class ESpiral( Sandable ):
    """
### Circular pattern with spirals

#### Parameters

* **Lines per Inch** - number of lines drawn within an inch of the spiral.
     Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
* **Sample rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
     spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
     121 to get a rotating triangle; 74 makes a rotating pentagon.
* **X Corner** and **Y Corner** - lower left corner to start the pattern.
* **Width** and **Length** - size of the pattern (spirals can go outside of the bounds).
"""

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "radius",          "Radius",               units="inches", default=min(width,length)/8., min=1.0, max=min(width,length)),
            DialogInt(   "rings",           "Rings",                default=3, min=1, max=max(width,length)),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default=1.0, min=0.1, max=24.0 ),
            DialogFloat( "angleRate",       "Sample rate",          units="degrees", default=15.0, min=-720.0, max=720.0 ),
            DialogFloat( "factor",          "Spacing factor",       default=1.0, min=.5, max=1.5 ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units="inches", default=width/2.0, min=0.0, max=width ),
            DialogFloat( "yCenter",         "Y Center",             units="inches", default=length/2.0, min=0.0, max=length ),
        ]

    def generate( self, params ):
        if not params.angleRate:
            params.angleRate=15.0

        chains = []
        for ring in range(params.rings):
            # FIX: Simplify the math
            if ring > 0:
                ringRadius          = ring * params.radius * 2.0
                ringCircumfrence    = 2.0 * math.pi * ringRadius
                spiralCount         = int(ringCircumfrence / (2.0 * params.radius))
                anglePerSpiral      = 360.0 / spiralCount
                angleEnd            = 45.0 + anglePerSpiral
            else:
                ringRadius          = 0.
                spiralCount         = 1
                anglePerSpiral      = 0.
                angleEnd            = 0.

            for spiral in range(spiralCount):
                xC = params.xCenter + cos(radians(spiral*anglePerSpiral)) * ringRadius
                yC = params.yCenter + sin(radians(spiral*anglePerSpiral)) * ringRadius
                aE = 0 if spiral == spiralCount-1 else angleEnd + 360. * spiral / spiralCount
                chains.append( Chains.spiral(xC,yC,params.radius*params.factor,params.linesPerInch,angleRate=params.angleRate,angleEnd=aE))
        return chains
