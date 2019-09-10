# health_system.py

"""Processes healing every turn"""

from source.ecs.components import HealEffect

from .system import System


class HealSystem(System):
    def process(self):
        for eid, health in self.engine.healths:
            health.curr_amount += health.tick_amount
            if health.curr_amount >= health.full_amount:
                # still processes tick but if full then no healing occurs
                health.curr_amount -= health.full_amount
                if health.cur_hp < health.max_hp:
                    health.cur_hp += 1

    def eat(self, entity, item_id) -> int:
        # get entity health component
        health = self.engine.healths.find(entity)
        # get item info and check for healing effect if eaten
        item = self.engine.items.find(item_id)
        if item.effect and isinstance(item.effect, HealEffect):
            # if healing was done, even if it was increased by 0
            # then return true
            info = self.engine.infos.find(item_id)
            old_hp = health.cur_hp
            temp_hp = health.cur_hp + item.effect.heal_amount
            health.cur_hp = min(temp_hp, health.max_hp)
            if old_hp == health.cur_hp:
                return 1
            return 2
        return 0
