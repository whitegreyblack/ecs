# astar.py

"""Implements astar A* pathfinding"""

import math
import time
from collections import namedtuple
from heapq import heappop, heappush

from source.common import cardinal, distance, join, join_drop_key, squares
from source.ecs.components import Position

# precompute square root (2) once vs every call
sqrt_two = math.sqrt(2)
def octile(a, b, abs=abs):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    if (dx < dy):
        return .4 * dx + dy
    else:
        return .4 * dy + dx

def astar(tiles, start, end, paths=squares, include_start=False):
    heap = []
    path = {}
    closed = set()
    # holds score from current node to neighbor
    gs = { (start.x, start.y): 0 }
    # holds score from current node to end node
    fs = { (start.x, start.y): octile((start.x, start.y), (end.x, end.y)) }
    
    heappush(heap, (fs[(start.x, start.y)], (start.x, start.y)))

    while heap:
        current = heappop(heap)[1]
        # found node: return reversed path
        if current == (end.x, end.y):
            data = []
            while current in path:
                data.append(current)
                current = path[current]
            data.reverse()
            if include_start:
                data.insert(0, (start.x, start.y))
            return data

        closed.add(current)
        for i, j in paths(exclude_center=True):
            neighbor = (current[0] + i, current[1] + j)
            new_g = gs[current] + octile(current, neighbor)
            # skips blocked positions
            if neighbor not in tiles:
                continue
            # skips positions already in heap with a better g score
            if neighbor in closed and new_g >= gs.get(neighbor, 0):
                continue
            # update heap with new g score node
            faster = new_g < gs.get(neighbor, 0)
            unexplored = neighbor not in [i[1] for i in heap]
            if faster or unexplored:
                path[neighbor] = current
                gs[neighbor] = new_g
                fs[neighbor] = new_g + octile(neighbor, (end.x, end.y))
                heappush(heap, (fs[neighbor], neighbor))
    return []

def astar_gui(tiles, start, end, paths=squares):
    """Note: This is for demo purposes only. Used only in demos/astar2.py"""
    heap = []
    path = {}
    closed = set()
    # holds score from current node to neighbor
    gs = { (start.x, start.y): 0 }
    # holds score from current node to end node
    fs = { (start.x, start.y): heuristic((start.x, start.y), (end.x, end.y)) }
    
    heappush(heap, (fs[(start.x, start.y)], (start.x, start.y)))

    while heap:
        current = heappop(heap)[1]
        closed.add(current)
        # found node: return reversed path

        if current == (end.x, end.y):
            for p in path:
                yield p, 2
            data = []
            while current in path:
                data.append(current)
                current = path[current]
            data.reverse()
            for d in data:
                yield d, 3
            return

        for i, j in squares(exclude_center=True):
            neighbor = (current[0] + i, current[1] + j)
            new_g = gs[current] + heuristic(current, neighbor)
            tile = tiles.get(neighbor, None)

            if not tile or tile in ('#', '+'):
                continue
                
            if neighbor in closed and new_g >= gs.get(neighbor, 0):
                continue

            faster = new_g < gs.get(neighbor, 0)
            unexplored = neighbor not in (i[1] for i in heap)
            if faster or unexplored:
                path[neighbor] = current
                gs[neighbor] = new_g
                fs[neighbor] = new_g + heuristic(neighbor, (end.x, end.y))
                heappush(heap, (fs[neighbor], neighbor))
    for p in path:
        yield p, 2

def bresenhams(tiles, start, end):
     # Setup initial conditions
    x1, y1 = start.x, start.y
    x2, y2 = end.x, end.y
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def pathfind(engine, start, end, pathfinder=astar):
    """Wrapper for ecs engine to use astar"""
    tiles = {
        (position.x, position.y)
            for _, position in join_drop_key(engine.tiles,engine.positions)
                if not position.blocks_movement
    }
    path = pathfinder(tiles, start, end)
    return path
