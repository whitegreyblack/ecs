# equipment_screen.py

"""Equipment screen"""

import curses
import random
import time
from collections import defaultdict
from textwrap import wrap

from source.common import (border, direction_to_keypress, eight_square, join,
                           scroll)
from source.messenger import Logger

from .screen import Screen


class EquipmentMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.logger = Logger()
        self.index = -1
        self.last_item_id = -1
        self.valid_keypresses.update({ 'escape', 'i' })

    def render_equipment(self):
        descriptions = self.engine.router.route(
            'equipment',
            'get_all',
            self.engine.player
        )
        for i, (eq, info, render) in enumerate(descriptions):
            if info and render:
                desc = f"{chr(i+97)}. {eq:9}: {render.char} {info.name}"
            else:
                desc = f"{chr(i+97)}. {eq:9}:    ---"
            self.terminal.addstr(i+2, 2, desc)
        self.set_valid_keypresses({ chr(x+97) for x in range(i+1) })
    
    def render_item(self):
        # get item id
        self.last_item_id = self.engine.router.route(
            'equipment', 
            'get_item_id', 
            self.engine.player, 
            self.index
        )
        
        # handles displaying alternate choices if slot is empty when selected
        if not self.last_item_id:
            items = list(self.engine.router.route(
                'inventory', 
                'get_all_by_eq_type', 
                self.engine.player,
                self.index
            ))
            if not items:
                self.index = -1
                self.logger.add("No items to equip to this slot.")
                return

            w, h = self.engine.width, self.engine.height
            border(self.terminal, w // 4, h // 4, w // 2, h // 2)
            self.terminal.addstr(h // 4, w // 4 + 1, '[info]')

            # hack to clear print area
            blank_line = ' ' * (w // 2 - 1)
            for y in range(h // 2 - 1):
                self.terminal.addstr(h // 4 + y + 1, w // 4 + 1, blank_line)

            self.terminal.addstr(h // 4 + 1, w // 4 + 1, 'items to equip:')
            keypresses = set()
            for i, (item, render, info) in enumerate(items):
                keypresses.add(chr(i+97))
                self.terminal.addstr(
                    h // 4 + 2 + i, 
                    w // 4 + 3, 
                    f"{chr(i+97)}. {info.name}"
                )
            self.set_valid_keypresses(keypresses)
            return
            
        # get item component properties
        item, render, info = self.engine.router.route(
            'equipment',
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

        # append actions
        actions = ('e', 'unequip')
        self.terminal.addstr(
            h // 4 + 4 + 2, 
            w // 4 + 3, 
            f'{actions[0]}: {actions[1]}'
        )
        self.set_valid_keypresses(set(actions[1]))

    def render_logs(self):
        logs = self.logger.messages
        if len(logs) >= 2:
            l = max(0, len(logs)) - 3
            logs = logs[l:]
        for y, log in enumerate(logs):
            log_y = self.engine.height - 3 + y
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
            self.terminal.addstr(0, 1, '[equipment]')
            self.render_equipment()
        else:
            self.render_item()
        self.render_logs()
        self.terminal.refresh()

    def set_valid_keypresses(self, keys):
        self.valid_keypresses = { 'escape', 'i' }.union(keys)

    def handle_input(self):
        key = self.engine.keypress
        if key == 'escape':
            if self.index < 0:
                self.engine.change_screen('gamescreen')
            else:
                self.index = -1
        elif key == 'i' and self.index == -1:
            self.engine.change_screen('inventorymenu')
        elif self.index > -1:
            if self.last_item_id:
                done = self.engine.router.route(
                    'equipment', 
                    'handle_item_action', 
                    key, 
                    self.engine.player, 
                    self.last_item_id
                )
                # reset the index
                if done:
                    self.index = -1
            else:
                done = self.engine.router.route(
                    'equipment',
                    'handle_item_selection',
                    self.index,
                    self.engine.player,
                    key
                )
                if done:
                    self.index = -1
        else:
            self.index = ord(key) - 97
