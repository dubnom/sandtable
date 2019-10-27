from sandable import Sandable
from dialog import DialogInt, DialogBreak, DialogFloat


class Sander(Sandable):
    """
### Draw cross-hatched rectangles

#### Parameters

* **Columns** - number of vertical columns to have.
* **Rows** - number of horizontal rows to have.
* **X Lines** - number of vertical cross-hatches to have in a box.
* **Y Lines** - number of horizontal cross-hatches to have in a box.
* **X and Y Origin** - lower left corner of the drawing. Usually not worth changing.
* **Width** and **Length** - how big the figure should be. Probably not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogInt("xSquares",        "Columns (X)",              default=2, min=1, max=40),
            DialogInt("ySquares",        "Rows (Y)",                 default=2, min=1, max=40),
            DialogInt("xLines",          "X Fill Lines",             default=4, min=1, max=16),
            DialogInt("yLines",          "Y Fill Lines",             default=4, min=1, max=16),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",                 units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",                 units=units, default=0.0),
            DialogFloat("width",           "Width",                    units=units, default=width, min=1.0, max=width),
            DialogFloat("length",          "Length",                   units=units, default=length, min=1.0, max=length),
        ]

    def generate(self, params):
        chain = []
        xSize = params.width / params.xSquares
        ySize = params.length / params.ySquares
        xSpacing = xSize / params.xLines
        ySpacing = ySize / params.yLines

        eps = 0.01

        xSquare = ySquare = 0
        xSquareDir = 1.0
        x = y = 0
        while(ySquare < params.ySquares):
            xLow = xSquare * xSize
            xHigh = xLow + xSize
            yLow = ySquare * ySize
            yHigh = yLow + ySize
            if x <= xLow + eps:
                xDir, x = 1.0, xLow
            else:
                xDir, x = -1.0, xHigh
            if y <= yLow + eps:
                yDir, y = 1.0, yLow
            else:
                yDir, y = -1.0, yHigh
            isHorizontal = (xSquare + ySquare) % 2
            xSquare += xSquareDir
            if xSquare < 0 or xSquare == params.xSquares:
                xSquare -= xSquareDir
                xSquareDir *= -1.0
                ySquare += 1.0
            xLow, xHigh, yLow, yHigh = xLow - eps, xHigh + eps, yLow - eps, yHigh + eps
            if isHorizontal:
                while yLow <= y <= yHigh:
                    chain.append((x, y))
                    x += xDir * xSize
                    xDir *= -1.0
                    chain.append((x, y))
                    y += yDir * ySpacing
            else:
                while xLow <= x <= xHigh:
                    chain.append((x, y))
                    y += yDir * ySize
                    yDir *= -1.0
                    chain.append((x, y))
                    x += xDir * xSpacing

        return [chain]
