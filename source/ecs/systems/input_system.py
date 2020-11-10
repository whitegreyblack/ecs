# input_system.py

"""Input system"""

import time

from source.ecs.systems.system import System


class InputSystem(System):
    def process(self, valid_keypresses=None) -> str:
        if not valid_keypresses:
            valid_keypresses = self.engine.screen.valid_keypresses
        keypress = None
        while keypress is None:
            char = self.engine.get_input()
            keypress = self.engine.keypress_from_input(char)
            if keypress in valid_keypresses:
                self.engine.requires_input = False
            else:
                keypress = None
            if not keypress:
                time.sleep(.001)
        self.engine.keypress = keypress
