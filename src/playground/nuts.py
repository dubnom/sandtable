from shapely.geometry import *
from pprint import pprint

# Dijsktra's algorithm from - https://gist.github.com/econchick/4666413
class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance


def dijsktra(graph, initial):
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes: 
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
        weight = current_weight + graph.distance[(min_node, edge)]
        if edge not in visited or weight < visited[edge]:
            visited[edge] = weight
            path[edge] = min_node

    return visited, path



def connect( chains ):
    # Calculate intersection of each polygon to every other polygon (may be many points)
    # Convert intersections into edges and polygons into nodes for a graph - still needs thought
    #   Edge: distances, polygon segment that makes up that distance
    #   Node: intersection point, polygon number
    # Draw first polygon (usually a simple background image)
    # For each polygon (in a potentially sorted list)
    #   Find shortest distance using dijsktra's algorithm from old polygon to new polygon
    #       If there is no shortest path - no intersections, draw straight line
    #   Draw shortest path
    #   Draw polygon
    #   old polygon = polygon

    for c1 in range(len(chains)):
        intersections = []
        p1 = LineString( chains[c1] ) 
        for c2 in range(len(chains)):
            if c1 != c2:
                i =  p1.intersection( LineString( chains[c2] ))
                if len(i):
                    intersections.append(i)
   
        print(c1, len(intersections))
        print("   ", end=' ')
        if len(intersections):
            for i in intersections:
                for j in i:
                    for k in j.coords:
                        print("(%4.2f,%4.2f)" % (k[0], k[1]), end=' ')
        print()


from random import randint
from math import sin, cos, radians

def test():
    circles = []
    chains = []
    if True:
        circles = [(8,10,2),(12,10,2),(2,2,2)]
    else:
        for c in range(5):
            x,y = randint(0,16), randint(0,16)
            r = randint(1,5)
            circles.append( (x,y,r))

    for (x,y,r) in circles:
        chains.append( [ (x+cos(radians(p*30))*r, y+sin(radians(p*30))*r) for p in range(12) ] )

    print("Circles\n",circles)
    connect( chains )

test()
