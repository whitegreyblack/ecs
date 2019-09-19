# screens.py

from .new_game_screen import NewGameScreen
from .screen import MenuScreen


class MainMenuScreen(MenuScreen):
    menu_title = "demo"
    def __init__(self, game):
        super().__init__(game)
        self.index = 0
        self.options += ['new game', 'quit']

    def handle_input(self, keypress):
        # ignore invalid keypresses
        if keypress not in self.valid_keypresses:
            return
        if keypress == 'escape':
            self.game.running = False
        elif keypress == 'enter' and self.index == 0:
            self.game.push_screen(NewGameScreen)
        elif keypress == 'enter' and self.index == 1:
            self.game.pop_screen()
        else:
            super().handle_input(keypress)
