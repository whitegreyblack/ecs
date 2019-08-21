# grave_system

"""Graveyard system class"""

import random
import time

from source.common import join
from source.ecs.components import Decay, Information, Item, Render, Position
from source.ecs.systems.system import System


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
        environment = 'bloodied floor'
        for entity, (_, tile, render, info) in tiles:
            if position.x == tile.x and position.y == tile.y:
                render = random.choice(self.engine.renders.shared[environment])
                self.engine.renders.add(entity, render)
                info = self.engine.infos.shared[environment]
                self.engine.infos.add(entity, info)

    def drop_body(self, entity):
        # get entity info
        position = self.engine.positions.find(entity)
        info = self.engine.infos.find(entity)
        render = self.engine.renders.find(entity)

        # build entity corpse
        name = f"{info.name} corpse"
        body = self.engine.entities.create()
        self.engine.items.add(body, Item('food'))
        for r in self.engine.renders.shared[name]:
            if r.color == render.color:
                break
        self.engine.renders.add(body, r)
        i = self.engine.infos.shared[name]
        self.engine.infos.add(body, i)
        self.engine.positions.add(
            body, 
            position.copy(
                movement_type=Position.MovementType.NONE,
                blocks_movement=False
            )
        )
        self.engine.decays.add(body, Decay(1000))

    def drop_inventory(self, entity):
        position = self.engine.positions.find(entity)
        inventory = self.engine.inventories.find(entity)
        if not inventory:
            return
        while inventory.items:
            item = inventory.items.pop()
            item_position = position.copy(
                movement_type=Position.MovementType.NONE,
                blocks_movement=False
            )
            print(item_position)
            self.engine.positions.add(item, item_position)

    def remove_from_inventory(self, entity):
        inventory = None
        for eid, inventory in self.engine.inventories:
            if entity.id in inventory.items:
                break
        inventory.items.remove(entity.id)

    def process(self, entity):
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
