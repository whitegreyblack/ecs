# test_component_manager.py

from source.common import join_drop_key
from source.ecs import Position, Render
from source.ecs.managers import ComponentManager


def test_manager():
    m = ComponentManager(Render)
    n = ComponentManager(Position)
    
    render = Render()
    position = Position()

    m.add(0, render)
    n.add(0, position)

    for r, p in join_drop_key(m, n):
        assert r == render
        assert p == position
