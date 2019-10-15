from math import radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Star( Sandable ):
    """
### Draw stars that can change size while rotating

Draw a star that has **Points** and an inside radius of **Inner radius 1** and an outside
radius of **Outer radius 1**.  For each **Number of stars**, rotate the star by
**Shift angle** and gradually change the size of the star to **Inner radius 2** and
**Outer radius 2**

#### Parameters

* **Points** - how many points on the star.
* **Inner and Outer Radii 1** - radii (inside and outside points) for star.
* **Inner and Outer Radii 2** - radii for the ending sizes of the star.
* **Starting angle** - amount the the entire drawing is rotated.
* **Shift angle** - number of degrees to shift the drawing between stars.
* **Number of stars** - number of stars to draw.

#### Examples

Description | Points | Inner/Outer Radii | Start | Shift | Stars
--- | --- | --- | --- | --- | ---
Splashy | 5 | 1, 3, 2, 7 | 32 | 5 | 20
David | 6 | 1, 4, 5, 8 | 0 | 5 | 6
Battlement | 12 | 6, 8, 1, 2 | 0 | 0 | 9
"""

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "points",          "Points",               min = 3, max = 75, default = 5 ),
            DialogFloat( "innerRadius1",    "Inner radius 1",       units = "inches", default = 3.0, min = 1.0, max = max(width,length)/2 ),
            DialogFloat( "outerRadius1",    "Outer radius 1",       units = "inches", default = min(width,length)/2, min = 2.0, max = max(width,length)/2),
            DialogFloat( "innerRadius2",    "Inner radius 2",       units = "inches", default = 0.0 ),
            DialogFloat( "outerRadius2",    "Outer radius 2",       units = "inches", default = 5.0 ),
            DialogFloat( "angleStart",      "Starting angle",       units = "degrees" ),
            DialogFloat( "angleShift",      "Shift angle",          units = "degrees", default = 0.0, min = 0.0, max = 15.0 ),
            DialogInt(   "steps",           "Number of stars",      default = 5, min = 0, max = 40 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
        ]

    def generate( self, params ):
        chain = []
        if params.steps > 0:
            steps = params.steps
            innerRate = (params.innerRadius2 - params.innerRadius1) / steps
            outerRate = (params.outerRadius2 - params.outerRadius1) / steps
        else:
            innerRate = outerRate = 0.0
            steps = 1

        angleStart = params.angleStart
        angle = 360.0 / params.points
        self.xCenter = params.xCenter
        self.yCenter = params.yCenter

        for step in range( steps ):
            innerRadius = params.innerRadius1 + innerRate * step
            outerRadius = params.outerRadius1 + outerRate * step
            for point in range( params.points ):
                innerAngle = angleStart + angle * point
                outerAngle = innerAngle + (angle / 2.0)
                chain.append( self._point( innerAngle, innerRadius ))
                chain.append( self._point( outerAngle, outerRadius ))
            chain.append( self._point( angleStart, innerRadius ))
            angleStart += params.angleShift

        if params.fitToTable:
            chain = Chains.circleToTable( chain, TABLE_WIDTH, TABLE_LENGTH )
        return [chain]

    def _point( self, angle, radius ):
        angle = radians( angle )
        return( (self.xCenter + cos( angle ) * radius, self.yCenter + sin( angle ) * radius))


