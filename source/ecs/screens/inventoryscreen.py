# inventoryscreen.py

"""Inventory screen class that renders and processes inputs for the inventory menu"""

import curses
import random
import time
from collections import defaultdict
from textwrap import wrap

from source.astar import pathfind
from source.common import (border, direction_to_keypress, eight_square, join,
                           scroll)
from source.ecs.components import Movement
from source.keyboard import valid_keypresses
from source.raycast import cast_light

from .screen import Screen


class InventoryMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = -1
        self.page = 0
        self.max_items = 14
        self.current_item_id = None
        self.valid_keypresses.update({
            'escape', 
            'enter', 
            'down', 
            'up', 
            'i',
            'less-than',
            'greater-than'
        })

    @property
    def empty(self):
        return self.size == 0

    @property
    def size(self):
        if self.items:
            return len(self.items)
        return 0

    def render_items(self):
        # will always find it since one is created on startup
        self.items = list(self.engine.inventory_system.get_unit_inventory(
            self.engine.player.id
        ))

        # helpstring = f"[e]at  [E]quip  [D]rop [l]ook [U]se"
        # self.terminal.addstr(
        #     self.engine.height - 2,
        #     self.engine.width // 2 - len(helpstring) // 2,
        #     helpstring
        # )

        # exit early if inventory is empty
        if not self.items:
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
        for i, item in enumerate(self.items[start:chunk]):
            if current_category is not item.category:
                current_category = item.category
                self.terminal.addstr(
                    i + current_row, 
                    2, 
                    item.category.capitalize()
                )
                current_row += 1
            cursor = '>' if i == self.index else ' '
            self.terminal.addstr(i + current_row, 3, f"{cursor} ")
            self.terminal.addch(
                i + current_row, 
                5, 
                item.char, 
                curses.color_pair(item.color)
            )
            self.terminal.addstr(i + current_row, 7, item.name)

    def render_item(self):
        # display single item information box
        w, h = self.engine.width, self.engine.height
        border(self.terminal, w // 4, h // 4, w // 2, h // 2)
        self.terminal.addstr(h // 4, w // 4 + 1, '[info]')

        # hack to clear print area
        blank_line = '.' * (w // 2 - 1)
        for y in range(h // 2 - 1):
            self.terminal.addstr(h // 4 + y + 1, w // 4 + 1, blank_line)

        item = self.items[self.index]
        self.terminal.addch(
            h // 4 + 1, 
            w // 4 + 3, 
            item.char,
            curses.color_pair(item.color)
        ) 
        self.terminal.addstr(h // 4 + 1, w // 4 + 5, item.name)
        self.terminal.addstr(h // 4 + 2, w // 4 + 3, item.category)
        if item.description:
            lines = wrap(item.description, w // 2 - 6)
            for y, line in enumerate(lines):
                self.terminal.addstr(h // 4 + 4 + y, w // 4 + 3, line)

    def render(self):
        if not self.current_item_id:
            self.terminal.erase()
            border(
                self.terminal, 
                0, 0, 
                self.engine.width-1, 
                self.engine.height-1
            )
            self.terminal.addstr(0, 1, '[inventory]')
            self.render_items()
        else:
            self.render_item()
        self.terminal.refresh()
    
    def handle_input(self):
        """TODO: disable up/down keypress when single item info box is shown"""
        key = self.engine.keypress
        if key == 'down':
            # if inventory ran for the first time and down was pressed 
            # -- initialize index
            if self.index is None and self.current_item_id is None:
                self.index = 0
            elif not self.empty and self.current_item_id is None:
                self.index = (self.index + 1) % self.size
        elif key == 'up':
            # if inventory ran for the first time and down was pressed 
            # -- initialize index
            if self.index is None and self.current_item_id is None:
                self.index = self.size - 1
            else:
                self.index = (self.index - 1) % self.size
        elif key == 'escape' or key == 'i':
            if self.current_item_id:
                self.current_item_id = None
            else:
                self.index = None
                self.engine.change_screen('gamescreen')
        elif key == 'enter':
            if not self.empty and self.index is not None:
                self.current_item_id = self.items[self.index]
        elif key == 'less-than':
            pass
        elif key == 'greater-than':
            pass
