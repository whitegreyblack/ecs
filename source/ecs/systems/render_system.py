# render_system.py

"""Render system class"""

from source.ecs.systems.system import System


class RenderSystem(System):
    def __init__(self, engine, terminal, logger=None):
        super().__init__(engine, logger)
        self.screen = None

    def process(self):
        self.screen.process()
