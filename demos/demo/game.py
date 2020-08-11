# game.py

"""Class to hold engine and ui's and handle running application"""

import time


class Game(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self.screens = None
        self.screen = None
        self.keyboard = None
        self.running = True
        self.screen_stack = []

    def push_screen(self, screen, *args):
        self.screen_stack.append(screen(self, *args))
        self.screen = self.screen_stack[-1]

    def pop_screen(self, pops=1):
        for _ in range(pops):
            self.screen_stack.pop()
        if not self.screen_stack:
            self.running = False
        else:
            self.screen = self.screen_stack[-1]

    def add_keyboard(self, keyboard):
        self.keyboard = keyboard

    @property
    def requires_keypress(self):
        return self.keypress is None

    def get_input(self):
        while True:
            char = self.terminal.getch()
            if char == 3: # ^C keyboard interrupt
                self.running = False
                return None
            keypress = self.keyboard.get(char, None)
            if not keypress:
                time.sleep(.001)
            else:
                return keypress

    def get_non_input(self):
        char = self.terminal.getch()
        if char == 3: # ^C keyboard interrupt
            self.running = False
            return
        return self.keyboard.get(char, None)

    def run(self):
        while self.running:
            self.screen.process()

if __name__ == "__main__":
    g = Game()
