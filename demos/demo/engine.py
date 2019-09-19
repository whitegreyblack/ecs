# engine.py

"""
Mini engine. Rewrite of source.engine due to removal of ui from old engine.

Defines systems, components, and managers that should be created and processed
during the main game.
"""
import random
import time

from source.common import join, join_drop_key, squares
from source.ecs import Position
from source.ecs.components import (AI, CurrentTurn, Information, Input,
                                   Movement, Position, TileMap, Turn)
from source.ecs.managers import ComponentManager, EntityManager
from source.generate import dimensions, matrix
from source.keyboard import keypress_to_direction

room = """
###############
#.............#
#.............#
#...#..#..#...#
#.............#
#.............#
###############"""[1:]

tick_time = 0.0
def timeout(tick_duration):
    """Times out if function processes faster than framerate"""
    def decorate(fn):
        def call(*args):
            global tick_time
            start = time.time()
            fn(*args)
            tick_time += time.time() - start
            if tick_time < tick_duration:
                time.sleep(tick_duration - tick_time)
                tick_time = 0.0
            return
        return call
    return decorate

def system_info(debug):
    def decorate(fn):
        def call(*args):
            arg, *args = args
            if debug:
                print(fn.__name__, 
                    arg.entity,
                    arg.current_turns.find(arg.entity))
            fn(arg)
        return call
    return decorate

@system_info(False)
def move_system(engine):
    for i, (p, m) in join(engine.positions, engine.movements):
        p.x += m.x
        p.y += m.y
        engine.movements.remove(i)

@system_info(False)
def initiative_system(engine):
    while True:
        entity = engine.entity
        # end of entity list
        if entity is None:
            engine.reset_entity_index()
            continue
        # entities that don't take any actions (tiles/items) are skipped
        if not engine.inputs.find(entity) and not engine.ais.find(entity):
            engine.next_entity()
            continue
        # add a current_turn component to make sure when iterating systems
        # only one entity is processed
        engine.current_turns.components.clear()
        engine.current_turns.add(entity, CurrentTurn())
        break
        
@system_info(True)
def input_system(engine):
    c = engine.current_turns.find(engine.entity)
    takes_turn = engine.inputs.find(engine.entity)
    if not c.finished and takes_turn:
        print('taking input')
        if takes_turn.needs_input:
            if engine.action is None:
                engine.requires_input = True
                return
            engine.inject_action()
            c.finished = True

@system_info(False)
def ai_system(engine):
    c = engine.current_turns.find(engine.entity)
    ai = engine.ais.find(engine.entity)
    if not c.finished and ai:
        room = engine.tilemaps.find(engine.room)
        position = engine.positions.find(engine.entity)
        spaces = {
            (x, y) 
                for y in range(1, room.height-1) 
                    for x in range(1, room.width-1)
        }
        moveable = [ 
            (x, y) 
                for x, y in squares(exclude_center=True) 
                    if (position.x+x, position.y+y) in spaces 
        ]
        engine.movements.add(engine.entity, 
                             Movement.random_move(moveable))
        c.finished = True

@system_info(False)
def cleanup_system(engine):
    engine.next_entity()

# def turn_system(engine):
#     room = engine.tilemaps.find(engine.room)
#     spaces = {
#         (x, y) for y in range(1, room.height-1) for x in range(1, room.width-1)
#     }
#     for e, p in engine.positions:
#         moveable = [ (x, y) for x, y in squares() if (p.x+x, p.y+y) in spaces ]
#         engine.movements.add(e, Movement.random_move(possible_spaces=moveable))

class Engine:
    def __init__(self):
        self.requires_input = False
        self.entities = EntityManager()
        self.player = None
        self.entity = None
        self.entity_index = -1
        self.system = None
        self.system_index = 0
        self.systems = []
        self.action = None

    def add_component(self, component_type):
        setattr(self, 
                component_type.manager, 
                ComponentManager(component_type))

    def add_components(self, *component_types):
        for ct in component_types:
            self.add_component(ct)

    def new_entity(self):
        return self.entities.create()

    def reset_entity_index(self):
        self.entity_index = 0
        self.entity = self.entities.entity_ids[self.entity_index]
    
    def next_entity(self):
        self.entity_index += 1
        if self.entity_index > len(self.entities.entity_ids) - 1:
            self.entity = None
        else:
            self.entity = self.entities.entity_ids[self.entity_index]

    def add_player(self):
        if self.player:
            return
        self.player = self.new_entity()
        self.positions.add(self.player, Position(1, 1))
        self.infos.add(self.player, Information("player"))
        self.inputs.add(self.player, Input(True))

    def del_player(self):
        self.positions.remove(self.player)
        self.infos.remove(self.player)
        self.inputs.remove(self.player)
        self.entities.remove(self.player)
        self.player = None
        self.requires_input = False

    def add_enemy(self):
        enemy = self.new_entity()
        self.positions.add(enemy, Position(5, 5))
        self.ais.add(enemy, AI())
        self.infos.add(enemy, Information("enemy"))

    def add_map(self): 
        m = matrix(room)
        w, h = dimensions(m)
        self.room = self.new_entity()
        self.tilemaps.add(self.room, TileMap(w, h))
        self.infos.add(self.room, Information("map"))

    def add_system(self, system):
        self.systems.append(system)

    def add_systems(self, *systems):
        self.systems += systems

    def reset_system_index(self):
        self.system_index = 0
        self.system = self.systems[self.system_index]

    def next_system(self):
        self.system_index += 1
        if self.system_index > len(self.systems) - 1:
            self.system = None
        else:
            self.system = self.systems[self.system_index]

    def handle_keypress(self, keypress):
        self.action = None
        print(keypress)
        if keypress in keypress_to_direction:
            self.action = Movement.keypress_to_direction(keypress)
            self.requires_input = False
        else:
            self.action = Movement(1, 1)
            self.requires_input = False
        print(self.action, self.requires_input)
    
    def inject_action(self):
        if not self.action or self.player:
            return
        manager = getattr(self, self.action.manager)
        manager.add(self.player, self.action)
        self.action = None

    # @timeout(tick_duration=.33)
    def process(self):
        global tick_time
        if not self.player:
            tick_duration = .33
        else:
            tick_duration = .0
        start = time.time()
        while True:
            if self.system is None:
                self.reset_system_index()
                break
            self.system(self) # process
            if self.requires_input:
                break
            self.next_system()
        tick_time += time.time() - start
        if tick_time < tick_duration:
            time.sleep(tick_duration - tick_time)
            tick_time = 0.0

    @classmethod
    def demo(self):
        e = Engine()
        e.add_components(Position, 
                         Information, 
                         AI, 
                         Movement,
                         Input, 
                         TileMap, 
                         CurrentTurn)
        # e.add_player()
        e.add_enemy()
        e.add_enemy()
        e.add_enemy()
        e.add_map()
        # e.add_systems(turn_system, move_system)
        e.add_systems(initiative_system, 
                      input_system,
                      ai_system, 
                      move_system,
                      cleanup_system)
        return e
