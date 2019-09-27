# map_panel.py

"""World and Map panels. World panel is a wrapper class for Map"""

from .panel import Panel


class LevelPanel(Panel):
    __slots__ = "terminal engine x y width height".split()
    def __init__(self, terminal, engine, x, y, width, height):
        super().__init__(terminal, x, y, width, height, None)
        self.engine = engine
    def render(self):
        self.terminal.addstr(self.y, self.x, 'MAPS')

class MapPanel(Panel):
    __slots__ =  "terminal x y width height title level_panel".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.level_panel = LevelPanel(
            terminal, 
            engine, 
            x + 1, 
            y + 1, 
            width - 2, 
            height - 2
            )
    def render(self):
        super().render()
        self.level_panel.render()
