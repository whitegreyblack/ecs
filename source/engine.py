# engine.py

"""Engine class to hold all objects"""

import curses
import random
import time
from dataclasses import dataclass, field

from source.ecs.components import (Collision, Information, Movement, Openable,
                                   Position)
from source.ecs.managers import ComponentManager, EntityManager
from source.ecs.screens import (
    DeathMenu, EquipmentMenu, GameMenu, GameScreen, InventoryMenu, LogMenu,
    LookingMenu, MainMenu)
from source.ecs.systems import RenderSystem
from source.messenger import Logger


class Engine(object):
    def __init__(self, components, systems, terminal, keyboard):
        self.running = True
        self.logger = Logger()
        self.debugger = Logger()
        self.entity = 0
        
        self.add_terminal(terminal)
        self.keyboard = keyboard

        self.entities = EntityManager()
        self.init_managers(components)
        self.init_systems(systems)

        self.screen = None
        self.entity = None
        self.entity_index = 0
        self.requires_input = True
        self.keypress = None

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
            self.__setattr__(
                component.manager,
                ComponentManager(component)
            )

    def init_systems(self, systems):
        for system_type in systems:
            name = f"{system_type.classname().replace('system', '')}_system"
            if system_type.__name__ == 'RenderSystem':
                system = system_type(self, self.terminal)
            else:
                system = system_type(self)
            self.__setattr__(name, system)

    def get_input(self):
        # curses.flushinp()
        return self.terminal.getch()

    def keypress_from_input(self, char):
        return self.keyboard.get(char, None)

    def initialize_screens(self):
        self.screens = {
        screen.__name__.lower(): screen(self, self.terminal)
            for screen in (
                GameMenu, 
                GameScreen, 
                MainMenu, 
                InventoryMenu,
                EquipmentMenu,
                DeathMenu, 
                LogMenu
            )
        } 
        self.screen = self.screens['mainmenu']

    def find_entity(self, entity_id):
        return self.entity_manager.find(entity_id)

    def add_world(self, world):
        # if hasattr(self, 'world') and getattr(self, 'world'):
        #     raise Exception("world already initialized")
        self.world = world

    def add_terminal(self, terminal):
        if not terminal:
            return
        if hasattr(self, 'terminal') and getattr(self, 'terminal'):
            raise Exception("terminal already initialized")
        self.terminal = terminal
        self.height, self.width = terminal.getmaxyx()

    def add_player(self, entity):
        self.player = entity
        self.player_id = entity.id

    def change_screen(self, name):
        self.screen.state = 'closed'
        self.screen = self.screens.get(name, 'gamemenu')
        self.screen.state = 'open'

    def next_entity(self):
        # for entity in self.entities:
        self.entity_index = (self.entity_index + 1) % len(self.entities.entities)
        self.entity = self.entities.entities[self.entity_index]

    def update_ai_behaviors(self):
        self.ai_system.update()

    def run(self):
        self.initialize_screens()
        self.entity = self.entities.entities[self.entity_index]
        while True:
            if 1:
                self.screen.render()
                self.screen.dirty = False
            processed = self.screen.process()
            if not processed:
                if self.requires_input:
                    self.keypress = self.input_system.process()
                processed = self.screen.process()
            if not self.running:
                # will not be shown if quit manually
                if self.player is None:
                    self.screens['deathmenu'].process()
                break
