from math import pow, radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Sander( Sandable ):
    """
### Simple figures that create a surprisingly large number of beautiful paterns

#### Hints

Try playing with **Sample rate** first.

#### Parameters

* **Inner radius** and **Outer radius** - how far from the center the spiral should start and end.
* **Lines per Inch** - number of lines drawn within an inch of the spiral.
  Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
* **Starting angle** - the angle the spiral starts at. The default of 0.0 starts to the right of center.
* **Sample rate** - how frequently points are calculated around the spiral.  Smaller numbers create rounder
  spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
  121 to get a rotating triangle; 74 makes a rotating pentagon.
* **Growth base power** - how quickly the outer rings of the spiral get farther from each other.
  The default of 1.0 creates a linear spiral, try 2.0 or more for a spiral that grows faster
  and 0.5 for a spiral that is big in the center.
* **Fill in spiral** - draw lines between points of each subsequent spiral arm.
  This creates a full filled-in spiral that looks pretty neat in sand.
* **X Center** and **Y Center** - where the center of the spiral will be relative to the table.
"""

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", min = 0.0, max = max(width,length) ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default = min(width,length)/2, min = 1.0, max = 100.0 ),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default = 1.0, min = 0.1, max = 24.0 ),
            DialogFloat( "angleStart",      "Starting angle",       units = "degrees", min = 0.0, max = 360.0, step = 15. ),
            DialogFloat( "angleRate",       "Sample rate",          units = "degrees", default = 15.0, min = -180.0, max = 180.0 ),
            DialogFloat( "base",            "Growth base power",    default = 1.0, min = 0.25, max = 10.0 ),
            DialogYesNo( "fill",            "Fill in spiral"        ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
        ]

    def generate( self, params ):
        if not params.angleRate:
            raise SandException( "Sample Rate cannot be zero" )
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius

        xCenter = params.xCenter
        yCenter = params.yCenter
        
        thickness = params.outerRadius - params.innerRadius
        points = int( (360.0 / abs(params.angleRate)) * params.linesPerInch * (params.outerRadius - params.innerRadius))
        divisor = pow((points * abs(params.angleRate)) / 360.0, params.base)
        point360 = 360.0 / abs( params.angleRate )
        
        chain = []
        for point in range( points ):
            angle   = radians( params.angleStart + point * params.angleRate )
            if params.fill:
                if point > point360:
                    radius  = params.innerRadius + thickness * (pow((((point - point360) * abs(params.angleRate)) / 360.0), params.base) / divisor)
                else:
                    radius = params.innerRadius
                x = xCenter + (cos( angle ) * radius)
                y = yCenter + (sin( angle ) * radius)
                chain.append( (x,y) )
            radius  = params.innerRadius + thickness * (pow(((point * abs(params.angleRate)) / 360.0), params.base) / divisor)
            x = xCenter + (cos( angle ) * radius)
            y = yCenter + (sin( angle ) * radius)
            chain.append( (x,y) )

        if params.fitToTable:
            chain = Chains.circleToTable( chain, TABLE_WIDTH, TABLE_LENGTH )
        return [chain]
