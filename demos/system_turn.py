# system_turn.py

import curses

from source.ecs.components import Health, Position, TileMap, Tile, Turn
from source.ecs.managers import ComponentManager, EntityManager
from source.ecs.screens import GameMenu, GameScreen, MainMenu
from source.ecs.systems import InputSystem, MapSystem, System
from source.engine import Engine
from source.events import CommandEvent, TurnEvent
from source.graph import DungeonMap, DungeonNode
from source.keyboard import keyboard
from source.maps import dungeons
from source.router import EventRouter, Router


class DemoMainMenu(MainMenu):
    def handle_input(self):
        # keep_open, exit_prog
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'escape' or (key == 'enter' and option == 'quit'):
            self.engine.running = False
        elif key == 'enter' and option == 'new game':
            # create world
            world_graph = {}
            mappairs = ((0, dungeons['shadowbarrow']),)
            g = {
                0: DungeonNode(0, child_id=1),
                1: DungeonNode(1, parent_id=0),
            }
            # create entity per node
            for eid, node in g.items():
                world_graph[eid] = node
                self.engine.entities.add(eid)
            # create components per entity
            for eid, mapstring in mappairs:
                self.engine.map_system.generate_map(eid, mapstring)
            spaces = find_empty_spaces(self.engine)
            # add player
            self.engine.player = self.engine.spawn_system.spawn_player(spaces.pop())
            # add player cursor
            self.engine.cursor = self.engine.spawn_system.spawn_cursor(self.engine.player)
            # add computers
            for i in range(2):
                self.engine.spawn_system.spawn_unit(spaces.pop())
            # add items
            for i in range(2):
                self.engine.spawn_system.spawn_item(spaces.pop())
            self.engine.change_screen('gamescreen')
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up': # up
            self.index = (self.index - 1) % len(self.options)

class TurnSystem(System):
    def process(self):
        ...

def create_engine(terminal):
    e = Engine()
    e.add_component_managers(Health, 
                             Position, 
                             Turn, 
                             TileMap, 
                             Tile)
    e.add_systems(InputSystem, TurnSystem, MapSystem)
    e.add_router(Router)
    e.add_event_router(EventRouter)
    e.add_entity_manager(EntityManager) # could be instantiated in engine
    e.add_terminal(terminal)
    e.add_keyboard(keyboard)
    e.add_screens(DemoMainMenu, GameScreen, GameMenu)

    return e

def main(terminal):
    e = create_engine(terminal)
    e.run()

if __name__ == "__main__":
    curses.wrapper(main)
