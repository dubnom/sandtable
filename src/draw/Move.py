from Sand import *
from dialog import *
import tinyg as emc

class Move( Sandable ):
    """
        <h3>Move the ball to a new location</h3>

        Hint: To avoid drawing over things, move the ball away!

        <ul>
         <li><i>X and Y Origin</i> - location on the table to move the ball to.
        </ul>"""

    def __init__( self, width, length ):
        try:
            with emc.emc() as e:
                x,y = e.getPosition()
        except:
            x,y = 0.,0.

        self.editor = [
            DialogFloat( "xOffset",         "X Origin",                 units = "inches", default = x ),
            DialogFloat( "yOffset",         "Y Origin",                 units = "inches", default = y ),
        ]

    def generate( self, params ):
        point = (params.xOffset, params.yOffset)
        return [[point, point]]

