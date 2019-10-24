from math import radians, sin, cos
from Sand import *
from sandable import Sandable
from dialog import *

class Sander( Sandable ):
    """
### Bulbs can create interesting flower-like images and beautiful geometric patterns

The formula works by imposing a sine wave of **Major frequency** and **Major amplitude** on top of a simple spiral.
**Minor frequency** and **Minor amplitude** are used to modify the sine wave by moving it forward or back a bit
as it goes around - small numbers create ripples, large numbers create cool interference patterns.

#### Parameters 

* **Major frequency** - number of bumps to put on the spiral.
* **Major amplitude** - size of the bumps.
* **Minor frequency** - how often to bend the major bumps forward and backward (numbers close to Major frequency are a good place to start).
* **Minor amplitude** - size of the bending in degrees. Smaller numbers are more subtle, larger numbers create greater folds.
* **Inner radius** and **Outer radius** - how far from the center the spiral should start and end.
* **Turns** - number of lines drawn within the spiral.
* **Sample rate** - angular spacing between points calculated around a 360 degree spiral. Smaller numbers create rounder drawings while larger numbers create spiked shapes.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.
"""

    def __init__( self, width, length, ballSize, units ):
        self.editor = [
            DialogFloat( "majorFreq",       "Major frequency",      units = "per rotation", default=3.0, min=0.0, max=179.0, randRange=(0.1,20.)),
            DialogFloat( "majorAmp",        "Major amplitude",      units = units, default=4.0, min=0.0, max=max(width,length) / 2.0),
            DialogFloat( "minorFreq",       "Minor frequency",      units = "per rotation", default=3.02, min=0.0, max=179.0, randRange=(0.1,20.)),
            DialogFloat( "minorAmp",        "Minor amplitude",      units = "degrees", default=20.0, min=0.0, max=90.0 ),
            DialogBreak(),
            DialogFloat( "innerRadius",     "Inner radius",         units = units, default=1.0, min=0.0, max=max(width,length) ),
            DialogFloat( "outerRadius",     "Outer radius",         units = units, default=min(width,length)/2, min=1.0, max=max(width,length)*1.5 ),
            DialogFloat( "turns",           "Turns",                default = 20.0, min = 0.1, max = max(width,length)*4 ),
            DialogInt(   "angleRate",       "Sample rate",          units = "degrees", default = 5, min = 1, max = 10 ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = units, default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = units, default = length / 2.0 ),
       ] 

    def generate( self, params ):
        chain = []
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius
        if params.angleRate:
            xCenter, yCenter = params.xCenter, params.yCenter
            points = int( (360.0 / abs(params.angleRate)) * params.turns)
            thickness = (params.outerRadius - params.innerRadius) / points
            
            majorFreq = params.majorFreq
            minorFreq = params.minorFreq

            for point in range( points ):
                angle   = point * params.angleRate
                radius  = params.innerRadius + thickness * point
                radius += params.majorAmp * sin( radians( angle * majorFreq ))
                angle1  = radians(angle + params.minorAmp * sin( radians( angle * minorFreq )))
                x = xCenter + radius * cos(angle1)
                y = yCenter + radius * sin(angle1)
                chain.append( (x,y) )

        return [chain]

