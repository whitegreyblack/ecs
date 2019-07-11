# grave_system

"""Graveyard system class"""

import time

from source.ecs.systems.system import System

alive = lambda message: message.lifetime > 0

class GraveyardSystem(System):
    def process(self):
        # remove old messages
        # messages = self.engine.logger.messages
        # self.engine.logger.messages = list(filter(alive, messages))
        ...
