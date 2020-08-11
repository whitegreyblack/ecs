# armor controller

"""Armor calculations"""

from source.common import join
from source.ecs.components import Armor

from .controller import Controller


class ArmorController(Controller):
    __slots__ = ['engine']
    router = 'armor'

    def get_total_armor_value(self, entity):
        armors = list(self.engine.router.route(
            'equipment',
            'get_armor_item_ids',
            entity
        ))
    
        defense = sum(armor.defense for armor in armors if armor is not None)
        print(defense)
        return defense
