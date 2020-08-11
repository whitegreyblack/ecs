# engine.py

"""Engine class to hold all objects"""

import logging
import random
import time
from collections import OrderedDict

from source.common import GameMode, join
from source.ecs.components import (Collision, Effect, Information, Movement,
                                   Openable, Position, components)
from source.ecs.managers import ComponentManager, EntityManager
from source.ecs.systems import RenderSystem
from source.logger import Logger
from source.router import Router
from source.screens import EmptyScreen
from source.stack import Stack


class Engine(object):

    def __init__(self, components, systems, terminal=None, keyboard=None):
        self.running: bool = True
        self.logger = Logger()
        self.debugger = Logger()
        # set to an invalid value. All entity ids are positive integers (>0)
        self.entity: int = -1
        
        self.add_terminal(terminal)
        self.keyboard: dict = keyboard

        self.world = None
        self.entities = EntityManager()
        self.init_managers(components)
        self.init_systems(systems)

        self.screens: Stack = Stack()
        self.router: Router = Router()
        
        self.entity: int = None
        self.entity_index: int = 0
        self.requires_input: bool = True
        self.keypress: str = None

        self.mode = GameMode.NORMAL
        self.entities_in_view: set = set()
        self.tiles_in_view: set = set()

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
        self.components = components
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

    def get_input(self):
        return self.terminal.read()

    def keypress_from_input(self, value):
        keys = self.keyboard.get(value, None)
        if isinstance(keys, tuple):
            return keys[int(self.terminal.state(self.terminal.TK_SHIFT))]
        return keys

    def get_keypress(self):
        self.requires_input = True
        return self.keypress

    def get_mouse_state(self):
        return (
            self.terminal.state(self.terminal.TK_MOUSE_X),
            self.terminal.state(self.terminal.TK_MOUSE_Y)
        )

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
        self.width = terminal.state(terminal.TK_WIDTH)
        self.height = terminal.state(terminal.TK_HEIGHT)

    @property
    def screen(self):
        return self.screens.top

    def add_screen(self, screen):
        self.screens.push(screen(self, self.terminal))

    def remove_screen(self, screens=1):
        for _ in range(screens):
            self.screens.pop()

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
                    blocks=False
                )
            )

    def reset_entity_index(self):
        self.entity_index = 0
        self.entity = self.entities.entity_ids[self.entity_index]

    def next_entity(self):
        self.entity_index += 1
        if self.entity_index > len(self.entities.entity_ids) - 1:
            self.entity = None
        else:
            self.entity = self.entities.entity_ids[self.entity_index]

    def update_ai_behaviors(self):
        self.ai_system.update()

    def clear_databases(self):
        for name, system in self.__dict__.items():
            if name.endswith('__system'):
                system.components.clear()

    def process(self):
        self.screen.render()
        processed = self.screen.process()
        if not processed:
            if self.requires_input:
                self.input_system.process()
            processed = self.screen.process()

    def run(self):
        if not self.screens:
            self.add_screen(EmptyScreen)
        self.entity = self.entities.entity_ids[self.entity_index]
        while self.running:
            self.process()
