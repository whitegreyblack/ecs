# empty_screen.py

from source.border import border
from source.keyboard import blt_keyboard as keyboard
from source.keyboard import movement_keypresses
from source.screens.screen import Screen


class EmptyScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.valid_keypresses.update(keyboard.values())

    def handle_input(self):
        self.engine.running = False
