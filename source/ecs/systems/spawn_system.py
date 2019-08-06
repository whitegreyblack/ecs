# spawn_system.py

"""Spawn system controls unit and item generation"""

from source.common import join, join_without_key
from source.ecs import (
    AI, Armor, Health, Information, Input, Inventory, Item, Position, Render)

from .system import System


class SpawnSystem(System):
    def __init__(self, engine, logger=None):
        super().__init__(engine, logger)
        self.respawn_rate = 50
        self.current_tick = -1

    def find_valid_spaces(self):
        return {
            (position.x, position.y)
                for _, position, visible in join_without_key(
                    self.engine.tiles, 
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visible.level < 1 and not position.blocks_movement
        }

    def find_empty_spaces(self):
        g = join_without_key(self.engine.tiles, self.engine.positions)
        return {
            (position.x, position.y)
                for _, position in g
                    if not position.blocks_movement
        }

    def find_unlit_spaces(self):
        g = join_without_key(self.engine.tiles, self.engine.positions)
        return {
            (position.x, position.y)
                for (_, position, visible) in join_without_key(
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
        self.engine.renders.add(computer, Render('g', depth=3))
        self.engine.ais.add(computer, AI())
        info = Information("goblin")
        self.engine.infos.add(computer, info)
        self.engine.healths.add(computer, Health(2, 2))
        
        # add items to inventory
        item = self.engine.entities.create()
        self.engine.items.add(item, Item('weapon'))
        self.engine.renders.add(item, Render('/'))
        self.engine.infos.add(item, Information('spear'))
        self.engine.inventories.add(computer, Inventory(items=[item.id]))

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
                    and eid != self.engine.player.id
        ]
        if len(units) < 3:
            if self.current_tick < 0:
                self.current_tick = self.respawn_rate
            self.current_tick -= 1
            if self.current_tick == -1:
                spaces = self.find_valid_spaces()
                # probably wouldn't happen but if it does then exit early
                if not spaces:
                    return
                space = spaces.pop()
                self.spawn_unit(space)
