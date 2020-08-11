# menu_screen.py

import time

from source.border import border
from source.keyboard import blt_keyboard as keyboard
from source.keyboard import movement_keypresses
from source.screens.confirm_menu_screen import ConfirmMenuScreen
from source.screens.screen import MenuScreen


class GameMenuScreen(MenuScreen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.title = 'game menu'
        self.options = ('back', 'main menu', 'quit')
        self.valid_keypresses.update({
            'escape',
            'enter',
            'close',
            'down',
            'up',
            'mouse-left',
            'mouse-move'
        })

    def handle_input(self):
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'close' or (key == 'enter' and option == 'quit'):
            self.engine.add_screen(ConfirmMenuScreen)
        elif key == 'escape' or (key == 'enter' and option == 'back'):
            self.engine.remove_screen()
        elif key == 'enter' and option == 'main menu':
            self.engine.remove_screen(2)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up':
            self.index = (self.index - 1) % len(self.options)
        elif key == 'mouse-left':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option == 'quit':
                self.engine.add_screen(ConfirmMenuScreen)
            elif option == 'back':
                self.engine.remove_screen()
            elif option == 'main menu':
                self.engine.remove_screen(2)
        elif key == 'mouse-move':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option:
                self.index = self.options.index(option)
