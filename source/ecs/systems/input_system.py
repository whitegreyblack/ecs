# input_system.py

"""Input system"""

import curses
import random
import time
from dataclasses import dataclass, field

from source.astar import pathfind
from source.common import eight_square, join, nine_square
from source.ecs.components import (Collision, Information, Item, Movement,
                                   Position, Render)
from source.ecs.systems.system import System
from source.keyboard import movement_keypresses

@dataclass
class Command:
    char: str
    keypress: str

@dataclass
class DoorAction:
    position: object
    direction: object
    def __iter__(self):
        yield self.x
        yield self.y
    @property
    def x(self):
        return self.position.x + self.direction.x
    @property
    def y(self):
        return self.position.y + self.direction.y

class InputSystem(System):
    def open_door(self, entity):
        """TODO: render log message when opening a door of multiple doors"""
        position = self.engine.positions.find(entity)        
        turn_over = False
        coordinates = []
        # get all cardinal coordinates surrounding current entity position
        for x, y in eight_square():
            coordinates.append((position.x + x, position.y + y))
        g = join(
            self.engine.openables, 
            self.engine.positions, 
            self.engine.renders
        )
        doors = {}
        # compare coordinates against entities that can be opened that have a
        # a position x, y value in the coordinates list.
        for entity_id, (openable, coordinate, render) in g:
            valid_coordinate = (coordinate.x, coordinate.y) in coordinates
            if valid_coordinate and not openable.opened:
                x = coordinate.x - position.x
                y = coordinate.y - position.y
                doors[(x, y)] = (openable, coordinate, render)
        door_to_open = None
        if not doors:
            self.engine.logger.add(f"No closed doors to open")
        elif len(doors) == 1:
            door_to_open, = doors.items()
        else:
            self.engine.logger.add(f"Which door to open?")
            self.engine.render_system.render_logs()
            char = self.engine.get_input()
            # invalid keypress
            if not 258 <= char < 262:
                self.engine.logger.add(f"You cancel opening a door due to input error")
                return turn_over
            keypress = self.engine.keyboard[char]
            movement = Movement.from_input(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel opening a door direction invalid error")
            door_to_open = ((movement.x, movement.y), door)
        if door_to_open:
            ((x, y), (openable, position, render)) = door_to_open
            openable.opened = True
            position.blocks_movement = False
            render.char = '/'
            self.engine.logger.add(f"You open the door")
            turn_over = True
        return turn_over    

    def close_door(self, entity):
        """TODO: cannot close door when unit is standing on the cell"""
        position = self.engine.positions.find(entity)
        turn_over = False
        coordinates = []
        for x, y in eight_square():
            coordinates.append((position.x + x, position.y + y))
        g = join(
            self.engine.openables, 
            self.engine.positions, 
            self.engine.renders
        )
        doors = {}
        # compare coordinates against entities that can be closed that have a
        # a position x, y value in the coordinates list.
        for entity_id, (openable, coordinate, render) in g:
            if (coordinate.x, coordinate.y) in coordinates and openable.opened:
                x = coordinate.x - position.x
                y = coordinate.y - position.y
                doors[(x, y)] = (openable, coordinate, render)
        door_to_close = None
        if not doors:
            self.engine.logger.add(f"No opened door to close")
        elif len(doors) == 1:
            door_to_close, = doors.items()
        else:
            self.engine.logger.add(f"Which door to open?")
            self.engine.render_system.render_logs()
            char = self.engine.get_input()
            # invalid keypress
            if not 258 <= char < 262:
                self.engine.logger.add(f"You cancel closing a door")
                return turn_over
            keypress = self.engine.keyboard[char]
            movement = Movement.from_input(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel closing a door")
            door_to_close = ((movement.x, movement.y), door)
        if door_to_close:
            ((x, y), (openable, position, render)) = door_to_close
            openable.opened = False
            position.blocks_movement = True
            render.char = '+'
            self.engine.logger.add(f"You close the door")
            turn_over = True
        return turn_over

    def collide(self, entity, collision):
        other = self.engine.entities.find(eid=collision.entity_id)
        collider = self.engine.infos.find(entity)
        collidee = self.engine.infos.find(other)

        health = self.engine.healths.find(eid=collision.entity_id)
        if not health and entity == self.engine.player:
            self.engine.logger.add(f'collided with a {collidee.name}({collision.entity_id})')
            return False
        elif health:
            if collider.name.startswith('goblin') and collidee.name.startswith('goblin'):
                # self.engine.logger.add(f"bumped into friendly")
                return True
            cur_hp = health.cur_hp
            max_hp = health.max_hp
            health.cur_hp -= 1
            log = f"Attacked {collidee.name} for 1 damage ({cur_hp}->{health.cur_hp})."
            if health.cur_hp < 1:
                self.drop_inventory(other)
                self.drop_body(other)
                self.delete(other)
                if other == self.engine.player:
                    self.engine.player = None
                    self.engine.running = False
                log += f" {collidee.name.capitalize()} died."
            self.engine.logger.add(log)
            return True

    def drop_inventory(self, entity):
        position = self.engine.positions.find(entity)
        inventory = self.engine.inventories.find(entity)
        if not inventory:
            return
        while inventory.items:
            item_id = inventory.items.pop()
            item = self.engine.entities.find(eid=item_id)
            item_position = position.copy(moveable=False, blocks_movement=False)
            self.engine.positions.add(item, item_position)
    
    def drop_body(self, entity):
        position = self.engine.positions.find(entity)
        info = self.engine.infos.find(entity)
        body = self.engine.entities.create()
        self.engine.items.add(body, Item())
        self.engine.renders.add(body, Render('%'))
        self.engine.infos.add(body, Information(f"{info.name} corpse"))
        self.engine.positions.add(body, position.copy(
            moveable=False,
            blocks_movement=False
        ))

    def delete(self, entity):
        for system in self.engine.systems:
            system.remove(entity)
        self.engine.entities.remove(entity)

    def move(self, entity, movement) -> bool:
        position = self.engine.positions.find(entity)
        if not position or not movement:
            return False
        x, y = position.x + movement.x, position.y + movement.y

        positions = [
            (entity_id, position)
                for entity_id, position in self.engine.positions
                    if position.map_id == self.engine.world.id
        ]

        for other_id, other_position in positions:
            if other_id == entity.id or not other_position.blocks_movement:
                continue
            future_position_blocked = (
                x == other_position.x and y == other_position.y
            )
            if future_position_blocked:
                return self.collide(entity, Collision(other_id))

        position.x += movement.x
        position.y += movement.y
        return True

    def check_down_stairs(self, entity):
        """Check if entity position is on stairs else return False"""
        turn_over = False
        position = self.engine.positions.find(entity)
        tilemap = self.engine.tilemaps.find(eid=position.map_id)

        # could just do a for loop b
        tiles = join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        )
        for eid, (tile, tile_position, render) in tiles:
            # only care about tiles with the current map id
            if position.map_id != self.engine.world.id:
                continue
            if tile_position == position and render.char == '>':
                turn_over = True
                break
        return turn_over

    def go_down(self, entity):
        tiles = join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        )
        up_stairs_position = None
        for eid, (tile, tile_position, render) in tiles:
            if tile_position.map_id != self.engine.world.id:
                continue
            if render.char == '<':
                up_stairs_position = tile_position
                break
        if not up_stairs_position:
            raise Exception("No upstairs tile found in tilemap")
        position = self.engine.positions.find(entity)
        position.x = up_stairs_position.x
        position.y = up_stairs_position.y
        position.map_id = self.engine.world.id
        return True

    def check_up_stairs(self, entity):
        """Check if entity position is on stairs else return False"""
        turn_over = False
        position = self.engine.positions.find(entity)
        tilemap = self.engine.tilemaps.find(eid=position.map_id)

        # could just do a for loop b
        tiles = join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        )
        for eid, (tile, tile_position, render) in tiles:
            # only care about tiles with the current map id
            if position.map_id != self.engine.world.id:
                continue
            if tile_position == position and render.char == '<':
                turn_over = True
                break
        return turn_over

    def go_up(self, entity):
        tiles = join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        )
        up_stairs_position = None
        for eid, (tile, tile_position, render) in tiles:
            if tile_position.map_id != self.engine.world.id:
                continue
            if render.char == '>':
                up_stairs_position = tile_position
                break
        if not up_stairs_position:
            raise Exception("No upstairs tile found in tilemap")
        position = self.engine.positions.find(entity)
        position.x = up_stairs_position.x
        position.y = up_stairs_position.y
        position.map_id = self.engine.world.id
        return True

    def wander(self, entity):
        possible_spaces = []
        for x, y in nine_square():
            possible_spaces.append((x, y))
        index = random.randint(0, len(possible_spaces)-1)
        x, y = possible_spaces[index]
        if x == 0 and y == 0:
            return True
        return self.move(entity, Movement(x, y))

    def wait(self, entity):
        return True

    def pick_item(self, entity):
        position = self.engine.positions.find(entity)
        inventory = self.engine.inventories.find(entity)
        g = join(
            self.engine.items,
            self.engine.positions,
            self.engine.infos
        )
        descriptions = []
        items_picked_up = []
        for eid, (item, item_position, info) in g:
            if (position.x, position.y) == (item_position.x, item_position.y):
                items_picked_up.append(eid)
                descriptions.append(info.name)
        if not items_picked_up:
            return False
        for eid in items_picked_up:
            # remove from map
            entity = self.engine.entities.find(eid)
            self.engine.visibilities.remove(entity)
            self.engine.renders.remove(entity)
            self.engine.positions.remove(entity)
            # add to inventory
            inventory.items.append(entity.id)
        self.engine.logger.add(f"Picked up {', '.join(descriptions)}")
        return True

    def player_command(self, entity):
        moved = False
        while True:
            exit_prog = False
            turn_over = False
            char = self.engine.get_input()
            if char == -1:
                break
            keypress = self.engine.keypress_from_input(char)
            self.engine.logger.add(f"{char}: {chr(char)}")
            if keypress == 'q':
                self.engine.running = False
                break
            elif char in movement_keypresses:
                turn_over = self.move(entity, Movement.from_input(keypress))
                moved = True
            elif keypress == 'escape':
                self.engine.render_system.main_menu.process()
                if not self.engine.running:
                    break
            elif keypress == 'i':
                self.engine.render_system.inventory_menu.process()
            elif keypress == 'o':
                turn_over = self.open_door(entity)
            elif keypress == 'c':
                turn_over = self.close_door(entity)
            elif keypress == 'comma':
                turn_over = self.pick_item(entity)
            elif keypress == 'l':
                self.engine.render_system.looking_menu.process()
            elif keypress == 'less-than':
                stairs_exists = self.check_up_stairs(entity)
                world_exists = self.engine.world.go_up()
                if stairs_exists and world_exists:
                    turn_over = self.go_up(entity)
                elif not stairs_exists:
                    self.engine.logger.add("No stairs to descend into")
                else:
                    self.engine.logger.add("No world to descend into")
            elif keypress == 'greater-than':
                if self.check_down_stairs(entity) and self.engine.world.go_down():
                    turn_over = self.go_down(entity)
            else:
                self.engine.logger.add(f"unknown command {char} {chr(char)}")
            self.engine.logger.add(f"{157}: {chr(157)}")
            if turn_over:
                break
            self.engine.render_system.process()
        return moved

    def computer_command(self, entity):
        """Computer commands currently only support mindless movement"""
        # simple ai logic (move, attack if enemy exists, run away)
        
        # check to see if computer is an pre-determined enemy entity
        position = self.engine.positions.find(entity)
        info = self.engine.infos.find(entity)
        ai = self.engine.ais.find(entity)

        if ai.behavior == 'wander':
            return self.wander(entity)
        elif ai.behavior == 'attack':
            if ai.path:
                path = ai.path.pop(0)
                movement = Movement(path[0] - position.x, path[1] - position.y)
            else:
                target_position = self.engine.positions.find(self.engine.player)
                # self.engine.logger.add(f"{position.x} {position.y}")
                # self.engine.logger.add(f"{target_position.x} {target_position.y}")
                ai.path = pathfind(self.engine, position, target_position)
                # self.engine.logger.add(f'finding path: {ai.path}')
                if not ai.path:
                    # self.engine.logger.add(f'{info.name}({entity.id}) lost enemy. Wandering')
                    ai.behavior = 'wander'
                    return self.wander(entity)
                path = ai.path.pop(0)
                # self.engine.logger.add(str(path))
                movement = Movement(path[0] - position.x, path[1] - position.y)
            # self.engine.logger.add(str(len(path)) + ' ' + str(movement))
            return self.move(entity, movement)
        elif ai.behavior == 'run':
            ...
        elif ai.behavior == 'wait':
            return self.wait(entity)

    def update_ai_behaviors(self):
        units = join(
            self.engine.healths,
            self.engine.positions,
            self.engine.infos,
            self.engine.ais
        )
        tiles = {
            (p.x, p.y)
                for _, (p, v) in join(
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if v.level > 1
        }
        
        for eid, (h, p, i, ai) in units:
            # self.engine.logger.add(f"Procesing {i.name}({eid})")
            v = (p.x, p.y) in tiles
            # self.engine.logger.add(f"{i.name}({eid}) was {ai.behavior}ing")
            # self.engine.logger.add(f"{i.name}({eid}), Can see player: {v}")
            if v:
                if ai.behavior != 'attack':
                    # self.engine.logger.add(f"{i.name}({eid}) is now attacking")
                    ai.behavior = 'attack'
                if ai.behavior == 'attack':
                    ai.path = None # overwrite path
            # player is not seen and monster was attacking but finished reaching path
            if not v and ai.behavior == 'attack':
                # self.engine.logger.add(f"goblin moving towards {ai.path}")
                if not ai.path:
                    # self.engine.logger.add(f"{i.name}({eid}) stopped attacking")
                    ai.behavior = 'wander'
        # self.engine.logger.add(f"Behaviors changed")

    def process(self):
        # need to make this as a list since inputs size can change during runtime
        inputs = list(self.engine.inputs)
        for entity_id, need_input in inputs:
            entity = self.engine.entities.find(entity_id)
            if not entity:
                continue
            ai = self.engine.ais.find(entity)
            if ai:
                command = self.computer_command(entity)
                # command = self.move(entity, Movement(0, 0))
            else:
                command = self.player_command(entity)
                if command:
                    self.engine.render_system.render_fov()
                    self.update_ai_behaviors()
            if not self.engine.running:
                break
