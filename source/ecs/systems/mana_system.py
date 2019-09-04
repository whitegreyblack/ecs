# mana_system.py

"""Processes mana regen every turn"""

from .system import System


class ManaRegenSystem(System):
    def process(self):
        for eid, mana in self.engine.manas:
            mana.curr_amount += mana.tick_amount
            if mana.curr_amount >= mana.full_amount:
                mana.curr_amount -= mana.full_amount
                if mana.cur_mp < mana.max_mp:
                    mana.cur_mp += 1
