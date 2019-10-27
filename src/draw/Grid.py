from sandable import Sandable
from dialog import DialogFloat, DialogBreak


class Sander(Sandable):
    """
### Draw horizontal and/or vertical lines

#### Hints

This method is useful for "erasing" the table.

#### Parameters

* **X and Y Spacing** - amount of space between veritcal **(X)** and horizontal **(Y)** lines.
   The smaller the numbers the closer the lines will be to one another (try 0.5).  Larger spacing doesn't
   "erase" as well but is done with larger number (try 3.0).
   If either number is set to 0 or left blank, that set of lines will be omitted.
* **X and Y Origin** - lower lefthand corner of the grid. Usually not worth changing.
* **Width** and **Length** - how big the grid should be. Probably not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("xSpacing",        "X Spacing (0 for none)",   units=units, default=0.0, min=0., max=width),
            DialogFloat("ySpacing",        "Y Spacing (0 for none)",   units=units, default=ballSize, min=0., max=length),
            DialogBreak(),
            DialogFloat("xOffset",         "X Origin",                 units=units, default=0.0),
            DialogFloat("yOffset",         "Y Origin",                 units=units, default=0.0),
            DialogFloat("width",           "Width",                    units=units, default=width, min=1.0, max=1000.0),
            DialogFloat("length",          "Length",                   units=units, default=length, min=1.0, max=1000.0),
        ]

    def generate(self, params):
        chains = []

        # Horizontal lines
        if params.ySpacing > 0.0:
            chain = []
            y, line = 0.0, 0
            while y <= params.length:
                points = [(params.xOffset, params.yOffset + y), (params.xOffset + params.width, params.yOffset + y)]
                chain += points[::-1] if line % 2 else points
                y += params.ySpacing
                line += 1
            chains.append(chain)

        # Vertical lines
        if params.xSpacing > 0.0:
            chain = []
            if len(chains):
                chain.append((chains[-1][-1][0], params.yOffset + params.width))
                chain.append((params.xOffset, params.yOffset + params.width))
            x, line = 0.0, 0
            while x <= params.width:
                points = [(params.xOffset + x, params.yOffset), (params.xOffset + x, params.yOffset + params.length)]
                chain += points[::-1] if line % 2 else points
                x += params.xSpacing
                line += 1
            chains.append(chain)

        return chains
