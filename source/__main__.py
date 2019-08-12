# world.py

"""Initializes engine and world objects created using ecs"""

import copy
import curses
import os
import random
import sys
import time

import click

from source.common import border, join, join_without_key
from source.description import shared_cache
from source.ecs import (AI, Armor, Collision, Decay, Effect,
                        Equipment, Health, Information, Input,
                        Inventory, Item, Movement, Openable, Position, Render,
                        Tile, TileMap, Visibility, Weapon, components)
from source.ecs.systems import systems
from source.engine import Engine
from source.graph import DungeonNode, WorldGraph, WorldNode, graph
from source.keyboard import keyboard
from source.maps import dungeons


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
    for i in range(0, curses.COLORS-1):
        curses.init_pair(i + 1, i, -1)
    return screen

def build_shared_components(engine):
    # build shared caches. Adds a double kv pair for each entry
    for info, (char, desc, color, _) in shared_cache.items():
        if isinstance(color, tuple):
            r = [Render(char, c) for c in color]
        else:
            r = [Render(char, color),]
        engine.renders.shared[info] = r
        i = Information(info, desc)
        engine.infos.shared[info] = i
    print(engine.infos.shared)
    
def add_world(engine, mappairs):
    world_graph = {}
    g = {
        0: DungeonNode(0, parent_id=None, child_id=1),
        1: DungeonNode(1, parent_id=0),
    }
    # create entity per node
    for eid, node in g.items():
        world_graph[eid] = node
        engine.entities.create(eid)
    # create components per entity
    for eid, mapstring in mappairs:
        engine.map_system.generate_map(eid, mapstring)

def find_empty_spaces(engine):
    return {
        (position.x, position.y)
            for _, position in join_without_key(engine.tiles, engine.positions)
                if not position.blocks_movement
    }

def add_player(engine, spaces):
    player = engine.entities.create()
    engine.add_player(player)
    engine.inputs.add(player, Input())
    if not spaces:
        raise Exception("No empty spaces to place player")
    space = spaces.pop()
    engine.positions.add(player, Position(*space, map_id=engine.world.id))
    engine.renders.add(player, Render('@'))
    engine.healths.add(player, Health(10, 20))
    engine.infos.add(player, Information("Hero"))
    engine.inventories.add(player, Inventory())
    engine.inputs.add(player, Input(needs_input=True))
    # create a weapon for player
    spear = engine.entities.create()
    engine.items.add(spear, Item('weapon'))
    engine.renders.add(spear, random.choice(engine.renders.shared['spear']))
    engine.infos.add(spear, engine.infos.shared['spear'])
    engine.weapons.add(spear, Weapon(4))
    e = Equipment(hand=spear.id)
    engine.equipments.add(player, e)

def add_computers(engine, npcs, spaces):
    for i in range(npcs):
        if not spaces:
            break
        engine.spawn_system.spawn_unit(spaces.pop())

def add_items(engine, items, spaces):
    for i in range(items):
        item = engine.entities.create()
        if not spaces:
            break
        space = spaces.pop()
        engine.positions.add(item, Position(
            *space, 
            map_id=engine.world.id, 
            moveable=False, 
            blocks_movement=False
        ))
        r = random.choice(engine.renders.shared['food'])
        engine.renders.add(item, r)
        engine.infos.add(item, engine.infos.shared['food'])
        engine.items.add(item, Item('food'))
        engine.decays.add(item, Decay())

def ecs_setup(terminal, dungeon, npcs, items):
    engine = Engine(
        components=components, 
        systems=systems,
        terminal=terminal,
        keyboard=keyboard
    )
    build_shared_components(engine)
    add_world(engine, ((0, dungeon),))
    spaces = find_empty_spaces(engine)
    add_player(engine, spaces)
    add_computers(engine, npcs, spaces)
    add_items(engine, items, spaces)
    return engine

def create_save_folder_if_not_exists():
    if not os.path.exists("source/saves"):
        os.mkdir("source/saves")

def main(terminal, dungeon, npcs, items):
    seed = random.randint(0, 10000)
    random.seed(seed)
    terminal = curses_setup(terminal)
    dungeon = dungeons.get(dungeon.lower(), 'small')
    engine = ecs_setup(terminal, dungeon=dungeon, npcs=npcs, items=items)
    engine.run()
    engine.count_objects()

@click.command()
@click.option('-d', '--dungeon', default='shadowbarrow')
@click.option('-n', '--npcs', default=1)
@click.option('-i', '--items', default=2)
@click.option('-d', '--debug', is_flag=True, default=False)
def preload(dungeon, npcs, items, debug):
    create_save_folder_if_not_exists()
    if debug:
        import tracemalloc
        tracemalloc.start()
    curses.wrapper(main, dungeon, npcs, items)
    if debug:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        for stat in top_stats:
            print(stat)
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))

if __name__ == "__main__":
    preload()
