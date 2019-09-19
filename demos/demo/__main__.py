# demos\demos.py

import curses

from source.common import border, join
from source.ecs.components import Position
from source.keyboard import keyboard

from .game import Game
from .main_menu_screen import MainMenuScreen
from .terminal import Terminal


def demo(screen):
    # turn off blinking and set to non-blocking input
    curses.curs_set(0)
    screen.nodelay(1)
    g = Game(Terminal(screen))
    g.push_screen(MainMenuScreen)
    g.add_keyboard(keyboard)
    g.run()

if __name__ == "__main__":
    curses.wrapper(demo)
