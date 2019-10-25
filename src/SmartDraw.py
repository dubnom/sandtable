from Sand import *
import shapely.geometry
from Chains import *

def SmartDraw(chains,width,height,ballSize):
    # Add the left starting object
    chains.insert( 0, [ (0.,0.), (0.,height), (0.,0.) ])

    lines = []
    intersections = []
    scanToY = []
    y = 0.
    while y <= height:
        lines.append( shapely.geometry.LineString( [ (0,y), (width,y) ] ))
        scanToY.append(y)
        y += ballSize
        intersections.append([])

    # Find all the intersections of the polygons with the scan lines
    # FIX: Where there is no intersection, find the closest scanline and pick a point
    for polyNum, chain in enumerate(chains):
        polygon = shapely.geometry.LineString(chain)
        for scanNum, line in enumerate(lines):
            intercepts = polygon.intersection(line)
            if intercepts:
                if intercepts.type == 'LineString':
                    for x,y in list(intercepts.coords):
                        intersections[scanNum].append( (x, polyNum) )
                elif intercepts.type == 'MultiPoint':
                    for pt in intercepts:
                        intersections[scanNum].append( (pt.x, polyNum) )
                elif intercepts.type == 'Point':
                    intersections[scanNum].append( (intercepts.x, polyNum) )

    # Sort each scan line into x order: [ (x,poly), (x1,poly1) ... (xN,polyN) ]
    # and convert polygon distances into left/right smallest distance table

    polysNeighbors = [{} for c in range(len(chains))]
    def updatePolyDistance(p, v ):
        if v[1] in polysNeighbors[p]:
            if polysNeighbors[p][v[1]][0] <= v[0]:
                return
        polysNeighbors[p][v[1]]=v

    def updatePolyDistances( pn0, pn1, x0, x1, scanNum ):
        d = x1 - x0
        updatePolyDistance(pn0, (d,pn1,x0,x1,scanNum))
        updatePolyDistance(pn1, (d,pn0,x1,x0,scanNum))

    for scanNum,scan in enumerate(intersections):
        oldPolyNum = -1
        for x,polyNum in sorted(scan):
            if oldPolyNum >= 0:
                if oldPolyNum != polyNum:
                    updatePolyDistances( oldPolyNum, polyNum, oldX, x, scanNum )
            oldX, oldPolyNum = x, polyNum
                

    def sortNeighbors(neighbors):
        s = list(neighbors.values())
        s.sort(key=lambda k:k[0])
        return s

    # Create a tree of all polygons by their shortest distance neighbor
    # with the first polygon as the root of the tree
    tree = {}
    def makeTree(parent):
        tree[ parent ] = []
        for child in sortNeighbors(polysNeighbors[parent]):
            if child[1] not in tree:
                tree[ parent ].append(makeTree( child[1] ))
        return parent 

    makeTree(0)

    # Create new chain using the new drawing order
    newChain = []

    def intersect(p1,p2,p3):
        return (p1[0]<=p3[0]<=p2[0] or p1[0]>=p3[0]>=p2[0]) and (p1[1]<=p3[1]<=p2[1] or p1[1]>=p3[1]>=p2[1])

    def chainIntersect(chain,point):
        p1 = chain[0]
        for index,p2 in enumerate(chain[1:]):
            if intersect(p1,p2,point):
                return index+1
            p1=p2
        return None

    def makeChain(node=0,pointNumber=0):
        children = [polysNeighbors[node][c] for c in tree[node]]
        chain = chains[node]
        chain = chain[pointNumber:] + chain[:pointNumber+1]
        p1 = chain[0]
        newChain.append(p1)
        for p2 in chain[1:]:
            for index,(dist, cn, x0, x1, scan) in enumerate(children):
                y = scanToY[scan]
                if intersect(p1,p2,(x0,y)):
                    newChain.append((x0,y))
                    newChain.append((x1,y))
                    makeChain(cn,chainIntersect(chains[cn],(x1,y)))
                    newChain.append((x1,y))
                    newChain.append((x0,y))
                    del children[index]
            newChain.append(p2)
            p1 = p2

    makeChain()

    # Make actual scanlines
    scanLines = []
    for scan,y in enumerate(scanToY):
        scanLines += ((width,y),(0,y)) if scan % 2 else ((0,y),(width,y))
    scanLines += ((0,y),(0,0))

    return [ scanLines, Chains.deDistance( newChain ) ]

if __name__ == '__main__':
    chains = [
        [ (3.,3.), (9.,11.), (7.,1.), (3.,3.) ],
        [ (15.,15.), (18.,15.), (18.,18.), (15.,18.), (15.,15.) ],
        [ (19.,16.), (20.,16.), (20.,17.), (19.,17.), (19.,16.) ],
        [ (10.,10.), (25.,10.), (25.,20.), (10.,20.), (10.,10.) ],
        [ (27,3), (29,11), (28,1), (27,3) ],
        [ (1,2), (2,2), (1,18) ],
    ]

    # Read the last gcode file, remove scan lines and scan line motion
    # and convert into chains
    import re
    pattern = re.compile('G01 X([0-9,\\\\.]+)Y(.+)$')
    chains = []
    with open('../%sgcode.ngc' % DATA_PATH,'r') as f:
        lines = f.readlines()
        chain = []
        for s in lines[2:-1]:
            if s.startswith("% Chain"):
                if len(chain):
                    chains.append(chain)
                    chain = []
            elif s.startswith("G01"):
                xs, ys = pattern.match(s).groups()
                chain.append( (float(xs),float(ys))) 
        if len(chain):
            chains.append(chain)

    del(chains[0])
    del(chains[-1])
    for chain in chains:
        del(chain[0])
        del(chain[-1])

    SmartDraw( chains,30.,20.,1. )
