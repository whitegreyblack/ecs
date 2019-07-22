# common.py

"""Holds commonly used classes or functions"""

import curses
import math
import random
import time

from source.keyboard import keypress_to_direction


def squares(exclude_center=False):
    """
    Yields x, y values indicating cardinal directions on a grid
    @exclude_center: parameter determines if (0, 0) should be returned
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            if exclude_center and (x, y) == (0, 0):
                continue
            yield x, y

def eight_square():
    """
    Yields x, y values indicating cardinal directions on a grid
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            if (x, y) != (0, 0):
                yield x, y

def nine_square():
    """
    Yields x, y values indicating cardinal directions on a grid including 0, 0
    """
    for x in range(-1, 2):
        for y in range(-1 ,2):
            yield x, y

def join(*managers):
    # at least two needed else returns dict items
    if len(managers) == 1:
        return managers.components.items()
    keys = set.intersection(*map(set, (m.components for m in managers)))
    for eid in keys:
        yield eid, (m.components[eid] for m in managers)

def distance(a, b):
    '''Returns a float that represents distance between two points'''
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
    screen.insch(y + dy, x + dx, curses.ACS_SBBS)

def direction_to_keypress(x, y):
    for keypress, direction in keypress_to_direction.items():
        if (x, y) == direction:
            return keypress
