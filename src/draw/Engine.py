from math import sqrt, radians, sin, cos
from Sand import *
from dialog import *
from Chains import *

class Engine( Sandable ):
    """
        <h3>Engine-Turned patterns</h3>

        <ul>
         <li><i>Rows</i> and </i>Columns</i> - number of rows and columns to create the engine-turned pattern with.
         <li><i>Lines per Inch</i> - number of lines drawn within an inch of the spiral.
             Changing this can make the lines closer together (try a number like 10) or farther apart (try 0.5).
         <li><i>Sample Rate</i> - how frequently points are calculated around the spiral.  Smaller numbers create rounder
             spirals while larger numbers create interesting shapes.  Try 120 to get a triangle;
             121 to get a rotating triangle; 74 makes a rotating pentagon.
         <li><i>Size Modifier</i> - smaller numbers decrease the size of the spiral, larger numbers increase the size.
         <li><i>X Corner<i> and <i>Y Corner</i> - lower left corner to start the pattern.
         <li><i>Width<i> and <i>Length<i> - size of the pattern (spirals can go outside of the bounds).
        </ul>
    """

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "rows",            "Rows",                 default=int(length/2), min=1, max=length ),
            DialogInt(   "cols",            "Columns",              default=int(width/2), min=1, max=width ),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default=1.0, min=0.1, max=15.0 ),
            DialogFloat( "angleRate",       "Sample Rate",          units="degrees", default=15.0, min=-360.0, max=360.0 ),
            DialogFloat( "sizeModifier",    "Size Modifier",        units="percent", default=1., min=.75, max=1.25 ),
            DialogBreak(),
            DialogFloat( "xCorner",         "X Corner",             units="inches", default=0.0, min=0.0, max=width, randRange=(0.,0.) ),
            DialogFloat( "yCorner",         "Y Corner",             units="inches", default=0.0, min=0.0, max=length, randRange=(0.,0.) ),
            DialogFloat( "width",           "Width",                units="inches", default=width, min=1.0, max=width, randRange=(width,width) ),
            DialogFloat( "length",          "Length",               units="inches", default=length, min=1.0, max=length, randRange=(length,length) ),
        ]

    def generate( self, params ):
        if not params.angleRate:
            params.angleRate=15.0

        radius = min(params.width / params.cols, params.length / params.rows) * sqrt(2.0) * .5 * params.sizeModifier
        points = int( (360.0 / abs(params.angleRate)) * params.linesPerInch * radius)
        point360 = 360.0 / abs( params.angleRate )
        angleOffset = ((points-1) * params.angleRate - 90) % 360
        rowSize, colSize = params.length / params.rows, params.width / params.cols
        rowHalf, colHalf = rowSize / 2, colSize / 2

        chains = []
        for row in range(params.rows):
            for col in range(params.cols):
                rev = params.cols-col-1 if row%2 else col
                xCenter = params.xCorner + rev * colSize + colHalf
                yCenter = params.yCorner + row * rowSize + rowHalf
                chain = []
                for point in xrange( points ):
                    angle = radians( point * params.angleRate - angleOffset)
                    r = radius * (point / float(points))
                    x = xCenter + cos( angle ) * r
                    y = yCenter + sin( angle ) * r
                    chain.append( (x,y) )
                if row%2:
                    if rev-1 >= 0:
                        chain.append( (x - colSize,y) )
                elif col+1 < params.cols:
                    chain.append( (x + colSize,y) )
                chains.append(chain)

        return chains