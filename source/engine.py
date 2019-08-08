# engine.py

"""Engine class to hold all objects"""

import curses
import random
import time
from collections import OrderedDict
from dataclasses import dataclass, field

from source.common import join
from source.ecs.components import (Collision, Effect, Information, Movement,
                                   Openable, Position, components)
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

        self.world = None
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
        for system_type in systems:
            name = f"{system_type.classname().replace('system', '')}_system"
            if system_type.__name__ == 'RenderSystem':
                system = system_type(self, self.terminal)
            else:
                system = system_type(self)
            self.__setattr__(name, system)

    def get_input(self):
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
        self.screen = self.screens.get(name, 'mainmenu')
        self.screen.state = 'open'

    def reset_entity_index(self):
        self.entity_index = 0
        self.entity = self.entities.entities[self.entity_index]

    def next_entity(self):
        # self.entity_index = (self.entity_index + 1) % len(self.entities.entities)
        self.entity_index += 1
        if self.entity_index > len(self.entities.entities) - 1:
            self.entity = None
        else:
            self.entity = self.entities.entities[self.entity_index]

    def update_ai_behaviors(self):
        self.ai_system.update()

    def clear_databases(self):
        systems = (v for k, v in self.__dict__.items() if k.endswith('__system'))
        for system in systems:
            system.components.clear()

    def get_keypress(self):
        self.requires_input = True
        return self.keypress

    def process(self, t):
        self.screen.render()
        processed = self.screen.process()
        if not processed:
            if self.requires_input:
                self.input_system.process()
            processed = self.screen.process()
        # time.sleep((max(1./25 - (time.time() - t), 0)))

    def run(self):
        self.initialize_screens()
        self.entity = self.entities.entities[self.entity_index]
        t = time.time()
        while self.running:
            self.process(t)
            t = time.time()

    def count_objects(self):
        """Debugging information and object counting"""
        m = 0
        s = 0
        for c in sorted(components, key=lambda x: x.classname()):
            l = len(getattr(self, c.manager).components)
            g = len(getattr(self, c.manager).shared)
            if c.manager == 'tiles': # ('renders', 'infos'):
                print(c.manager, l, g, c.instantiated)
            else:
                print(c.manager, l, g)
            m += l
            s += g
        print('total objects:', m, s)

        print(len(list(join(
            self.tiles, 
            self.positions, 
            self.visibilities, 
            self.renders, 
            self.infos
        ))))

        print(len(list(join(
            self.healths,
            self.positions,
            self.infos,
            self.renders
        ))))

        print(len(list(join(
            self.healths,
            self.positions,
            self.infos,
            self.renders,
            self.inventories
        ))))
