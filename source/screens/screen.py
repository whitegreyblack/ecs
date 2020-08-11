# screens.py

"""
Base Screen Class

UI composed of Screen => [ Panel | Panel | Panel ]

Screens should be borderable and have keypress actions
Panels should be borderable only

Screens should inherit from Panel and Borderable?
"""

from source.border import border
from source.common import colorize

class Screen:
    def __init__(self, engine, terminal):
        self.engine = engine
        self.terminal = terminal
        self.valid_keypresses = {'escape'}

    def render(self):
        self.terminal.clear()
        self.terminal.refresh()

    def process(self):
        if not self.engine.requires_input:
            self.handle_input()
            self.engine.requires_input = True
            return True
        return False

    def add_border(self):
        for i, j, c in border(0, 0, self.engine.width, self.engine.height):
            self.terminal.printf(i, j, c)

    def add_title(self):
        self.terminal.printf(1, 0, f'[[{self.title}]]')

    def add_string(self, x, y, string, color=None):
        if color:
            string = colorize(string, color)
        self.terminal.printf(x, y, string)

class MenuScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.index = 0
        self.title = 'main menu screen'
        self.options = None
        self.mapper = dict()
        self.render_calls = [
            self.add_border,
            self.add_title,
            self.add_options
        ]

    def render(self):
        self.terminal.clear()
        for renderer in self.render_calls:
            renderer()
        self.terminal.refresh()

    def button_colors(self, i):
        if i == self.index:
            return "black", "white"
        else:
            return "white", "black"

    def add_options(self):
        x = self.engine.width // 2
        y = self.engine.height // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_y_offset = -1
        option_x_offset = -(highlight_len // 2)

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(i)
            option_x = x + option_x_offset
            option_y = y + option_y_offset + i
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            self.terminal.printf(option_x, option_y, string)
            for i in range(highlight_len):
                self.mapper[(option_x + i, option_y)] = option
