# raycast.py

"""
Uses raycast algorithm to determine visibility
"""

import math
import time
from array import array

from source.common import j, join, join_drop_key

sintable = array('f', [
    0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453,
    0.12187, 0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192,
    0.25882, 0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461,
    0.39073, 0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000,
    0.51504, 0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566,
    0.62932, 0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934,
    0.73135, 0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902,
    0.81915, 0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295,
    0.89101, 0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969,
    0.94552, 0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815,
    0.98163, 0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756,
    0.99863, 0.99939, 0.99985, 1.00000, 0.99985, 0.99939, 0.99863, 0.99756,
    0.99619, 0.99452, 0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815,
    0.97437, 0.97030, 0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969,
    0.93358, 0.92718, 0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295,
    0.87462, 0.86603, 0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902,
    0.79864, 0.78801, 0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934,
    0.70711, 0.69466, 0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566,
    0.60182, 0.58779, 0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000,
    0.48481, 0.46947, 0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461,
    0.35837, 0.34202, 0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192,
    0.22495, 0.20791, 0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453,
    0.08716, 0.06976, 0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490,
    -0.05234, -0.06976, -0.08716, -0.10453, -0.12187, -0.13917, -0.15643,
    -0.17365, -0.19081, -0.20791, -0.22495, -0.24192, -0.25882, -0.27564,
    -0.29237, -0.30902, -0.32557, -0.34202, -0.35837, -0.37461, -0.39073,
    -0.40674, -0.42262, -0.43837, -0.45399, -0.46947, -0.48481, -0.50000,
    -0.51504, -0.52992, -0.54464, -0.55919, -0.57358, -0.58779, -0.60182,
    -0.61566, -0.62932, -0.64279, -0.65606, -0.66913, -0.68200, -0.69466,
    -0.70711, -0.71934, -0.73135, -0.74314, -0.75471, -0.76604, -0.77715,
    -0.78801, -0.79864, -0.80902, -0.81915, -0.82904, -0.83867, -0.84805,
    -0.85717, -0.86603, -0.87462, -0.88295, -0.89101, -0.89879, -0.90631,
    -0.91355, -0.92050, -0.92718, -0.93358, -0.93969, -0.94552, -0.95106,
    -0.95630, -0.96126, -0.96593, -0.97030, -0.97437, -0.97815, -0.98163,
    -0.98481, -0.98769, -0.99027, -0.99255, -0.99452, -0.99619, -0.99756,
    -0.99863, -0.99939, -0.99985, -1.00000, -0.99985, -0.99939, -0.99863,
    -0.99756, -0.99619, -0.99452, -0.99255, -0.99027, -0.98769, -0.98481,
    -0.98163, -0.97815, -0.97437, -0.97030, -0.96593, -0.96126, -0.95630,
    -0.95106, -0.94552, -0.93969, -0.93358, -0.92718, -0.92050, -0.91355,
    -0.90631, -0.89879, -0.89101, -0.88295, -0.87462, -0.86603, -0.85717,
    -0.84805, -0.83867, -0.82904, -0.81915, -0.80902, -0.79864, -0.78801,
    -0.77715, -0.76604, -0.75471, -0.74314, -0.73135, -0.71934, -0.70711,
    -0.69466, -0.68200, -0.66913, -0.65606, -0.64279, -0.62932, -0.61566,
    -0.60182, -0.58779, -0.57358, -0.55919, -0.54464, -0.52992, -0.51504,
    -0.50000, -0.48481, -0.46947, -0.45399, -0.43837, -0.42262, -0.40674,
    -0.39073, -0.37461, -0.35837, -0.34202, -0.32557, -0.30902, -0.29237,
    -0.27564, -0.25882, -0.24192, -0.22495, -0.20791, -0.19081, -0.17365,
    -0.15643, -0.13917, -0.12187, -0.10453, -0.08716, -0.06976, -0.05234,
    -0.03490, -0.01745, -0.00000
])
 
costable = array('f', [
    1.00000, 0.99985, 0.99939, 0.99863, 0.99756, 0.99619, 0.99452,
    0.99255, 0.99027, 0.98769, 0.98481, 0.98163, 0.97815, 0.97437, 0.97030,
    0.96593, 0.96126, 0.95630, 0.95106, 0.94552, 0.93969, 0.93358, 0.92718,
    0.92050, 0.91355, 0.90631, 0.89879, 0.89101, 0.88295, 0.87462, 0.86603,
    0.85717, 0.84805, 0.83867, 0.82904, 0.81915, 0.80902, 0.79864, 0.78801,
    0.77715, 0.76604, 0.75471, 0.74314, 0.73135, 0.71934, 0.70711, 0.69466,
    0.68200, 0.66913, 0.65606, 0.64279, 0.62932, 0.61566, 0.60182, 0.58779,
    0.57358, 0.55919, 0.54464, 0.52992, 0.51504, 0.50000, 0.48481, 0.46947,
    0.45399, 0.43837, 0.42262, 0.40674, 0.39073, 0.37461, 0.35837, 0.34202,
    0.32557, 0.30902, 0.29237, 0.27564, 0.25882, 0.24192, 0.22495, 0.20791,
    0.19081, 0.17365, 0.15643, 0.13917, 0.12187, 0.10453, 0.08716, 0.06976,
    0.05234, 0.03490, 0.01745, 0.00000, -0.01745, -0.03490, -0.05234, -0.06976,
    -0.08716, -0.10453, -0.12187, -0.13917, -0.15643, -0.17365, -0.19081,
    -0.20791, -0.22495, -0.24192, -0.25882, -0.27564, -0.29237, -0.30902,
    -0.32557, -0.34202, -0.35837, -0.37461, -0.39073, -0.40674, -0.42262,
    -0.43837, -0.45399, -0.46947, -0.48481, -0.50000, -0.51504, -0.52992,
    -0.54464, -0.55919, -0.57358, -0.58779, -0.60182, -0.61566, -0.62932,
    -0.64279, -0.65606, -0.66913, -0.68200, -0.69466, -0.70711, -0.71934,
    -0.73135, -0.74314, -0.75471, -0.76604, -0.77715, -0.78801, -0.79864,
    -0.80902, -0.81915, -0.82904, -0.83867, -0.84805, -0.85717, -0.86603, 
    -0.87462, -0.88295, -0.89101, -0.89879, -0.90631, -0.91355, -0.92050,
    -0.92718, -0.93358, -0.93969, -0.94552, -0.95106, -0.95630, -0.96126,
    -0.96593, -0.97030, -0.97437, -0.97815, -0.98163, -0.98481, -0.98769,
    -0.99027, -0.99255, -0.99452, -0.99619, -0.99756, -0.99863, -0.99939,
    -0.99985, -1.00000, -0.99985, -0.99939, -0.99863, -0.99756, -0.99619,
    -0.99452, -0.99255, -0.99027, -0.98769, -0.98481, -0.98163, -0.97815,
    -0.97437, -0.97030, -0.96593, -0.96126, -0.95630, -0.95106, -0.94552,
    -0.93969, -0.93358, -0.92718, -0.92050, -0.91355, -0.90631, -0.89879,
    -0.89101, -0.88295, -0.87462, -0.86603, -0.85717, -0.84805, -0.83867,
    -0.82904, -0.81915, -0.80902, -0.79864, -0.78801, -0.77715, -0.76604,
    -0.75471, -0.74314, -0.73135, -0.71934, -0.70711, -0.69466, -0.68200,
    -0.66913, -0.65606, -0.64279, -0.62932, -0.61566, -0.60182, -0.58779,
    -0.57358, -0.55919, -0.54464, -0.52992, -0.51504, -0.50000, -0.48481,
    -0.46947, -0.45399, -0.43837, -0.42262, -0.40674, -0.39073, -0.37461,
    -0.35837, -0.34202, -0.32557, -0.30902, -0.29237, -0.27564, -0.25882,
    -0.24192, -0.22495, -0.20791, -0.19081, -0.17365, -0.15643, -0.13917,
    -0.12187, -0.10453, -0.08716, -0.06976, -0.05234, -0.03490, -0.01745,
    -0.00000, 0.01745, 0.03490, 0.05234, 0.06976, 0.08716, 0.10453, 0.12187,
    0.13917, 0.15643, 0.17365, 0.19081, 0.20791, 0.22495, 0.24192, 0.25882,
    0.27564, 0.29237, 0.30902, 0.32557, 0.34202, 0.35837, 0.37461, 0.39073,
    0.40674, 0.42262, 0.43837, 0.45399, 0.46947, 0.48481, 0.50000, 0.51504,
    0.52992, 0.54464, 0.55919, 0.57358, 0.58779, 0.60182, 0.61566, 0.62932,
    0.64279, 0.65606, 0.66913, 0.68200, 0.69466, 0.70711, 0.71934, 0.73135,
    0.74314, 0.75471, 0.76604, 0.77715, 0.78801, 0.79864, 0.80902, 0.81915,
    0.82904, 0.83867, 0.84805, 0.85717, 0.86603, 0.87462, 0.88295, 0.89101,
    0.89879, 0.90631, 0.91355, 0.92050, 0.92718, 0.93358, 0.93969, 0.94552,
    0.95106, 0.95630, 0.96126, 0.96593, 0.97030, 0.97437, 0.97815, 0.98163,
    0.98481, 0.98769, 0.99027, 0.99255, 0.99452, 0.99619, 0.99756, 0.99863,
    0.99939, 0.99985, 1.00000
])

def no_tilemap_error(world_id, components):
    print(f"""\n
Exception:
    Could not find tilemap for id: {world_id}. 
    Tilemaps: {components}")"""[1:]
    )

def distance(x, y, a, b, d=10):
    return math.sqrt((x - a) ** 2 + (y - b) ** 2)

# `timings for raycast`
# 15    0.723    0.048    1.573    0.105 raycast.py:135(<listcomp>) (500x100 map)
# 10    0.175    0.017    0.365    0.037 raycast.py:137(<listcomp>) (200x80 map)
# 24    0.040    0.002    0.075    0.003 raycast.py:139(<listcomp>) (58x17 map)
def cast_light(engine, x0, x1, y0, y1):
    """Wrapper for raycast so that engine is not a parameter to raycast"""
    player = engine.positions.find(engine.player)
    tilemap = engine.tilemaps.find(engine.world.id)
    if not tilemap:
        no_tilemap_error(engine.world.id, engine.tilemaps.components.keys())
        exit(0)
    tiles = [
        (v, p)
            for v, p in join_drop_key(
                engine.visibilities,
                engine.positions
            )
            if p.map_id == engine.world.id
                and x0 <= p.x < x1
                and y0 <= p.y < y1
    ]
    blocked = {
        (position.x, position.y)
            for _, position in tiles
                if position.blocks_movement
    }
    raycast(tiles, blocked, tilemap.width, tilemap.height, player)

def cast_light2(engine, x0, x1, y0, y1):
    """Wrapper for raycast so that engine is not a parameter to raycast"""
    player = engine.positions.find(engine.player)
    tilemap = engine.tilemaps.find(engine.world.id)
    if not tilemap:
        no_tilemap_error(engine.world.id, engine.tilemaps.components.keys())
        exit(0)
    tiles = dict()
    blocked = set()
    for v, p in join_drop_key(engine.visibilities, engine.positions):
        if (p.map_id == engine.world.id 
            and x0 <= p.x < x1
            and y0 <= p.y < y1
        ):
            v.level = max(0, min(v.level, 1))
            tiles[(p.x, p.y)] = v
            if p.blocks_movement:
                blocked.add((p.x, p.y))
    raycast2(tiles, blocked, tilemap.width, tilemap.height, player)

def raycast(tiles, blocked, width, height, player):
    """Sends out 120 rays (more if needed) where each ray is a degree"""
    # main algo to determine if light touches a block
    lighted = {(player.x, player.y)}
    for i in range(0, 361, 3):
        ax = sintable[i]
        ay = costable[i]

        x = player.x
        y = player.y
        for z in range(10):
            x += ax
            y += ay
            if not (0 <= x < width and 0 <= y < height):
                break
            rx = int(round(x))
            ry = int(round(y))
            lighted.add((rx, ry))
            if (rx, ry) in blocked:
                break
    
    # all blocks touched have their visiblities set to max visibility
    for visible, position in tiles:
        if (position.x, position.y) in lighted:
            visible.level = 2
        else:
            visible.level = max(0, min(visible.level, 1))

def raycast2(tiles, blocked, width, height, player):
    """Sends out 120 rays (more if needed) where each ray is a degree"""
    # main algo to determine if light touches a block
    tiles[(player.x, player.y)].level = 2
    for i in range(0, 361, 3):
        ax = sintable[i]
        ay = costable[i]

        x = player.x
        y = player.y
        for z in range(10):
            x += ax
            y += ay
            if not (0 <= x < width and 0 <= y < height):
                break
            rx = int(round(x))
            ry = int(round(y))
            if (rx, ry) in tiles and tiles[(rx, ry)].level < 2:
                tiles[(rx, ry)].level = 2
            if (rx, ry) in blocked:
                break

""" `script specific timings`
58 x 17 = ~986
    1    0.002    0.002    0.005    0.005 raycast.py:140(<listcomp>)
100 x 25 = ~2500:
    1    0.002    0.002    0.005    0.005 raycast.py:140(<listcomp>)
100 x 50 = ~5000
       1    0.004    0.004    0.010    0.010 raycast.py:140(<listcomp>)
    5000    0.002    0.000    0.002    0.000 raycast.py:224(<lambda>)
    ---
    5000    0.002    0.000    0.002    0.000 raycast.py:237(<lambda>)
       1    0.010    0.010    0.021    0.021 raycast.py:131(cast_light)
       1    0.001    0.001    0.001    0.001 raycast.py:167(raycast)
       1    0.020    0.020    0.041    0.041 raycast.py:131(cast_light)
100 x 100 = ~10000 (without listcomp)
    10000    0.005    0.000    0.005    0.000 raycast.py:246(<lambda>)
        5    0.148    0.030    0.302    0.060 raycast.py:131(cast_light)
        5    0.008    0.002    0.011    0.002 raycast.py:167(raycast)
100 x 100 = ~10000 (with listcomp)
    10000    0.006    0.000    0.006    0.000 raycast.py:247(<lambda>)
        5    0.000    0.000    0.339    0.068 raycast.py:131(cast_light)
        5    0.102    0.020    0.215    0.043 raycast.py:140(<listcomp>)
        5    0.068    0.014    0.113    0.023 raycast.py:167(raycast)

    10000    0.005    0.000    0.005    0.000 raycast.py:248(<lambda>) 
        5    0.000    0.000    0.273    0.055 raycast.py:131(cast_light)
        5    0.083    0.017    0.169    0.034 raycast.py:140(<listcomp>)
        5    0.055    0.011    0.091    0.018 raycast.py:167(raycast)

        5    0.000    0.000    0.205    0.041 raycast.py:131(cast_light)
        5    0.065    0.013    0.133    0.027 raycast.py:140(<listcomp>)
        5    0.008    0.002    0.008    0.002 raycast.py:160(<setcomp>)
        5    0.041    0.008    0.064    0.013 raycast.py:167(raycast)

    10000    0.005    0.000    0.005    0.000 raycast.py:256(<lambda>)
        5    0.000    0.000    0.204    0.041 raycast.py:131(cast_light)
        5    0.064    0.013    0.132    0.026 raycast.py:140(<listcomp>)
        5    0.008    0.002    0.008    0.002 raycast.py:160(<setcomp>)
cast_light1 vs cast_light2
    0> 0.020981311798095703
    0> 0.020981311798095703
    0> 0.02198028564453125
    0> 0.02198004722595215
    0> 0.0209810733795166
    SUM0> 0.021380805969238283
    1> 0.02897334098815918
    1> 0.03496837615966797
    1> 0.02996993064880371
    1> 0.04096269607543945
    1> 0.029972553253173828
    SUM1> 0.03296937942504883
"""

if __name__ == "__main__":
    import copy
    import random
    import time
    from source.common import scroll
    from source.ecs.components import Position, Visibility, TileMap
    from source.ecs.managers import ComponentManager, EntityManager
    from source.engine import Engine
    from source.maps import generate_poisson_array, array_to_matrix, dimensions, string
    from source.graph import WorldGraph, DungeonNode

    # define engine
    engine = Engine(
        components=(Position, Visibility), 
        systems=None, 
        terminal=None, 
        keyboard=None
    )

    # define component managers
    engine.positions = ComponentManager(Position)
    engine.visibilities = ComponentManager(Visibility)
    engine.tilemaps = ComponentManager(TileMap)

    # create world to use
    filterer = lambda x: 4 <= x < 5
    x, y = 191, 24
    m = array_to_matrix(
        generate_poisson_array(x, y), 
        width=x, height=y, 
        filterer=filterer
    )

    # define world
    w = engine.entities.create()
    engine.world = WorldGraph({w: DungeonNode(w)}, w)

    # define map properties
    t = TileMap(x, y)
    engine.tilemaps.add(w, t)

    # define map objects
    for y, row in enumerate(m):
        for x, cell in enumerate(row):

            e = engine.entities.create()
            engine.positions.add(e, Position(
                x, y, 
                map_id=w,
                blocks_movement=cell is '#'
            ))
            engine.visibilities.add(e, Visibility())
    
    # define player
    e = engine.entities.create()
    engine.player = e
    
    # define random unblocked position
    walkable = [
        (p.x, p.y)
            for p in engine.positions.components.values()
                if not p.blocks_movement
    ]
    random.shuffle(walkable)
    p = Position(*walkable.pop(0))
    engine.positions.add(e, p)

    # loop until keyboard interrupt th  en print timing results for both methods
    ss = []
    ts = []
    iters = 10
    n = copy.deepcopy(m)
    while True:

        # get camera offsets
        off_x = scroll(p.x, 57, x)
        off_y = scroll(p.y, 17, y)

        for recorder in (ss, ts):
            # do some calculations
            t = time.time()
            cast_light(engine, off_x, 57 + off_x, off_y, 17 + off_y)
            s = time.time()

            # save the timing result
            recorder.append(s - t)

            # edit the map buffer with seen positions and player position
            for p, v in join_drop_key(engine.positions, engine.visibilities):
                m[p.y][p.x] = ' ' if v.level == 0 else n[p.y][p.x]
            p = engine.positions.find(engine.player)
            m[p.y][p.x] = '@'

            # render
            print(string(m))

        try:
            c = input().strip()
        except KeyboardInterrupt:
            break

        p = engine.positions.find(engine.player)
        if c == 'w' and n[p.y-1][p.x] == '.':
            m[p.y][p.x] = '.'
            p.y += -1
        if c == 'a' and n[p.y][p.x-1] == '.':
            m[p.y][p.x] = '.'
            p.x += -1
        if c == 's' and n[p.y+1][p.x] == '.':
            m[p.y][p.x] = '.'
            p.y += 1
        if c == 'd' and n[p.y][p.x+1] == '.':
            m[p.y][p.x] = '.'
            p.x += 1

    # output timing results
    for s, t in zip(ss, ts):
        print(f'1> {s:04f} | 2> {s:04f}')
    print(f'S> {sum(ss) / len(ss):04f} | S> {sum(ts) / len(ts):04f}')
