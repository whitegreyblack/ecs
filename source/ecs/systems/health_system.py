# health_system.py

"""Processes healing every turn"""

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
