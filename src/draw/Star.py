from math import radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Star( Sandable ):
    """
        <h3>Draw a star that can change size while rotating</h3>

        <p>Draw a star that has <i>Points</i> and an inside radius of <i>Inner radius 1</i> and an outside
        radius of <i>Outer radius 1</i>.  For each <i>Number of stars</i>, rotate the star by
        <i>Shift angle</i> and gradually change the size of the star to <i>Inner radius 2</i> and
        <i>Outer radius 2</i></p>

        <ul>
         <li><i>Points</i> - how many points on the star.
         <li><i>Inner and Outer Radii 1</i> - radii (inside and outside points) for star.
         <li><i>Inner and Outer Radii 2</i> - radii for the ending sizes of the star.
         <li><i>Starting angle</i> - amount the the entire drawing is rotated.
         <li><i>Shift angle</i> - number of degrees to shift the drawing between stars.
         <li><i>Number of stars</i> - number of stars to draw.
        </ul>

        Some interesting drawings:<br>
        <blockquote>
         <table>
          <tr><th>Description</th><th>Points</th><th>Inner/Outer Radii</th><th>Start, Shift, Stars</th></tr>
          <tr><td>Splashy</td><td>5</td><td>1, 3, 2, 7</td><td>32, 5, 20</td></tr>
          <tr><td>David</td><td>6</td><td>1, 4, 5, 8</td><td>0, 5, 6</td></tr>
          <tr><td>Battlement</td><td>12</td><td>6, 8, 1, 2</td><td>0, 0, 9</td></tr>
         </table>
        </blockquote>"""

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


