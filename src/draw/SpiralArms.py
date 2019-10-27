from sandable import Sandable
from dialog import DialogInt, DialogFloat, DialogYesNo, DialogBreak
from Chains import Chains
from math import radians, sin, cos


class Sander(Sandable):
    """
### Draw clockwise and counter-clockwise spiral arms from the center

#### Hints

Smaller **CW and CCW angular distances** make drawings that look more like flowers.

#### Parameters

* **CW and CCW arms** - number of clockwise and counter-clockwise arms.
* **CW and CCW angular distances** - angular distance that each arm rotates by the time it gets to the
     **Outer radius**. Higher numbers (try 360) give tighter spirals while lower numbers (try 30) will
     look more like flower petals.  CW and CCW refer to the normal direction of the spirals if the **angular
     distance** is positive, but these directions can be reversed by using negative numbers.  Zero draws straight
     lines from the **Inner radius** to the **Outer radius**.
* **Points per arm** - the number of points used to draw each spiral arm.  Smaller numbers will look
     more like angular lines while larger numbers will generate curves.
* **Inner radius** and **Outer radius** - how far from the center the spiral should start and end.
* **X Center** and **Y Center** - where the center of the drawing will be relative to the table.
"""

    def __init__(self, width, length, ballSize, units):
        self.width = width
        self.length = length
        radius = min(width, length) / 2.0
        mRadius = max(width, length) / 2.0
        self.editor = [
            DialogInt("cwArms",          "CW arms",              default=12, min=1, max=120),
            DialogFloat("cwAngular",       "CW angular distance",  default=30.0, units="degrees"),
            DialogInt("ccwArms",         "CCW arms",             default=12, min=1, max=120),
            DialogFloat("ccwAngular",      "CCW angular distance", default=30.0, units="degrees"),
            DialogInt("points",          "Points per arm",       default=10, min=2),
            DialogYesNo("fitToTable",      "Fit to table"),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
            DialogFloat("innerRadius",     "Inner radius",         units=units, default=radius * 0.15, min=0.0, max=mRadius),
            DialogFloat("outerRadius",     "Outer radius",         units=units, default=radius, min=1.0, max=mRadius),
        ]

    def generate(self, params):
        chains = [
            self._arms(params.xCenter, params.yCenter, params.innerRadius, params.outerRadius, params.cwArms, -params.cwAngular, params.points),
            self._arms(params.xCenter, params.yCenter, params.innerRadius, params.outerRadius, params.ccwArms, params.ccwAngular, params.points)
        ]
        if params.fitToTable:
            chains = [Chains.circleToTable(c, self.width, self.length) for c in chains]
        return chains

    def _arms(self, xCenter, yCenter, innerRadius, outerRadius, arms, angularDistance, armPoints):
        degreesPerArm = 360.0 / arms
        degreesPerPoint = angularDistance / armPoints
        radiusPerPoint = (outerRadius - innerRadius) / armPoints
        chain = []
        for arm in range(arms):
            startingAngle = arm * degreesPerArm
            chainArm = []
            for point in range(armPoints):
                angle = radians(startingAngle + point * degreesPerPoint)
                radius = innerRadius + point * radiusPerPoint
                x = xCenter + cos(angle) * radius
                y = yCenter + sin(angle) * radius
                chainArm.append((x, y))
            chain += chainArm
            chainArm.reverse()
            chain += chainArm
        return chain
