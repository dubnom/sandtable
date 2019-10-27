from math import sin, exp, radians
from sandable import Sandable
from dialog import DialogFloat, DialogInt, DialogBreak


class Sander(Sandable):
    """
### Gradually decaying interaction between two two-dimensional pendulums.

Harmonographs are curves that would be created in the physical world if a pen pendulum
was drawing over a drawing surface pendulum. Both pendulums have different X and Y frequencuies and phases.

#### Hints

The harmonograph generates curves similar to Lissajous but more complex
because there are two Lissajous figures that interact with one another and the
curves are gradually decaying, similar to a pendulum.

#### Parameters

* **Decay Rate** - the rate at which the pendulum amplitudes decay for ever point drawn.  Lower numbers will make
     the pendulums decay slower and therefore draw lines that are closer together. Higher numbers would do the oposite.
* **Number of Steps** - the number of points used to draw the harmonograph.  More points will allow the pendulums
     to decay closer to the center.
* **Frequencies** - frequencies of the "pen" (X1, Y1) and the "surface" (X2, Y2).  Smaller numbers yield simpler
     images.  Non-integers yield drawings that look more like scribbles or freeform.
* **Amplitudes** - amplitudes indicate the amount of "energy" in each pendulum axis. Higher numbers
     mean that the pendulums are swinging over a larger area. The amplitudes do not change the frequencies, and
     amplitudes decay over time.
* **Phases** - phases indicate the angular offsets between each of the frequencies. When all of the phases are 0,
     the frequencies are all "in-phase", or directly related to one another.  Changing the phase changes this relationship
     and tends to skew different portions of the harmonograph curve.  Try playing with different numbers to get interesting
     variations.
* **X and Y Center** - the center of drawing. Usually these should be left alone.

#### Examples

Description | Frequencies | Amplitudes | Phases
--- | --- | --- | ---
Clover | 2, 10, 6, 12 | 9, 9, 4, 4 | 0, 0, 0, 0
Race Track | 2, 3, 6, 5 | 9, 9, 4, 4 | 0, 0, 0, 0
Butterfly | 1, 3, 2, 4 | 9, 9, 4, 4 | 0, 0, 0, 0
Eight | 5, 3, 2, 5 | 9, 9, 4, 4 | 0, 0, 0, 0
Squished Eight | 5, 3, 2, 5 | 9, 9, 4, 4 | 30, 0, 0, 0
Ellipse | 1, 1, 1, 1 | 9, 9, 4, 4 | 90, 0, 0, 0
Mouth | 1, 1, 2, 1 | 9, 9, 4, 4 | 90, 0, 0, 0
Infinity | 1, 1, 2, 1 | 9, 9, 4, 4 | 0, 0, 0, 0
"""

    def __init__(self, width, length, ballSize, units):
        self.editor = [
            DialogFloat("decay",           "Decay Rate",           default=0.0001, min=.00000001),
            DialogInt("steps",           "Number of Steps",      default=1000, min=1000, max=20000),
            DialogFloat("f1",              "X1 Frequency",         default=5.0, min=0.1, max=30.0, rRound=0),
            DialogFloat("f2",              "X2 Frequency",         default=10.0, min=0.1, max=30.0, rRound=0),
            DialogFloat("f3",              "Y1 Frequency",         default=7.0, min=0.1, max=30.0, rRound=0),
            DialogFloat("f4",              "Y2 Frequency",         default=12.0, min=0.1, max=30.0, rRound=0),
            DialogFloat("a1",              "X1 Amplitude",         units=units, default=width / 4.0, min=0.0),
            DialogFloat("a2",              "X2 Amplitude",         units=units, default=width / 4.0, min=0.0),
            DialogFloat("a3",              "Y1 Amplitude",         units=units, default=length / 4.0, min=0.0),
            DialogFloat("a4",              "Y2 Amplitude",         units=units, default=length / 4.0, min=0.0),
            DialogFloat("p1",              "X1 Phase",             units="degrees", default=0.0, min=0.0, max=180.0, rRound=0),
            DialogFloat("p2",              "X2 Phase",             units="degrees", default=0.0, min=0.0, max=180.0, rRound=0),
            DialogFloat("p3",              "Y1 Phase",             units="degrees", default=0.0, min=0.0, max=180.0, rRound=0),
            DialogFloat("p4",              "Y2 Phase",             units="degrees", default=0.0, min=0.0, max=180.0, rRound=0),
            DialogBreak(),
            DialogFloat("xCenter",         "X Center",             units=units, default=width / 2.0),
            DialogFloat("yCenter",         "Y Center",             units=units, default=length / 2.0),
        ]

    def generate(self, params):
        chain = []
        xCenter = params.xCenter
        yCenter = params.yCenter

        decay = params.decay

        (a1, a2, a3, a4) = (params.a1, params.a2, params.a3, params.a4)
        (f1, f2, f3, f4) = (radians(params.f1), radians(params.f2), radians(params.f3), radians(params.f4))
        (p1, p2, p3, p4) = (radians(params.p1), radians(params.p2), radians(params.p3), radians(params.p4))

        for t in range(params.steps):
            dk = exp(-decay * t)
            x = xCenter + a1 * sin(t * f1 + p1) * dk + a2 * sin(t * f2 + p2) * dk
            y = yCenter + a3 * sin(t * f3 + p3) * dk + a4 * sin(t * f4 + p4) * dk
            chain.append((x, y))

        return [chain]
