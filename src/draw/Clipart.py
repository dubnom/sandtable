from builtins import range
from os import listdir
from Sand import *
from dialog import *

import cam
from Chains import *

class Clipart( Sandable ):
    """
        <h3>Draw clipart images (currently only DXF is supported)</h3>

        Hint: You have to browse through directories to find interesting things.<br>
        Hint: Filling the image is very cool. <br>

        <p>Horizontal lines are used to "erase" the background. They are also used to hide the way the ball to creates
        sections of the drawing that aren't connected to one-another.</p>

        <ul>
         <li><i>File Name</i> - name of the file to be drawn.  Files use a rudimentary file browser that supports
             directories.  Search through the directories to find interesting things to draw.
         <li><i>Number of Fill Iterations</i> - indicates how many shrunken-down drawings should be done inside the
             main image.  Each shrunken drawing is </i>Fill Decrement</i> away from the previous edge.  Details get
             lost as the fill image gets smaller. to completely fill in the image use higher numbers, the fill will
             automatically stop when it becomes too small (try 25).
         <li><i>Fill Decrement</i> - amount to shrink the outside image(s) by for the purpose of filling-in the drawing.
             The smaller the <i>Fill Decrement</i> is the tighter the lines are (try .25).
         <li><i>Width</i> and <i>Length</i> - how big the drawing should be. Probably not worth changing.
         <li><i>Starting locations</i> - where on the table the drawing should be drawn. Also normally not worth changing.
        </ul>"""

    def __init__( self, width, length ):
        cfg = LoadConfig()
        self.editor = [
            DialogFile(  "filename",            "File Name",                default = CLIPART_PATH, filter = '.dxf' ),
            DialogInt(   "iterations",          "Number of Fill Iterations",default = 0, min = 0, max = 200 ),
            DialogFloat( "decrement",           "Fill Decrement",           units = "inches", default = 0.5, min = 0.0, max = 2.0 ),
            DialogFloat( "ballSize",            "Ball Size",                units = "inches", default = cfg.ballSize, min = 0.25 ),
            DialogBreak(),
            DialogFloat( "xOffset",             "X Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "yOffset",             "Y Origin",                 units = "inches", default = 0.0 ),
            DialogFloat( "width",               "Width (x)",                units = "inches", default = width, min = 1.0, max = 1000.0 ),
            DialogFloat( "length",              "Length (y)",               units = "inches", default = length, min = 1.0, max = 1000.0 ),
        ]

    def generate( self, params ):
        chains = []
        filename = params.filename
        if filename.endswith( '.dxf' ):
            cam.read_DXF( filename )
        elif filename.endswith( '.svg' ):
            cam.read_SVG( filename )
        else:
            return chains

        for layer in range((len(cam.boundarys)-1),-1,-1):
            if cam.toolpaths[layer] == []:
                path = cam.boundarys[layer]
            else:
                path = cam.toolpaths[layer]
            for segment in range(len(path)):
                chain = []
                for vertex in range(0,len(path[segment])):
                    x = path[segment][vertex][cam.X]
                    y = path[segment][vertex][cam.Y]
                    chain.append( (x,y) )
                chains.append( chain )
        
        chains = Chains.autoScaleCenter( chains, [(0.0,0.0),(params.width,params.length)] )

        if params.iterations:
            import shrinky
            newChains = chains
            for chain in shrinky.shrinky( chains, params.iterations, -params.decrement ) :
                newChains += chain
        else:
            newChains = chains

        return Chains.scanalize( newChains, params.xOffset, params.yOffset, params.width, params.length, 1.0 / params.ballSize )

