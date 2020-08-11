# spell_screen.py

"""
Displays magic spell list
"""

import random
import time
from collections import defaultdict
from textwrap import wrap

from source.common import GameMode, direction_to_keypress, join, scroll
from source.ecs.components import Spell
from source.logger import Logger

from .screen import Screen


class SpellScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.title: str = "spell book"
        self.index = -1
        self.last_spell_id = -1
        # add the keypress to return back to game screen
        self.valid_keypresses.update({ 'tilde' })

    def render_spells(self):
        spellbook = self.engine.spellbooks.find(self.engine.player)
        if not spellbook:
            string = 'no spells learned'
            self.terminal.addstr(
                self.engine.height // 2,
                self.engine.width // 2 - len(string) // 2,
                string
            )
            return
        
        current_row = 2
        # spell will be an entity id located in the spells manager
        for i, spell in enumerate(spellbook.spells):
            info = self.engine.infos.shared[Spell.identify[spell]]
            # current row letter
            self.terminal.addstr(i + current_row, 3, f"{chr(i + 97)}.")
            # name of spell
            self.terminal.addstr(i + current_row, 6, info.name)
            current_row  += 1

        # based on the last value of i, new keypresses will be added
        self.set_valid_keypresses(
            { chr(x+97) for x in range(i+1) }.union({ 'enter' })
        )

    def render(self):
        self.terminal.erase()
        self.add_border()
        self.render_spells()
        self.terminal.refresh()

    def select_magic(self, index):
        mana = self.engine.manas.find(self.engine.player)
        spellbook = self.engine.spellbooks.find(self.engine.player)
        spell_id = spellbook.spells[index]
        spell_name = Spell.identify[spell_id] # spell name
        spell = self.engine.spells.shared[spell_name]
        if mana.cur_mp < spell.mana_cost:
            self.engine.logger.add(f"You don't have enough mana to cast {spell_name}")
            return False
        cursor = self.engine.cursors.find(self.engine.cursor)
        cursor.using = spellbook.spells[index]
        return True

    def set_valid_keypresses(self, keys):
        self.valid_keypresses = { 'escape', 'tilde' }.union(keys)

    def handle_input(self):
        key = self.engine.keypress
        if key != 'escape' and key != 'tilde':
            selected = self.select_magic(ord(key) - 97)
            if not selected:
                return
            self.engine.change_mode(GameMode.MAGIC)
        self.engine.change_screen('gamescreen')
