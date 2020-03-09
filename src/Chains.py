import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import numpy as np
from scipy import interpolate
import math


class Chains():
    """
    Chains are arrays of one or more "chain".
    A chain is an array of one or more points.
    A point is a set containing (x,y) as floats.

    Generic functions that take Chains and return new Chains -
        scale, transform, rotate, fit, autoScaleCenter

    Other generic functions -
        calcExtents, isInside, epsilon

    Sandtable specific functions -
        bounds, saveImage, makeImage, makeRealisticImage, makeGCode,
        estimateMachiningTime, scanalize, morph, combine, expand

    Currently all of the methods in Chains are static,
    in the future Chains may be converted into a class that
    supports array operations and will be used through instantiation.
    """

    LEFT = 0x01
    RIGHT = 0x02
    TOP = 0x04
    BOTTOM = 0x08

    EPSILON = 1E-5

    # For drawing realistic images
    COLOR_LIGHT = (255, 255, 244)     # (197, 197, 189)
    COLOR_NEUTRAL = (127, 127, 127)     # (183, 177, 143)
    COLOR_DARK = (56, 52, 41)     # (168, 158, 123)
    _lines = [(3, 3, COLOR_NEUTRAL), (-3, -3, COLOR_NEUTRAL), (-2, -2, COLOR_LIGHT), (-2, -1, COLOR_LIGHT),
              (-1, -2, COLOR_LIGHT), (-1, -1, COLOR_LIGHT), (0, 0, COLOR_DARK), (1, 1, COLOR_DARK),
              (1, 2, COLOR_DARK), (2, 1, COLOR_DARK), (2, 2, COLOR_DARK)]

    conversion = {'inches': 1, 'mm': 25.4, 'cm': 2.54}

    @staticmethod
    def calcExtents(chains):
        """Return two points that indicate the lower left and upper right extents of the chains"""
        xLow = yLow = 1E100
        xHigh = yHigh = -1E100
        for chain in chains:
            if chain:
                xp, yp = list(zip(*chain))
                xLow, yLow = min(xLow, min(xp)), min(yLow, min(yp))
                xHigh, yHigh = max(xHigh, max(xp)), max(yHigh, max(yp))
        return (xLow, yLow), (xHigh, yHigh)

    @staticmethod
    def scale(chains, scale):
        """Multiply every point in the chains by the scale factors"""
        return [[(p[0] * scale[0], p[1] * scale[1]) for p in chain] for chain in chains]

    @staticmethod
    def transform(chains, offset):
        """Move (add) an offset to every point in the chains"""
        return [[(p[0] + offset[0], p[1] + offset[1]) for p in chain] for chain in chains]

    @staticmethod
    def rotate(chains, angle):
        """Rotate the chain by angle degrees around 0,0"""
        sin = math.sin(math.radians(angle))
        cos = math.cos(math.radians(angle))
        return [[(p[0]*cos - p[1]*sin, p[0]*sin + p[1]*cos) for p in chain] for chain in chains]

    @staticmethod
    def round(chains, precision):
        """Round the chains to a given precision"""
        return [[(round(p[0], precision), round(p[1], precision)) for p in chain] for chain in chains]

    @staticmethod
    def fit(chains, newExtents):
        """Fit the chain to newExtents. This may stretch one or both axes"""
        oldExtents = Chains.calcExtents(chains)
        width, length = oldExtents[1][0] - oldExtents[0][0], oldExtents[1][1] - oldExtents[0][1]
        if width <= 0.0 or length <= 0.0:
            return chains
        xScale = (newExtents[1][0] - newExtents[0][0]) / width
        yScale = (newExtents[1][1] - newExtents[0][1]) / length
        newChains = []
        for chain in chains:
            newChain = []
            for point in chain:
                newX = newExtents[0][0] + (point[0] - oldExtents[0][0]) * xScale
                newY = newExtents[0][1] + (point[1] - oldExtents[0][1]) * yScale
                newChain.append((newX, newY))
            newChains.append(newChain)
        return newChains

    @staticmethod
    def autoScaleCenter(chains, newExtents, zoom=1.0):
        """Preserve x/y ratio while scaling and centering the chains to the newExtents"""
        oldExtents = Chains.calcExtents(chains)
        width, length = oldExtents[1][0] - oldExtents[0][0], oldExtents[1][1] - oldExtents[0][1]
        if width <= 0.0 or length <= 0.0:
            return chains
        xScale = (newExtents[1][0] - newExtents[0][0]) / width
        yScale = (newExtents[1][1] - newExtents[0][1]) / length
        scale = min(xScale, yScale) * zoom
        xOffset = (newExtents[1][0] - newExtents[0][0] - scale * width) / 2.0
        yOffset = (newExtents[1][1] - newExtents[0][1] - scale * length) / 2.0
        newChains = []
        for chain in chains:
            newChain = []
            for point in chain:
                newX = newExtents[0][0] + xOffset + scale * (point[0] - oldExtents[0][0])
                newY = newExtents[0][1] + yOffset + scale * (point[1] - oldExtents[0][1])
                newChain.append((newX, newY))
            newChains.append(newChain)
        if zoom > 1.0:
            newChains = Chains.bound(newChains, newExtents)
        return newChains

    @staticmethod
    def spiral(xCenter, yCenter, radiusStart, radiusEnd=0.0, turns=1.0, angleRate=15.0, angleStart=0.0, base=1.0, fill=False, angleEnd=None):
        thickness = radiusEnd - radiusStart
        points = int(abs(turns * 360. / angleRate))
        divisor = pow((points * abs(angleRate)) / 360.0, base)
        point360 = 360.0 / abs(angleRate)

        if angleEnd is not None:
            angleStart = -(((points-1) * angleRate - angleEnd) % 360)

        chain = []
        for point in range(points):
            angle = math.radians(angleStart + point * angleRate)
            if fill:
                if point > point360:
                    radius = radiusStart + thickness * (math.pow((((point - point360) * abs(angleRate)) / 360.0), base) / divisor)
                else:
                    radius = radiusStart
                x = xCenter + math.cos(angle) * radius
                y = yCenter + math.sin(angle) * radius
                chain.append((x, y))
            radius = radiusStart + thickness * (math.pow(((point * abs(angleRate)) / 360.0), base) / divisor)
            x = xCenter + math.cos(angle) * radius
            y = yCenter + math.sin(angle) * radius
            chain.append([x, y])
        return chain

    @staticmethod
    def bound(chains, boundary):
        """Clip the chains to fit within the boundary. Logic is used to go around the
           edges of the SandTable when lines go off one side and come back on another"""
        oldPoint = None
        lastPoint = None
        isClipping = False
        newChains = []
        for chain in chains:
            newChain = []
            for point in chain:
                if oldPoint:
                    points = Chains._clip(oldPoint, point, boundary)
                    if points is None:
                        isClipping = True
                    else:
                        if lastPoint != points[0]:
                            if isClipping:
                                newChain += Chains._nastySandTableLogic(lastPoint, points[0], boundary)
                            newChain.append(points[0])
                        newChain.append(points[1])
                        lastPoint = points[1]
                        isClipping = lastPoint[0] != point[0] or lastPoint[1] != point[1]
                oldPoint = point
            newChains.append(newChain)
        return newChains

    # The Sand Table has no z axis so this method fixes up line boundary problems.
    # If a line goes out of bounds on one edge and comes back on another, the method
    # creates some extra lines to move around the edge of the table to the new edge.
    @staticmethod
    def _nastySandTableLogic(p1, p2, boundary):
        points = []
        d1 = Chains._clipDirection(p1, boundary)
        d2 = Chains._clipDirection(p2, boundary)

        if d1 & d2:
            pass
        elif d1 & Chains.LEFT:
            if d2 & Chains.RIGHT:
                height = boundary[1][1] - boundary[0][1]
                distance = p1[1] - boundary[0][1] + p2[1] - boundary[0][1]
                if distance < height:
                    points = [(boundary[0][0], boundary[0][1]), (boundary[1][0], boundary[0][1])]
                else:
                    points = [(boundary[0][0], boundary[1][1]), (boundary[1][0], boundary[1][1])]
            else:
                points = [(p1[0], p2[1])]
        elif d1 & Chains.RIGHT:
            if d2 & Chains.LEFT:
                height = boundary[1][1] - boundary[0][1]
                distance = p1[1] - boundary[0][1] + p2[1] - boundary[0][1]
                if distance < height:
                    points = [(boundary[1][0], boundary[0][1]), (boundary[0][0], boundary[0][1])]
                else:
                    points = [(boundary[1][0], boundary[1][1]), (boundary[0][0], boundary[1][1])]
            else:
                points = [(p1[0], p2[1])]
        elif d1 & Chains.TOP:
            if d2 & Chains.BOTTOM:
                width = boundary[1][0] - boundary[0][0]
                distance = p1[0] - boundary[0][0] + p2[0] - boundary[0][0]
                if distance < width:
                    points = [(boundary[0][0], boundary[1][1]), (boundary[0][0], boundary[0][1])]
                else:
                    points = [(boundary[1][0], boundary[1][1]), (boundary[1][0], boundary[0][1])]
            else:
                points = [(p2[0], p1[1])]
        elif d1 & Chains.BOTTOM:
            if d2 & Chains.TOP:
                width = boundary[1][0] - boundary[0][0]
                distance = p1[0] - boundary[0][0] + p2[0] - boundary[0][0]
                if distance < width:
                    points = [(boundary[0][0], boundary[0][1]), (boundary[0][0], boundary[1][1])]
                else:
                    points = [(boundary[1][0], boundary[0][1]), (boundary[1][0], boundary[1][1])]
            else:
                points = [(p2[0], p1[1])]

        return points

    @staticmethod
    def _clipDirection(p, box):
        code = 0
        if p:
            if p[1] >= box[1][1]:
                code |= Chains.TOP
            elif p[1] <= box[0][1]:
                code |= Chains.BOTTOM
            if p[0] >= box[1][0]:
                code |= Chains.RIGHT
            elif p[0] <= box[0][0]:
                code |= Chains.LEFT
        return code

    @staticmethod
    def epsilon(a, b):
        """Compare two number to see if they are close (within Chains.EPSILON)"""
        return math.fabs(a - b) < Chains.EPSILON

    @staticmethod
    def isInside(point, boundary):
        """Determine if a point is within the specified boundary"""
        return point[0] >= boundary[0][0] and point[0] <= boundary[1][0] and point[1] >= boundary[0][1] and point[1] <= boundary[1][1]

    # Cohen-Sutherland algorithm. Converted from wikipedia Pascal code
    @staticmethod
    def _compOutCode(p, box):
        code = 0
        if p[1] > box[1][1]:
            code |= Chains.TOP
        elif p[1] < box[0][1]:
            code |= Chains.BOTTOM
        if p[0] > box[1][0]:
            code |= Chains.RIGHT
        elif p[0] < box[0][0]:
            code |= Chains.LEFT
        return code

    @staticmethod
    def _clip(point1, point2, box):
        p1 = [point1[0], point1[1]]
        p2 = [point2[0], point2[1]]

        outcode1 = Chains._compOutCode(p1, box)
        outcode2 = Chains._compOutCode(p2, box)
        while True:
            if not outcode1 and not outcode2:
                return p1, p2
            elif outcode1 & outcode2:
                return None

            outcodeOut = outcode1 if outcode1 else outcode2

            if Chains.TOP & outcodeOut:
                x, y = p1[0] + (p2[0] - p1[0]) * (box[1][1] - p1[1]) / (p2[1] - p1[1]), box[1][1]
            elif Chains.BOTTOM & outcodeOut:
                x, y = p1[0] + (p2[0] - p1[0]) * (box[0][1] - p1[1]) / (p2[1] - p1[1]), box[0][1]

            if Chains.RIGHT & outcodeOut:
                x, y = box[1][0], p1[1] + (p2[1] - p1[1]) * (box[1][0] - p1[0]) / (p2[0] - p1[0])
            elif Chains.LEFT & outcodeOut:
                x, y = box[0][0], p1[1] + (p2[1] - p1[1]) * (box[0][0] - p1[0]) / (p2[0] - p1[0])

            # Now we move outside point to intersection point to clip, and get ready for next pass.
            if outcodeOut == outcode1:
                p1[0], p1[1] = x, y
                outcode1 = Chains._compOutCode(p1, box)
            else:
                p2[0], p2[1] = x, y
                outcode2 = Chains._compOutCode(p2, box)

    @staticmethod
    def saveImage(chains, box, fileName, imageWidth, imageHeight, imageType):
        """Save the chains as a PNG file to disk"""
        if imageType == 'Realistic':
            pic = Chains.makeRealisticImage(chains, box, imageWidth, imageHeight)
        else:
            pic = Chains.makeImage(chains, box, imageWidth, imageHeight)
        pic.save(fileName, "PNG")

    @staticmethod
    def makeImage(chains, box, imageWidth, imageHeight):
        """Convert chains into a schematic image"""
        pic = Image.new("RGB", (imageWidth, imageHeight))
        draw = ImageDraw.Draw(pic)

        # Scale the coordinate system
        extents = Chains.calcExtents(chains + [box])
        offset = (-extents[0][0], -extents[0][1])
        xScale = float(imageWidth - 1) / (extents[1][0] - extents[0][0])
        yScale = float(imageHeight - 1) / (extents[1][1] - extents[0][1])
        scale = (min(xScale, yScale), min(xScale, yScale))

        # Draw grid
        rules = []
        x = box[0][0]
        while x < box[1][0]:
            rules.append([(x, box[0][1]), (x, box[1][1])])
            x += 5.0
        y = box[0][1]
        while y < box[1][1]:
            rules.append([(box[0][0], y), (box[1][0], y)])
            y += 5.0
        Chains._drawChains(draw, rules, offset, scale, (64, 32, 32), imageHeight)

        # Draw the unbounded chains
        Chains._drawChains(draw, chains, offset, scale, (128, 128, 128), imageHeight)

        # Draw the bounding box
        boxChains = [[box[0], (box[0][0], box[1][1]), box[1], (box[1][0], box[0][1]), box[0]]]
        Chains._drawChains(draw, boxChains, offset, scale, (200, 0, 0), imageHeight)

        # Draw the bounded chains
        Chains._drawChains(draw, Chains.bound(chains, box), offset, scale, (128, 250, 250), imageHeight)
        return pic

    @staticmethod
    def _drawChains(draw, chains, offset, scale, color, imageHeight):
        for chain in Chains._makeReadyToDraw(Chains.scale(Chains.transform(chains, offset), scale), imageHeight - 1):
            draw.line(chain, fill=color)

    @staticmethod
    def _drawChainsAuto(draw, chains, offset, scale, imageHeight):
        count = len(chains)
        if count > 0:
            base = 16.
            div = (255.-base) / count
            colors = [(int(c*div+base),)*3 for c in range(count)]
        for color, chain in zip(colors, Chains._makeReadyToDraw(Chains.scale(Chains.transform(chains, offset), scale), imageHeight - 1)):
            draw.line(chain, fill=color)

    @staticmethod
    def _makeReadyToDraw(chains, imageHeight):
        return [[(float(p[0]), imageHeight-float(p[1])) for p in chain] for chain in chains]

    @staticmethod
    def makeRealisticImage(chains, box, imageWidth, imageHeight):
        """Convert chains into a realistic image of what it would look like in sand"""
        pic = Image.open("images/background.png").resize((imageWidth, imageHeight))
        draw = ImageDraw.Draw(pic)

        # Scale the coordinate system
        extents = Chains.calcExtents([box])
        offset = (-extents[0][0], -extents[0][1])
        xScale = float(imageWidth - 1) / (extents[1][0] - extents[0][0])
        yScale = float(imageHeight - 1) / (extents[1][1] - extents[0][1])
        scale = (min(xScale, yScale), min(xScale, yScale))

        oldX, oldY = None, None
        for chain in Chains._makeReadyToDraw(Chains.scale(Chains.transform(Chains.bound(chains, box), offset), scale), imageHeight-1):
            for newX, newY in chain:
                if oldX is not None:
                    for x, y, c in Chains._lines:
                        draw.line([(oldX+x, oldY+y), (newX+x, newY+y)], fill=c)
                oldX, oldY = newX, newY
        return pic

    @staticmethod
    def convertUnits(chains, fromUnits, toUnits):
        """Convert between measurement units"""
        if fromUnits == toUnits:
            return chains
        unitConv = Chains.conversion[toUnits] / Chains.conversion[fromUnits]
        return [[(p[0]*unitConv, p[1]*unitConv) for p in chain] for chain in chains]

    @staticmethod
    def makeGCode(chains, box, feed, fileName, machUnits, tableUnits):
        """Convert chains into a bounded G-Code file"""
        with open(fileName, 'w') as f:
            unitConv = 1.
            if machUnits == 'inches':
                print('G20', file=f)
                fmtStr = 'G01 X%.2fY%.2f'
                if tableUnits == 'mm':
                    unitConv = 1. / 2.54
            else:
                print('G21', file=f)
                fmtStr = 'G01 X%.1fY%.1f'
                if tableUnits == 'inches':
                    unitConv = 25.4

            print('F', feed, file=f)
            for chainNum, chain in enumerate(Chains.bound(chains, box)):
                print('%% Chain %d' % chainNum, file=f)
                for point in chain:
                    print(fmtStr % (point[0]*unitConv, point[1]*unitConv), file=f)
            print('M2', file=f)

    @staticmethod
    def estimateMachiningTime(chains, feed, accel):
        """Estimate the amount time, distance, and points to draw the chains in sand"""
        feed /= 60.0               # Feed is in units/minute convert to units/second
        accelTime = feed / accel   # Time to accelerate to full speed v=at

        # Distance to accelerate to full speed s=1/2at^2
        accelDist = (accel * accelTime ** 2.) / 2.0
        twoDist = accelDist * 2.0

        time = 0.0
        distance = 0.0
        pointCount = 0
        p0 = None
        for chain in chains:
            for p1 in chain:
                if p0:
                    dist = math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)
                    distance += dist
                    if dist >= twoDist:
                        time += accelTime + ((dist - twoDist) / feed) + accelTime
                    else:
                        time += 2.0 * math.sqrt(dist / accel)
                pointCount += 1
                p0 = p1
        return time, distance, pointCount

    @staticmethod
    def makeSVG(chains, fileName):
        """Output a Scalable Vector Graphics (SVG) file"""
        extents = Chains.calcExtents(chains)
        xOff, yOff = extents[0][0], extents[0][1]
        xMax, yMax = extents[1][0], extents[1][1]
        width, length = xMax - xOff, yMax - yOff
        with open(fileName, 'w') as f:
            print('<svg width="%g" height="%g" version="1.1" xmlns="http://www.w3.org/2000/svg">' % (width, length), file=f)
            for chain in chains:
                points = " ".join(['%.4g,%.4g' % (point[0]-xOff, length-(point[1]-yOff)) for point in chain])
                print('  <polyline points="%s" stroke="black" stroke-width="1" />' % points, file=f)
            print('</svg>', file=f)

    @staticmethod
    def scanalize(chains, xOffset, yOffset, width, length, rowsPerInch=1.0):
        """Add scanlines, and appropriate movements, to draw the chains using hidden
           entry and exit points (along the scanlines)"""

        # Create the actual scanlines
        scanlines = []
        for rowNum in range(int(length * rowsPerInch) + 1):
            row = rowNum / rowsPerInch
            points = [(0.0, row), (width, row)]
            if rowNum % 2:
                points.reverse()
            scanlines += points
        if scanlines[-1][0] == 0.0:
            scanlines.append(scanlines[-2])

        # Reorder each of the chains where the first point is the rightmost one
        chains = list(map(Chains._reprocessChain, chains))

        # Sort all of the chains where the leftmost is first
        chains.sort(key=lambda chain: chain[0][0])

        # For each chain
        # Find rightmost row intercept
        # Go from current point all the way to the right
        # Move to correct row
        # Move to rightmost row intercept

        previousRow = -1.0
        previousChain = None
        for chain in chains:
            x, y = chain[0][0], math.floor(chain[0][1] * rowsPerInch + 0.5) / rowsPerInch
            chain.insert(0, (x, y))
            if previousRow != y:
                chain.insert(0, (width, y))
                previousRow = y
            elif previousChain:
                del previousChain[-1]
            previousChain = chain

            x, y = chain[-1][0], math.floor(chain[-1][1] * rowsPerInch + 0.5) / rowsPerInch
            chain.append((x, y))
            chain.append((width, y))

        chains.insert(0, scanlines)
        chains.append([(width, 0.0)])
        return Chains.transform(chains, (xOffset, yOffset))

    @staticmethod
    def _reprocessChain(chain):
        """Rearrange an individual chain (polygon) to have the right-most point first"""
        index, xHigh = None, None
        for i, (x, y) in enumerate(chain):
            if xHigh is None or x > xHigh:
                index, xHigh = i, x
        # Return the end of chain + start of chain
        return chain[index:] + chain[:index+1]

    @staticmethod
    def morph(start, end, steps):
        """Morph one chain (start) into another (end) through a series of steps (steps)
           morph() returns a list of chains"""
        # Flatten both start and end chains
        startchain = Chains.combine(start)
        endchain = Chains.combine(end)

        # If chains are different sizes, expand smaller chain by interpolating some points
        if len(startchain) < len(endchain):
            Chains.expand(startchain, len(endchain))
        elif len(endchain) < len(startchain):
            Chains.expand(endchain, len(startchain))

        # Create incremental dx, dy for each point in the chains
        dx = []
        dy = []
        for point1, point2 in zip(startchain, endchain):
            dx.append((point2[0] - point1[0]) / steps)
            dy.append((point2[1] - point1[1]) / steps)

        # Generate an array of chains, one entry for each step
        results = [[[(point[0]+s*x, point[1]+s*y) for point, x, y in zip(startchain, dx, dy)]] for s in range(steps+1)]
        return results

    @staticmethod
    def combine(chains):
        """Convert chains (a list of chains) into a single chain (a polyline)"""
        newChain = []
        for chain in chains:
            newChain += chain
        return newChain

    @staticmethod
    def expand(chain, newlen):
        """Interpolate new points within chain until it reaches newlen in length.
           Attempt to distribute the new points evenly throughout the chain."""
        length = len(chain)
        if not length:
            return
        if length == 1:
            chain.append(chain[0])
            length += 1
        more = newlen - length
        step = float(length) / more
        while more > 0:
            index = int(more * step)
            if index >= length - 2:
                index = length - 2
            newpoint = ((chain[index][0] + chain[index+1][0]) / 2.0, (chain[index][1] + chain[index+1][1]) / 2.0)
            chain.insert(index + 1, newpoint)
            length += 1
            more -= 1

    @staticmethod
    def circleToTable(chain, width, length):
        """Expand circular to rectangular geometry to better fill a rectangular table"""
        xCenter, yCenter = width/2.0, length/2.0

        # Find the maximum radius from the center of the table
        if False:
            maxRadius = 0.0
            for p in chain:
                maxRadius = max(maxRadius, math.sqrt((p[0]-xCenter)**2+(p[1]-yCenter)**2))
        maxRadius = min(xCenter, yCenter)

        def sgn(x):
            return (x > 0.)-(x < 0.)

        newChain = []
        for p in chain:
            # Scale to unit circle
            u, v = (p[0]-xCenter) / maxRadius, (p[1]-yCenter) / maxRadius
            if True:    # Simple stretching
                r = math.sqrt(u**2 + v**2)
                if abs(u) < Chains.EPSILON or abs(v) < Chains.EPSILON:
                    x, y = u, v
                elif u**2 > v**2:
                    x, y = sgn(u) * r, sgn(v) * abs((v * r)/u)
                else:
                    x, y = sgn(u) * abs((u * r)/v), sgn(v) * r

            if False:   # FG-Squircular Mapping
                if abs(u) < Chains.EPSILON or abs(v) < Chains.EPSILON:
                    x, y = u, v
                else:
                    r = math.sqrt(u**2+v**2-math.sqrt((u**2+v**2)*(u**2+v**2-4*u**2*v**2)))
                    x = (sgn(u*v) / (v*math.sqrt(2))) * r
                    y = (sgn(u*v) / (u*math.sqrt(2))) * r

            # Scale to size of table
            x, y = xCenter + x * xCenter, yCenter + y * yCenter
            newChain.append((x, y))

        return newChain

    @staticmethod
    def deDupe(chains, epsilon=.01):
        """Remove duplicate points (points closer than epsilon)"""
        newChains = []
        for chain in chains:
            oldX = oldY = None
            newChain = []
            for x, y in chain:
                if oldX is None or abs(x-oldX) >= epsilon or abs(y-oldY) >= epsilon:
                    newChain.append((x, y))
                oldX, oldY = x, y
            newChains.append(newChain)
        return newChains

    @staticmethod
    def deDistance(chain, epsilon=.1):
        """Simplify a chain by removing points until the distance is greater than epsilon"""
        newChain = []
        if len(chain) > 0:
            oldX, oldY = chain[0]
            newChain.append((oldX, oldY))
            for x, y in chain[1:]:
                distance = math.sqrt((x-oldX)**2+(y-oldY)**2)
                if distance <= epsilon:
                    continue
                newChain.append((x, y))
                oldX, oldY = x, y
        return newChain

    @staticmethod
    def deDistances(chains, epsilon=.1):
        """Simplify chains"""
        return [Chains.deDistance(chain, epsilon) for chain in chains]

    @staticmethod
    def Spline(chain, expansion=5):
        """Post processor to insert extra points (splines) into a chain"""
        if len(chain) > 3:
            arr = np.array(chain)
            try:
                tck, u = interpolate.splprep([arr[:, 0], arr[:, 1]], s=0)
            except TypeError:
                return chain
            newLen = len(chain) * expansion
            stepSize = 1. / newLen
            unew = np.arange(0, (1+newLen) * stepSize, stepSize)
            new = interpolate.splev(unew, tck)
            return list(zip(new[0].tolist(), new[1].tolist()))
        return chain

    @staticmethod
    def splines(chains, expansion=5):
        """Post processor to insert extra points (splines) into chains"""
        return [Chains.Spline(chain) for chain in Chains.deDupe(chains)]
