# menu_screen.py

import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast

from .screen import Screen


class MenuScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = 0
        self.options = ('back', 'main menu', 'quit')
        self.valid_keypresses.update({'escape', 'enter', 'down', 'up'})

    def render(self):
        x = self.engine.width // 2
        y = self.engine.height // 2
        
        option_y_offset = - 1
        option_x_offset = - (max(map(len, self.options)) // 2)
        current_x_offset = -2
 
        self.terminal.erase()
        border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
        self.terminal.addstr(0, 1, '[main_menu]')
        for i, option in enumerate(self.options):
            current_option = i == self.index
            current_index_offset = 0
            if current_option:
                current_index_offset = current_x_offset
            self.terminal.addstr(
                y + option_y_offset + i,
                x + option_x_offset + current_index_offset,
                f"{'> ' if current_option else ''}{option}"
            )
        self.terminal.refresh()

    def handle_input(self):
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'escape' or (key == 'enter' and option == 'back'):
            self.engine.change_screen('gamescreen')
        if key == 'enter' and option == 'main menu':
            self.engine.change_screen('mainscreen')
        elif key == 'enter' and option == 'quit':
            self.engine.running = False
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up':
            self.index = (self.index - 1) % len(self.options)
