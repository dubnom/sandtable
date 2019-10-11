from math import radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class SpiralArms( Sandable ):
    """
        <h3>Draw clockwise and counter-clockwise spiral arms from the center</h3>

        Hint: Smaller <i>CW and CCW angular distances</i> make drawings that look more like flowers.

        <ul>
         <li><i>CW and CCW arms</i> - number of clockwise and counter-clockwise arms.
         <li><i>CW and CCW angular distances</i> - angular distance that each arm rotates by the time it gets to the
             <i>Outer radius</i>. Higher numbers (try 360) give tighter spirals while lower numbers (try 30) will
             look more like flower petals.  CW and CCW refer to the normal direction of the spirals if the <i>angular
             distance</i> is positive, but these directions can be reversed by using negative numbers.  Zero draws straight
             lines from the <i>Inner radius</i> to the <i>Outer radius</i>.
         <li><i>Points per arm</i> - the number of points used to draw each spiral arm.  Smaller numbers will look
             more like angular lines while larger numbers will generate curves.
         <li><i>Inner radius</i> and <i>Outer radius</i> - how far from the center the spiral should start and end.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the drawing will be relative to the table.
        </ul>"""

    def __init__( self, width, length ):
        radius = min(width,length) / 2.0
        mRadius = max(width,length) / 2.0
        self.editor = [
            DialogInt(   "cwArms",          "CW arms",              default = 12, min = 1, max = 120 ),
            DialogFloat( "cwAngular",       "CW angular distance",  default = 30.0, units = "degrees" ),
            DialogInt(   "ccwArms",         "CCW arms",             default = 12, min = 1, max = 120 ),
            DialogFloat( "ccwAngular",      "CCW angular distance", default = 30.0, units = "degrees" ),
            DialogInt(   "points",          "Points per arm",       default = 10, min = 2 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", default = radius * 0.15, min = 0.0, max = mRadius ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default = radius, min = 1.0, max = mRadius ),
        ]

    def generate( self, params ):
        chains = [
            self._arms( params.xCenter, params.yCenter, params.innerRadius, params.outerRadius, params.cwArms, -params.cwAngular, params.points),
            self._arms( params.xCenter, params.yCenter, params.innerRadius, params.outerRadius, params.ccwArms, params.ccwAngular, params.points)
        ]
        if params.fitToTable:
            chains = [ Chains.circleToTable( c, TABLE_WIDTH, TABLE_LENGTH ) for c in chains ]
        return chains

    def _arms( self, xCenter, yCenter, innerRadius, outerRadius, arms, angularDistance, armPoints ):
        degreesPerArm = 360.0 / arms
        degreesPerPoint = angularDistance / armPoints
        radiusPerPoint = (outerRadius - innerRadius) / armPoints
        chain = []
        for arm in range( arms ):
            startingAngle = arm * degreesPerArm
            chainArm = []
            for point in range( armPoints ):
                angle = radians( startingAngle + point * degreesPerPoint )
                radius = innerRadius + point * radiusPerPoint
                x = xCenter + cos( angle ) * radius
                y = yCenter + sin( angle ) * radius
                chainArm.append( (x,y) )
            chain += chainArm
            chainArm.reverse()
            chain += chainArm
        return chain

