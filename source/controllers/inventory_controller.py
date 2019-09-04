# inventory_controller.py

"""Handles internal inventory functions"""

from source.common import join
from source.ecs.components import Equipment, Inventory, Position

from .controller import Controller


class InventoryController(Controller):
    __slots__ = ['engine']
    router_name = 'inventory'

    def get_inventory_size(self, entity):
        inventory = self.engine.inventories.find(entity)
        if not inventory:
            return 0
        return len(inventory.items)

    def get_item_id(self, entity, index):
        inventory = self.engine.inventories.find(entity)
        return inventory.items[index]

    def get_item_id_by_eq_type(self, entity, index, eq_type):
        inventory = self.engine.inventories.find(entity)
        current_index = 0
        for item_id in inventory.items:
            item = self.engine.items.find(item_id)
            if not item.equipment_types:
                continue
            if eq_type in item.equipment_types:
                if current_index == index:
                    return item_id
                current_index += 1
        return None

    def get_all(self, entity):
        inventory = self.engine.inventories.find(entity)
        if not inventory:
            yield None

        for item_id in inventory.items:
            item = self.engine.items.find(item_id)
            render = self.engine.renders.find(item_id)
            info = self.engine.infos.find(item_id)
            yield item, render, info

    def get_all_by_eq_type(self, entity, eq_type_index):
        inventory = self.engine.inventories.find(entity)
        eq_type = Equipment.equipment[eq_type_index]
        for item_id in inventory.items:
            item = self.engine.items.find(item_id)
            if not item.equipment_types:
                continue
            if eq_type in item.equipment_types:
                render = self.engine.renders.find(item_id)
                info = self.engine.infos.find(item_id)
                yield item, render, info

    def get_page(self, entity, page, count):
        inventory = self.engine.inventories.find(entity)
        if not inventory:
            yield None

        buckets = { category: [] for category in inventory.categories }

        # sort items in inventory
        for item_id in inventory.items:
            item = self.engine.items.find(item_id)
            render = self.engine.renders.find(item_id)
            info = self.engine.infos.find(item_id)
            buckets[item.category].append((item, render, info))
        
        start = page * count
        end = start = count + 1
        index = 0
        early_exit = None
        # get items in each bucket by category order
        for category in inventory.categories:
            for item, render, info in buckets[category]:
                if start <= index < end:
                    yield category, item, render, info
                index += 1
                if index > end:
                    early_exit = True
                    break
            if early_exit:
                break

    def get_item(self, item_id) -> object:
        item = self.engine.items.find(item_id)
        render = self.engine.renders.find(item_id)
        info = self.engine.infos.find(item_id)
        return item, render, info

    def add_item(self, entity, item_id) -> bool:
        """Item is added and then entire inventory is reordered"""
        inventory = self.engine.inventories.find(entity)
        item = self.engine.items.find(item_id)
        items = [(item_id, Inventory.categories.index(item.category))]
        for inv_item_id in inventory.items:
            item = self.engine.items.find(inv_item_id)
            items.append((inv_item_id, Inventory.categories.index(item.category)))
        items.sort(key=lambda x: x[1])
        inventory.items = [i[0] for i in items]

    def remove_item(self, entity, item_id):
        inventory = self.engine.inventories.find(entity)
        inventory.items.remove(item_id)

    def equip_item(self, entity, item_id, eq_type):
        """Keypress action: e"""
        inventory = self.engine.inventories.find(entity)
        inventory.items.remove(item_id)
        return self.engine.router.route(
            'equipment',
            'equip_item',
            entity,
            item_id,
            eq_type
        )

    def drop_item(self, entity, index) -> bool:
        """Keypress action: d"""
        inventory = self.engine.inventories.find(entity)
        item = inventory.items[index]
        inventory.items.remove(item)
        info = self.engine.infos.find(item)
        position = self.engine.positions.find(entity)
        item_position = position.copy(
            map_id = position.map_id,
            movement_type = Position.MovementType.NONE,
            blocks_movement = False
        )
        self.engine.positions.add(item, item_position)
        self.engine.logger.add(f"You drop the {info.name} onto the ground.")

        # map_controller.add_item_to_floor(item_id)
        return True

    def eat_item(self, entity, item_id) -> bool:
        inventory = self.engine.inventories.find(entity)
        info = self.engine.infos.find(item_id)
        self.engine.logger.add(f"You eat the {info.name}. It tastes bitter.")
        # remove item from engine
        self.engine.items.remove(item_id)
        self.engine.renders.remove(item_id)
        self.engine.infos.remove(item_id)
        self.engine.entities.remove(item_id)
        inventory.items.remove(item_id)
        return True

    def keypress(self, key, entity, item_id) -> bool:
        if key == 'd':
            return self.drop_item(entity, item_id)
        elif key == 'e':
            item = self.engine.items.find(item_id)
            if item.category == 'weapon':
                ... # equip | need context on which equipment slot to equip
            elif item.category == 'food':
                return self.eat_item(entity, item_id)
        return False
