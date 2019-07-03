# astar.py

"""Implements astar heuristic pathfinding"""

import math
import time
from collections import namedtuple

from source.common import distance, join, squares
from source.ecs.components import Position

node = namedtuple("Node", "distance_f distance_g distance_h parent position")

# def hueristic(node, goal):
#     dx = abs(node[0] - goal[0])
#     dy = abs(node[1] - goal[1])
#     return 1 * (dx + dy) + (math.sqrt(2) - 2 * 1) * min(dx, dy)

# def hueristic(node, goal):
#     dx = abs(node[0] - goal[0])
#     dy = abs(node[1] - goal[1])
#     return 1 * max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

def hueristic2(node, goal):   
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    if (dx > dy):
        return 1 * (dx - dy) + math.sqrt(2) * dy
    else:
        return 1 * (dy - dx) + math.sqrt(2) * dx

def hueristic3(node, goal):   
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    if (dx > dy):
        dx, dy = dy, dx
    return 1 * (dx - dy) + math.sqrt(2) * dy

def calc(start, end):
    return int(distance(start, end) * 10)

def check(l, neighbor, f):
    return any(n.position == neighbor and n.distance_f < f for n in l)

def pathfind(engine, start, end):
    tiles = {
        (position.x, position.y): render.char
            for _, (_, position, render) in join(
                engine.tiles,
                engine.positions,
                engine.renders
            )
    }
    path = astar(tiles, start, end)
    return path

def astar(tiles, start, end):
    openlist = set()
    closelist = []
    # convert start to x, y value
    openlist.add(node(0, 0, 0, None, (start.x, start.y)))

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
