# equipment_screen.py

"""Equipment screen"""

import curses
import random
import time
from collections import defaultdict
from textwrap import wrap

from source.common import (border, direction_to_keypress, eight_square, join,
                           scroll)
from source.ecs.components import Movement, Equipment
# from source.keyboard import valid_keypresses
from source.messenger import Logger

from .screen import Screen


class EquipmentMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.valid_keypresses.update({'escape', 'down', 'up'})

    def render(self):
        self.terminal.erase()
        border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
        self.terminal.addstr(0, 1, '[equipment]')
        e = self.engine.equipments.find(self.engine.player)
        keys = set()
        for y, eq_type in enumerate(Equipment.equipment):
            eq = getattr(e, eq_type)
            if eq:
                i = self.engine.infos.find(eq).name
            else:
                i = ""
            key_to_add = chr(y + 97)
            keys.add(key_to_add)
            s = f"{key_to_add}. {eq_type.capitalize():8}:  {i}"
            self.terminal.addstr(y+2, 2, s)
        self.valid_keypresses.update(keys)
        self.terminal.refresh()

    def handle_input(self):
        if self.engine.keypress == 'escape':
            self.engine.change_screen('gamescreen')
        elif self.engine.keypress in self.valid_keypresses:
            self.engine.logger.add(f"pressed {self.engine.keypress}")
