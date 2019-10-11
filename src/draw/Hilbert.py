from Sand import *
from dialog import *
from Chains import *

class Hilbert( Sandable ):
    """
        <h3>Hilbert Fractal</h3>

        Hint: Read the Wikipedia article on <a href="http://en.wikipedia.org/wiki/Hilbert_curve">Hilbert curves</a>

        <ul>
        <ul>
         <li><i>Depth of fractility</i> - number of times that lines will be replaced with the Hilbert shape.
         <li><i>Auto-fit to table</i> - if this is set to "Yes" then the curve is automatically stretched
             in both dimensions (width and length) to make it fit the table. If this is set to "No" then the
             curve is scaled evenly to be as big as possible without distortion.
         <li><i>X and Y Origin</i> - lower left corner of the drawing. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the figure should be. Probably not worth changing.
        </ul>"""

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "depth",               "Depth of fractility",      default = 2, min = 1, max = 7 ),
            DialogYesNo( "fit",                 "Auto-fit to table",        default = False ),
            DialogBreak(),
            DialogFloat( "xOffset",             "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",             "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",               "Width (x)",                units = "inches", default = width ),
            DialogFloat( "length",              "Length (y)",               units = "inches", default = length ),
        ]

    def generate( self, params ):
        self.chain = []
        xi = 1.0 #params.width
        xj = 0.0
        yi = 0.0
        yj = 1.0 #params.length
        self._hilbert( 0.0, 0.0, xi, xj, yi, yj, params.depth )
        bounds = [(params.xOffset,params.yOffset),(params.xOffset+params.width,params.yOffset+params.length)]
        if params.fit:
            return Chains.fit( [self.chain], bounds )
        return Chains.autoScaleCenter( [self.chain], bounds )

    def _hilbert( self, x0, y0, xi, xj, yi, yj, n ):
        if n <= 0:
            X = x0 + (xi + yi)/2
            Y = y0 + (xj + yj)/2
            self.chain.append( (X, Y) )
        else:
            self._hilbert( x0,               y0,               yi/2, yj/2, xi/2, xj/2, n - 1 )
            self._hilbert( x0 + xi/2,        y0 + xj/2,        xi/2, xj/2, yi/2, yj/2, n - 1 )
            self._hilbert( x0 + xi/2 + yi/2, y0 + xj/2 + yj/2, xi/2, xj/2, yi/2, yj/2, n - 1 )
            self._hilbert( x0 + xi/2 + yi,   y0 + xj/2 + yj,  -yi/2,-yj/2,-xi/2,-xj/2, n - 1 )
