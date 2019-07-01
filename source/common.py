# common.py

"""Holds commonly used classes or functions"""

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
