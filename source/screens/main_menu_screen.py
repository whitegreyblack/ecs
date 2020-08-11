# start_screen.py

from source.border import border
from source.keyboard import blt_keyboard as keyboard
from source.keyboard import movement_keypresses
from source.screens import ConfirmMenuScreen, GameScreen
from source.screens.screen import MenuScreen


class MainMenuScreen(MenuScreen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.title = 'main menu'
        self.options = ('new game', 'options', 'quit')
        self.valid_keypresses.update({
            'close',
            'escape',
            'enter',
            'up',
            'down',
            'mouse-left',
            'mouse-move'
        })

    def handle_input(self):
        # keep_open, exit_prog
        key = self.engine.keypress
        option = self.options[self.index]
        if key == 'enter' and option == 'quit':
            self.engine.running = False
        elif key in ('escape', 'close'):
            self.engine.add_screen(ConfirmMenuScreen)
        elif key == 'enter' and option == 'new game':
            self.engine.add_screen(GameScreen)
        elif key == 'enter' and option == 'options':
            self.engine.running = False
            #self.engine.add_screen(OptionScreen)
        elif key == 'down':
            self.index = (self.index + 1) % len(self.options)
        elif key == 'up':
            self.index = (self.index - 1) % len(self.options)
        elif key == 'mouse-left':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option == 'quit' or option == 'options':
                self.engine.running = False
            elif option == 'new game':
                self.engine.add_screen(GameScreen)
        elif key == 'mouse-move':
            option = self.mapper.get(self.engine.get_mouse_state(), None)
            if option:
                self.index = self.options.index(option)
