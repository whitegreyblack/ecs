# screens.py

"""Menus and Game Screen classes"""


import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast


class Panel:
    __slots__ = ['terminal', 'x', 'y', 'width', 'height', 'title']
    def __init__(self, terminal, x, y, width, height, title):
        """Just a rectangle"""
        self.terminal = terminal
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

    def add_string(self, x, y, string, color=0):
        if not isinstance(string, str):
            string = str(string)
        if color > 0:
            color = curses.color_pair(color)
        self.terminal.addstr(y, x, string, color)

    def render(self):
        border(self.terminal, self.x, self.y, self.width, self.height)
        self.terminal.addstr(self.x, self.y + 1, f"[{self.title}]")

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
