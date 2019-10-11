from math import radians, sin
from Sand import *
from dialog import *
    
class Waves( Sandable ):
    """
        <h3>Draw waves</h3>

        Hint: Try changing the <i>Shift per line</i>

        <ul>
         <li><i>Wave Height</i> - height in inches of each of the waves.
         <li><i>Lines per Inch</i> - number of vertical lines of waves per inch.
         <li><i>Waves per Line</i> - number of waves per horizontal line.
         <li><i>Shift per Line</i> - amount to shift waves over each line.
         <li><i>Wave increment</i> - percent to increase/decrease number of waves for each line.
             Very small changes from a 100% yield large changes to the number of waves since
             the effect is cumulative for each line.
         <li><i>X and Y Origin</i> - lower left corner of the drawing. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the figure should be. Probably not worth changing.
        </ul>"""

    def __init__( self, width, length ):
        self.editor = [
            DialogFloat( "wHeight",          "Wave Height",          units = "inches", default = 1.0, min = 0.0, max = length ),
            DialogFloat( "linesPerInch",    "Lines per Inch",       default = 2.0, min = 0.001, max = 10.0 ),
            DialogFloat( "waves",           "Waves per Line",       default = 3.0, min = 0.0, max = 500.0 ),
            DialogFloat( "shift",           "Shift per Line",       units = "degrees", default = 5.0, min = 0.0 ),
            DialogFloat( "increment",       "Wave increment",       units = "percent", default = 100.0 ),
            DialogBreak(),
            DialogFloat( "xOffset",         "X Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",             units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width",                units = "inches", default = width, min = 1.0, max = 1000.0 ),
            DialogFloat( "length",          "Length",               units = "inches", default = length, min = 1.0, max = 1000.0 ),
        ]

    def generate( self, params ):
        xPerInch = 3 
        xCount = int( xPerInch * params.width )
        xScale = params.width / xCount
        xyScale = (360.0 * params.waves) / xCount
        yCount = int( params.length * params.linesPerInch )
        yScale = 1.0 / params.linesPerInch
        waveMultiplier = 1.0
        increment = params.increment * 0.01
        
        chains = []
        for y in range( 0, yCount ):
            chain = [] 
            for x in range( xCount ):
                xPoint = params.xOffset + x * xScale
                yPoint = params.yOffset + y * yScale + params.wHeight * sin( radians( waveMultiplier * x * xyScale + y * params.shift ))
                chain.append( (xPoint,yPoint) )
            if y % 2:
                chain.reverse()
            chains.append( chain )
            waveMultiplier *= increment 
        
        return chains

