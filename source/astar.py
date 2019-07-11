# astar.py

"""Implements astar A* pathfinding"""

import math
import time
from collections import namedtuple
from heapq import heappop, heappush

from source.common import distance, join, squares
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

def pathfind(engine, start, end):
    """Wrapper for ecs engine to use astar"""
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
            return data

        closed.add(current)
        for i, j in squares(exclude_center=True):
            neighbor = (current[0] + i, current[1] + j)
            new_g = gs[current] + octile(current, neighbor)
            tile = tiles.get(neighbor, None)

            if not tile or tile in ('#', '+'):
                continue
                
            if neighbor in closed and new_g >= gs.get(neighbor, 0):
                continue

            faster = new_g < gs.get(neighbor, 0)
            unexplored = neighbor not in [i[1] for i in heap]
            if faster or unexplored:
                path[neighbor] = current
                gs[neighbor] = new_g
                fs[neighbor] = new_g + octile(neighbor, (end.x, end.y))
                heappush(heap, (fs[neighbor], neighbor))
    return []

def astar_gui(tiles, start, end):
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
            new_g = gs[current] + octile(current, neighbor)
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
                fs[neighbor] = new_g + octile(neighbor, (end.x, end.y))
                heappush(heap, (fs[neighbor], neighbor))
    for p in path:
        yield p, 2
