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
from source.ecs import (AI, Collision, Decay, Destroy, Effect, Experience,
                        Health, Information, Input, Inventory, Item, Movement,
                        Openable, Position, Render, Tile, TileMap, Visibility,
                        components)
from source.ecs.systems import systems
from source.engine import Engine
from source.graph import DungeonNode, WorldGraph, WorldNode, graph
from source.keyboard import keyboard
from source.maps import dungeons, extend, create_field_matrix


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

def add_world(engine, dungeon):
    world_graph = {}
    g = {
        0: (DungeonNode(0, None), dungeon)
    }
    # create entity per node
    for eid, (node, mapstring) in g.items():
        world_graph[eid] = node
        engine.entities.create(eid)
    # create components per entity
    for eid, (node, mapstring) in g.items():
        add_map(engine, eid, mapstring)
    engine.world = WorldGraph(world_graph, 0)

def add_map(engine, eid, mapstring):
    # add entity that holds tiles

    world = engine.entities.find(eid=eid)
    dungeon = [[c for c in row] for row in mapstring.split('\n')]
    tilemap = TileMap(len(dungeon[0]), len(dungeon))
    engine.tilemaps.add(world, tilemap)
    # add tiles
    for y, row in enumerate(dungeon):
        for x, c in enumerate(row):
            tile = engine.entities.create()
            engine.tiles.add(tile, Tile())
            position = Position(
                x, 
                y,
                map_id=world.id,
                moveable=False, 
                blocks_movement=c in ('#', '+')
            )
            engine.visibilities.add(tile, Visibility())
            engine.positions.add(tile, position)
            engine.renders.add(tile, Render(char=c))
            if c == '#':
                engine.infos.add(tile, Information('wall'))
            elif c in ('/', '+'):
                engine.infos.add(tile, Information('door'))
                engine.openables.add(tile, Openable(opened=c=='/'))
            elif c == '"':
                engine.infos.add(tile, Information('grass'))
            elif c == '~':
                engine.infos.add(tile, Information('water'))
            else:
                engine.infos.add(tile, Information('floor'))

def find_space(engine):
    spaces = set()
    for eid, (tile, position) in join(engine.tiles, engine.positions):
        if not position.blocks_movement:
            spaces.add((position.x, position.y))
    return spaces

def find_empty_space(engine):
    spaces = find_space(engine)
    for entity_id, (hp, pos) in join(engine.healths, engine.positions):
        spaces.remove((pos.x, pos.y))
    for entity_id, (item, pos) in join(engine.items, engine.positions):
        spaces.remove((pos.x, pos.y))
    if not spaces:
        return None
    return spaces.pop()

def add_player(engine):
    player = engine.entities.create()
    # engine.ai.add(player, AI())
    engine.inputs.add(player, Input())
    space = find_empty_space(engine)
    if not space:
        raise Exception("No empty spaces to place player")
    # engine.ais.add(player, AI())
    engine.positions.add(player, Position(*space, map_id=engine.world.id))
    engine.renders.add(player, Render('@', depth=3))
    engine.healths.add(player, Health(30, 20))
    engine.infos.add(player, Information("Hero"))
    engine.inventories.add(player, Inventory())
    engine.inputs.add(player, Input(needs_input=True))
    engine.add_player(player)

def add_computers(engine, npcs):
    for i in range(npcs):
        computer = engine.entities.create()
        space = find_empty_space(engine)
        if not space:
            break
        engine.inputs.add(computer, Input())
        engine.positions.add(
            computer, 
            Position(*space, map_id=engine.world.id)
        )
        engine.renders.add(computer, Render('g', depth=3))
        engine.ais.add(computer, AI())
        engine.infos.add(computer, Information("goblin"))
        engine.healths.add(computer, Health(2, 2))

        # add items to inventory
        item = engine.entities.create()
        engine.items.add(item, Item())
        engine.renders.add(item, Render('/'))
        engine.infos.add(item, Information('spear'))
        inventory = Inventory(items=[item.id])
        engine.inventories.add(computer, inventory)

def add_items(engine, items):
    for i in range(items):
        item = engine.entities.create()
        space = find_empty_space(engine)
        if not space:
            raise Exception("No empty spaces to place item")
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
    add_world(engine, dungeon)
    # add_map(engine, dungeon)
    add_player(engine)
    add_computers(engine, npcs)
    add_items(engine, items)

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
@click.option('-d', '--dungeon', default='dungeon')
@click.option('-n', '--npcs', default=2)
@click.option('-i', '--items', default=2)
def preload(dungeon, npcs, items):
    curses.wrapper(main, dungeon, npcs, items)

if __name__ == "__main__":
    preload()
