# stair_functions

"""Handles stair climbing/descending"""

import random

from source.common import join, join_drop_key, squares
from source.maps import MapType


def go_up(engine, entity):
    """Check if entity position is on stairs. If true go up"""
    went_up = False
    position = engine.positions.find(entity)
    tilemap = engine.tilemaps.find(position.map_id)
    g = join_drop_key(engine.tiles, engine.positions, engine.renders)
    for _, tile_position, render in g:
        if (tile_position.map_id == engine.world.id
            and tile_position == position
            and render.char == '<'):
            break
        else:
            tile_position = None
        
    if not tile_position:
        engine.logger.add('Could not go up since not on stairs')
        return went_up

    old_id = engine.world.id
    up = engine.world.go_up()
    if old_id != engine.world.id:
        engine.map_system.regenerate_map(old_id)
    else:
        engine.logger.add('no parent node.')

    for _, (_, tile_position, render) in join(
        engine.tiles,
        engine.positions,
        engine.renders
    ):
        if (tile_position.map_id == engine.world.id
            and render.char == '>'):
            break
    
    position = tile_position.copy(
        movement_type=position.movement_type,
        blocks=position.blocks
    )
    engine.positions.remove(engine.player)
    engine.positions.add(engine.player, position)
    return True

def go_down(engine, entity):
    """Check if entity position is on stairs. If true go down"""
    went_down = False
    position = engine.positions.find(entity)
    tilemap = engine.tilemaps.find(eid=position.map_id)
    
    # should only return 1 tile/render pair
    g = join_drop_key(engine.tiles, engine.positions, engine.renders)
    for _, tile_position, render in g:
        # tile from current map / same map position as entity / is down stairs
        if (tile_position.map_id == engine.world.id
            and tile_position == position
            and render.char == '>'):
            break
        else:
            tile_position = None
    
    if not tile_position:
        engine.logger.add('Could not go down since not on stairs')
        return went_down
    
    old_id = engine.world.id
    engine.world.go_down()
    if old_id == engine.world.id:
        # TODO: generate child map to go down. For now return False
        # engine.logger.add('Could not go down since no child map')
        # return went_down
        engine.map_system.generate_map(MapType.CAVE)
        engine.world.go_down()
    else:
        engine.map_system.regenerate_map(old_id)

    for _, (_, tile_position, render) in join(
        engine.tiles,
        engine.positions,
        engine.renders
    ):
        # tile from current map / is up stairs
        if (tile_position.map_id == engine.world.id
            and render.char == '<'):
            break

    if not tile_position:
        engine.logger.add('Could not go down since child map has no up stairs')
        return went_down
    
    # send entity to the position of stairs on child map
    position = tile_position.copy(
        movement_type=position.movement_type,
        blocks=position.blocks
    )
    engine.positions.remove(engine.player)
    engine.positions.add(engine.player, position)
    return True
