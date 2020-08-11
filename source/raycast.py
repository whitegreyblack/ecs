# raycast.py

"""
    Uses raycast algorithm to determine visibility
"""
import math
import time

from source.common import j, join, join_drop_key
from source.tables import costable, sintable


# -- helper functions --
# TODO: modify print to be an output function so that it can be piped
def no_tilemap_error(world_id, components):
    print(textwrap.dedent(f"""\n
        Exception:
            Could not find tilemap for id: {world_id}.
            Tilemaps: {components}")"""[1:]
    ))

def distance(x, y, a, b, d=10) -> float:
    return math.sqrt((x - a) ** 2 + (y - b) ** 2)

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
                if position.blocks
    }

def raycast(tiles, blocked, width, height, player):
    # start with player position which is always lighted
    lighted = {(player.x, player.y)}
    integer, r = int, round
    for i in range(0, 361, 1):
        ax, ay = sintable[i], costable[i]
        # pull values out so access is localized
        x, y = player.x, player.y
        for z in range(10):
            x += ax
            y += ay
            if not (0 <= x < width and 0 <= y < height):
                break
            rx, ry = integer(r(x)), integer(r(y))
            lighted.add((rx, ry))
            if (rx, ry) in blocked:
                break
    
    # all blocks found have their visiblities set to max visibility else
    # their visibility level is set based on their last visibility level
    for visible, position in tiles:
        if (position.x, position.y) in lighted:
            visible.level = 2
        else:
            visible.level = max(0, min(visible.level, 1))
    return lighted

def cast_light(
        engine,
        x0, x1, y0, y1,
        tilebuilder=get_tiles,
        blockfunc=get_blocked,
        raycaster=raycast
    ):
    """Wrapper for raycast so that engine is not a parameter to raycast"""
    player = engine.positions.find(engine.player)
    tilemap = engine.tilemaps.find(engine.world.id)
    
    if not tilemap:
        no_tilemap_error(engine.world.id, engine.tilemaps.components.keys())
        exit(0)

    tiles = tilebuilder(engine, x0, x1, y0, y1)
    blocked = get_blocked(tiles)
    engine.tiles_in_view = raycaster(
        tiles,
        blocked,
        tilemap.width,
        tilemap.height,
        player
    )

# TODO: more research on which built-in data struct is better: set, list, dict
def raycast2(tiles, blocked, width, height, player):
    # start with player position which is always lighted
    tiles[(player.x, player.y)].level = 2
    integer, r = int, round
    for i in range(0, 361, 1):
        ax, ay = sintable[i], costable[i]
        # pull values out so access is localized
        x, y = player.x, player.y
        for z in range(10):
            x += ax
            y += ay
            if not (0 <= x < width and 0 <= y < height):
                break
            rx, ry = integer(r(x)), integer(r(y))
            if (rx, ry) in tiles and tiles[(rx, ry)].level < 2:
                tiles[(rx, ry)].level = 2
            if (rx, ry) in blocked:
                break

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
            if p.blocks:
                blocked.add((p.x, p.y))
    raycaster(tiles, blocked, tilemap.width, tilemap.height, player)
