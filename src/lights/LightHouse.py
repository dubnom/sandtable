from math import radians, sin, cos, fmod
from Sand import TABLE_WIDTH, TABLE_LENGTH
from dialog import DialogFloat, DialogColor
from ledable import Ledable


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.editor = [
            DialogFloat("xOffset",         "X Center",         units="inches", default=TABLE_WIDTH/2, min=0.0, max=TABLE_WIDTH),
            DialogFloat("yOffset",         "Y Center",         units="inches", default=TABLE_LENGTH/4, min=0.0, max=TABLE_LENGTH),
            DialogFloat("angleRate",       "Angle Rate",       units="degrees", default=5.0, min=1.0, max=30.0),
            DialogFloat("beamWidth",       "Beam Width",       units="degrees", default=30.0, min=4.0, max=90.0),
            DialogColor("color",           "Color",            default=(255, 255, 255)),
        ]

    def generator(self, leds, params):
        width, length = TABLE_WIDTH, TABLE_LENGTH
        cols, rows = self.cols, self.rows
        self.lights = [
            # Physical light location            Led range                            Reference
            (((0.0, 0.0), (width, 0.0)),         (cols*2+rows-1, cols+rows)),       # Bottom
            (((width, 0.0), (width, length)),    (cols+rows-1, cols)),              # Right
            (((0.0, length), (width, length)),   (0, cols-1)),                      # Top
            (((0.0, 0.0), (0.0, length)),        (cols*2+rows, cols*2+rows*2-1)),   # Left
        ]

        angle = 0.0
        dist = 1000.0
        beamWidth = params.beamWidth / 2.0
        end = (rows+cols)*2
        color = params.color
        def ray(a): return ((params.xOffset, params.yOffset), (params.xOffset+dist*cos(radians(a)), params.yOffset+dist*sin(radians(a))))

        while True:
            low = self._ledFromRay(ray(angle + beamWidth))
            high = self._ledFromRay(ray(angle - beamWidth))

            leds.clear()
            if low is None or high is None:
                yield False
            else:
                high = high+end if high < low else high
                while low <= high:
                    leds.set(low % end, color)
                    low += 1
                yield True

            angle = fmod(angle + params.angleRate, 360.0)

    def _ledFromRay(self, ray):
        for light in self.lights:
            point = self._lineIntersect(light[0], ray)
            if point:
                break
        if point:
            x, y = point[0], point[1]
            ledRange = light[1]
            if light[0][1][0] - light[0][0][0]:
                slope = x / (light[0][1][0] - light[0][0][0])
            else:
                slope = y / (light[0][1][1] - light[0][0][1])
            led = ledRange[0] + slope * (ledRange[1] - ledRange[0])
            return int(led)
        return None

    def _lineIntersect(self, line1, line2):
        xDiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        yDiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
        def det(a, b): return a[0] * b[1] - a[1] * b[0]

        div = det(xDiff, yDiff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x, y = det(d, xDiff) / div, det(d, yDiff) / div

        def within(l, offset, v): return ((l[0][offset] <= v <= l[1][offset]) or (l[0][offset] >= v >= l[1][offset]))

        if within(line1, 0, x) and within(line1, 1, y) and within(line2, 0, x) and within(line2, 1, y):
            return (x, y)
        return None
