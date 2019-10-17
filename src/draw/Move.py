from Sand import *
from dialog import *
import mach


class Sander( Sandable ):
    """
### Move the ball to a new location

#### Hints

To avoid drawing over things, move the ball away!

#### Parameters

* **X and Y Origin** - location on the table to move the ball to.
"""

    def __init__( self, width, length ):
        try:
            with mach.mach() as e:
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

