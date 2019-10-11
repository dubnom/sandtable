from math import sqrt, radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Fermat( Sandable ):
    """
        <h3>Fermat spiral (with a yin/yang inside)</h3>

        <ul>
         <li><i>Radius</i> - how far from the center the spiral should end.
         <li><i>Turns</i> - number of lines in each arm of the spiral.
         <li><i>Starting angle</i> - the angle the spiral starts at. The default of 0.0 starts to the right of center.
         <li><i>Sample rate</i> - how frequently points are calculated around the spiral.  Smaller numbers create rounder
             spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
             121 to get a rotating triangle; 74 makes a rotating pentagon.
         <li><i>Fill</i> - draw lines between points of each subsequent spiral arm. This creates a fully
             filled-in spiral that looks pretty neat in sand.
         <li><i>X Center</i> and <i>Y Center</i> - where the center of the spiral will be relative to the table.
        </ul>"""

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "radius",          "Radius",               units = "inches", default = min(width,length)/2, min = 1.0, max = max(width,length)*2.0 ),
            DialogFloat( "turns",           "Turns",                default = 10.0, min = .1, max = 200.0 ),
            DialogFloat( "angleStart",      "Starting angle",       units = "degrees" ),
            DialogFloat( "angleRate",       "Sample rate",          units = "degrees", min = 1, default = 5.0 ),
            DialogYesNo( "fill",            "Fill",                 default = False ),
            DialogYesNo( "fitToTable",      "Fit to table"          ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
        ]

    def generate( self, params ):
        xCenter = params.xCenter
        yCenter = params.yCenter
        
        points = int( params.turns * 360.0 / params.angleRate)
        size = params.radius / sqrt( params.turns * 360.0 )
        
        chain1, chain2 = [], []
        for point in xrange( points, 0, -1 ):
            angle = point * params.angleRate
            radius = size * sqrt( angle )
            angle = radians( params.angleStart + angle )
            chain1.append( (xCenter + cos( angle ) * radius, yCenter + sin( angle ) * radius ) )
            chain2.append( (xCenter - cos( angle ) * radius, yCenter - sin( angle ) * radius ) )
    
        if params.fill:
            results = []
            for p1, p2 in zip( chain1, chain2 ):
                results.append( p1 )
                results.append( p2 )
        else:
            results = chain1 + chain2[::-1]

        if params.fitToTable:
            results = Chains.circleToTable( results, TABLE_WIDTH, TABLE_LENGTH )

        return [results]