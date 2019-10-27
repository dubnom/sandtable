from Sand import CLIPART_PATH
from sandable import Sandable, inchesToUnits
from dialog import DialogFile, DialogFloat, DialogInt, DialogBreak

import cam
from Chains import Chains


class Sander(Sandable):
    """
### Draw clipart images (currently only DXF is supported)

#### Hints

You have to browse through directories to find interesting things.
Filling the image is very cool.

Horizontal lines are used to "erase" the background. They are also used to hide the way the ball to creates
sections of the drawing that aren't connected to one-another.

#### Parameters

* **File Name** - name of the file to be drawn.  Files use a rudimentary file browser that supports
  directories.  Search through the directories to find interesting things to draw.
* **Number of Fill Iterations** - indicates how many shrunken-down drawings should be done inside the
  main image.  Each shrunken drawing is **Fill Decrement** away from the previous edge.  Details get
  lost as the fill image gets smaller. to completely fill in the image use higher numbers, the fill will
  automatically stop when it becomes too small (try 25).
* **Fill Decrement** - amount to shrink the outside image(s) by for the purpose of filling-in the drawing.
  The smaller the **Fill Decrement** is the tighter the lines are (try .25).
* **Width** and **Length** - how big the drawing should be. Probably not worth changing.
* **Starting locations** - where on the table the drawing should be drawn. Also normally not worth changing.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFile("filename",            "File Name",                default=CLIPART_PATH, filter='.dxf'),
            DialogInt("iterations",          "Number of Fill Iterations", default=0, min=0, max=60),
            DialogFloat("decrement",           "Fill Decrement",           units=units, default=0.5, min=0.0, max=inchesToUnits(2.0, units)),
            DialogFloat("ballSize",            "Ball Size",                units=units, default=ballSize, min=inchesToUnits(0.25, units)),
            DialogBreak(),
            DialogFloat("xOffset",             "X Origin",                 units=units, default=0.0),
            DialogFloat("yOffset",             "Y Origin",                 units=units, default=0.0),
            DialogFloat("width",               "Width (x)",                units=units, default=width, min=1.0, max=width*2),
            DialogFloat("length",              "Length (y)",               units=units, default=length, min=1.0, max=length*2),
        ]

    def generate(self, params):
        chains = []
        filename = params.filename
        if filename.endswith('.dxf'):
            cam.read_DXF(filename)
        elif filename.endswith('.svg'):
            cam.read_SVG(filename)
        else:
            return chains

        for layer in range((len(cam.boundarys)-1), -1, -1):
            if cam.toolpaths[layer] == []:
                path = cam.boundarys[layer]
            else:
                path = cam.toolpaths[layer]
            for segment in range(len(path)):
                chain = []
                for vertex in range(0, len(path[segment])):
                    x = path[segment][vertex][cam.X]
                    y = path[segment][vertex][cam.Y]
                    chain.append((x, y))
                chains.append(chain)

        chains = Chains.autoScaleCenter(chains, [(0.0, 0.0), (params.width, params.length)])

        if params.iterations:
            import shrinky
            newChains = chains
            for chain in shrinky.shrinky(chains, params.iterations, -params.decrement):
                newChains += chain
        else:
            newChains = chains

        return Chains.scanalize(newChains, params.xOffset, params.yOffset, params.width, params.length, 1.0 / params.ballSize)
