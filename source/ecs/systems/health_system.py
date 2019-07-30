# health_system.py

"""Processes healing every turn"""

from .system import System


class HealSystem(System):
    def process(self):
        for eid, health in self.engine.healths:
            health.heal_curr += health.heal_tick
            if health.heal_curr >= health.heal_full:
                # still processes tick but if full then no healing occurs
                health.heal_curr -= health.heal_full
                if health.cur_hp < health.max_hp:
                    health.cur_hp += 1
