# grave_system

"""Graveyard system class"""

import time

from source.common import join
from source.ecs.components import Information, Item, Render, Decay
from source.ecs.systems.system import System

alive = lambda message: message.lifetime > 0

class GraveSystem(System):

    def delete(self, entity):
        for system in self.engine.systems:
            system.remove(entity)
        self.engine.entities.remove(entity)

    def color_environment(self, entity):
        position = self.engine.positions.find(entity)
        tiles = join(
            self.engine.tiles,
            self.engine.positions, 
            self.engine.renders,
            self.engine.infos
        )
        for eid, (_, tile, render, info) in tiles:
            if position.x == tile.x and position.y == tile.y:
                if render.char == '.':
                    render.char = '*'
                info.name = 'bloodied floor'

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
        self.engine.decays.add(body, Decay())

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

    def process(self, entity):
        # remove old messages
        # messages = self.engine.logger.messages
        # self.engine.logger.messages = list(filter(alive, messages))
        if entity == self.engine.player:
            self.engine.player = None
            return
        if not self.engine.items.find(entity):
            self.drop_inventory(entity)
            self.drop_body(entity)
            self.color_environment(entity)
        self.delete(entity)
