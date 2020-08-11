# configrm_screen.py

import time

from source.border import border
from source.common import colorize
from source.keyboard import blt_keyboard as keyboard
from source.keyboard import movement_keypresses
from source.screens.screen import MenuScreen


class ConfirmMenuScreen(MenuScreen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.options = ('yes', 'no')
        self.valid_keypresses.update({
            'close',
            'escape',
            'enter',
            'close',
            'left',
            'right',
            'mouse-move',
            'mouse-left',
        })
        self.text = "Do you really want to quit?"
        self.render_calls.append(self.add_text)

    def add_text(self):
        x = self.engine.width // 2 - len(self.text) // 2
        y = self.engine.height // 2 - 1
        self.terminal.printf(x, y, self.text)

    def add_options(self):
        x = self.engine.width // (len(self.options) + 1)
        y = self.engine.height // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_x_offset = x
        option_y_offset = 1

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(i)
            option_x = x + (option_x_offset * i)
            option_y = y + option_y_offset
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            self.terminal.printf(option_x, option_y, string)
            for i in range(-1, highlight_len + 2):
                for j in range(-1, 2):
                    self.mapper[(option_x + i, option_y + j)] = option

    def handle_input(self):
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'escape' or (key == 'enter' and option == 'yes'):
            self.engine.running = False
        if key == 'enter' and option == 'no':
            self.engine.remove_screen()
        elif key == 'right':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'left':
            self.index = (self.index - 1) % len(self.options)
        elif key == 'mouse-left':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option == 'yes':
                self.engine.running = False
            elif option == 'no':
                self.engine.remove_screen()
        elif key == 'mouse-move':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option:
                self.index = self.options.index(option)
