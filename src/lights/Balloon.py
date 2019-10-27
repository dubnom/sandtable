from Sand import Ledable
from dialog import DialogInt, DialogFloat
import random


class BalloonData(object):
    position = 0
    size = 0
    growthRate = 0
    color = (0, 0, 0)
    speed = 0
    accel = 0
    accCount = 0


class Lighter(Ledable):
    def __init__(self, cols, rows):
        self.editor = [
            DialogInt("balloons",     "Number of Balloons",       default=7, min=1, max=15),
            DialogInt("minSize",      "Minimum Size",             units="pixels", default=1, min=1, max=min(cols, rows)),
            DialogInt("maxSize",      "Maximum Size",             units="pixels", default=min(cols, rows)/4., min=1, max=min(cols, rows)),
            DialogFloat("maxSpeed",     "Maximum Speed",            units="pixels/second", default=10., min=0.01, max=min(cols, rows)),
        ]

    def generator(self, leds, cols, rows, params):
        self.leds = leds
        self.params = params
        end = leds.count
        balloons = [self._newBalloon() for i in range(params.balloons)]

        while True:
            leds.clear()
            for i, b in enumerate(balloons):
                for delta in range(0, int(b.size+1)):
                    color = leds.RGBDim(b.color, 1. - (delta/b.size))
                    leds.set(int(b.position+delta) % end, color)
                    leds.set(int(b.position-delta) % end, color)
                b.position = (b.position + b.accel) % end
                b.accCount -= 1
                if b.accCount <= 0:
                    b.accel, b.accCount = self._randomAcceleration()
                b.size += b.growthRate
                if b.size > params.maxSize:
                    b.growthRate = -self._randomGrowthRate()
                elif b.size < params.minSize:
                    b.growthRate = self._randomGrowthRate()
            yield True

    def _newBalloon(self):
        b = BalloonData()
        b.position = random.randint(0, self.leds.count)
        b.size = random.uniform(self.params.minSize, self.params.maxSize)
        b.growthRate = self._randomGrowthRate()
        b.color = self.leds.RGBRandomBetter()
        b.speed = random.uniform(-self.params.maxSpeed, self.params.maxSpeed)
        b.accel, b.accCount = self._randomAcceleration()
        return b

    def _randomAcceleration(self):
        return (random.uniform(-1., 1.), random.randint(10, 100))

    def _randomGrowthRate(self):
        return .1 * random.random() + .01
