# inventoryscreen.py

"""Inventory screen class that renders and processes inputs for the inventory menu"""

import curses
import random
import time

from source.astar import pathfind
from source.color import colors
from source.common import border, direction_to_keypress, eight_square, join, scroll
from source.ecs.components import Movement
from source.keyboard import valid_keypresses
from source.raycast import cast_light

from .screen import Screen


class InventoryMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = -1
        self.size = 0
        self.valid_keypresses.update({'escape', 'enter', 'down', 'up', 'i'})
        self.current_item_id = None

    @property
    def empty(self):
        return self.size == 0

    def render_items(self):
        # will always find it since one is created on startup
        inventory = self.engine.inventories.find(self.engine.player)
        items = []
        self.item_ids = []
        for eid, (_, info) in join(self.engine.items, self.engine.infos):
            if eid in inventory.items:
                items.append(info)
                self.item_ids.append(eid)
        # helpstring = f"[e]at  [E]quip  [D]rop [l]ook [U]se"
        # self.terminal.addstr(
        #     self.engine.height - 2,
        #     self.engine.width // 2 - len(helpstring) // 2,
        #     helpstring
        # )

        if not items:
            string = 'no items in inventory'
            self.terminal.addstr(
                self.engine.height // 2, 
                self.engine.width // 2 - len(string) // 2, 
                string
            )
            return
        # update inventory size for cursor calculations
        self.size = len(items)
        for i, info in enumerate(items):
            cursor = '>' if i == self.index else ' '
            char = chr(97+i) + '.'
            self.terminal.addstr(1+i, 3, f"{cursor} {char} {info.name}")

    def render_item(self):
        w, h = self.engine.width, self.engine.height
        border(self.terminal, w // 4, h // 4, w // 2, h // 2)
        self.terminal.addstr(h // 4, w // 4 + 1, '[info]')

        info = self.engine.infos.find(eid=self.current_item_id)
        render = self.engine.renders.find(eid=self.current_item_id)
        self.terminal.addstr(h // 4 + 1, w // 4 + 3, f"{render.char} {info.name}")

    def render(self):
        if not self.current_item_id:
            self.terminal.erase()
            border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
            self.terminal.addstr(0, 1, '[inventory]')
            self.render_items()
        else:
            self.render_item()
        self.terminal.refresh()
    
    def handle_input(self):
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
                self.current_item_id = self.item_ids[self.index]
