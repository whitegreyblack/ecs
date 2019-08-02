# common.py

"""Holds commonly used classes or functions"""

import curses
import math
import random
import time

from source.keyboard import keypress_to_direction


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

def eight_square() -> tuple:
    """
    Yields x, y values indicating cardinal directions on a grid
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            if (x, y) != (0, 0):
                yield x, y

def nine_square() -> tuple:
    """
    Yields x, y values indicating cardinal directions on a grid including 0, 0
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            yield x, y

def parse_data(raw: str, fields: int):
    """Returns avg values of join timings"""
    avg = lambda x: sum(float(i) for i in x) / len(x)
    data = raw.replace('\n', ' ').split(' ')
    for i in range(fields):
        print(avg(data[i::fields]))

def j(*managers) -> set:
    return set.intersection(*map(set, (m.components for m in managers)))

def join(*managers) -> tuple:
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.items()
    keys = set.intersection(*map(set, (m.components for m in managers)))
    for eid in keys:
        yield eid, (m.components[eid] for m in managers)

def join_on(keys, *managers):
    ks = set.intersection(*map(set, (m.components for m in managers)))
    ks.intersection_upate(keys)
    for eid in keys:
        yield eid, (m.components[eid] for m in managers)

def join_without_key(*managers) -> tuple:
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.items()
    keys = set.intersection(*map(set, (m.components for m in managers)))
    for eid in keys:
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

def scroll(position: int, termsize: int, mapsize: int) -> str:
    halfscreen = termsize // 2
    # less than half the screen - nothing
    if position < halfscreen:
        return 0
    elif position >= mapsize - halfscreen:
        return mapsize - termsize
    else:
        return position - halfscreen
