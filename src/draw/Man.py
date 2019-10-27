from math import radians, sin, cos
from sandable import Sandable, inchesToUnits
from dialog import DialogFloat, DialogBreak


class Sander(Sandable):
    """
### Draw a stick-figure man

This drawing method is intended to be used for animated movies but can also be used to draw a single stick-figure.

#### Hints

Everything is referenced to the figure's neck location.

#### Parameters

* **X and Y Neck locations** - where on the table to draw the neck. Every other part of the stick-figure
  is drawn relative to the neck.
* **Angles** - Shoulders and thighs come straight out of the body at a right-angle when set to 0 degrees.
  Positive angles point the extremity down while negative angles point it up.
  **Elbow and Calf Angles** are relative to their attached shoulder or thigh.  When these angles
  are set to 0, the extremity points straight out in the same direction of what they are attached to.  Positive
  angles point down while negative point up.
* **Sizes** - size of each extremity.  Generally **Angles** should be changed more frequently
  than **Sizes**.
"""

    def __init__(self, width, length, ballSize, units):
        size1 = inchesToUnits(1, units)
        self.editor = [
            DialogFloat("xNeck",                   "X Location of Neck",       units=units, default=width / 2.0),
            DialogFloat("yNeck",                   "Y Location of Neck",       units=units, default=length / 1.5),
            DialogBreak(),
            DialogFloat("leftShoulderAngle",       "Left shoulder angle",      units="degrees", default=-20.0, min=-60.0, max=60.0),
            DialogFloat("leftElbowAngle",          "Left elbow angle",         units="degrees", default=-20.0, min=-60.0, max=60.0),
            DialogFloat("rightShoulderAngle",      "Right shoulder angle",     units="degrees", default=-20.0, min=-60.0, max=60.0),
            DialogFloat("rightElbowAngle",         "Right elbow angle",        units="degrees", default=-20.0, min=-60.0, max=60.0),
            DialogFloat("leftKneeAngle",           "Left thigh angle",         units="degrees", default=50.0,  min=-60.0, max=60.0),
            DialogFloat("leftCalfAngle",           "Left calf angle",          units="degrees", default=20.0,  min=-60.0, max=60.0),
            DialogFloat("rightKneeAngle",          "Right thigh angle",        units="degrees", default=60.0,  min=-60.0, max=60.0),
            DialogFloat("rightCalfAngle",          "Right calf angle",         units="degrees", default=20.0,  min=-60.0, max=60.0),
            DialogBreak(),
            DialogFloat("headSize",                "Head Size (radius)",       units=units, default=size1),
            DialogFloat("neckLength",              "Neck length",              units=units, default=size1),
            DialogFloat("bodyLength",              "Body length",              units=units, default=size1*4),
            DialogFloat("thighLength",             "Thigh length",             units=units, default=size1*2),
            DialogFloat("calfLength",              "Calf length",              units=units, default=size1*2),
            DialogFloat("upperArmLength",          "Upper arm length",         units=units, default=size1*2),
            DialogFloat("foreArmLength",           "Forearm length",           units=units, default=size1*2),
        ]

    def generate(self, params):
        chain = []

        # Draw the head
        neck = (params.xNeck, params.yNeck)
        for a in range(0, 360, 5):
            angle = radians(a - 90)
            x = neck[0] + cos(angle) * params.headSize
            y = neck[1] + params.headSize + sin(angle) * params.headSize
            chain.append((x, y))
        chain.append(neck)

        # Draw the body
        crotch = (params.xNeck, params.yNeck - params.bodyLength)
        chain.append(crotch)

        # Draw the left leg (and return to body)
        angle = radians(params.leftKneeAngle)
        x = crotch[0] - cos(angle) * params.thighLength
        y = crotch[1] - sin(angle) * params.thighLength
        knee = (x, y)
        chain.append(knee)

        angle = radians(params.leftCalfAngle + params.leftKneeAngle)
        x = knee[0] - cos(angle) * params.calfLength
        y = knee[1] - sin(angle) * params.calfLength
        foot = (x, y)
        chain.append(foot)
        chain.append(knee)
        chain.append(crotch)

        # Draw the right leg (and return to body)
        angle = radians(params.rightKneeAngle)
        x = crotch[0] + cos(angle) * params.thighLength
        y = crotch[1] - sin(angle) * params.thighLength
        knee = (x, y)
        chain.append(knee)

        angle = radians(params.rightCalfAngle + params.rightKneeAngle)
        x = knee[0] + cos(angle) * params.calfLength
        y = knee[1] - sin(angle) * params.calfLength
        foot = (x, y)
        chain.append(foot)
        chain.append(knee)
        chain.append(crotch)

        # Move to the shoulders
        shoulders = (neck[0], neck[1] - params.neckLength)
        chain.append(shoulders)

        # Draw the left arm (and return to body)
        angle = radians(params.leftShoulderAngle)
        x = shoulders[0] - cos(angle) * params.upperArmLength
        y = shoulders[1] - sin(angle) * params.upperArmLength
        elbow = (x, y)
        chain.append(elbow)

        angle = radians(params.leftShoulderAngle + params.leftElbowAngle)
        x = elbow[0] - cos(angle) * params.foreArmLength
        y = elbow[1] - sin(angle) * params.foreArmLength
        wrist = (x, y)
        chain.append(wrist)
        chain.append(elbow)
        chain.append(shoulders)

        # Draw the right arm (and return to body)
        angle = radians(params.rightShoulderAngle)
        x = shoulders[0] + cos(angle) * params.upperArmLength
        y = shoulders[1] - sin(angle) * params.upperArmLength
        elbow = (x, y)
        chain.append(elbow)

        angle = radians(params.rightShoulderAngle + params.rightElbowAngle)
        x = elbow[0] + cos(angle) * params.foreArmLength
        y = elbow[1] - sin(angle) * params.foreArmLength
        wrist = (x, y)
        chain.append(wrist)
        chain.append(elbow)
        chain.append(shoulders)

        # Return to neck
        chain.append(neck)

        return [chain]
