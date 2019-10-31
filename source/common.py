# common.py

"""Holds commonly used classes or functions"""

import curses
import math
import random
import time
from enum import Enum, auto

from source.keyboard import keypress_to_direction


class GameMode(Enum):
    DEBUG = auto()
    NORMAL = auto()
    LOOKING = auto()
    MISSILE = auto()
    MAGIC = auto()

def find_empty_spaces(engine):
    return {
        (position.x, position.y)
            for _, position in join_drop_key(engine.tiles, engine.positions)
                if not position.blocks_movement
    }

def dot() -> tuple:
    """Wrapper for a single point"""
    yield 0, 0

def squares(exclude_center:bool=False) -> tuple:
    """
        Yields x, y values indicating cardinal directions on a grid
        @exclude_center: parameter determines if (0, 0) should be returned
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            if exclude_center and (x, y) == (0, 0):
                continue
            yield x, y

def cardinal(exclude_center: bool=False) -> tuple:
    """
        Yields x, y values indicating axial/cross directions on a grid.
        @exclude_center: parameter determines if (0, 0) should be returned
    """
    yield 0, -1
    yield -1, 0
    if not exclude_center:
        yield 0, 0
    yield 1, 0
    yield 0, 1

def diamond(radius=2, exclude_center: bool=False) -> tuple:
    """
        Yields all x, y, values representing a units withing 2 units
        @exclude_center: parameter determines if (0, 0) should be returned
    """
    for x in range(-radius, radius+1):
        for y in range(-radius, radius+1):
            if x == 0 and y == 0 and exclude_center:
                continue
            if abs(x) + abs(y) < radius+1:
                yield x, y

def circle(radius=2, exclude_center: bool=False) -> tuple:
    """
        Yields all x, y values representing points in a circle with r=radius
        @exclude_center: parameter determines if (0, 0) should be returned
    """
    if radius < 0:
        return
    rr = (radius + 1) * (radius + 1) - (radius >> 1)
    for x in range(-radius, radius + 1):
        rxx = x * x
        for y in range(-radius, radius + 1):
            ryy = y * y
            if rxx + ryy < rr:
                if exclude_center and x == 0 and y== 0:
                    continue
                yield x, y

def parse_data(raw: str, fields: int):
    """Returns avg values of join timings"""
    avg = lambda x: sum(float(i) for i in x) / len(x)
    data = raw.replace('\n', ' ').split(' ')
    for i in range(fields):
        print(avg(data[i::fields]))

def entity_component(eid, *managers):
    for m in managers:
        yield m.components[eid]

def j(first, *rest) -> set:
    keys = set(first.components)
    for d in rest:
        keys.intersection_update(d.components)
    for k in keys:
        yield k

def join(*managers) -> tuple:
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.items()
    for eid in j(*managers):
        yield eid, (m.components[eid] for m in managers)

def join_on(keys, *managers):
    ks = set.intersection(*map(set, (m.components for m in managers)))
    ks.intersection_upate(keys)
    for eid in keys:
        yield eid, (m.components[eid] for m in managers)

def join_drop_key(*managers) -> tuple:
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.values()
    for eid in j(*managers):
        yield (m.components[eid] for m in managers)

def join_conditional(*managers, key=True, conditions=None) -> tuple:
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.items()
    # filter by id matching
    keys = set.intersection(*map(set, (m.components for m in managers)))
    for eid in keys:
        # with conditional, additional filters by conditions
        components = list(m.components[eid] for m in managers)
        skip = False
        for i, condition in conditions:
            if condition(components[i]):
                skip = True
                break
        if not skip:
            if key:
                yield eid, components
            else:
                yield components

def distance(a: int, b: int) -> float:
    '''Returns a value that represents distance between two points'''
    return math.sqrt(math.pow((b[0] - a[0]), 2) + math.pow((b[1] - a[1]), 2))

def border(screen: object, x: int, y: int, dx: int, dy: int) -> None:
    """
    Draws a box with given input parameters using the default characters
    """
    screen.vline(y, x, curses.ACS_SBSB, dy)
    screen.vline(y, x + dx, curses.ACS_SBSB, dy)
    screen.hline(y, x, curses.ACS_BSBS, dx)
    screen.hline(y + dy, x, curses.ACS_BSBS, dx)
    screen.addch(y, x, curses.ACS_BSSB)
    screen.addch(y, x + dx, curses.ACS_BBSS)
    screen.addch(y + dy, x, curses.ACS_SSBB)
    try:
        screen.addch(y + dy, x + dx, curses.ACS_SBBS)
    except:
        screen.insch(y + dy, x + dx, curses.ACS_SBBS)

def direction_to_keypress(x: int, y: int) -> str:
    """Returns the keypress that correlates with a given (x, y) direction"""
    for keypress, direction in keypress_to_direction.items():
        if (x, y) == direction:
            return keypress

def scroll(position: int, termsize: int, mapsize: int) -> int:
    # if map can fit entirely in the terminal view, no offset needed
    if mapsize < termsize:
        return 0
    halfscreen = termsize // 2
    # less than half the screen - also no offset needed
    if position < halfscreen:
        return 0
    elif position >= mapsize - halfscreen:
        return mapsize - termsize
    else:
        return position - halfscreen
