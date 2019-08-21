# missile_screen.py

"""Missle menu"""

import curses
import random
import time
from collections import defaultdict
from textwrap import wrap

from source.common import (border, direction_to_keypress, eight_square, join,
                           scroll)
from source.ecs.components import Movement, Equipment
from source.keyboard import valid_keypresses
from source.messenger import Logger

from .screen import Screen


class MissileMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.map_panel_x = 17
        self.map_panel_y = 1
        self.cursor_x = -1
        self.cursor_y = -1
        self.valid_keypresses.update({'escape', 'down', 'up', 'left', 'right'})

    def setup_cursor_position(self):
        position = self.engine.positions.find(self.engine.player)
        self.cursor_x = position.x
        self.cursor_y = position.y

    def trigger_cursor(self, state):
        curses.curs_set(state)

    def process(self):
        self.trigger_cursor(True)
        ret = super().process()
        self.trigger_cursor(False)
        return ret

    def render(self):
        # draw the cursor
        print(self.cursor_x, self.cursor_y)
        if self.cursor_x == -1 and self.cursor_y == -1:
            print('setting up')
            self.setup_cursor_position()
        self.terminal.addch(
            self.cursor_y + self.map_panel_y,
            self.cursor_x + self.map_panel_x,
            'o'
        )
        self.terminal.refresh()

    def handle_input(self):
        keypress = self.engine.keypress
        self.engine.logger.add(keypress)
        if keypress == 'down':
            self.cursor_y += 1
        elif keypress == 'up':
            self.cursor_y -= 1
        elif keypress == 'escape':
            self.engine.change_screen('gamemenu')
