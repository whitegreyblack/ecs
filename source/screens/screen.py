# screens.py

"""Menus and Game Screen classes"""


import curses
import textwrap
import time

from source.common import border, join
from source.keyboard import keyboard, movement_keypresses
from source.raycast import cast_light, raycast


class Panel:
    __slots__ = ['terminal', 'x', 'y', 'width', 'height', 'title']
    def __init__(self, terminal, x, y, width, height, title):
        """Just a rectangle"""
        self.terminal = terminal
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

    def add_string(self, x, y, string, color=0):
        if not isinstance(string, str):
            string = str(string)
        if color > 0:
            color = curses.color_pair(color)
        self.terminal.addstr(y, x, string, color)

    def render(self):
        border(self.terminal, self.x, self.y, self.width-1, self.height-1)
        self.terminal.addstr(self.y, self.x + 1, f"[{self.title}]")

class MessagePanel(Panel):
    __slots__ = ['terminal', 'logger', 'x', 'y', 'width', 'height']
    def __init__(self, terminal, logger, x, y, width, height):
        """Just a rectangle"""
        self.terminal = terminal
        self.logger = logger
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self):
        """
            Adds the maximum number of possible messages to the panel by
            adding messages in reverse order then rendering the messages
            by re-reversing the message list to get the correct order of
            events.
            If a string will take up more space than the remaining panel
            space then the string will not be added and the message list
            will stop appending new strings.
        """
        logs = []
        for message in reversed(self.logger.messages):
            # -2 accounts for the indentation: '> '
            strings = list(enumerate(message.strings(self.width - 2)))
            if len(strings) + len(logs) > self.height:
                break
            logs += strings
        logs.reverse()
        for y, (i, log) in enumerate(logs):
            self.terminal.addstr(self.y + y,
                                 self.x, 
                                 f"{'>' if i == 0 else ' '} {log}")

class LogPanel(Panel):
    __slots__ = [
        'terminal', 
        'x', 'y', 
        'width', 
        'height', 
        'title', 
        'message_panel'
        ]
    def __init__(
            self, 
            terminal, 
            logger, 
            x, y, 
            width, 
            height, 
            title, 
            x_offset=2, 
            y_offset=1
    ):
        """Just a rectangle"""
        self.terminal = terminal
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.message_panel = MessagePanel(
            terminal,
            logger,
            x + x_offset,
            y + y_offset,
            width - x_offset * 2,
            height - y_offset * 2
            )
    
    def render(self):
        super().render()
        self.message_panel.render()

class Screen:
    def __init__(self, engine, terminal):
        self.engine = engine
        self.terminal = terminal
        self.valid_keypresses = {'escape'}

    def process(self):
        if not self.engine.requires_input:
            self.handle_input()
            self.engine.requires_input = True
            return True
        return False

    def border(self):
        border(self.terminal, 0, 0, self.engine.width - 1, self.engine.height - 1)
        self.terminal.addstr(0, 1, f"[{type(self).menu_title}]")
