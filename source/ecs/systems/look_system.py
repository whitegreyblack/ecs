# look_system.py

import random

from .system import System


class LookSystem(System):
    def process(self):
        entity = self.engine.cursor
        if self.engine.requires_input:
            return False
        command = self.engine.get_keypress()
        self.engine.requires_input = True
        return self.engine.command_system.process(entity, command)
