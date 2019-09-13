# world.py

"""Initializes engine and world objects created using ecs"""

import copy
import curses
import os
import random
import sys
import time

import click

from source.common import border, join, join_drop_key
from source.controllers import (EquipmentController, InventoryController,
                                controllers)
from source.description import shared_cache
from source.ecs import (
    AI, Armor, Collision, Cursor, Decay, Effect, Equipment, HealEffect, Health,
    Information, Input, Inventory, Item, Mana, Movement, Openable, Position,
    Render, Tile, TileMap, Visibility, Weapon, components)
from source.ecs.systems import systems
from source.engine import Engine
from source.graph import DungeonNode, WorldGraph, WorldNode
from source.keyboard import keyboard
from source.maps import dungeons
from source.router import Router


def resize(screen):
    y, x = screen.getmaxyx()
    if (x, y) != (80, 25):
        os.system('mode con: cols=80 lines=25')
        curses.resize_term(26, 80)

def curses_setup(screen):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    screen.nodelay(1)
    # initialize colors and save init_pair index values
    for i in range(0, curses.COLORS - 1):
        curses.init_pair(i + 1, i, -1)
    return screen

def build_shared_components(engine):
    # build shared caches. Adds a double kv pair for each entry
    for info, (char, desc, color, _) in shared_cache.items():
        if isinstance(color, tuple):
            engine.renders.shared[info] = [Render(char, c) for c in color]
        else:
            engine.renders.shared[info] = [Render(char, color),]
        engine.infos.shared[info] = Information(info, desc)
    
def add_world(engine, mappairs):
    world_graph = {}
    g = {
        0: DungeonNode(0, child_id=1),
        1: DungeonNode(1, parent_id=0),
    }
    # create entity per node
    for eid, node in g.items():
        world_graph[eid] = node
        engine.entities.add(eid)
    # create components per entity
    for eid, mapstring in mappairs:
        engine.map_system.generate_map(eid, mapstring)

def find_empty_spaces(engine):
    return {
        (position.x, position.y)
            for _, position in join_drop_key(engine.tiles, engine.positions)
                if not position.blocks_movement
    }

def add_router(engine):
    engine.add_router(Router, controllers)

def ecs_setup(terminal, dungeon):
    engine = Engine(
        components=components, 
        systems=systems,
        terminal=terminal,
        keyboard=keyboard
    )
    add_router(engine)
    build_shared_components(engine)
    add_world(engine, ((0, dungeon),))
    spaces = find_empty_spaces(engine)
    # add player
    engine.player = engine.spawn_system.spawn_player(spaces.pop())
    # add player cursor
    engine.cursor = engine.spawn_system.spawn_cursor(engine.player)
    # add computers
    for i in range(2):
        engine.spawn_system.spawn_unit(spaces.pop())
    # add items
    for i in range(2):
        engine.spawn_system.spawn_item(spaces.pop())
    return engine

def count_objects(engine):
    """Debugging information and object counting"""
    m = 0
    s = 0
    for c in sorted(components, key=lambda x: x.classname()):
        l = len(getattr(engine, c.manager).components)
        g = len(getattr(engine, c.manager).shared)
        print(c.manager, l, g)
        m += l
        s += g
    print('total objects:', m, s)

    # environment entities
    print('tiles:', len(list(join(
        engine.tiles, 
        engine.positions, 
        engine.visibilities, 
        engine.renders, 
        engine.infos
    ))))
    # movable units
    print('units:', len(list(join(
        engine.healths,
        engine.positions,
        engine.infos,
        engine.renders
    ))))
    # items
    print('items:', len(list(join(
        engine.healths,
        engine.positions,
        engine.infos,
        engine.renders,
        engine.inventories
    ))))

def create_save_folder_if_not_exists():
    if not os.path.exists("source/saves"):
        os.mkdir("source/saves")

def main(terminal, dungeon):
    seed = random.randint(0, 10000)
    random.seed(seed)
    terminal = curses_setup(terminal)
    dungeon = dungeons.get(dungeon.lower(), 'small')
    engine = ecs_setup(terminal, dungeon=dungeon)
    engine.run()
    count_objects(engine)

@click.command()
@click.option('-w', '--world', default='shadowbarrow')
@click.option('-d', '--debug', is_flag=True, default=False)
def preload(world, debug):
    create_save_folder_if_not_exists()
    if debug:
        import tracemalloc
        tracemalloc.start()
        curses.wrapper(main, world)
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('traceback')
        for stat in top_stats:
            print(stat)
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))
    else:
        curses.wrapper(main, world)


if __name__ == "__main__":
    preload()
