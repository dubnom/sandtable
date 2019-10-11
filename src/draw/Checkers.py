from Sand import *
from dialog import *

class Checkers( Sandable ):
    """
        <h3>Draw cross-hatched rectangles</h3>

        <ul>
         <li><i>Columns</i> - number of vertical columns to have.
         <li><i>Rows</i> - number of horizontal rows to have.
         <li><i>X Lines</i> - number of vertical cross-hatches to have in a box.
         <li><i>Y Lines</i> - number of horizontal cross-hatches to have in a box.
         <li><i>X and Y Origin</i> - lower left corner of the drawing. Usually not worth changing.
         <li><i>Width</i> and <i>Length</i> - how big the figure should be. Probably not worth changing.
        </ul>"""

    def __init__( self, width, length ):
        self.editor = [
            DialogInt(   "xSquares",        "Columns (X)",              default = 2, min = 1, max = width ),
            DialogInt(   "ySquares",        "Rows (Y)",                 default = 2, min = 1, max = length ),
            DialogInt(   "xLines",          "X Lines",                  default = 4, min = 1, max = 16 ),
            DialogInt(   "yLines",          "Y Lines",                  default = 4, min = 1, max = 16 ),
            DialogBreak(),
            DialogFloat( "xOffset",         "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",         "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",           "Width",                    units = "inches", default = width, min = 1.0, max = width ),
            DialogFloat( "length",          "Length",                   units = "inches", default = length, min = 1.0, max = length ),
        ]

    def generate( self, params ):
        chain = []
        xSize = params.width / params.xSquares
        ySize = params.length / params.ySquares
        xSpacing = xSize / params.xLines
        ySpacing = ySize / params.yLines
        
        eps = 0.01
        
        xSquare = ySquare = 0
        xSquareDir = 1.0
        x = y = 0
        while( ySquare < params.ySquares ):
            xLow    = xSquare * xSize
            xHigh   = xLow + xSize
            yLow    = ySquare * ySize
            yHigh   = yLow + ySize 
            if x <= xLow + eps: xDir, x = 1.0, xLow
            else:               xDir, x = -1.0, xHigh
            if y <= yLow + eps: yDir, y = 1.0, yLow
            else:               yDir, y = -1.0, yHigh
            isHorizontal = (xSquare + ySquare ) % 2
            xSquare += xSquareDir
            if xSquare < 0 or xSquare == params.xSquares:
                xSquare -= xSquareDir
                xSquareDir *= -1.0
                ySquare += 1.0
            xLow, xHigh, yLow, yHigh = xLow - eps, xHigh + eps, yLow - eps, yHigh + eps
            if isHorizontal:
                while yLow <= y <= yHigh:
                    chain.append( (x, y) )
                    x += xDir * xSize
                    xDir *= -1.0
                    chain.append( (x, y) )
                    y += yDir * ySpacing
            else:
                while xLow <= x <= xHigh:
                    chain.append( (x, y) )
                    y += yDir * ySize
                    yDir *= -1.0
                    chain.append( (x, y) )
                    x += xDir * xSpacing

        return [chain]


