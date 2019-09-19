# game_screen.py

import curses

from source.common import border, join
from source.ecs.components import Position
from source.generate import dimensions, matrix, string
from source.keyboard import movement_keypresses

from .engine import Engine
from .game_menu_screen import InGameMenuScreen
from .screen import Screen

room = """
###############
#.............#
#.............#
#...#..#..#...#
#.............#
#.............#
###############"""[1:]

class GameScreen(Screen):
    menu_title = "play"
    def __init__(self, game, name):
        super().__init__(game)
        self.valid_keypresses.update({
            'escape', 
            'left', 
            'right', 
            'up', 
            'down',
            'a'
        })
        self.engine = Engine.demo()

    def render(self, terminal):
        m = matrix(room)
        w, h = dimensions(m)
        x = terminal.width // 2  - w // 2
        y = terminal.height // 2 - h // 2
        for j, s in enumerate(string(m).split('\n')):
            terminal.add_string(x, y+j, s)

        for e, p in self.engine.positions:
            terminal.add_char(x + p.x, y + p.y, str(e))

    def handle_input(self, keypress):
        if keypress == 'escape':
            self.game.push_screen(InGameMenuScreen)
        elif keypress == 'a':
            self.engine.add_player()
        elif keypress == 'd':
            self.engine.del_player()
        # engine commands
        elif self.engine.requires_input and keypress is not None:
            self.engine.handle_keypress(keypress)

    def process(self):
        if not self.engine.player:
            get_input = self.game.get_non_input
        else:
            get_input = self.game.get_input
        self.handle_input(get_input())
        self.engine.process()
        self.prerender(self.game.terminal)
        self.render(self.game.terminal)
        self.postrender(self.game.terminal)
        """
        basic game loop
        processInput();
        update();
        render();
        """