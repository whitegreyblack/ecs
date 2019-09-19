# screens.py

"""Menus and Game Screen classes"""


import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast


class Screen:
    def __init__(self, engine, terminal):
        self.engine = engine
        self.terminal = terminal
        self.valid_keypresses = {'escape'}

    def process(self):
        if not self.engine.requires_input:
            self.handle_input()
            self.engine.requires_input = True
            return True
        return False

    def border(self):
        border(self.terminal, 0, 0, self.engine.width - 1, self.engine.height - 1)
        self.terminal.addstr(0, 1, f"[{type(self).menu_title}]")
