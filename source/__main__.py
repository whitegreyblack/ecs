# world.py

"""World created using ecs systems and msvcrt getch for input"""

import copy
import curses
import os
import random
import time

import click

from source.ecs import (AI, Collision, Destroy, Effect, Experience, Health,
                        Information, Input, Inventory, Item, Movement,
                        Openable, Position, Render, Tile, TileMap, Visibility,
                        components)
from source.ecs.managers import join
from source.ecs.systems import systems
from source.engine import Engine
from source.keyboard import keyboard
from source.logging import Logger
from source.maps import dungeons


def curses_setup(screen):
    curses.curs_set(0)
    # screen.nodelay(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    screen.border()
    screen.addstr(0, 1, '[__main__]')

def find_empty_space(engine):
    open_spaces = set()
    for entity_id, (tile, pos) in join(engine.tiles, engine.positions):
        if not pos.blocks_movement:
            open_spaces.add((pos.x, pos.y))
    for entity_id, (hp, pos) in join(engine.healths, engine.positions):
        open_spaces.remove((pos.x, pos.y))
    for entity_id, (item, pos) in join(engine.items, engine.positions):
        open_spaces.remove((pos.x, pos.y))
    if not open_spaces:
        return None
    return open_spaces.pop()

def add_player(engine):
    player = engine.entities.create()
    # engine.ai.add(player, AI())
    engine.inputs.add(player, Input())
    space = find_empty_space(engine)
    if not space:
        raise Exception("No empty spaces to place player")
    # engine.ais.add(player, AI())
    engine.positions.add(player, Position(*space))
    engine.renders.add(player, Render('@'))
    engine.healths.add(player, Health(20, 20))
    engine.infos.add(player, Information("you"))
    engine.inventories.add(player, Inventory())
    engine.add_player(player)

def add_computers(engine, npcs):
    for _ in range(npcs):
        computer = engine.entities.create()
        space = find_empty_space(engine)
        if not space:
            break
        engine.inputs.add(computer, Input(is_player=False))
        engine.positions.add(computer, Position(*space))
        engine.renders.add(computer, Render('g'))
        engine.ais.add(computer, AI())
        engine.infos.add(computer, Information("goblin"))
        engine.healths.add(computer, Health(2, 2))

def add_map(engine, mapstring):
    # add entity that holds tiles
    tilemap = engine.entities.create()
    engine.world = tilemap
    dungeon = [[c for c in row] for row in mapstring.split('\n')]
    tm = TileMap(len(dungeon[0]), len(dungeon))
    engine.tilemaps.add(tilemap, tm)

    # add tiles
    wall_info = Information('wall')
    door_info = Information('door')
    floor_info = Information('floor')
    for y, row in enumerate(dungeon):
        for x, c in enumerate(row):
            tile = engine.entities.create()
            position = Position(
                x, 
                y, 
                moveable=False, 
                blocks_movement=c in ('#', '+')
            )
            engine.visibilities.add(tile, Visibility())
            engine.positions.add(tile, position)
            engine.tiles.add(tile, Tile(entity_id=tilemap.id))
            engine.renders.add(tile, Render(char=c))
            if c == '#':
                engine.infos.add(tile, wall_info)
            elif c in ('/', '+'):
                engine.infos.add(tile, door_info)
                engine.openables.add(tile, Openable(opened=c=='/'))
            else:
                engine.infos.add(tile, floor_info)

def add_items(engine, items):
    for i in range(items):
        item = engine.entities.create()
        space = find_empty_space(engine)
        if not space:
            raise Exception("No empty spaces to place item")
        engine.positions.add(
            item, 
            Position(*space, moveable=False, blocks_movement=False)
        )
        engine.renders.add(item, Render('%'))
        engine.infos.add(item, Information("food item"))
        engine.items.add(item, Item())
        engine.logger.add(f"{item.id} @ ({space})") # show us item position

def ecs_setup(terminal, dungeon, npcs, items):
    engine = Engine(
        components=components, 
        systems=systems,
        terminal=terminal,
        keyboard=keyboard
    )
    print(engine)
    add_map(engine, dungeon)
    # add_screens(engine)
    add_player(engine)
    add_computers(engine, npcs)
    add_items(engine, items)

    # engine.logger.add(f"count: {len(engine.entities.entities)}")
    return engine

def main(terminal, dungeon, npcs, items):
    curses_setup(terminal)
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
