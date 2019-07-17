# command_system.py

"""Refactor from input_system.py"""

import random

from source.common import eight_square, join, nine_square, squares
from source.ecs.components import (Collision, Information, Item, Movement,
                                   Render)
from source.ecs.systems.system import System
from source.keyboard import movement_keypresses, keypress_to_direction


class CommandSystem(System):

    def close_door(self, entity):
        """TODO: cannot close door when unit is standing on the cell"""
        position = self.engine.positions.find(entity)
        turn_over = False
        # get all cardinal coordinates surrounding current entity position
        coordinates = [
            (position.x + x, position.y + y)
                for x, y in squares(exclude_center=True)
        ]
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
            self.engine.logger.add(f"Which door to close?")
            self.engine.screen.render_logs_panel()
            char = self.engine.get_input()
            # invalid keypress
            if not 258 <= char < 262:
                self.engine.logger.add(f"You cancel closing a door")
                return turn_over
            keypress = self.engine.keyboard[char]
            movement = Movement.keypress_to_direction(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel closing a door")
            else:
                door_to_close = ((movement.x, movement.y), door)
        if door_to_close:
            ((x, y), (openable, position, render)) = door_to_close
            openable.opened = False
            position.blocks_movement = True
            render.char = '+'
            self.engine.logger.add(f"You close the door")
            turn_over = True
        return turn_over

    def open_door(self, entity):    
        """TODO: render log message when opening a door of multiple doors"""
        position = self.engine.positions.find(entity)
        turn_over = False
        # get all cardinal coordinates surrounding current entity position
        coordinates = [
            (position.x + x, position.y + y)
                for x, y in squares(exclude_center=True)
        ]
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
            self.engine.screen.render_logs_panel()
            char = self.engine.get_input()
            # invalid keypress
            if not 258 <= char < 262:
                self.engine.logger.add(f"You cancel opening a door due to input error")
                return turn_over
            keypress = self.engine.keyboard[char]
            movement = Movement.keypress_to_direction(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel opening a door direction invalid error")
            else:
                door_to_open = ((movement.x, movement.y), door)
        if door_to_open:
            ((x, y), (openable, position, render)) = door_to_open
            openable.opened = True
            position.blocks_movement = False
            render.char = '/'
            self.engine.logger.add(f"You open the door")
            turn_over = True
        return turn_over    

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

    def delete(self, entity):
        for system in self.engine.systems:
            system.remove(entity)
        self.engine.entities.remove(entity)

    def drop_body(self, entity):
        position = self.engine.positions.find(entity)
        info = self.engine.infos.find(entity)
        body = self.engine.entities.create()
        self.engine.items.add(body, Item())
        self.engine.renders.add(body, Render('%'))
        self.engine.infos.add(body, Information(f"a {info.name} corpse"))
        self.engine.positions.add(body, position.copy(
            moveable=False,
            blocks_movement=False
        ))

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

    def collide(self, entity, collision):
        # oob. No logged message
        if collision.entity_id == -1:
            return False
        other = self.engine.entities.find(eid=collision.entity_id)
        collider = self.engine.infos.find(entity)
        player = entity == self.engine.player
        collidee = self.engine.infos.find(other)

        health = self.engine.healths.find(eid=collision.entity_id)
        if not health and entity == self.engine.player:
            self.engine.logger.add(f'Collided with a {collidee.name}.')
            return False
        elif health:
            # same species coexist
            if collider.name == collidee.name:
                return True
            cur_hp = health.cur_hp
            max_hp = health.max_hp
            health.cur_hp -= 1
            strings = []
            if player:
                strings.append(f"You attack the {collidee.name} for 1 damage")
            else:
                strings.append(f"The {collider.name} attacks the {collidee.name} for 1 damage")
            strings.append(f"({cur_hp}->{health.cur_hp}).")
            if health.cur_hp < 1:
                self.drop_inventory(other)
                self.drop_body(other)
                self.delete(other)
                if other == self.engine.player:
                    self.engine.player = None
                    self.engine.running = False
                strings.append(f"The {collidee.name} dies.")
            self.engine.logger.add(' '.join(strings))
            return True

    def move(self, entity, movement) -> bool:
        position = self.engine.positions.find(entity)
        if not position or not movement:
            return False
        x, y = position.x + movement.x, position.y + movement.y

        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
            return self.collide(entity, Collision(-1))

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

    def process(self, entity, command):
        if command in movement_keypresses:
            return self.move(entity, Movement.keypress_to_direction(command))
        elif command == 'escape':
            self.engine.change_screen('gamemenu')
            return False
        elif command == 'i':
            self.engine.change_screen('inventorymenu')
            return False
        elif command == 'e':
            self.engine.change_screen('equipmentmenu')
            return False
        elif command == 'comma':
            return self.pick_item(entity)
        elif command == 'o':
            return self.open_door(entity)
        elif command == 'c':
            return self.close_door(entity)
