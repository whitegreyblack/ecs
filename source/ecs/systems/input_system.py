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
from source.keyboard import movement_keypresses, valid_keypresses


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

    # def player_command(self, entity):
    #     moved = False
    #     while True:
    #         exit_prog = False
    #         turn_over = False
    #         char = self.engine.get_input()
    #         if char == -1:
    #             break
    #         keypress = self.engine.keypress_from_input(char)
    #         if keypress == 'q':
    #             self.engine.running = False
    #             break
    #         elif char in movement_keypresses:
    #             turn_over = self.move(entity, Movement.from_input(keypress))
    #             moved = True
    #         elif keypress == 'escape':
    #             self.engine.render_system.main_menu.process()
    #             if not self.engine.running:
    #                 break
    #         elif keypress == 'i':
    #             self.engine.render_system.inventory_menu.process()
    #         elif keypress == 'e':
    #             self.engine.render_system.equipment_menu.process()
    #         elif keypress == 'o':
    #             turn_over = self.open_door(entity)
    #         elif keypress == 'c':
    #             turn_over = self.close_door(entity)
    #         elif keypress == 'comma':
    #             turn_over = self.pick_item(entity)
    #         elif keypress == 'l':
    #             self.engine.render_system.looking_menu.process()
    #         elif keypress == 'less-than':
    #             stairs_exists = self.check_up_stairs(entity)
    #             world_exists = self.engine.world.go_up()
    #             if stairs_exists and world_exists:
    #                 turn_over = self.go_up(entity)
    #             elif not stairs_exists:
    #                 self.engine.logger.add("No stairs to descend into")
    #             else:
    #                 self.engine.logger.add("No world to descend into")
    #         elif keypress == 'greater-than':
    #             self.engine.logger.add("going down")
    #             can_go_down = self.check_down_stairs(entity) 
    #             did_go_down = self.engine.world.go_down()
    #             self.engine.logger.add(f"{can_go_down}, {did_go_down}")
    #             if can_go_down and did_go_down:
    #                 turn_over = self.go_down(entity)
    #         else:
    #             self.engine.logger.add(f"unknown command {char} {chr(char)}")
    #         if turn_over:
    #             break
    #         self.engine.render_system.process()
    #     return moved

    def process(self, keypresses=None) -> str:
        if not keypresses:
            keypresses = self.engine.screen.valid_keypresses
        keypress = None
        while keypress is None:
            char = self.engine.get_input()
            keypress = self.engine.keypress_from_input(char)
            if keypress in keypresses:
                self.engine.requires_input = False
            else:
                keypress = None
            if not keypress:
                time.sleep(.005)
        self.engine.keypress = keypress
