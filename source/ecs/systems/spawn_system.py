# spawn_system.py

"""Spawn system controls unit and item generation"""

import random

from source.common import join, join_drop_key
from source.ecs import (
    AI, Armor, Health, Information, Input, Inventory, Item, Position, Render)

from .system import System


class SpawnSystem(System):
    def __init__(self, engine, logger=None):
        super().__init__(engine, logger)
        # TODO: move to a new spawn Component attached to the tilemap
        self.respawn_rate = 50
        self.current_tick = self.respawn_rate

    def find_valid_spaces(self) -> list:
        return [
            (position.x, position.y)
                for _, position, visible in join_drop_key(
                    self.engine.tiles, 
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visible.level < 2 and not position.blocks_movement
        ]

    def find_empty_spaces(self):
        return [
            (position.x, position.y)
                for _, position in join_drop_key(
                    self.engine.tiles, 
                    self.engine.positions
                )
                if not position.blocks_movement
        ]

    def find_unlit_spaces(self):
        g = join_drop_key(self.engine.tiles, self.engine.positions)
        return {
            (position.x, position.y)
                for (_, position, visible) in join_drop_key(
                    self.engine.tiles,
                    self.engine.positions,
                    self.engine.visibilities
                )
                if visible.level > 1
                    and not position.blocks_movement
        }

    def spawn_unit(self, space):
        # create unit entity
        computer = self.engine.entities.create()
        self.engine.inputs.add(computer, Input())
        self.engine.positions.add(
            computer,
            Position(*space, map_id=self.engine.world.id)
        )
        self.engine.ais.add(computer, AI())
        render = random.choice(self.engine.renders.shared['goblin'])
        self.engine.renders.add(computer, render)
        info = self.engine.infos.shared['goblin']
        self.engine.infos.add(computer, info)
        self.engine.healths.add(computer, Health(2, 2))
        
        # add items to inventory
        item = self.engine.entities.create()
        self.engine.items.add(item, Item('weapon'))
        r = random.choice(self.engine.renders.shared['spear'])
        self.engine.renders.add(item, r)
        self.engine.infos.add(item, self.engine.infos.shared['spear'])
        self.engine.inventories.add(computer, Inventory(items=[item]))

        # self.engine.logger.add(f"Created a {info.name} from spawn_system!")

    def spawn_item(self):
        ...

    def process(self):
        units = [
            (eid, health, position)
                for eid, (health, position) in join(
                    self.engine.healths,
                    self.engine.positions
                )
                if position.map_id == self.engine.world.id
                    and eid != self.engine.player
        ]
        if len(units) < 3:
            if self.current_tick < 0:
                # self.engine.logger.add('resetting current tick')
                self.current_tick = self.respawn_rate
            # self.engine.logger.add(self.current_tick)
            self.current_tick -= 1
            if self.current_tick == 0:
                spaces = self.find_valid_spaces()
                # probably wouldn't happen but if it does then exit early
                if not spaces:
                    return
                random.shuffle(spaces)
                space = spaces.pop()
                self.spawn_unit(space)
