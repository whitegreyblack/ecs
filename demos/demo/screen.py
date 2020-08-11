# screen.py


class Screen(object):
    menu_title = "base screen"
    def __init__(self, game):
        self.game = game
        self.valid_keypresses: set = set()

    def render(self, terminal):
        ...

    def prerender(self, terminal):
        terminal.erase()
        terminal.border(self.menu_title)

    def postrender(self, terminal):
        terminal.refresh()

    def process(self):
        self.prerender(self.game.terminal)
        self.render(self.game.terminal)
        self.postrender(self.game.terminal)
        self.handle_input(self.game.get_input())

class MenuScreen(Screen):
    menu_title = "base menu screen"
    def __init__(self, game):
        super().__init__(game)
        self.index = 0
        self.options = []
        self.valid_keypresses.update({'escape', 'up', 'down', 'enter'})
    
    def render(self, terminal):
        x = terminal.width // 2 - (max(map(len, self.options)) // 2)
        y = terminal.height // 2 - 1
        current_x_offset = -2
        for i, option in enumerate(self.options):
            current_option = i == self.index
            if current_option:
                current_index_offset = current_x_offset
            else:
                current_index_offset = 0
            terminal.add_string(x + current_index_offset, 
                                y + 2 * i - 1, 
                                f"{'> ' if current_option else ''}{option}")

    def handle_input(self, keypress):
        print('got', keypress)
        if keypress == 'up':
            self.index = (self.index - 1) % len(self.options)
        elif keypress == 'down':
            self.index = (self.index + 1) % len(self.options)
