# start_screen.py

import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast

from .screen import Screen


class StartScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = 0
        self.cursor_x = 0
        self.cursor_y = 0
        self.options = ('new game', 'quit')
        self.valid_keypresses.update({'escape', 'enter', 'up', 'down'})

    def render(self):
        x = self.engine.width // 2 - (max(map(len, self.options)) // 2)
        y = self.engine.height // 2 - 1
        
        current_x_offset = -2
 
        self.terminal.erase()
        border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
        self.terminal.addstr(0, 1, '[main_menu]')
        for i, option in enumerate(self.options):
            current_option = i == self.index
            current_index_offset = 0
            if current_option:
                current_index_offset = current_x_offset
            self.terminal.addstr(y + i, 
                                 x + current_index_offset,
                                 f"{'> ' if current_option else ''}{option}")
        self.terminal.refresh()

    def handle_input(self):
        # keep_open, exit_prog
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'escape' or (key == 'enter' and option == 'quit'):
            self.engine.running = False
        elif key == 'enter' and option == 'new game':
            self.engine.change_screen('gamescreen')
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up': # up
            self.index = (self.index - 1) % len(self.options)
