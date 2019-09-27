# screens.py

"""
Base Screen Class

UI composed of Screen => [ Panel | Panel | Panel ]

Screens should be borderable and have keypress actions
Panels should be borderable only

Screens should inherit from Panel and Borderable?
"""


class Screen:
    def __init__(self, engine, terminal):
        self.engine = engine
        self.terminal = terminal
        self.valid_keypresses = {'escape'}

    def process(self):
        if not self.engine.requires_input:
            self.handle_input()
            self.engine.requires_input = True
            return True
        return False

    def border(self):
        border(self.terminal, 
               0, 0, 
               self.engine.width - 1, 
               self.engine.height - 1)
        self.terminal.addstr(0, 1, f"[{type(self).menu_title}]")
