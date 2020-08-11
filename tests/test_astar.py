# test_astar

"""Test astar methods"""

from collections import namedtuple

from source.pathfind import octile

node = namedtuple("Node", "x y")

def test_hueristic_non_diagonal():
    """(0, 0) -> (1, 0) => 1.0"""
    a = node(0, 0)
    b = node(1, 0)
    assert int(octile(a, b) * 10) == 10

def test_hueristic_diagonal():
    """(0, 0) -> (1, 1) => 1.41"""
    a = node(0, 0)
    b = node(1, 1)
    assert int(octile(a, b) * 10) == 14

def test_hueristic_diagonal2():
    """(0, 0) -> (1, 1) => 1.41"""
    a = node(0, 0)
    b = node(-1, -1)
    assert int(octile(a, b) * 10) == 14


if __name__ == "__main__":
    print("Usage: py -m pytest tests\\test_astar.py")
