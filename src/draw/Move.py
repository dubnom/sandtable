from sandable import Sandable
from dialog import DialogFloat
import mach


class Sander(Sandable):
    """
### Move the ball to a new location

#### Hints

To avoid drawing over things, move the ball away!

#### Parameters

* **X and Y Origin** - location on the table to move the ball to.
"""

    def __init__(self, width, length, ballSize, units):
        try:
            with mach.mach() as e:
                x, y = e.getStatus()['pos']
        except Exception:
            x, y = 0., 0.

        self.editor = [
            DialogFloat("xOffset",         "X Origin",                 units=units, default=x),
            DialogFloat("yOffset",         "Y Origin",                 units=units, default=y),
        ]

    def generate(self, params):
        point = (params.xOffset, params.yOffset)
        return [[point, point]]
