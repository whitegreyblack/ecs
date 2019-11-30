# raycast.py

"""
Uses raycast algorithm to determine visibility
"""

import math
import time
from source.tables import sintable, costable

from source.common import j, join, join_drop_key


# -- helper functions -- 
# TODO: modify print to be an output function so that it can be piped
def no_tilemap_error(world_id, components):
    print(f"""\n
Exception:
    Could not find tilemap for id: {world_id}. 
    Tilemaps: {components}")"""[1:]
    )

def distance(x, y, a, b, d=10) -> float:
    return math.sqrt((x - a) ** 2 + (y - b) ** 2)

# 22    0.382    0.017    0.898    0.041 raycast.py:26(<listcomp>)
def get_tiles(engine, x0, x1, y0, y1) -> list:
    tiles = []
    for v, p in join_drop_key(engine.visibilities, engine.positions):
        if (p.map_id == engine.world.id and x0 <= p.x < x1 and y0 <= p.y < y1):
            tiles.append((v, p))
    return tiles
    # return [
    #     (v, p)
    #         for v, p in join_drop_key(
    #             engine.visibilities,
    #             engine.positions
    #         )
    #         if p.map_id == engine.world.id
    #             and x0 <= p.x < x1
    #             and y0 <= p.y < y1
    # ]

def get_blocked(tiles) -> set:
    return {
        (position.x, position.y)
            for _, position in tiles
                if position.blocks_movement
    }

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
    return lighted

def raycast2(tiles, blocked, width, height, player):
    """Sends out 120 rays (more if needed) where each ray is a degree"""
    # main algo to determine if light touches a block
    tiles[(player.x, player.y)].level = 2
    for i in range(0, 361, 3):
        ax = sintable[i]
        ay = costable[i]
        # pull values out so access is localized
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

"""
Difference in cast_light1 vs castlight2 is the tiles variable in cl1 is a list and cl2 is a set
"""

# `timings for raycast`
# 15    0.723    0.048    1.573    0.105 raycast.py:135(<listcomp>) (500x100 map)
# 10    0.175    0.017    0.365    0.037 raycast.py:137(<listcomp>) (200x80 map)
# 24    0.040    0.002    0.075    0.003 raycast.py:139(<listcomp>) (58x17 map)
def cast_light(engine, x0, x1, y0, y1, tilebuilder=get_tiles, blockfunc=get_blocked, raycaster=raycast):
    """Wrapper for raycast so that engine is not a parameter to raycast"""
    player = engine.positions.find(engine.player)
    tilemap = engine.tilemaps.find(engine.world.id)
    
    if not tilemap:
        no_tilemap_error(engine.world.id, engine.tilemaps.components.keys())
        exit(0)

    tiles = tilebuilder(engine, x0, x1, y0, y1)
    blocked = get_blocked(tiles)
    engine.tiles_in_view = raycaster(tiles, blocked, tilemap.width, tilemap.height, player)

def cast_light2(engine, x0, x1, y0, y1, raycaster=raycast2):
    """Wrapper for raycast so that engine is not a parameter to raycast"""
    player = engine.positions.find(engine.player)
    tilemap = engine.tilemaps.find(engine.world.id)

    if not tilemap:
        no_tilemap_error(engine.world.id, engine.tilemaps.components.keys())
        exit(0)
    
    tiles = dict()
    blocked = set()
    
    for v, p in join_drop_key(engine.visibilities, engine.positions):
        if (p.map_id == engine.world.id and x0 <= p.x < x1 and y0 <= p.y < y1):
            v.level = max(0, min(v.level, 1))
            tiles[(p.x, p.y)] = v
            if p.blocks_movement:
                blocked.add((p.x, p.y))
    raycaster(tiles, blocked, tilemap.width, tilemap.height, player)

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

191 x 50 ~ 9550 tiles
Timing comparisons between raycast and cast_light methods in python and c
+-------------+-------------+-------------+
| cast_light1 | cast_light2 | cast_light  |
| raycaster1  | raycaster2  | raycast_c   |
+-------------+-------------+-------------+
| 1> 0.018982 | 2> 0.017984 | 3> 0.016984 |
| 1> 0.022980 | 2> 0.022979 | 3> 0.016985 |
| 1> 0.023978 | 2> 0.019981 | 3> 0.016983 |
| 1> 0.021981 | 2> 0.018989 | 3> 0.016984 |
| 1> 0.021984 | 2> 0.018983 | 3> 0.016984 |
| 1> 0.024325 | 2> 0.020980 | 3> 0.016985 |
| 1> 0.022976 | 2> 0.017984 | 3> 0.017987 |
| 1> 0.024423 | 2> 0.020980 | 3> 0.016984 |
| 1> 0.021486 | 2> 0.018985 | 3> 0.016984 |
| 1> 0.024980 | 2> 0.018982 | 3> 0.017984 |
| 1> 0.022985 | 2> 0.018983 | 3> 0.016984 |
| 1> 0.022980 | 2> 0.021979 | 3> 0.016985 |
| 1> 0.022981 | 2> 0.023978 | 3> 0.016985 |
| 1> 0.022985 | 2> 0.021979 | 3> 0.016989 |
| 1> 0.022980 | 2> 0.019981 | 3> 0.016984 |
| 1> 0.021979 | 2> 0.028974 | 3> 0.021978 |
| 1> 0.022982 | 2> 0.019983 | 3> 0.016985 |
| 1> 0.022988 | 2> 0.020980 | 3> 0.016982 |
| 1> 0.022990 | 2> 0.021979 | 3> 0.016984 |
| 1> 0.023980 | 2> 0.019981 | 3> 0.016985 |
| 1> 0.023982 | 2> 0.021978 | 3> 0.017984 |
| 1> 0.023985 | 2> 0.022978 | 3> 0.016984 |
| 1> 0.018984 | 2> 0.022977 | 3> 0.016985 |
| 1> 0.021987 | 2> 0.024976 | 3> 0.016985 |
| 1> 0.022981 | 2> 0.022978 | 3> 0.016982 |
| 1> 0.023986 | 2> 0.021979 | 3> 0.016984 |
| 1> 0.022984 | 2> 0.020980 | 3> 0.017984 |
| 1> 0.022983 | 2> 0.021980 | 3> 0.016988 |
| 1> 0.022982 | 2> 0.021979 | 3> 0.016993 |
| 1> 0.022973 | 2> 0.017984 | 3> 0.016985 |
| 1> 0.022985 | 2> 0.018983 | 3> 0.016984 |
| 1> 0.023973 | 2> 0.022978 | 3> 0.016984 |
| 1> 0.026975 | 2> 0.028973 | 3> 0.032970 |
| 1> 0.029974 | 2> 0.024976 | 3> 0.017983 |
| 1> 0.031970 | 2> 0.024976 | 3> 0.026978 |
| 1> 0.020984 | 2> 0.018982 | 3> 0.027973 |
| 1> 0.032970 | 2> 0.022977 | 3> 0.016985 |
| 1> 0.022975 | 2> 0.021487 | 3> 0.017984 |
| 1> 0.022980 | 2> 0.021981 | 3> 0.016983 |
| 1> 0.018985 | 2> 0.018982 | 3> 0.016984 |
| 1> 0.022982 | 2> 0.018984 | 3> 0.016983 |
| 1> 0.023985 | 2> 0.023979 | 3> 0.017983 |
| 1> 0.023974 | 2> 0.019981 | 3> 0.017986 |
| 1> 0.022976 | 2> 0.017983 | 3> 0.016985 |
| 1> 0.022985 | 2> 0.022285 | 3> 0.016984 |
| 1> 0.033969 | 2> 0.018986 | 3> 0.017805 |
| 1> 0.022986 | 2> 0.022978 | 3> 0.017982 |
| 1> 0.023977 | 2> 0.019982 | 3> 0.017983 |
| 1> 0.022976 | 2> 0.020980 | 3> 0.016985 |
| 1> 0.023975 | 2> 0.021979 | 3> 0.016987 |
| 1> 0.020984 | 2> 0.018983 | 3> 0.016984 |
| 1> 0.018986 | 2> 0.018981 | 3> 0.016984 |
| 1> 0.023983 | 2> 0.017983 | 3> 0.016989 |
| 1> 0.022975 | 2> 0.021980 | 3> 0.016985 |
| 1> 0.022978 | 2> 0.017984 | 3> 0.016984 |
| 1> 0.023984 | 2> 0.022492 | 3> 0.016985 |
| 1> 0.021982 | 2> 0.020980 | 3> 0.016984 |
| 1> 0.022983 | 2> 0.020980 | 3> 0.017985 |
| 1> 0.027975 | 2> 0.019982 | 3> 0.020981 |
| 1> 0.022985 | 2> 0.022979 | 3> 0.016984 |
| 1> 0.022976 | 2> 0.021981 | 3> 0.016983 |
| 1> 0.021979 | 2> 0.020981 | 3> 0.016985 |
| 1> 0.022979 | 2> 0.021981 | 3> 0.016984 |
| 1> 0.019985 | 2> 0.017984 | 3> 0.015985 |
| 1> 0.022985 | 2> 0.018981 | 3> 0.016983 |
| 1> 0.022984 | 2> 0.020980 | 3> 0.016984 |
| 1> 0.022974 | 2> 0.018982 | 3> 0.016982 |
+-------------+-------------+-------------+
+-------------+-------------+
| 1> 0.003996 | 2> 0.004995 |
| 1> 0.005000 | 2> 0.004996 |
| 1> 0.005997 | 2> 0.004996 |
| 1> 0.003998 | 2> 0.003994 |
| 1> 0.004995 | 2> 0.005994 |
| 1> 0.005006 | 2> 0.004995 |
| 1> 0.004996 | 2> 0.005994 |
| 1> 0.006999 | 2> 0.004995 |
| 1> 0.005998 | 2> 0.005001 |
| 1> 0.005998 | 2> 0.004996 |
| 1> 0.004997 | 2> 0.005994 |
| 1> 0.004997 | 2> 0.004995 |
| 1> 0.005992 | 2> 0.005997 |
| 1> 0.004996 | 2> 0.005995 |
| 1> 0.007001 | 2> 0.004996 |
| 1> 0.005997 | 2> 0.004992 |
| 1> 0.005998 | 2> 0.004996 |
| 1> 0.005994 | 2> 0.003996 |
| 1> 0.006995 | 2> 0.008992 |
| 1> 0.007991 | 2> 0.007993 |
+-------------+-------------+
(list comprehension) ^
-- vs --
(for loop) v
+-------------+-------------+
| 1> 0.005993 | 2> 0.005996 |
| 1> 0.005987 | 2> 0.005995 |
| 1> 0.006000 | 2> 0.005995 |
| 1> 0.006002 | 2> 0.005994 |
| 1> 0.004986 | 2> 0.005993 |
| 1> 0.005000 | 2> 0.006992 |
| 1> 0.005999 | 2> 0.005995 |
| 1> 0.006002 | 2> 0.006992 |
| 1> 0.005994 | 2> 0.005994 |
| 1> 0.005991 | 2> 0.004995 |
| 1> 0.006971 | 2> 0.005994 |
| 1> 0.005994 | 2> 0.005995 |
| 1> 0.005996 | 2> 0.005994 |
| 1> 0.005999 | 2> 0.005994 |
| 1> 0.006003 | 2> 0.005996 |
| 1> 0.004996 | 2> 0.005994 |
| 1> 0.005992 | 2> 0.004996 |
| 1> 0.005998 | 2> 0.004995 |
| 1> 0.005996 | 2> 0.004994 |
| 1> 0.005001 | 2> 0.004994 |
| 1> 0.005001 | 2> 0.005994 |
| 1> 0.005999 | 2> 0.004996 |
| 1> 0.005998 | 2> 0.004995 |
| 1> 0.005998 | 2> 0.004996 |
+-------------+-------------+
"""
