# screens.py

"""Menus and Game Screen classes"""


import curses
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast


class Screen:
    def __init__(self, engine, terminal):
        self.engine = engine
        self.terminal = terminal
        self.state = 'closed'
        self.valid_keypresses = set()

    def process(self):
        if not self.engine.requires_input:
            self.handle_input()
            self.engine.requires_input = True
            return True
        return False

    def get_input(self):
        """Needs override from children classes that inherit screen"""
        return False

    @property
    def running(self):
        return self.state == 'open'

class MainMenu(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = 0
        self.options = ('new game', 'quit')
        self.cursor_x = 0
        self.cursor_y = 0
        self.valid_keypresses.update({'escape', 'enter', 'up', 'down'})

    def render(self):
        x = self.engine.width // 2
        y = self.engine.height // 2
        
        option_y_offset = - 1
        option_x_offset = -(max(map(len, self.options)) // 2)
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

class LookingMenu(Screen):
    def __init__(self, engine, terminal, map_x=0, map_y=0):
        super().__init__(engine, terminal)
        self.valid_keypresses.update({'escape'})
        self.map_x = map_x
        self.map_y = map_y
        self.cursor_x = 0
        self.cursor_y = 0

    def setup_cursor_position(self):
        position = self.engine.positions.find(self.engine.player)
        self.cursor_x = position.x
        self.cursor_y = position.y

    def trigger_cursor(self, state):
        curses.curs_set(state)

    def process(self):
        self.setup_cursor_position()
        self.trigger_cursor(True)
        super().process()
        self.trigger_cursor(False)

    def render(self):
        self.engine.logger.add("Looking rendered")
        units = join(
            self.engine.healths,
            self.engine.infos,
            self.engine.positions
        )
        # will get items on floor
        items = join(
            self.engine.items,
            self.engine.infos,
            self.engine.positions
        )

        unit_added = True
        for eid, (h, i, p) in units:
            if (p.x, p.y) == (self.cursor_x, self.cursor_y):
                self.terminal.addstr(
                    self.cursor_y + self.map_y - 1, 
                    self.cursor_x + self.map_x + 1,
                    i.name
                )
                unit_added = True
        for eid, (_, i, p) in items:
            if (p.x, p.y) == (self.cursor_x, self.cursor_y):
                self.terminal.addstr(
                    self.cursor_y + self.map_y, 
                    self.cursor_x + self.map_x + 1,
                    i.name
                )
        self.terminal.move(
            self.cursor_y + self.map_y, 
            self.cursor_x + self.map_x
        )        
        self.terminal.refresh()

    # def get_input(self):
    #     char = self.terminal.getch()
    #     keypress = self.engine.keyboard.get(char, None)
    #     if not keypress:
    #         return True
    #     q_keypress = keypress == 'q'
    #     esc_keypress = keypress == 'escape'
    #     if q_keypress or esc_keypress:
    #         return False
    #     elif keypress == 'up':
    #         self.cursor_y -= 1
    #         return True
    #     elif keypress == 'down':
    #         self.cursor_y += 1
    #     elif keypress == 'left':
    #         self.cursor_x -= 1
    #     elif keypress == 'right':
    #         self.cursor_x += 1
    #     return True
    def handle_input(self):
        if self.engine.keypress == 'escape':
            self.engine.change_screen('gamescreen')

class DeathMenu(Screen):
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

class LogMenu(Screen):
    def render(self):
        self.terminal.erase()
        border(self.terminal, 0, 0, self.engine.width-1, self.engine.height-1)
        self.terminal.addstr(0, 1, '[logs]')
        self.render_items()
        self.terminal.refresh()
    
    def get_input(self):
        char = self.terminal.getch()
        return False

class GameMenu(Screen):
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
            self.engine.change_screen('mainmenu')
        elif key == 'enter' and option == 'quit':
            self.engine.running = False
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up':
            self.index = (self.index - 1) % len(self.options)
