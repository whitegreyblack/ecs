# inventoryscreen.py

"""
Inventory screen class that renders and processes inputs for the inventory menu
"""

import curses
import random
import time
from collections import defaultdict
from textwrap import wrap

from source.common import (border, direction_to_keypress, eight_square, join,
                           scroll)
from source.messenger import Logger

from .screen import Screen


class InventoryMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.logger = Logger()
        self.page = 0
        self.max_items = 14
        self.index = -1
        self.last_item_id = -1
        self.valid_keypresses.update({ 'escape', 'e' })

    def render_items(self):
        items = list(self.engine.router.route(
            'inventory', 
            'get_all', 
            self.engine.player
        ))

        if not items:
            string = 'no items in inventory'
            self.terminal.addstr(
                self.engine.height // 2, 
                self.engine.width // 2 - len(string) // 2, 
                string
            )
            return

        # update inventory size for cursor calculations
        start = self.page * self.max_items
        chunk = start + self.max_items + 1

        # display items by item list order. Add cursor indicator if available
        current_row = 1
        current_category = None
        for i, (item, render, info) in enumerate(items[start:chunk]):
            if current_category is not item.category:
                current_category = item.category
                self.terminal.addstr(
                    i + current_row, 
                    2, 
                    item.category.capitalize()
                )
                current_row += 1
            self.terminal.addstr(i + current_row, 3, f"{chr(i + 97)}.")
            self.terminal.addch(
                i + current_row,
                6, 
                render.char, 
                curses.color_pair(render.color)
            )
            self.terminal.addstr(i + current_row, 8, info.name)

        self.set_valid_keypresses(
            { chr(x+97) for x in range(i+1) }.union({ 'enter' })
        )

    def render_item(self):
        # get item information
        self.last_item_id = self.engine.router.route(
            'inventory', 
            'get_item_id', 
            self.engine.player, 
            self.index
        )
        item, render, info = self.engine.router.route(
            'inventory',
            'get_item',
            self.last_item_id
        )

        # display single item information box
        w, h = self.engine.width, self.engine.height
        border(self.terminal, w // 4, h // 4, w // 2, h // 2)
        self.terminal.addstr(h // 4, w // 4 + 1, '[info]')

        # hack to clear print area
        blank_line = ' ' * (w // 2 - 1)
        for y in range(h // 2 - 1):
            self.terminal.addstr(h // 4 + y + 1, w // 4 + 1, blank_line)

        # add the character representing item selected
        self.terminal.addch(
            h // 4 + 1, 
            w // 4 + 3, 
            render.char,
            curses.color_pair(render.color)
        ) 
        self.terminal.addstr(h // 4 + 1, w // 4 + 5, info.name)
        self.terminal.addstr(h // 4 + 2, w // 4 + 3, item.category)
        save_y = 0
        if info.description:
            lines = wrap(info.description, w // 2 - 6)
            for y, line in enumerate(lines):
                self.terminal.addstr(h // 4 + 4 + y, w // 4 + 3, line)
            save_y = y
        actions = []
        keys = { 'd' }
        if item.category == 'weapon':
            actions.append('e: equip')
            keys.add('e')
        elif item.category == 'food':
            actions.append('e: eat')
            keys.add('e')
        elif item.category == 'use':
            actions.append('u: use')
            keys.add('u')
        actions.append('d: drop')
        if actions:
            for y, line in enumerate(actions):
                self.terminal.addstr(
                    h // 4 + 4 + save_y + y + 2, 
                    w // 4 + 3, 
                    line
                )
        self.set_valid_keypresses(keys)

    def render_logs(self):
        logs = self.logger.messages
        if len(logs) >= 2:
            l = max(0, len(logs)) - 3
            logs = logs[l:]
        for y, log in enumerate(logs):
            log_y = self.engine.height - 4 + y
            self.terminal.addstr(log_y, 1, str(log))

    def render(self):
        if self.index < 0:
            self.terminal.erase()
            border(
                self.terminal, 
                0, 0, 
                self.engine.width - 1, 
                self.engine.height - 1
            )
            self.terminal.addstr(0, 1, '[inventory]')
            self.render_items()
        else:
            self.render_item()
        self.render_logs()
        self.terminal.refresh()

    def set_valid_keypresses(self, keys):
        self.valid_keypresses = { 'escape', 'e' }.union(keys)

    def handle_keypress(self, key):
        # iid = self.engine.inventory_controller.get_item_id(
        #     self.engine.player,
        #     self.index
        # )
        done = self.engine.router.route(
            'inventory',
            'keypress',
            key,
            self.engine.player,
            self.last_item_id
        )
        # done = self.engine.inventory_controller.keypress(
        #     key,
        #     self.engine.player,
        #     self.last_item_id
        # )
        if not done:
            return
        self.index = -1
    
    def handle_input(self):
        key = self.engine.keypress
        if key == 'escape':
            if self.index < 0:
                self.engine.change_screen('gamescreen')
            else:
                self.index = -1
        elif key == 'e' and self.index == -1:
            self.engine.change_screen('equipmentmenu')
        elif self.index > -1:
            self.handle_keypress(key)
        else:
            self.index = ord(key) - 97
