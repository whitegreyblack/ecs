# test_components

"""Testing individual components"""

from source.ecs.components import Position

def test_position_add():
    p = Position(2, 3)
    q = Position(5, 1)

    assert p + q == Position(7, 4)
