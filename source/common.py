# common.py

"""Holds commonly used classes or functions"""

import math


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
    first, *rest = managers
    keys = set(first.components.keys())
    for manager in rest:
        keys = keys.intersection(set(manager.components.keys()))
    for eid in keys:
        yield eid, (m.components[eid] for m in managers)

def distance(a, b):
    '''Returns a float that represents distance between two points'''
    return math.sqrt(math.pow((b[0] - a[0]), 2) + math.pow((b[1] - a[1]), 2))