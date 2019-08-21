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

# currrent  : 4    0.073    0.018    0.170    0.042 astar.py:25(<dictcomp>)
#           :10    0.194    0.019    0.449    0.045 astar.py:26(<dictcomp>)
# dbg flag 1: 4    0.107    0.027    0.422    0.106 astar.py:26(<dictcomp>)
# w/o key   :15    0.281    0.019    0.634    0.042 astar.py:28(<dictcomp>)
# floor cond:20    0.369    0.018    0.846    0.042 astar.py:29(<dictcomp>)
# expand #/+:13    0.239    0.018    0.543    0.042 astar.py:30(<dictcomp>)
# no renders:35    0.513    0.015    1.189    0.034 astar.py:33(<setcomp>)
# &{:} to {}:19    0.295    0.016    0.676    0.036 astar.py:31(<setcomp>)
def pathfind(engine, start, end):
    """Wrapper for ecs engine to use astar"""
    tiles = {
        (position.x, position.y)
            for _, position in join_drop_key(
                engine.tiles,
                engine.positions
            )
            if not position.blocks_movement
    }
    path = astar(tiles, start, end)
    return path

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
