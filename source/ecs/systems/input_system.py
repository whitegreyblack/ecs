# input_system.py

"""Input system"""

import curses
import random
import time
from dataclasses import dataclass, field

from source.common import eight_square, join, nine_square
from source.ecs.components import (Collision, Information, Item, Movement,
                                   Position, Render)
from source.ecs.systems.system import System
from source.pathfind import pathfind


class InputSystem(System):
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
            return 'center'
        return keypress_from_direction(x, y)

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
        for entity, (item, item_position, info) in g:
            if (position.x, position.y) == (item_position.x, item_position.y):
                items_picked_up.append(entity)
                descriptions.append(info.name)
        if not items_picked_up:
            return False
        for entity in items_picked_up:
            # remove from map
            self.engine.visibilities.remove(entity)
            self.engine.renders.remove(entity)
            self.engine.positions.remove(entity)
            # add to inventory
            inventory.items.append(entity.id)
        self.engine.logger.add(f"Picked up {', '.join(descriptions)}")
        return True

    def process(self, valid_keypresses=None) -> str:
        if not valid_keypresses:
            valid_keypresses = self.engine.screen.valid_keypresses
        keypress = None
        while keypress is None:
            char = self.engine.get_input()
            keypress = self.engine.keypress_from_input(char)
            if keypress in valid_keypresses:
                self.engine.requires_input = False
            else:
                keypress = None
            if not keypress:
                time.sleep(.001)
        self.engine.keypress = keypress
