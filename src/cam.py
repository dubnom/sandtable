#!/usr/bin/env python
#
# cam.py
#
# Neil Gershenfeld
#
# (c) Massachusetts Institute of Technology 2006
# Permission granted for experimental and personal use;
# license for commercial sale available from MIT.
#
# Neal is brilliant, but this code was written in 2006 and is fairly terrible due to
# the use of global variables, lack of classes, embed UI with logic, misused parentheses,
# print statements, bitwise logic operators, and some formats dont work.
# As such, the file has been heavily modified to fix some of these issues.
#
# flake8: noqa
#

import logging
from svgelements import SVG, Path, Shape, Move, Close, Line, Arc, CubicBezier, QuadraticBezier

CURVE_STEPS = 20


def read_SVG(filename: str):
    svg = SVG.parse(filename)
    chains = []

    for element in svg.elements():
        if isinstance(element, Path):
            path = element
        elif isinstance(element, Shape):
            path = Path(element)
            path.reify()
        else:
            continue

        if len(path) == 0:
            continue

        chain = []
        for segment in path:
            if isinstance(segment, Move):
                if chain:
                    chains.append(chain)
                chain = [(segment.end.x, segment.end.y)] if segment.end is not None else []
            elif isinstance(segment, Close):
                if segment.end is not None:
                    chain.append((segment.end.x, segment.end.y))
                if chain:
                    chains.append(chain)
                chain = []
            elif isinstance(segment, Line):
                if segment.end is not None:
                    chain.append((segment.end.x, segment.end.y))
            else:
                # Arc, CubicBezier, QuadraticBezier — sample along the curve
                for i in range(1, CURVE_STEPS + 1):
                    pt = segment.point(i / CURVE_STEPS)
                    chain.append((pt.x, pt.y))

        if chain:
            chains.append(chain)

    return chains
