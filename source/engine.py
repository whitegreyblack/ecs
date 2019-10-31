# engine.py

"""Engine class to hold all objects"""

import curses
import random
import time
from collections import OrderedDict
from dataclasses import dataclass, field

from source.common import GameMode, join
from source.ecs.components import (Collision, Effect, Information, Movement,
                                   Openable, Position, components)
from source.ecs.managers import ComponentManager, EntityManager
from source.ecs.systems import RenderSystem
from source.logger import Logger
from source.screens import (DeathScreen, EquipmentScreen, GameScreen,
                            InventoryScreen, MenuScreen, SpellScreen,
                            StartScreen)


class Engine(object):

    def __init__(self, components, systems, terminal=None, keyboard=None):
        self.running = True
        self.logger = Logger()
        self.debugger = Logger()
        # set to an invalid value. All entity ids are positive integers (>0)
        self.entity = -1
        
        self.add_terminal(terminal)
        self.keyboard = keyboard

        self.world = None
        self.entities = EntityManager()
        self.init_managers(components)
        self.init_systems(systems)

        self.screen = None
        self.entity = None
        self.entity_index = 0
        self.requires_input = True
        self.keypress = None

        self.mode = GameMode.NORMAL
        self.entities_in_view = set()
        self.tiles_in_view = set()

    def __repr__(self):
        attributes = []
        # systems = []
        for attr, value in self.__dict__.items():
            if isinstance(value, ComponentManager):
                attributes.append(attr)
        return f"Engine({', '.join(attributes)})"

    @property
    def systems(self):
        for value in self.__dict__.values():
            if isinstance(value, ComponentManager):
                yield value

    def init_managers(self, components):
        for component in components:
            if isinstance(component, Effect):
                self.__setattr__(
                    component.manager,
                    ComponentManager(component),
                    OrderedDict
                )
            else:
                self.__setattr__(
                    component.manager,
                    ComponentManager(component)
                )

    def init_systems(self, systems):
        if not systems:
            return
        for system_type in systems:
            name = f"{system_type.classname().replace('system', '')}_system"
            if system_type.__name__ == 'RenderSystem':
                system = system_type(self, self.terminal)
            else:
                system = system_type(self)
            self.__setattr__(name, system)

    def add_router(self, router, controllers):
        self.router = router(self, controllers)

    def get_input(self):
        # curses.flushinp()
        return self.terminal.getch()

    def keypress_from_input(self, char):
        return self.keyboard.get(char, None)

    def initialize_screens(self):
        self.screens = {
            screen.__name__.lower(): screen(self, self.terminal)
                for screen in (
                    GameScreen, 
                    MenuScreen,
                    StartScreen, 
                    InventoryScreen,
                    EquipmentScreen,
                    DeathScreen,
                    SpellScreen,
                )
        } 
        self.screen = self.screens['startscreen']

    def find_entity(self, entity_id):
        return self.entity_manager.find(entity_id)

    def add_world(self, world):
        self.world = world

    def add_terminal(self, terminal):
        if not terminal:
            return
        if hasattr(self, 'terminal') and getattr(self, 'terminal'):
            raise Exception("terminal already initialized")
        self.terminal = terminal
        self.height, self.width = terminal.getmaxyx()

    def change_screen(self, name):
        self.screen.state = 'closed'
        self.screen = self.screens.get(name, None)
        if not self.screen:
            raise ValueError(f"Invalid screen name: {name}")
        self.screen.state = 'open'

    def change_mode(self, mode):
        if mode == self.mode:
            raise ValueError("Cannot change to same mode")
        old_mode = self.mode
        self.mode = mode
        if old_mode == GameMode.NORMAL:
            player_position = self.positions.find(self.player)
            self.positions.add(
                self.cursor, 
                player_position.copy(
                    movement_type=Position.MovementType.VISIBLE, 
                    blocks_movement=False
                )
            )

    def reset_entity_index(self):
        self.entity_index = 0
        self.entity = self.entities.entity_ids[self.entity_index]

    def next_entity(self):
        # self.entity_index = (self.entity_index + 1) % len(self.entities.entity_ids)
        self.entity_index += 1
        if self.entity_index > len(self.entities.entity_ids) - 1:
            self.entity = None
        else:
            self.entity = self.entities.entity_ids[self.entity_index]

    def update_ai_behaviors(self):
        self.ai_system.update()

    def clear_databases(self):
        systems = (
            system
                for system_name, system in self.__dict__.items() 
                    if system_name.endswith('__system')
            )
        for system in systems:
            system.components.clear()

    def get_keypress(self):
        self.requires_input = True
        return self.keypress

    def process(self):
        self.screen.render()
        processed = self.screen.process()
        if not processed:
            if self.requires_input:
                self.input_system.process()
            processed = self.screen.process()

    def run(self):
        self.initialize_screens()
        self.entity = self.entities.entity_ids[self.entity_index]
        while self.running:
            self.process()
