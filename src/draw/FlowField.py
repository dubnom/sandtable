from math import ceil, cos, radians, sin, sqrt

from Chains import Chains
from dialog import DialogBreak, DialogFloat, DialogInt, DialogYesNo
from sandable import Sandable, inchesToUnits


DEFAULT_SEED_COUNT = 24
MIN_SEED_COUNT = 8
MAX_SEED_COUNT = 400

DEFAULT_STEPS_PER_LINE = 80
MIN_STEPS_PER_LINE = 20
MAX_STEPS_PER_LINE = 1000

DEFAULT_STEP_SIZE_INCHES = 0.16
MIN_STEP_SIZE_INCHES = 0.01
MAX_STEP_SIZE_INCHES = 0.5

DEFAULT_SIMPLIFY_SPACING_INCHES = 0.18
MAX_SIMPLIFY_SPACING_INCHES = 1.0

DEFAULT_FIELD_SCALE = 0.25
MIN_FIELD_SCALE = 0.01
MAX_FIELD_SCALE = 3.0

DEFAULT_ROTATION_DEGREES = 25.0
MIN_ANGLE_DEGREES = -180.0
MAX_ANGLE_DEGREES = 180.0

DEFAULT_PHASE_DEGREES = 0.0
DEFAULT_BIDIRECTIONAL = False

MIN_DRAW_DIMENSION_INCHES = 1.0
MAX_DRAW_DIMENSION = 1000.0

SEED_GRID_CENTER_OFFSET = 0.5
MIN_LENGTH_EPSILON = 1e-6
FIELD_MAGNITUDE_EPSILON = 1e-9

FIELD_Y_COS_SCALE = 1.31
FIELD_X_COS_SCALE = 0.87
FIELD_Y_SIN_SCALE = 1.17


class Sander(Sandable):
    """
### Draw flowing contour-like streamlines

#### Hints

Try changing **Field Scale** and **Rotation** first.

#### Parameters

* **Seed count** - how many initial streamlines are started.
* **Steps per line** - maximum points generated for each streamline.
* **Step size** - distance traveled at each integration step.
* **Simplify spacing** - minimum spacing between kept points after generation.
* **Field scale** - frequency of the underlying vector field.
* **Rotation** - rotates the field direction globally.
* **Phase** - shifts the trigonometric field for different patterns.
* **Bidirectional** - trace each streamline both forward and backward.
* **X and Y Origin** - lower-left corner of the active region.
* **Width and Length** - size of the active region.
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogInt("seeds", "Seed count", default=DEFAULT_SEED_COUNT, min=MIN_SEED_COUNT, max=MAX_SEED_COUNT),
            DialogInt("steps", "Steps per line", default=DEFAULT_STEPS_PER_LINE, min=MIN_STEPS_PER_LINE, max=MAX_STEPS_PER_LINE),
            DialogFloat("stepSize", "Step size", units=units, default=inchesToUnits(DEFAULT_STEP_SIZE_INCHES, units), min=inchesToUnits(MIN_STEP_SIZE_INCHES, units), max=inchesToUnits(MAX_STEP_SIZE_INCHES, units)),
            DialogFloat("simplify", "Simplify spacing", units=units, default=inchesToUnits(DEFAULT_SIMPLIFY_SPACING_INCHES, units), min=0.0, max=inchesToUnits(MAX_SIMPLIFY_SPACING_INCHES, units)),
            DialogFloat("scale", "Field scale", default=DEFAULT_FIELD_SCALE, min=MIN_FIELD_SCALE, max=MAX_FIELD_SCALE),
            DialogFloat("rotation", "Rotation", units="degrees", default=DEFAULT_ROTATION_DEGREES, min=MIN_ANGLE_DEGREES, max=MAX_ANGLE_DEGREES),
            DialogFloat("phase", "Phase", units="degrees", default=DEFAULT_PHASE_DEGREES, min=MIN_ANGLE_DEGREES, max=MAX_ANGLE_DEGREES),
            DialogYesNo("bidirectional", "Bidirectional", default=DEFAULT_BIDIRECTIONAL),
            DialogBreak(),
            DialogFloat("xOffset", "X Origin", units=units, default=0.0),
            DialogFloat("yOffset", "Y Origin", units=units, default=0.0),
            DialogFloat("width", "Width", units=units, default=width, min=inchesToUnits(MIN_DRAW_DIMENSION_INCHES, units), max=MAX_DRAW_DIMENSION),
            DialogFloat("length", "Length", units=units, default=length, min=inchesToUnits(MIN_DRAW_DIMENSION_INCHES, units), max=MAX_DRAW_DIMENSION),
        ]
        self.ballSize = ballSize

    def isRealtime(self):
        return False

    def _field(self, x, y, params):
        phase = radians(params.phase)
        # A smooth, deterministic vector field made from mixed trig waves.
        vx = sin((x + phase) * params.scale) + cos((y - phase) * params.scale * FIELD_Y_COS_SCALE)
        vy = cos((x - phase) * params.scale * FIELD_X_COS_SCALE) - sin((y + phase) * params.scale * FIELD_Y_SIN_SCALE)
        rot = radians(params.rotation)
        rx = vx * cos(rot) - vy * sin(rot)
        ry = vx * sin(rot) + vy * cos(rot)
        mag = sqrt(rx * rx + ry * ry)
        if mag < FIELD_MAGNITUDE_EPSILON:
            return (0.0, 0.0)
        return (rx / mag, ry / mag)

    def _inside(self, x, y, x0, y0, x1, y1):
        return x0 <= x <= x1 and y0 <= y <= y1

    def _trace(self, x, y, direction, params, x0, y0, x1, y1):
        chain = []
        for _ in range(params.steps):
            if not self._inside(x, y, x0, y0, x1, y1):
                break
            chain.append((x, y))
            vx, vy = self._field(x, y, params)
            x += direction * vx * params.stepSize
            y += direction * vy * params.stepSize
        return chain

    def generate(self, params):
        x0 = params.xOffset
        y0 = params.yOffset
        x1 = x0 + params.width
        y1 = y0 + params.length

        seeds = max(1, int(params.seeds))
        cols = max(1, int(sqrt(seeds * params.width / max(params.length, MIN_LENGTH_EPSILON))))
        rows = max(1, int(ceil(float(seeds) / cols)))
        x_step = params.width / cols
        y_step = params.length / rows

        chains = []
        for row in range(rows):
            for col in range(cols):
                if len(chains) >= seeds:
                    break
                x = x0 + (col + SEED_GRID_CENTER_OFFSET) * x_step
                y = y0 + (row + SEED_GRID_CENTER_OFFSET) * y_step
                forward = self._trace(x, y, 1.0, params, x0, y0, x1, y1)
                if params.bidirectional:
                    backward = self._trace(x, y, -1.0, params, x0, y0, x1, y1)
                    backward.reverse()
                    chain = backward[:-1] + forward if len(backward) > 1 else forward
                else:
                    chain = forward
                if len(chain) > 1:
                    chains.append(chain)
            if len(chains) >= seeds:
                break
        # Remove nearly-duplicate points to keep machining time practical.
        if params.simplify > 0.0:
            chains = Chains.deDistances(chains, epsilon=params.simplify)
        chains = [chain for chain in chains if len(chain) > 1]
        return Chains.scanalize(chains, params.xOffset, params.yOffset, params.width, params.length, 1.0 / self.ballSize)
    