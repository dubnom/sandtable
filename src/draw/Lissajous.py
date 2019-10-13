from math import radians, sin, cos, floor, fabs
from Sand import *
from dialog import *
    
class Lissajous( Sandable ):
    """
        <h3>Pretty curves that describe complex harmonic motion</h3>

        Hint: Check out the Wikipedia description of the <a href="http://en.wikipedia.org/wiki/Lissajous_curve">Lissajous Curve</a>

        <ul>
         <li><i>A and B Frequencies</i> - the ratio that describes the harmonic is very sensitive to A/B.<br>
             If <i>A</i> == <i>B</i> and <i>Delta</i> == 0 then the ratio is 1 and a line is drawn.<br>
             If <i>A</i> == <i>B</i> and <i>Delta</i> == 90 an elipse will be drawn.<br>
             Setting <i>A</i>=1 and <i>B</i>=2 will draw a figure eight.<br>
             Play with the numbers to make pretty looping patterns (try <i>A</i>=2 and <i>B</i>=5).
         <li><i>Delta</i> - is the X angular offset.  Try setting <i>Delta</i> to one of these numbers: 0, 30, 45, 90.
             Other numbers are interesting as well.
         <li><i>X and Y Center</i> - where the center of the figure will be relative to the table. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the figure should be. Probably not worth changing.
        </ul>"""

    EPSILON = 1E-4

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "aFreq",           "A Frequency",          default = 8.0, min = 0.001, max = 100.0, rRound=0 ),
            DialogFloat( "bFreq",           "B Frequency",          default = 9.0, min = 0.001, max = 100.0, rRound=0 ),
            DialogFloat( "delta",           "Delta",                units = "degrees", default = 0.0 ),
            DialogBreak(),
            DialogFloat( "xCenter",         "X Center",             units = "inches", default = width / 2.0 ),
            DialogFloat( "yCenter",         "Y Center",             units = "inches", default = length / 2.0 ),
            DialogFloat( "width",           "Width (x)",            units = "inches", default = width, min = 1.0, max = 1000.0 ),
            DialogFloat( "length",          "Length (y)",           units = "inches", default = length, min = 1.0, max = 1000.0 ),
        ]

    def generate( self, params ):
        xScale = params.width / 2.0 
        yScale = params.length / 2.0
        res = 0.25
        
        chain = []
        for p in range( 10000 ):
            xPoint = params.xCenter + xScale * sin( radians( res * p * params.aFreq + params.delta)) 
            yPoint = params.yCenter + yScale * sin( radians( res * p * params.bFreq ))
            chain.append( (xPoint, yPoint) )
            if len(chain) > 4 and self._closeEnough( chain[0], chain[-2] ) and self._closeEnough( chain[1], chain[-1] ):
                break;

        return [chain]

    def _closeEnough( self, p1, p2 ):
        return fabs( p1[0] - p2[0] ) < self.EPSILON and fabs( p1[1] - p2[1] ) < self.EPSILON

