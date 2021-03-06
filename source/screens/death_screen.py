# death_screen.py

import time

from source.common import join
from source.keyboard import blt_keyboard as keyboard, movement_keypresses
from source.raycast import cast_light, raycast

from .screen import Screen


class DeathScreen(Screen):
    def __init__(self, engine, terminal):
        # add the keypress suite since any button ends this screen
        super().__init__(engine, terminal)
        self.valid_keypresses.update(keyboard.values())

    def render(self):
        # adds a full sized bordered window that informs user they have lost
        x = self.engine.width // 2
        y = self.engine.height // 2
        title = "death screen"
        message = "you died"

        self.terminal.erase()
        # border(self.terminal, 0, 0, self.engine.width - 1, self.engine.height - 1)
        self.terminal.printf(1, 0, f"{title}")
        self.terminal.printf(x - len(message) // 2, y, message)
        self.terminal.refresh()
    
    def handle_input(self):
        # turn the game engine off
        self.engine.running = False
