# test_graph.py

"""Test graph node properties and methods"""

from source.graph import DungeonNode, Node, WorldNode, find_child, find_parent

def test_find_child():
    nodes = {
        0: WorldNode(0, 1),
        1: DungeonNode(1, 0, 2),
        2: DungeonNode(2, 1),
    }

    assert find_child(nodes, 0, 0) == False
    assert find_child(nodes, 0, 1) == True
    assert find_child(nodes, 0, 2) == True
    assert find_child(nodes, 0, 3) == False

def test_find_parent():
    nodes = {
        0: WorldNode(0, 1),
        1: DungeonNode(1, 0, 2),
        2: DungeonNode(2, 1),
    }

    assert find_parent(nodes, 2, 2) == False
    assert find_parent(nodes, 2, 1) == True
    assert find_parent(nodes, 2, 0) == True
    assert find_parent(nodes, 2, 3) == False
