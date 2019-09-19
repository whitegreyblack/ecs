# door_functions

"""Handles door opening/closing"""

import random
from source.common import join, squares


def open_door(engine, entity):
    """TODO: render log message when opening a door of multiple doors"""
    position = engine.positions.find(entity)
    turn_over = False
    # get all coordinates surrounding current entity position
    coordinates = [
        (position.x + x, position.y + y)
            for x, y in squares(exclude_center=True)
    ]
    g = join(engine.openables, engine.positions, engine.renders, engine.infos)
    doors = {}
    # compare coordinates against entities that can be opened that have a
    # a position x, y value in the coordinates list.
    for openable_id, (openable, coordinate, render, info) in g:
        valid_coordinate = (coordinate.x, coordinate.y) in coordinates
        if valid_coordinate and not openable.opened:
            x = coordinate.x - position.x
            y = coordinate.y - position.y
            doors[(x, y)] = (
                openable_id, 
                openable, 
                coordinate, 
                render, 
                info
            )
    door_to_open = None
    if not doors:
        engine.logger.add(f"No closed doors to open.")
    elif len(doors) == 1:
        door_to_open, = doors.values()
    else:
        engine.logger.add(f"Which door to open?")
        engine.screen.render()
        engine.input_system.process(
            valid_keypresses=set(keypress_to_direction).union(('escape',))
        )
        keypress = engine.get_keypress()
        movement = Movement.keypress_to_direction(keypress)
        # valid direction keypress but not valid door direction
        door = doors.get((movement.x, movement.y), None)
        if not door:
            engine.logger.add(
                f"You cancel opening a door direction invalid error."
            )
        else:
            door_to_open = door
    if door_to_open:
        door, openable, position, render, info = door_to_open
        openable.opened = True
        position.blocks_movement = False
        # replace info
        engine.infos.add(
            door,
            engine.infos.shared['opened wooden door']
        )
        # replace the render
        engine.renders.add(
            door, 
            random.choice(engine.renders.shared['opened wooden door'])
        )
        engine.logger.add(f"You open the door.")
        turn_over = True
    return turn_over

def close_door(engine, entity):
    """TODO: cannot close door when unit is standing on the cell"""
    position = engine.positions.find(entity)
    turn_over = False
    # get all coordinates surrounding current entity position
    coordinates = [
        (position.x + x, position.y + y)
            for x, y in squares(exclude_center=True)
    ]
    g = join(engine.openables, engine.positions, engine.renders)
    doors = {}
    # compare coordinates against entities that can be closed that have a
    # a position x, y value in the coordinates list.
    for closeable_id, (closeable, coordinate, render) in g:
        if (coordinate.x, coordinate.y) in coordinates and closeable.opened:
            x = coordinate.x - position.x
            y = coordinate.y - position.y
            doors[(x, y)] = (closeable_id, closeable, coordinate, render)
    door_to_close = None
    if not doors:
        engine.logger.add(f"No opened door to close.")
    elif len(doors) == 1:
        door_to_close, = doors.values()
    else:
        engine.logger.add(f"Which door to close?")
        engine.screen.render()
        engine.input_system.process(
            keypresses=set(keypress_to_direction.keys()).union(('escape',))
        )
        keypress = engine.get_keypress()
        movement = Movement.keypress_to_direction(keypress)
        # valid direction keypress but not valid door direction
        door = doors.get((movement.x, movement.y), None)
        if not door:
            engine.logger.add(f"You cancel closing a door.")
        else:
            door_to_close = door
    if door_to_close:
        door, closeable, position, render = door_to_close
        closeable.opened = False
        position.blocks_movement = True
        engine.renders.add(
            door, 
            random.choice(engine.renders.shared['closed wooden door'])
        )
        engine.logger.add(f"You close the door.")
        turn_over = True
    return turn_over
