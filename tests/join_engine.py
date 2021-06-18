# tests\join_engine.py

import random
from dataclasses import dataclass

from source.common import condition
from source.contextmanagers import Timer
from source.ecs.components import Position, Tile, Visibility
from source.ecs.managers import DictComponentManager
from source.join import join, join_drop_key


@dataclass
class World:
    id: int = 0


class Engine:
    def __init__(self, *components):
        self.components = components
        self.world = World()
        self.init_managers()

    def init_managers(self):
        for component in self.components:
            setattr(self, component.manager, DictComponentManager(component))


def populate_engine(e):
    for i in range(1000):
        e.positions.add(i, Position(i, i, random.randint(0, 1)))
    for i in range(0, 1000, 2):
        e.visibilities.add(i, Visibility())
    for i in range(0, 500):
        e.tiles.add(i, Tile())


def time_joins(e: Engine):
    """Testing new joins with engine syntax"""
    times = []

    # join
    with Timer() as t:
        for _, (_, p, _) in join(e.visibilities, e.positions, e.tiles):
            if p.map_id == e.world.id:
                pass
    times.append(("join_for", t.secs))

    with Timer() as t:
        tiles = [
            (v, p, T)
            for _, (v, p, T) in join(e.visibilities, e.positions, e.tiles)
            if p.map_id == e.world.id
        ]
    times.append(("join_list", t.secs))

    # join without key
    with Timer() as t:
        for (_, p, _) in join_drop_key(e.visibilities, e.positions, e.tiles):
            if p.map_id == e.world.id:
                pass
    times.append(("join_drop_key_for", t.secs))

    with Timer() as t:
        tiles = [
            (v, p, e)
            for (v, p, T) in join_drop_key(
                e.visibilities, e.positions, e.tiles
            )
            if p.map_id == e.world.id
        ]
    times.append(("join_drop_key_list", t.secs))

    # join conditional
    with Timer() as t:
        tiles = [
            (v, p)
            for _, (v, p) in join(
                e.visibilities,
                condition(e.positions, lambda x: x.map_id == e.world.id),
            )
        ]
    times.append(("join_conditional_list", t.secs))

    # join conditional without key
    with Timer() as t:
        tiles = [
            (v, p)
            for v, p in join_drop_key(
                e.visibilities,
                condition(e.positions, lambda x: x.map_id == e.world.id),
            )
        ]
    times.append(("join_drop_key_conditional_unpack", t.secs))

    # join conditional without key as list
    with Timer() as t:
        tiles = list(
            join_drop_key(
                e.visibilities,
                condition(e.positions, lambda x: x.map_id == e.world.id),
            )
        )
    times.append(("join_drop_key_conditional_list", t.secs))

    return times


def time_join(engine):
    times = []
    with Timer() as t:
        g = engine.tiles.join(engine.positions, engine.visibilities)
        for entity_id, components in g:
            pass
    times.append(("join_on_tiles", t.secs))

    with Timer() as t:
        g = engine.positions.join(engine.tiles, engine.visibilities)
        for entity_id, components in g:
            pass
    times.append(("join_on_positions", t.secs))

    with Timer() as t:
        g = engine.visibilities.join(engine.tiles, engine.positions)
        for entity_id, components in g:
            pass
    times.append(("join_on_visibilities", t.secs))

    with Timer() as t:
        g = join(engine.positions, engine.tiles, engine.visibilities)
        for entity_id, components in g:
            pass
    times.append(("generic join", t.secs))

    return times


def output_sorted_times(timer, times):
    print(timer.__name__)
    times.sort(key=lambda x: x[1])
    for j, time in times:
        print(f"{time:.6f}", j)


if __name__ == "__main__":
    e = Engine(Position, Visibility, Tile)
    populate_engine(e)
    output_sorted_times(time_join, time_join(e))
    output_sorted_times(time_joins, time_joins(e))
