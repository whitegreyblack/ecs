# minimap.py

import math
import random

from config import DIFFICULTY_MULTIPLIER, MAX_RETRY, MAX_ROOMS
from model import GraphContext, Point, RenderContext, Ruler
from path import random_path as path


def output(matrix):
    return '\n'.join(''.join(row) for row in matrix)

def build_graph_context(graph) -> (Point, Point):
    # min of both axes using most points with min x and min y
    points = list(graph.keys())
    points.sort(key=lambda x: x[0])
    x1, x2 = points[0][0], points[-1][0]
    points.sort(key=lambda x: x[1])
    y1, y2 = points[0][1], points[-1][1]
    return GraphContext(Point(x1, y1), Point(x2, y2))

def debug(placement_type, buffer, p, q, graph):
    print(f"""
Out of bounds build error: {placement_type}:
    x={p.x}, y={p.y}, tx={q.x}, ty={q.y}
    xrange: {graph.nw.x} -> {graph.se.x}, yrange: {graph.nw.y} -> {graph.se.y}
    buffer: {len(buffer[0])} x {len(buffer)}"""[1:])
    print(output(buffer))
    exit(1)

def place_structure(placement_type, buffer, char, p, q, graph):
    try:
        buffer[q.y][q.x] = char
    except IndexError:
        debug(placement_type, buffer, p, q, graph)

def distance(p, q):
    return math.sqrt((p.x + q.x)**2 + (p.y + q.y)**2)

def analyze_graph(points):
    leaves = []
    cuts = []

    for p, ns in points.items():
        if len(ns) != 1:
            continue
        leaves.append(p)
        nl = list(ns)
    
        # if len(points[nl[0]]) == 2:
        #     print('neighbor is connected')
        # while len(points[list(ns)[0]]) == 2:
        #     for nns in points[list(ns)[0]]:
        #         if nns == p:
        #             continue
        #         if len(points[nns]) != 2:
        #             break
        #         p = ns
        #         ns = points[nns]
        #     cuts.append(nns)
    
    print(f"""
graph: 
    random starting point (X)
    # of points (o): {len(points)}
    # of leaves (L): {len(leaves)}
    # of valid cuts: {len(cuts)}"""[1:])
    return leaves, cuts

def build_nodes(difficulty):
    max_rooms = MAX_ROOMS * DIFFICULTY_MULTIPLIER[difficulty]
    while True:
        x, y, cur_retry = 0, 0, 0
        points = { (x, y): set() }
        
        while len(points) < max_rooms and cur_retry < MAX_RETRY:
            cur_retry += 1

            for dx, dy in path():
                tx, ty = x + dx, y + dy
                points[(x, y)].add((tx, ty))
            
                if (tx, ty) in points:
                    points[(tx, ty)].add((x, y))
                else:
                    points[(tx, ty)] = {(x, y)}
                x, y = tx, ty
        
        leaves, cuts = analyze_graph(points)

        if len(cuts) < 1:
            break

    up_stairs, down_stairs = None, None
    cur_retry = 0

    while cur_retry < MAX_RETRY:
        pts = list(points.keys())
        random.shuffle(pts)
        up_stairs, down_stairs, *_ = pts
    
        if distance(Point(*up_stairs), Point(*down_stairs)) > math.sqrt(8):
            break
    
        cur_retry += 1

    return points, up_stairs, down_stairs, leaves, cuts

def map_graph(points, up_stairs, down_stairs, leaves, cuts, render):
    if not leaves:
        leaves = []

    graph = build_graph_context(points)
    width = (graph.dimensions.width + 1) * (render.width + 1) - render.width + 2
    height = (graph.dimensions.height + 1) * (render.height + 1) - render.height + 2
    buffer = [['.' for _ in range(width)] for _ in range(height)]

    for (x, y), path in points.items():
        char = 'o'
        tx = (x - graph.nw.x) * (render.width + 1) + 1
        ty = (y - graph.nw.y) * (render.height + 1) + 1
        if (x, y) == up_stairs:
            char = '<'
        elif (x, y) == down_stairs:
            char = '>'
        elif (x, y) == (0, 0):
            char = 'X'
        elif (x, y) in leaves:
            char = 'L'
        elif (x, y) in cuts:
            char = 'C'

        place_structure('room', buffer, char, Point(x, y), Point(tx, ty), graph)

        for nx, ny in path:
            dx, dy = nx - x, ny - y
            
            if (dx, dy) in ((-1, 0), (1, 0)):
                char = '-'
                hallway = [ (tx + dx * i, ty + dy) for i in range(1, render.width + 1) ]
            else:
                char = '|'
                hallway = [ (tx + dx, ty + dy * j) for j in range(1, render.height + 1) ]

            for ttx, tty in hallway:
                place_structure('room', buffer, char, Point(x, y), Point(ttx, tty), graph)

    print(output(buffer))
    # for p, k in sorted(points.items(), key=lambda x: len(x[1])):
    #     print(p, k)

if __name__ == "__main__":
    map_graph(*build_nodes(difficulty=0), Ruler(3, 1))
