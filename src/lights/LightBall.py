from Sand import LED_OFFSETS, TABLE_WIDTH, TABLE_LENGTH
import mach
from ledable import Ledable

class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = []

    def generator(self, leds, cols, rows, params):
        lights = [
            (-3, (64, 64, 64)),
            (-2, (128, 128, 128)),
            (-1, (192, 192, 192)),
            (0,  (255, 255, 255)),
            (1,  (192, 192, 192)),
            (2,  (128, 128, 128)),
            (3,  (64, 64, 64))]

        # Number of leds off the drawing surface (bottom left, top right)
        xOffset = LED_OFFSETS[0][0]
        xSlope = (cols - LED_OFFSETS[0][0] - LED_OFFSETS[1][0]) / TABLE_WIDTH
        yOffset = LED_OFFSETS[0][1]
        ySlope = (rows - LED_OFFSETS[0][1] - LED_OFFSETS[1][1]) / TABLE_LENGTH

        with mach.mach() as e:
            oldX, oldY = -1, -1
            while True:
                # Poll EMC for the location
                status = e.getStatus()
                x, y = status['pos'][0], status['pos'][1]
                if x != oldX or y != oldY:
                    col = min(int(xOffset + x * xSlope), cols)
                    row = min(int(yOffset + y * ySlope), rows)
                    leds.clear()
                    for offset, color in lights:
                        c = col + offset
                        if c >= 0 and c < cols:
                            leds.set(c, color)
                            leds.set(rows + 2 * cols - c - 1, color)
                        r = row + offset
                        if r >= 0 and r < rows:
                            leds.set(cols + rows - r - 1, color)
                            leds.set(2 * cols + rows + r, color)
                    oldX, oldY = x, y
                    yield True
                else:
                    yield False
