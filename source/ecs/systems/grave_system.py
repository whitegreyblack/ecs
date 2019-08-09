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
                entity = self.engine.entities.find(eid=eid)
                if render.char == '.':
                    if '*' not in self.engine.renders.shared:
                        self.engine.renders.shared['*'] = Render('*')
                    self.engine.renders.add(
                        entity,
                        self.engine.renders.shared['*']
                    )
                if 'bloodied floor' not in self.engine.infos.shared:
                    i = Information('bloodied floor')
                    self.engine.infos.shared['bloodied floor'] = i
                self.engine.infos.add(
                    entity,
                    self.engine.infos.shared['bloodied floor']
                )

    def drop_body(self, entity):
        position = self.engine.positions.find(entity)
        info = self.engine.infos.find(entity)
        body = self.engine.entities.create()
        self.engine.items.add(body, Item('food'))
        self.engine.renders.add(body, Render('%'))
        self.engine.infos.add(body, Information(f"{info.name} corpse"))
        self.engine.positions.add(body, position.copy(
            moveable=False,
            blocks_movement=False
        ))
        self.engine.decays.add(body, Decay(10))

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

    def remove_from_inventory(self, entity):
        inventory = None
        for eid, inventory in self.engine.inventories:
            if entity.id in inventory.items:
                break
        inventory.items.remove(entity.id)

    def process(self, entity):
        # remove old messages
        # messages = self.engine.logger.messages
        # self.engine.logger.messages = list(filter(alive, messages))
        if entity == self.engine.player:
            self.engine.player = None
            return
        # if the entity is a unit
        if not self.engine.items.find(entity):
            self.drop_inventory(entity)
            self.drop_body(entity)
            self.color_environment(entity)
        # if the entity exists inside a container
        elif not self.engine.positions.find(entity):
            print('entity exists in container')
            self.remove_from_inventory(entity)
        self.delete(entity)
