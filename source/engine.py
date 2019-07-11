# engine.py

"""Engine class to hold all objects"""

import curses
import random
import time
from dataclasses import dataclass, field

from source.ecs.components import (Collision, Information, Movement, Openable,
                                   Position)
from source.ecs.managers import ComponentManager, EntityManager
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

    def find_entity(self, entity_id):
        return self.entity_manager.find(entity_id)

    def add_world(self, world):
        if hasattr(self, 'world') and getattr(self, 'world'):
            raise Exception("world already initialized")
        self.world = world

    def add_terminal(self, terminal):
        if not terminal:
            return
        if hasattr(self, 'terminal') and getattr(self, 'terminal'):
            raise Exception("terminal already initialized")
        self.terminal = terminal
        self.height, self.width = terminal.getmaxyx()
        print(self.height, self.width)

    def add_player(self, entity):
        self.player = entity
        self.player_id = entity.id

    def add_component(self, entity, component, *args):
        manager = getattr(self, component + '_manager')
        if not manager:
            raise Exception(f"No component of type name: {component}")
        manager.add(entity, self.components[component](*args))

    def get_manager(self, component):
        manager = getattr(self, component)
        if not manager:
            raise Exception(f"No component of type name: {component}")
        return manager

    def startup(self):
        self.render_system.initialize_coordinates()
        self.render_system.initialize_menus()

    def run(self):
        self.startup()
        while True:
            self.render_system.render_fov()
            self.render_system.process()
            self.movements.components.clear()
            self.input_system.process()
            if not self.running:
                if self.player is None:
                    self.render_system.death_menu.process()
                break
