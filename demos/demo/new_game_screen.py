# new_game_screen.py

from .game_screen import GameScreen
from .screen import MenuScreen


class NewGameScreen(MenuScreen):
    menu_title = "new game"
    def __init__(self, game):
        super().__init__(game)
        self.index = 0
        self.options += ['barbarian', 'archer', 'wizard']

    def handle_input(self, keypress):
        if keypress == 'escape':
            self.game.pop_screen()
        elif keypress == 'enter' and self.index == 0:
            self.game.push_screen(GameScreen, 'hero')
        elif keypress == 'enter' and self.index == 1:
            self.game.push_screen(GameScreen, 'hero')
        elif keypress == 'enter' and self.index == 2:
            self.game.push_screen(GameScreen, 'hero')
        else:
            super().handle_input(keypress)
