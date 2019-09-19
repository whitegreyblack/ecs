# death_screen.py

import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast

from .screen import Screen


class DeathScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.valid_keypresses.update(keyboard.values())

    def render(self):
        x = self.engine.width // 2
        y = self.engine.height // 2
        string = "you died"

        self.terminal.erase()
        border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
        self.terminal.addstr(0, 1, '[death screen]')
        self.terminal.addstr(y, x-len(string)//2, string)
        self.terminal.refresh()
    
    def handle_input(self):
        self.engine.running = False
        # self.engine.change_screen('mainmenu')
