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

from source.border import border
from source.common import colorize, join, join_drop_key
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
from source.scenemanager import SceneManager
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

def action_main_menu_system(scene, engine, terminal):
    key = scene.key
    option = scene.get_option()
    print("Scene", scene)
    if key == 'enter' and option == 'quit':
        scene.manager.pop()
    elif key in ('escape', 'close'):
        scene.manager.push(ConfirmMenuScreen())
    # elif key == 'enter' and option == 'new game':
    #     self.engine.add_screen(GameScreen)
    # elif key == 'enter' and option == 'options':
    #     self.engine.running = False
    #     self.engine.add_screen(OptionScreen)
    elif key == 'down':
        scene.next_option()
    elif key == 'up':
        scene.prev_option()
    # elif key == 'mouse-left':
    #     option = self.mapper.get(self.engine.get_mouse_state(), None)
    #     if option == 'quit' or option == 'options':
    #         self.engine.running = False
    #     elif option == 'new game':
    #         self.engine.add_screen(GameScreen)
    # elif key == 'mouse-move':
    #     option = self.mapper.get(self.engine.get_mouse_state(), None)
    #     if option:
    #         self.index = self.options.index(option)

class Screen:
    manager = None
    def __init__(self, systems, keys):
        self.systems = systems
        self.keys = {'close', 'escape'}.union(keys)
        self.key = None
        self.redraw = True

    def add_border(self, terminal):
        width = terminal.state(terminal.TK_WIDTH)
        height = terminal.state(terminal.TK_HEIGHT)
        for x, y, char in border(0, 0, width, height):
            terminal.printf(x, y, char)

    def add_title(self, terminal):
        terminal.printf(1, 0, f'[[{self.title}]]')

    def add_string(self, terminal, x, y, string, color=None):
        if color:
            string = colorize(string, color)
        terminal.printf(x, y, string)

    def process(self, engine, terminal):
        for system in self.systems:
            system(self, engine, terminal)

    def get_draw_methods(self):
        return ('add_border', 'add_title', 'add_options')

    def render(self, engine, terminal):
        draw_methods = self.get_draw_methods()
        if self.redraw:
            terminal.clear()
            for draw_method in draw_methods:
                method = getattr(self, draw_method)
                method(terminal)
            terminal.refresh()
        self.redraw = False

class MenuScreen(Screen):
    systems = (
        render_menu_system,
        input_system,
        action_main_menu_system
    )
    options = None
    keys = {
        'close',
        'escape',
        'enter',
        'mouse-left',
        'mouse-move'
    }
    def __init__(self, systems=None, options=None, keys=None):
        if not systems:
            systems = self.__class__.systems
        if not options:
            options = self.__class__.options
        if not keys:
            keys = self.__class__.keys
        print(self.__class__, self.__class__.keys)
        super().__init__(systems, keys)
        self.index = 0
        self.options = options
        self.mapper = dict()

    def get_option(self):
        return self.options[self.index]

    def prev_option(self):
        self.index = (self.index - 1) % len(self.options)

    def next_option(self):
        self.index = (self.index + 1) % len(self.options)

    def button_colors(self, terminal, i):
        if i == self.index:
            return "black", "white"
        else:
            return "white", "black"

    def add_options(self, terminal):
        x = terminal.state(terminal.TK_WIDTH) // 2
        y = terminal.state(terminal.TK_HEIGHT) // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_y_offset = -1
        option_x_offset = -(highlight_len // 2)

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(terminal, i)
            option_x = x + option_x_offset
            option_y = y + option_y_offset + i
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            terminal.printf(option_x, option_y, string)
            for i in range(highlight_len):
                self.mapper[(option_x + i, option_y)] = option

class StartMenuScreen(MenuScreen):
    title = "main menu"
    options = ('new game', 'options', 'quit')
    keys = {'up', 'down'}

class GameMenuScreen(MenuScreen):
    title = "game menu"
    options = ('back', 'main menu', 'settings', 'quit')
    keys = {'up', 'down'}

class ConfirmMenuScreen(MenuScreen):
    title = "confirm menu"
    options = ('yes', 'no')
    keys = {'left', 'right'}

    def get_draw_methods(self):
        return ('add_border', 'add_title', 'add_options', 'add_text')

    def add_text(self, terminal):
        text = "Do you really want to quit?"
        x = terminal.state(terminal.TK_WIDTH) // 2 - len(text) // 2
        y = terminal.state(terminal.TK_HEIGHT) // 2 - 1
        terminal.printf(x, y, text)

    def add_options(self, terminal):
        x = terminal.state(terminal.TK_WIDTH) // (len(self.options) + 1)
        y = terminal.state(terminal.TK_HEIGHT) // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_x_offset = x
        option_y_offset = 1

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(terminal, i)
            option_x = x + (option_x_offset * i)
            option_y = y + option_y_offset
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            terminal.printf(option_x, option_y, string)
            for i in range(-1, highlight_len + 2):
                for j in range(-1, 2):
                    self.mapper[(option_x + i, option_y + j)] = option

if __name__ == "__main__":
    # preload()
    terminal.open()
    sm = SceneManager(StartMenuScreen())
    sm.run(None, terminal)
