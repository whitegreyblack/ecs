# equipment_controller.py

"""Handles internal equipment functions"""

from source.common import join
from source.ecs.components import Equipment, Position

from .controller import Controller


class EquipmentController(Controller):
    __slots__ = ['engine']
    router_name = 'equipment'
    
    def get_all(self, entity):
        e = self.engine.equipments.find(entity)
        for eq_type in Equipment.equipment:
            item = getattr(e, eq_type)
            if item:
                info = self.engine.infos.find(item)
                render = self.engine.renders.find(item)
            else:
                info = None
                render = None
            yield eq_type.replace('_', ' '), info, render

    def get_armor_item_ids(self, entity):
        eq = self.engine.equipments.find(entity)
        if not eq:
            return
        for eq_type in ('head', 'body', 'feet'):
            item = getattr(eq, eq_type)
            yield item

    def get_item_id(self, entity, index):
        e = self.engine.equipments.find(entity)
        return getattr(e, Equipment.equipment[index])

    def get_item(self, item_id):
        item = self.engine.items.find(item_id)
        render = self.engine.renders.find(item_id)
        info = self.engine.infos.find(item_id)
        return item, render, info

    def drop_item(self, entity, iid):
        unequipped = self.unequip_item(entity, iid)
        if not unequipped:
            return unequipped
        info = self.engine.infos.find(iid)
        position = self.engine.positions.find(entity)
        item_position = position.copy(
            map_id = position.map_id,
            movement_type = Position.MovementType.NONE,
            blocks_movement = False
        )
        self.engine.positions.add(iid, item_position)
        self.engine.logger.add(f"You drop the {info.name} onto the ground.")
        return True

    def send_to_inventory(self, entity, iid):
        unequipped = self.unequip_item(entity, iid)
        if not unequipped:
            return unequipped
        info = self.engine.infos.find(iid)
        self.engine.router.route('inventory', 'add_item', entity, iid)
        self.engine.logger.add(
            f"You remove the {info.name} and place it into your inventory."
        )
        return True

    def equip_item(self, entity, item_id, eq_type):
        eq = self.engine.equipments.find(entity)
        if not getattr(eq, eq_type):
            setattr(eq, eq_type, item_id)
            print(self.engine.infos.find(item_id))
            print(eq_type, item_id)
            return True
        else:
            return False

    def unequip_item(self, entity, iid):
        e = self.engine.equipments.find(entity)
        eq_type = None
        for eq in Equipment.equipment:
            if getattr(e, eq) == iid:
                eq_type = eq
                break
        if not eq_type:
            return False
        setattr(e, eq_type, None)
        return True

    def handle_item_action(self, key, entity, item_id):
        if key == 'd':
            return self.drop_item(entity, item_id)
        elif key == 'e':
            return self.send_to_inventory(entity, item_id)

    def handle_item_selection(self, slot_index, entity, selection):
        eq_type = Equipment.equipment[slot_index]
        item_index = ord(selection) - 97
        item_id = self.engine.router.route(
            'inventory',
            'get_item_id_by_eq_type',
            entity,
            item_index,
            eq_type
        )
        return self.engine.router.route(
            'inventory',
            'equip_item',
            entity,
            item_id,
            eq_type
        )
