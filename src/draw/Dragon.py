from Sand import *
from dialog import *
from Chains import *

class Dragon( Sandable ):
    """
### Dragon Fractal

#### Hint

Read the Wikipedia article on [Dragon Curves](http://en.wikipedia.org/wiki/Dragon_curve)

#### Parameters

* **Depth of fractility** - number of times that lines will be replaced with the dragon shape.
* **Auto-fit to table** - if this is set to "Yes" then the curve is automatically stretched
  in both dimensions (width and length) to make it fit the table. If this is set to "No" then the
  curve is scaled evenly to be as big as possible without distortion.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
""" 

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "depth",               "Depth of fractility",      default = 8, min = 1, max = 14 ),
            DialogYesNo( "fit",                 "Auto-fit to table",        default = False ),
            DialogBreak(),
            DialogFloat( "xOffset",             "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",             "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",               "Width (x)",                units = "inches", default = width ),
            DialogFloat( "length",              "Length (y)",               units = "inches", default = length ),
        ]

    def generate( self, params ):
        self.x = 0.0
        self.y = 0.0
        self.dx = 1.0
        self.dy = 0.0
        self.chain = [ (self.x, self.y) ]
        self.dragon( params.depth, 0 )
        bounds = [(params.xOffset,params.yOffset),(params.xOffset+params.width,params.yOffset+params.length)]
        if params.fit:
            return Chains.fit( [self.chain], bounds )
        return Chains.autoScaleCenter( [self.chain], bounds )
    
    def dragon( self, level, turn ):
        if level == 0:
            self.x += self.dx
            self.y += self.dy
            self.chain.append( (self.x, self.y) )
        else:
            self.dragon( level - 1, 0 )
            if turn:
                self.dx, self.dy = self.dy, -self.dx
            else:
                self.dx, self.dy = -self.dy, self.dx
            self.dragon( level - 1, 1 )
