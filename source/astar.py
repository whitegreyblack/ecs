# astar.py

"""Implements astar heuristic pathfinding"""

from collections import namedtuple
from source.common import squares, join, distance
from source.ecs.components import Position
import time

node = namedtuple("Node", "distance_f distance_g distance_h parent position")

def calc(start, end):
    return int(distance(start, end) * 10)

def check(l, neighbor, f):
    return any(n.position == neighbor and n.distance_f < f for n in l)

def astar(engine, start, end):
    beg = time.time()
    openlist = set()
    closelist = []
    # convert start to x, y value
    openlist.add(node(0, 0, 0, None, (start.x, start.y)))

    g = join(
        engine.tiles,
        engine.positions,
        engine.renders
    )
    tiles = {
        (p.x, p.y): r.char
            for _, (_, p, r) in g
    }

    while openlist:
        nodeq = min(openlist, key=lambda x: x.distance_f)
        openlist.remove(nodeq)

        for i, j in squares(exclude_center=True):
            neighbor = (nodeq.position[0] + i, nodeq.position[1] + j)
            if neighbor == (end.x, end.y):
                closelist.append(nodeq)
                closelist.append(node(1, 1, 2, nodeq.position, neighbor))
                return closelist
            tile = tiles.get((neighbor[0], neighbor[1]), None)
            if tile and tile not in ("#", "+"):
                heuristic_g = nodeq.distance_g + calc(nodeq.position, neighbor)
                heuristic_h = calc(neighbor, (end.x, end.y))
                heuristic_f = heuristic_g + heuristic_h

                if check(openlist, neighbor, heuristic_f):
                    continue
                elif check(closelist, neighbor, heuristic_f):
                    continue
                else:
                    openlist.add(node(
                        heuristic_f, 
                        heuristic_g, 
                        heuristic_h, 
                        nodeq.position, 
                        neighbor
                    ))
        closelist.append(nodeq)
    if not openlist:
        return []
    return closelist
