from math import radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Rose( Sandable ):
    """
        <h3>Draw rose curves (pretty flowerlike drawings)</h3>

        Hint: Read the Wikipedia article on <a href="http://en.wikipedia.org/wiki/Rose_(mathematics)">Rose (mathematics)</a>

        <ul>
         <li><i>Petals</i> - number of petals in the flower.
         <li><i>Starting angle</i> - amount to rotate the flower.
         <li><i>Shift angle</i> - amount to rotate each subsequent petal. 
         <li><i>Sample rate</i> - how frequently to draw a point when going around the flower.
         <li><i>Lines per Inch</i> - number of flowers to draw per inch. 
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the flower will be relative to the table.
         <li><i>Inner radius</i> and <i>Outer radius</i> - how far from the center the should start and end.
        </ul>"""

    def __init__( self, width, length ):
        radius = min(width,length) / 2.0
        mRadius = max(width,length) / 2.0
        self.editor = [
            DialogFloat( "petals",          "Petals",               default = 7.0, min = 0.001, max = 45.0 ),
            DialogFloat( "angleStart",      "Starting angle",       units = "degrees", min = -180., max = 180. ),
            DialogFloat( "angleShift",      "Shift angle",          units = "degrees", default = 0.0, min = -10.0, max = 10.0 ),
            DialogFloat( "angleRate",       "Sample rate",          units = "degrees", default = 3.0, min = 1.0, max = 10.0 ),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default = 1.0, min = 0.001, max = 16.0 ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
            DialogFloat( "innerRadius",     "Inner radius",         units = "inches", default = radius * .15, min = 0.0, max = mRadius ),
            DialogFloat( "outerRadius",     "Outer radius",         units = "inches", default = radius, min = 1.0, max = mRadius ),
        ]

    def generate( self, params ):
        chain = []
        if params.innerRadius > params.outerRadius:
            params.innerRadius, params.outerRadius = params.outerRadius, params.innerRadius
        if params.angleRate:
            xCenter = params.xCenter
            yCenter = params.yCenter
            k = params.petals / 2.0

            thickness = params.outerRadius - params.innerRadius
            lines = int( thickness * params.linesPerInch )
            points = int( 360.0 / params.angleRate )
            angleStart = radians( params.angleStart )
            for line in xrange( lines ):
                inRadius = params.innerRadius
                outRadius = thickness * float(line) / float(lines)
                for point in xrange( points ):
                    angle   = radians( point * params.angleRate )
                    radius  = inRadius + outRadius * abs(sin( k * angle ))
                    angle += angleStart
                    x = xCenter + (cos( angle ) * radius)
                    y = yCenter + (sin( angle ) * radius)
                    chain.append( (x,y) )
                angleStart += radians( params.angleShift )
        if params.fitToTable:
            chain = Chains.circleToTable( chain, TABLE_WIDTH, TABLE_LENGTH )
        return [chain]


