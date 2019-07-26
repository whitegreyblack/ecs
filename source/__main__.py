# world.py

"""Initializes engine and world objects created using ecs"""

import copy
import curses
import os
import random
import time

import click

from source.color import colors
from source.common import border, join
from source.ecs import (AI, Armor, Collision, Decay, Destroy, Effect,
                        Equipment, Experience, Health, Information, Input,
                        Inventory, Item, Movement, Openable, Position, Render,
                        Tile, TileMap, Visibility, Weapon, components)
from source.ecs.systems import systems
from source.engine import Engine
from source.graph import DungeonNode, WorldGraph, WorldNode, graph
from source.keyboard import keyboard
from source.maps import create_field_matrix, dungeons, extend


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

def add_world(engine, mappairs):
    world_graph = {}
    g = {
        0: DungeonNode(0, None)
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
            for _, (_, position) in join(engine.tiles, engine.positions)
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
    engine.renders.add(player, Render('@', depth=3))
    engine.healths.add(player, Health(30, 20))
    engine.infos.add(player, Information("Hero"))
    engine.inventories.add(player, Inventory())

    engine.inputs.add(player, Input(needs_input=True))
    # create a weapon for player
    spear = engine.entities.create()
    engine.items.add(spear, Item())
    engine.renders.add(spear, Render('/'))
    engine.infos.add(spear, Information('spear'))
    engine.weapons.add(spear, Weapon(4))
    e = Equipment(hand=spear.id)
    engine.equipments.add(player, e)

def add_computers(engine, npcs, spaces):
    for i in range(npcs):
        computer = engine.entities.create()
        if not spaces:
            break
        space = spaces.pop()
        engine.inputs.add(computer, Input())
        engine.positions.add(
            computer, 
            Position(*space, map_id=engine.world.id)
        )
        engine.renders.add(computer, Render('g', depth=3))
        engine.ais.add(computer, AI())
        engine.infos.add(computer, Information("goblin"))
        engine.healths.add(computer, Health(2, 2))
        # if i == 0:
        #     engine.armors.add(computer, Armor(2))

        # add items to inventory
        item = engine.entities.create()
        engine.items.add(item, Item())
        engine.renders.add(item, Render('/'))
        engine.infos.add(item, Information('spear'))
        inventory = Inventory(items=[item.id])
        engine.inventories.add(computer, inventory)

def add_items(engine, items, spaces):
    for i in range(items):
        item = engine.entities.create()
        if not spaces:
            break
        space = spaces.pop()
        engine.positions.add(
            item, 
            Position(
                *space, 
                map_id=engine.world.id, 
                moveable=False, 
                blocks_movement=False
            )
        )
        engine.renders.add(item, Render('%'))
        engine.infos.add(item, Information("food item"))
        engine.items.add(item, Item())
        engine.decays.add(item, Decay())

def ecs_setup(terminal, dungeon, npcs, items):
    engine = Engine(
        components=components, 
        systems=systems,
        terminal=terminal,
        keyboard=keyboard
    )
    add_world(engine, ((0, dungeon),))
    spaces = find_empty_spaces(engine)
    add_player(engine, spaces)
    add_computers(engine, npcs, spaces)
    add_items(engine, items, spaces)

    # engine.logger.add(f"count: {len(engine.entities.entities)}")
    return engine

def main(terminal, dungeon, npcs, items):
    seed = random.randint(0, 10000)
    random.seed(seed)
    terminal = curses_setup(terminal)
    dungeon = dungeons.get(dungeon.lower(), 'small')
    engine = ecs_setup(terminal, dungeon=dungeon, npcs=npcs, items=items)
    engine.run()

@click.command()
@click.option('-d', '--dungeon', default='shadowbarrow')
@click.option('-n', '--npcs', default=1)
@click.option('-i', '--items', default=2)
def preload(dungeon, npcs, items):
    curses.wrapper(main, dungeon, npcs, items)

if __name__ == "__main__":
    preload()
