# game_menu_screen.py

from .screen import MenuScreen


class InGameMenuScreen(MenuScreen):
    menu_title = "menu"
    def __init__(self, game):
        super().__init__(game)
        self.options += ['exit to main menu', 'exit game']

    def handle_input(self, keypress):
        if keypress == 'escape':
            self.game.pop_screen()
        elif keypress == 'enter' and self.index == 0:
            self.game.pop_screen(2)
        elif keypress == 'enter' and self.index == 1:
            self.game.pop_screen(3)
        else:
            # handles up/down keypresses
            super().handle_input(keypress)
