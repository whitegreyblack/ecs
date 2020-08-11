# demo/raycast.py

import copy
import random
import time

# from raycast import raycast as c_raycast
from source.common import join_drop_key, scroll
from source.ecs.components import Position, TileMap, Visibility
from source.ecs.managers import ComponentManager, EntityManager
from source.engine import Engine
from source.generate import (array_to_matrix, dimensions,
                             generate_poisson_array, string)
from source.graph import DungeonNode, WorldGraph
from source.raycast import cast_light, cast_light2
from source.raycast import raycast as py_raycast
from source.raycast import raycast2 as py_raycast2

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
# x, y = 191, 100 
x, y = 58, 17
m = array_to_matrix(
    generate_poisson_array(x, y), 
    width=x, height=y, 
    filter=filterer
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
            blocks=cell is '#'
        ))
        engine.visibilities.add(e, Visibility())

# define player
e = engine.entities.create()
engine.player = e

# define random unblocked position
walkable = [
    (p.x, p.y)
        for p in engine.positions.components.values()
            if not p.blocks
]
random.shuffle(walkable)
p = Position(*walkable.pop(0))
engine.positions.add(e, p)

# Testing notes: need 4 different combinations
#   | cast_light | cast_light2 |
# --+------------+-------------+
# 1 | py_raycast | py_raycast  |
# 2 | c_raycast  | c_raycast   |
# loop until keyboard interrupt th  en print timing results for both methods
clpy = []
# clc = []
cl2py = []
# cl2c = []
iters = 10
n = copy.deepcopy(m)
combinations = (
    (clpy, cast_light, py_raycast), 
    (cl2py, cast_light2, py_raycast2),
    # (clc, cast_light, c_raycast),
    # (clc, cast_light2, c_raycast)
)
while True:

    # get camera offsets
    off_x = scroll(p.x, 57, x)
    off_y = scroll(p.y, 17, y)

    for recorder, caster, raycaster in combinations:
        # do some calculations
        t = time.time()
        caster(
            engine, 
            off_x, 
            57 + off_x, 
            off_y, 
            17 + off_y, 
            raycaster=raycaster
        )
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
results = '| ' + '\n| '.join(
    ' '.join(
        f'{i+1}> {time:04f} |' 
            for i, time in enumerate((s, t))
    )
    for s, t in zip(clpy, cl2py) #, clc)
)
print(results)
# print(f'S> {sum(clpy) / len(clpy):04f} | S> {sum(cl2py) / len(cl2py):04f}')
