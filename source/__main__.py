# world.py

"""Initializes engine and world objects created using ecs"""

import copy
import logging
import os
import random
import sys
import time

import click
from bearlibterminal import terminal

from source.common import join, join_drop_key
from source.controllers import (EquipmentController, InventoryController,
                                controllers)
from source.debug import count_objects
from source.description import TILEMAPTYPES, shared_cache, spells
from source.ecs import (
    AI, Armor, Collision, Cursor, Decay, Effect, Equipment, HealEffect, Health,
    Information, Input, Inventory, Item, Mana, Movement, Openable, Position,
    Render, Spell, Tile, TileMap, TileMapType, Visibility, Weapon, components)
from source.ecs.systems import systems
from source.engine import Engine
from source.graph import DungeonNode, WorldGraph, WorldNode
from source.keyboard import blt_keyboard as keyboard
from source.maps import dungeons
from source.screens import MainMenuScreen


def build_shared_components(engine):
    # build shared caches. Adds a double kv pair for each entry
    for (info, char, desc, color) in shared_cache:
        if isinstance(color, tuple):
            engine.renders.shared[info] = [Render(char, c) for c in color]
        else:
            engine.renders.shared[info] = [Render(char, color),]
        engine.infos.shared[info] = Information(info, desc)

    # add specific map type properties
    for map_type, attributes in TILEMAPTYPES.items():
        engine.tilemaptypes.shared[map_type] = TileMapType(**attributes)

def build_spells(engine):
    for spellname, (manacost, char, colors, desc) in spells.items():
        spell_id = engine.entities.create()
        # spell specific shareed cache
        Spell.identify[spell_id] = spellname
        # shared cache will hold all spell info that is needed to build a spell
        engine.spells.shared[spellname] = Spell(manacost)
        engine.renders.shared[spellname] = [Render(char, c) for c in colors]
        engine.infos.shared[spellname] = Information(spellname, desc)

def add_world(engine, *map_info):
    # example of world graph system
    # world_graph = {}
    # g = {
    #     0: DungeonNode(0, child_id=1),
    #     1: DungeonNode(1, parent_id=0),
    # }

    # # create entity per node
    # for eid, node in g.items():
    #     world_graph[eid] = node
    #     engine.entities.add(eid)

    # create components per entity
    for map_type, map_string in map_info:
        engine.map_system.generate_map(map_type, map_string)

def ecs_setup(terminal, dungeon_info):
    engine = Engine(
        components=components,
        systems=systems,
        terminal=terminal,
        keyboard=keyboard
    )
    for controller in controllers:
        engine.router.add_controller(controller.router, controller(engine))
    build_shared_components(engine)
    add_world(engine, dungeon_info)
    build_spells(engine)
    engine.add_screen(MainMenuScreen)

    return engine

def create_save_folder_if_not_exists():
    if not os.path.exists("saves"):
        os.mkdir("saves")

def main(terminal, world):
    seed = random.randint(0, 10000)
    random.seed(seed)
    dungeon_info = dungeons.get(world.lower(), 'small')
    engine = ecs_setup(terminal, dungeon_info=dungeon_info)
    engine.run()
    return engine

def blt_setup():
    terminal.open()
    terminal.set("input: filter=[keyboard,mouse]")
    terminal.set("U+E100: ./source/images/sword.png, size=8x16")
    terminal.set("U+E200: ./source/images/health.png, size=8x16")
    terminal.set("U+E300: ./source/images/mana.png, size=8x16")
    terminal.set("U+E400: ./source/images/shield.png, size=16x16")

@click.command()
@click.option('-t', '--term', default='blt')
@click.option('-w', '--world', default='shadowbarrow')
@click.option('-d', '--debug', is_flag=True, default=False)
def preload(term, world, debug):
    """Things to do before running the engine"""
    # setup logger
    # logging.basicConfig(
    #     filename="game.log",
    #     filemode='w',
    #      level=logging.INFO
    # )
    # logging.info("Started")
    # setup system folders and paths
    create_save_folder_if_not_exists()
    # setup terminal
    if term == "blt":
        blt_setup()
        engine = main(terminal, world)
        if debug:
            count_objects(engine)

def keypress_from_input(value):
    keys = keyboard.get(value, None)
    if isinstance(keys, tuple):
        return keys[int(terminal.state(terminal.TK_SHIFT))]
    return keys

def demo_render_system(scene, scenemanager, engine, terminal):
    terminal.clear()
    if scene.redraw:
        terminal.printf(1, 2, "adding 1")
    else:
        terminal.printf(1, 2, "didn't need redraw")
    terminal.refresh()
    scene.redraw = False

def demo_action_system(scene, engine, terminal):
    if scene.key in ('close', 'escape'):
        scene.manager.pop()

def render_menu_system(scene, engine, terminal):
    scene.render(engine, terminal)

def input_system(scene, engine, terminal):
    value = terminal.read()
    key = keypress_from_input(value)
    if key in scene.keys:
        scene.key = key
        scene.redraw = True

def inspect_system(scene, engine, terminal):
    print(f"Action: {scene.key}")

if __name__ == "__main__":
    preload()
