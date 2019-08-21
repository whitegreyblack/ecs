# command_system.py

"""Refactor from input_system.py"""

import curses
import random
import time

from source.common import GameMode, join, join_drop_key, squares
from source.ecs.components import (Collision, Effect, Information, Item,
                                   MeleeHitEffect, Movement, Position,
                                   RangeHitEffect, Render)
from source.ecs.systems.system import System
from source.keyboard import keypress_to_direction, movement_keypresses
from source.messenger import Logger
from source.pathfind import pathfind, bresenhams


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
            door, closeable, position, render = door_to_close
            closeable.opened = False
            position.blocks_movement = True
            self.engine.renders.add(
                door, 
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
            self.engine.renders,
            self.engine.infos
        )
        doors = {}
        # compare coordinates against entities that can be opened that have a
        # a position x, y value in the coordinates list.
        for openable_id, (openable, coordinate, render, info) in g:
            valid_coordinate = (coordinate.x, coordinate.y) in coordinates
            if valid_coordinate and not openable.opened:
                x = coordinate.x - position.x
                y = coordinate.y - position.y
                doors[(x, y)] = (
                    openable_id, 
                    openable, 
                    coordinate, 
                    render, 
                    info
                )
        door_to_open = None
        if not doors:
            self.engine.logger.add(f"No closed doors to open.")
        elif len(doors) == 1:
            door_to_open, = doors.values()
        else:
            self.engine.logger.add(f"Which door to open?")
            self.engine.screen.render()
            self.engine.input_system.process(
                valid_keypresses=set(keypress_to_direction).union(('escape',))
            )
            keypress = self.engine.get_keypress()
            movement = Movement.keypress_to_direction(keypress)
            # valid direction keypress but not valid door direction
            door = doors.get((movement.x, movement.y), None)
            if not door:
                self.engine.logger.add(
                    f"You cancel opening a door direction invalid error."
                )
            else:
                door_to_open = door
        if door_to_open:
            door, openable, position, render, info = door_to_open
            openable.opened = True
            position.blocks_movement = False
            # replace info
            self.engine.infos.add(
                door,
                self.engine.infos.shared['opened wooden door']
            )
            # replace the render
            self.engine.renders.add(
                door, 
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
        for entity in items_picked_up:
            # remove from map
            self.engine.visibilities.remove(entity)
            # self.engine.renders.remove(entity)
            self.engine.positions.remove(entity)
            # add to inventory
            inventory.items.append(entity)
        if len(items) > 2:
            item_str = f"a {', a '.join(items[:len(items)-1])}, and a {items[-1]}"
        elif len(items) == 2:
            item_str = f"a {items[0]} and a {items[1]}"
        else:
            item_str = f"a {items[0]}"
        self.engine.logger.add(f"You pick up {item_str}.")
        return True

    def missile(self, cursor):
        self.engine.logger.add("Throwing")
        end = self.engine.positions.find(cursor)
        cursor_component = self.engine.cursors.find(cursor)
        start = self.engine.positions.find(cursor_component.entity)
        equipment = self.engine.equipments.find(cursor_component.entity)
        if equipment.missile and equipment.ammo:
            ...
        elif equipment.ammo:
            ammo_id = equipment.ammo
            info = self.engine.infos.find(ammo_id)
            if info.name == 'stone':
                self.engine.logger.add("Throwing stones")
                # remove stone from inventory
                ammo = equipment.ammo
                equipment.ammo = None
                path = pathfind(self.engine, start, end, pathfinder=bresenhams)
                # add a position component to thrown item
                position = Position(
                    *path[-1], 
                    self.engine.world.id, 
                    movement_type=Position.MovementType.NONE,
                    blocks_movement=None
                )
                self.engine.positions.add(ammo, position)
                # check if there is a unit in the path of the throw item
                # if there is one then calculate damage.
                ...
                # add ranged hit effect to effect list
                effect = RangeHitEffect(cursor, '*', '0', path)
                self.engine.effects.add(cursor_component.entity, effect)
        return True

    def check_tile_info(self, position):
        describeables = list()
        for p, i in join_drop_key(self.engine.positions, self.engine.infos):
            if (position.x == p.x and 
                position.y == p.y and 
                i.name is not 'floor'
            ):
                describeables.append(i.name)
        self.engine.logger.add(', '.join(describeables))

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
            self.engine.effects.add(entity, MeleeHitEffect(other, '*', 0))
        self.engine.logger.add(''.join(strings))
        return True

    def collide(self, entity, collision):
        if __debug__:
            self.engine.logger.add(f"{entity}")
        # oob or environment collision. No logged message. Exit early
        if collision.entity == -1:
            return False
        other = collision.entity
        is_player = entity == self.engine.player
        collidee = self.engine.infos.find(other)
        health = self.engine.healths.find(eid=collision.entity)
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
        if __debug__:
            self.engine.logger.add(f"player: {self.engine.player}")
            self.engine.logger.add(f"cursor: {self.engine.cursor}")
            self.engine.logger.add(f"{entity} {movement}")

        # if entity has no position component return early
        position = self.engine.positions.find(entity)
        if not position or not movement:
            return False

        # save temp positions for collision checking
        x, y = position.x + movement.x, position.y + movement.y

        # check map collisions
        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
            return self.collide(entity, Collision(-1))

        # check unit collisions for specific movment types
        if position.movement_type == Position.MovementType.GROUND:
            # check unit collisions
            for entity_id, entity_position in self.engine.positions:
                if (entity_position.x == x and 
                    entity_position.y == y and 
                    entity_position.map_id == self.engine.world.id and 
                    entity_id != entity and 
                    entity_position.blocks_movement is True
                ):
                    return self.collide(entity, Collision(entity_id))

        if position.movement_type == Position.MovementType.VISIBLE:
            for entity_position, visible in join_drop_key(
                self.engine.positions, 
                self.engine.visibilities
            ):
                if (entity_position.x == x and
                    entity_position.y == y and
                    entity_position.map_id == self.engine.world.id and
                    visible.level < 2
                ):
                    return False

        # no collisions. move to the new position
        position.x += movement.x
        position.y += movement.y

        # check 
        if entity == self.engine.player:
            self.check_for_floor_items(position)
        elif entity == self.engine.cursor:
            self.check_tile_info(position)
            return False
        return True

    def go_up(self, entity):
        """Check if entity position is on stairs. If true go up"""
        went_up = False
        position = self.engine.positions.find(entity)
        tilemap = self.engine.tilemaps.find(position.map_id)
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
            movement_type=position.movement_type,
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
            movement_type=position.movement_type,
            blocks_movement=position.blocks_movement
        )
        self.engine.positions.remove(self.engine.player)
        self.engine.positions.add(self.engine.player, position)
        return True

    def able_to_target(self, entity: int) -> bool:
        eq = self.engine.equipments.find(entity)
        # most likely will not happen but handle anyways
        if not eq:
            self.engine.logger.add("You do not have any equipment on.")
        elif eq and not eq.missile:
            if eq.ammo:
                ammo = self.engine.infos.find(eq.ammo)
                if ammo.name == 'stone':
                    return True
            self.engine.logger.add("Cannot target without a missile weapon.")
        elif eq and not eq.ammo:
            self.engine.logger.add("Cannot target without any missile ammo.")
        else:
            return True
        return False

    def process(self, entity: int, command: str) -> bool:
        """
        Eventually would like this functions to be called somewhat like this:
            >>> self.actions[self.engine.mode][command](entity, command)
            or
            >>> self.actions[self.engine.mode][command](entity)
        """
        if __debug__:
            Logger.instance.add(f'command: {command}')
        if self.engine.mode == GameMode.NORMAL:
            print(f'Normal mode: command - {command}')
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
            # currenty disabled -- to reenable add the char to the allowed keypresses
            elif command == 'l':
                self.engine.change_mode(GameMode.LOOKING)
                return False
            elif command == 't':
                if self.able_to_target(entity):
                    self.engine.change_mode(GameMode.MISSILE)
                return False
            elif command == 'tilde':
                self.engine.change_mode(GameMode.DEBUG)
                return False
        elif self.engine.mode == GameMode.LOOKING:
            if command in movement_keypresses:
                self.engine.logger.add(f"Moving cursor {command}")
                return self.move(entity, Movement.keypress_to_direction(command))
                # return False
            elif command == 'escape' or command == 'l':
                self.engine.change_mode(GameMode.NORMAL)
                return False
        elif self.engine.mode == GameMode.MISSILE:
            if command in movement_keypresses:
                self.engine.logger.add(f"Moving cursor {command}")
                return self.move(entity, Movement.keypress_to_direction(command))
                # return False
            elif command == 'escape' or command == 't':
                self.engine.change_mode(GameMode.NORMAL)
                return False
            elif command == 'enter':
                t = self.missile(entity)
                self.engine.mode = GameMode.NORMAL
                self.engine.logger.add(t)
                return t
        elif self.engine.mode == GameMode.DEBUG:
            if command in movement_keypresses:
                self.engine.logger.add(f"Moving cursor {command}")
                return self.move(entity, Movement.keypress_to_direction(command))
            elif command == 'escape' or command == 'tilde':
                self.engine.change_mode(GameMode.NORMAL)
                return False
        return False
