# command_system.py

"""Refactor from input_system.py"""

import curses
import random
import time

from source.common import eight_square, join, nine_square, squares
from source.ecs.components import (Collision, Effect, Information, Item,
                                   Movement, Render)
from source.ecs.systems.system import System
from source.keyboard import keypress_to_direction, movement_keypresses


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
        for closeable_id, (closeable, coordinate, render) in g:
            if (coordinate.x, coordinate.y) in coordinates and closeable.opened:
                x = coordinate.x - position.x
                y = coordinate.y - position.y
                doors[(x, y)] = (closeable_id, closeable, coordinate, render)
        print(doors)
        door_to_close = None
        if not doors:
            self.engine.logger.add(f"No opened door to close.")
        elif len(doors) == 1:
            door_to_close, = doors.values()
        else:
            self.engine.logger.add(f"Which door to close?")
            self.engine.screen.render()
            self.engine.input_system.process(
                keypresses=set(keypress_to_direction.keys()).union(('escape',))
            )
            keypress = self.engine.get_keypress()
            movement = Movement.keypress_to_direction(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel closing a door.")
            else:
                door_to_close = door
        if door_to_close:
            print(door_to_close)
            door_id, closeable, position, render = door_to_close
            door_entity = self.engine.entities.find(door_id)
            closeable.opened = False
            position.blocks_movement = True
            self.engine.renders.add(
                door_entity, 
                random.choice(self.engine.renders.shared['closed wooden door'])
            )
            self.engine.logger.add(f"You close the door.")
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
        for openable_id, (openable, coordinate, render) in g:
            valid_coordinate = (coordinate.x, coordinate.y) in coordinates
            if valid_coordinate and not openable.opened:
                x = coordinate.x - position.x
                y = coordinate.y - position.y
                doors[(x, y)] = (openable_id, openable, coordinate, render)
        door_to_open = None
        if not doors:
            self.engine.logger.add(f"No closed doors to open.")
        elif len(doors) == 1:
            door_to_open, = doors.values()
        else:
            self.engine.logger.add(f"Which door to open?")
            self.engine.screen.render()
            self.engine.input_system.process(
                keypresses=set(keypress_to_direction.keys()).union(('escape',))
            )
            keypress = self.engine.get_keypress()
            movement = Movement.keypress_to_direction(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(f"You cancel opening a door direction invalid error.")
            else:
                door_to_open = door
        if door_to_open:
            openable_id, openable, position, render = door_to_open
            openable_entity = self.engine.entities.find(openable_id)
            openable.opened = True
            position.blocks_movement = False
            self.engine.renders.add(
                openable_entity, 
                random.choice(self.engine.renders.shared['opened wooden door'])
            )
            self.engine.logger.add(f"You open the door.")
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
        items = []
        items_picked_up = []
        for eid, (item, item_position, info) in g:
            if (position.x, position.y) == (item_position.x, item_position.y):
                items_picked_up.append(eid)
                items.append(info.name)
        if not items_picked_up:
            return False
        for eid in items_picked_up:
            # remove from map
            entity = self.engine.entities.find(eid)
            self.engine.visibilities.remove(entity)
            # self.engine.renders.remove(entity)
            self.engine.positions.remove(entity)
            # add to inventory
            inventory.items.append(entity.id)
        if len(items) > 2:
            item_str = f"a {', a '.join(items[:len(items)-1])}, and a {items[-1]}"
        elif len(items) == 2:
            item_str = f"a {items[0]} and a {items[1]}"
        else:
            item_str = f"a {items[0]}"
        self.engine.logger.add(f"You pick up {item_str}.")
        return True

    def check_for_floor_items(self, position):
        query = join(
            self.engine.items, 
            self.engine.positions, 
            self.engine.infos
        )
        items = []
        for eid, (_, tile, info) in query:
            if position == tile:
                items.append(info.name)
        if items:
            if len(items) > 2:
                item_str = f"a {', a'.join(items[:len(items)-1])}, and a {items[-1]}"
            elif len(items) == 2:
                item_str = f"a {items[0]} and a {items[1]}"
            else:
                item_str = f"a {items[0]}"
            self.engine.logger.add(f"You step on {item_str}.")

    def attack(self, entity, other):
        # attacker properties
        is_player = entity == self.engine.player
        attacker = self.engine.infos.find(entity)
        equipment = self.engine.equipments.find(entity)

        # attackee properties
        attackee = self.engine.infos.find(other)
        health = self.engine.healths.find(other)
        armor = self.engine.armors.find(other)
        
        # damage calculations
        damage = 1
        if equipment and equipment.hand:
            weapon = self.engine.weapons.find(eid=equipment.hand)
            if weapon:
                damage = weapon.damage

        # armor based reductions
        if armor:
            damage = max(0, damage - armor.defense)

        # final health loss
        health.cur_hp -= damage

        # record fight
        strings = []
        if is_player:
            strings.append(f"You attack the {attackee.name} for {damage} damage")
        else:
            strings.append(f"The {attacker.name} attacks the {attackee.name} for {damage} damage")
        if damage < 1:
            strings.append(f", but the attack did no damage!")
        else:
            strings.append(".")
        if health.cur_hp < 1:
            strings.append(f" The {attackee.name} dies.")
            self.engine.grave_system.process(other)
        else:
            # add a hit effect
            self.engine.effects.add(entity, Effect(other.id, '*', 0))
        self.engine.logger.add(''.join(strings))
        return True

    def collide(self, entity, collision):
        # oob or environment collision. No logged message. Exit early
        if collision.entity_id == -1:
            return False
        other = self.engine.entities.find(eid=collision.entity_id)
        is_player = entity == self.engine.player
        collidee = self.engine.infos.find(other)
        health = self.engine.healths.find(eid=collision.entity_id)
        if not health:
            if is_player:
                self.engine.logger.add(f'Collided with a {collidee.name}.')
            return False
        # process unit to unit collision
        collider = self.engine.infos.find(entity)
        # same species coexist
        if collider.name == collidee.name:
            return True
        return self.attack(entity, other)

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
                        and entity_id != entity.id
                        and position.blocks_movement
        ]

        for other_id, other_position in positions:
            future_position_blocked = (
                x == other_position.x and y == other_position.y
            )
            if future_position_blocked:
                return self.collide(entity, Collision(other_id))
        position.x += movement.x
        position.y += movement.y

        if entity == self.engine.player:
            self.check_for_floor_items(position)
        return True

    def go_up(self, entity):
        """Check if entity position is on stairs. If true go up"""
        went_up = False
        position = self.engine.positions.find(entity)
        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        for _, (_, tile_position, render) in join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        ):
            if (tile_position.map_id == self.engine.world.id
                and tile_position == position
                and render.char == '<'):
                break
            else:
                tile_position = None
            
        if not tile_position:
            self.engine.logger.add('Could not go up since not on stairs')
            return went_up

        old_id = self.engine.world.id
        up = self.engine.world.go_up()
        if old_id != self.engine.world.id:
            self.engine.map_system.regenerate_map(old_id)
        else:
            self.engine.logger.add('no parent node.')

        for _, (_, tile_position, render) in join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        ):
            if (tile_position.map_id == self.engine.world.id
                and render.char == '>'):
                break
        
        position = tile_position.copy(
            moveable=position.moveable, 
            blocks_movement=position.blocks_movement
        )
        self.engine.positions.remove(self.engine.player)
        self.engine.positions.add(self.engine.player, position)
        return True

    def go_down(self, entity):
        """Check if entity position is on stairs. If true go down"""
        went_down = False
        position = self.engine.positions.find(entity)
        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        
        # should only return 1 tile/render pair
        for _, (_, tile_position, render) in join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        ):
            # tile from current map / same map position as entity / is down stairs
            if (tile_position.map_id == self.engine.world.id
                and tile_position == position
                and render.char == '>'):
                break
            else:
                tile_position = None
        
        if not tile_position:
            self.engine.logger.add('Could not go down since not on stairs')
            return went_down
        
        old_id = self.engine.world.id
        self.engine.world.go_down()
        if old_id == self.engine.world.id:
            # TODO: generate child map to go down. For now return False
            # self.engine.logger.add('Could not go down since no child map')
            # return went_down
            self.engine.map_system.generate_map()
            self.engine.world.go_down()
        else:
            self.engine.map_system.regenerate_map(old_id)

        for _, (_, tile_position, render) in join(
            self.engine.tiles,
            self.engine.positions,
            self.engine.renders
        ):
            # tile from current map / is up stairs
            if (tile_position.map_id == self.engine.world.id
                and render.char == '<'):
                break

        if not tile_position:
            self.engine.logger.add('Could not go down since child map has no up stairs')
            return went_down
        
        # send entity to the position of stairs on child map
        position = tile_position.copy(
            moveable=position.moveable, 
            blocks_movement=position.blocks_movement
        )
        self.engine.positions.remove(self.engine.player)
        self.engine.positions.add(self.engine.player, position)
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
        elif command == 'greater-than':
            return self.go_down(entity)
        elif command == 'less-than':
            return self.go_up(entity)
