# inventory_system.py

"""Handles internal inventory"""

from collections import namedtuple

from source.common import join
from source.ecs.components import Inventory

from .system import System

inventory_item = namedtuple("Item", "category char name color description")

class InventorySystem(System):
    def get_unit_inventory(self, eid):
        inventory = self.engine.inventories.find(eid=eid)

        buckets = {
            category: []
                for category in inventory.categories
        }

        # iterate all items and sort
        for item_id in inventory.items:
            item = self.engine.items.find(eid=item_id)
            render = self.engine.renders.find(eid=item_id)
            info = self.engine.infos.find(eid=item_id)
            buckets[item.category].append((
                render.char,
                render.color, 
                info.name,
                info.description
            ))
        
        # print items in each bucket by category order
        for category in inventory.categories:
            for char, color, name, description in buckets[category]:
                yield inventory_item(category, char, name, color, description)
