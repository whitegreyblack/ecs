# rogue.py

from copy import deepcopy

from bearlibterminal import terminal

from source.border import border
from source.common import colorize, join, join_drop_key
from source.ecs.components import Information, Position, Render
from source.ecs.managers.component_manager import ComponentManager
from source.ecs.managers.entity_manager import EntityManager
from source.generate import string
from source.keyboard import blt_keyboard as keyboard
from source.logger import Logger
from source.router import Router
from source.scenemanager import SceneManager


def keypress_from_input(value):
    keys = keyboard.get(value, None)
    if isinstance(keys, tuple):
        return keys[int(terminal.state(terminal.TK_SHIFT))]
    return keys

class Engine(object):

    def __init__(self, components):
        self.logger = Logger()

        # set to an invalid value. All entity ids are positive integers (>0)
        self.entity: int = -1
        self.world = None
        self.entities = EntityManager()
        self.init_managers(components)
        self.systems = list()
        # self.router: Router = Router()

        # TODO: send this variable to the game screen instead
        # self.mode = GameMode.NORMAL
        # probably remove this too
        # self.entities_in_view: set = set()
        # self.tiles_in_view: set = set()

        # def init_systems(self, *systems):
        #     # systems are name unique so they can be called specifically by named
        #     for system in systems:
        #         # name = f"{system_type.classname().replace('system', '')}_system"
        #         # system = system_type(self)
        #         # self.__setattr__(name, system)
        #     self.systems.append(name)
    def add_system(self, system):
        self.systems.append(system)

    def init_managers(self, components):
        self.components = components
        for component in components:
            self.__setattr__(component.manager, ComponentManager(component))

    def find_entity(self, entity_id):
        return self.entity_manager.find(entity_id)

    def process(self):
        for system in systems:
            system.process()

class Screen:
    manager = None
    def __init__(self, title, keys):
        self.title = title
        self.keys = {'close', 'escape', 'enter'}.union(keys)
        self.key = None

    def add_border(self, engine, terminal):
        width = terminal.state(terminal.TK_WIDTH)
        height = terminal.state(terminal.TK_HEIGHT)
        for x, y, char in border(0, 0, width, height):
            terminal.printf(x, y, char)

    def add_title(self, engine, terminal):
        terminal.printf(1, 0, f'[[{self.title}]]')

    def add_string(self, terminal, x, y, string, color=None):
        if color:
            string = colorize(string, color)
        terminal.printf(x, y, string)

    def process(self, engine, terminal):
        for system in (self.render, self.input_receive, self.input_handle):
            system(engine, terminal)

    def get_mouse_state(self, terminal):
        return (
            terminal.state(terminal.TK_MOUSE_X),
            terminal.state(terminal.TK_MOUSE_Y)
        )

    def get_draw_methods(self):
        yield self.add_border
        yield self.add_title

    def render(self, engine, terminal):
        terminal.clear()
        for draw_method in self.get_draw_methods():
            draw_method(engine, terminal)
        terminal.refresh()

    def input_receive(self, engine, terminal):
        value = terminal.read()
        key = keypress_from_input(value)
        if key in self.keys:
            self.key = key

    def input_handle(self, engine, terminal):
        if self.key in ('close', 'escape'):
            self.manager.pop()

class MenuScreen(Screen):
    def __init__(self, title, options, keys):
        super().__init__(title, {'mouse-left', 'mouse-move'}.union(keys))
        self.options = options
        self.index = 0
        self.options = options
        self.mapper = dict()

    def get_option(self):
        return self.options[self.index]

    def prev_option(self):
        self.index = (self.index - 1) % len(self.options)

    def next_option(self):
        self.index = (self.index + 1) % len(self.options)

    def button_colors(self, terminal, i):
        if i == self.index:
            return "black", "white"
        else:
            return "white", "black"

    def get_draw_methods(self):
        yield from super().get_draw_methods()
        yield self.add_options

    def add_options(self, engine, terminal):
        x = terminal.state(terminal.TK_WIDTH) // 2
        y = terminal.state(terminal.TK_HEIGHT) // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_y_offset = -1
        option_x_offset = -(highlight_len // 2)

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(terminal, i)
            option_x = x + option_x_offset
            option_y = y + option_y_offset + i
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            terminal.printf(option_x, option_y, string)
            for i in range(highlight_len):
                self.mapper[(option_x + i, option_y)] = option

class StartMenuScreen(MenuScreen):
    def __init__(self):
        super().__init__(
            "main menu",
            ('new game', 'options', 'quit'),
            {'up', 'down'}
        )

    def input_handle(self, engine, terminal):
        key = self.key
        option = self.get_option()
        if key == 'enter' and option == 'quit':
            self.manager.empty()
        elif key in ('escape', 'close'):
            self.manager.push(ConfirmMenuScreen())
        elif key == 'enter' and option == 'new game':
            self.manager.push(RogueGameScreen())
        elif key == 'enter' and option == 'options':
            self.manager.push(OptionScreen())
        elif key == 'down':
            self.next_option()
        elif key == 'up':
            self.prev_option()
        elif key == 'mouse-left':
            option = self.mapper.get(self.get_mouse_state(terminal), None)
            if option == 'quit':
                self.manager.pop()
            elif option == 'options':
                self.manager.push(OptionScreen())
            elif option == 'new game':
                self.manager.push(RogueGameScreen())
        elif key == 'mouse-move':
            option = self.mapper.get(self.get_mouse_state(terminal), None)
            if option:
                self.index = self.options.index(option)

class GameMenuScreen(MenuScreen):
    def __init__(self):
        super().__init__(
            "game menu",
            ('back', 'main menu', 'settings', 'quit'),
            {'up', 'down', 'mouse-left', 'mouse-move'}
        )

class ConfirmMenuScreen(MenuScreen):
    def __init__(self):
        super().__init__(
            title="confirm menu",
            options=('yes', 'no'),
            keys={'left', 'right', 'mouse-left', 'mouse-move'}
        )

    def get_draw_methods(self):
        yield from super().get_draw_methods()
        yield self.add_text

    def add_text(self, engine, terminal):
        text = "Do you really want to quit?"
        x = terminal.state(terminal.TK_WIDTH) // 2 - len(text) // 2
        y = terminal.state(terminal.TK_HEIGHT) // 2 - 1
        terminal.printf(x, y, text)

    def add_options(self, engine, terminal):
        x = terminal.state(terminal.TK_WIDTH) // (len(self.options) + 1)
        y = terminal.state(terminal.TK_HEIGHT) // 2

        max_option_len = max(map(len, self.options))
        highlight_len = max_option_len + 2
        option_x_offset = x
        option_y_offset = 1

        for i, option in enumerate(self.options):
            color, bkcolor = self.button_colors(terminal, i)
            option_x = x + (option_x_offset * i)
            option_y = y + option_y_offset
            string = colorize(
                "{:^{w}}".format(option, w=highlight_len),
                color=color,
                bkcolor=bkcolor
            )
            terminal.printf(option_x, option_y, string)
            for i in range(-1, highlight_len + 2):
                for j in range(-1, 2):
                    self.mapper[(option_x + i, option_y + j)] = option

    def input_handle(self, engine, terminal):
        key = self.key
        option = self.get_option()
        if (key == 'enter' and option == 'yes') or key == 'close':
            self.manager.empty()
        elif (key == 'enter' and option == 'no') or key == 'escape':
            self.manager.pop()
        elif key == 'left':
            self.next_option()
        elif key == 'right':
            self.prev_option()
        elif key == 'mouse-left':
            option = self.mapper.get(self.get_mouse_state(terminal), None)
            if option == 'yes':
                self.manager.empty()
            elif option == 'no':
                self.manager.pop()
        elif key == 'mouse-move':
            option = self.mapper.get(self.get_mouse_state(terminal), None)
            if option:
                self.index = self.options.index(option)

class OptionScreen(MenuScreen):
    def __init__(self):
        super().__init__(
            title="options",
            options=('back',),
            keys={'up', 'down', 'mouse-left', 'mouse-move'}
        )
    def input_handle(self, engine, terminal):
        key = self.key
        option = self.get_option()
        if (key == 'enter' and option == 'back'):
            self.manager.pop()


class RogueGameScreen(Screen):
    def __init__(self, keys=None):
        super().__init__("game", {'mouse-move'})
        self.bkcolors = ("#642b09","#c46404")
        self.mapper = dict()
        self.selection = None

    # def get_draw_methods(self):
    #     yield from super().get_draw_methods()
    #     yield self.draw_board

    # def draw_board(self, engine, terminal):
    #     width = terminal.state(terminal.TK_WIDTH) // 2 - 4
    #     height = terminal.state(terminal.TK_HEIGHT) // 2 - 4
    #     tiles = {
    #         (i, j): ChessTile(self.bkcolors[(j * 7 + i) % 2])
    #             for i in range(8) for j in range(8)
    #     }
    #     for (p, r) in join_drop_key(engine.positions, engine.renders):
    #         tile = tiles[(p.x, p.y)]
    #         self.mapper[(p.x + width, p.y + height)] = r.char
    #         tile.piece = r
    #         tile.highlighted = self.selection == (p.x + width, p.y + height)

    #     for (i, j), tile in tiles.items():
    #         terminal.printf(
    #             width + i,
    #             height + j,
    #             colorize(tile.piece, tile.color, tile.bkcolor)
    #         )

    def input_handle(self, engine, terminal):
        if self.key in ('close', 'escape'):
            self.manager.push(ConfirmMenuScreen())
        elif self.key == 'mouse-move':
            piece = self.mapper.get(self.get_mouse_state(terminal), None)
            if piece:
                self.selection = self.get_mouse_state(terminal)
            else:
                self.selection = None

    def process(self, engine, terminal):
        """
            Draw/Render
            Handle Input/Inject Engine
            Engine Process/Update
        """
        for system in (self.render, self.input_receive, self.input_handle):
            system(engine, terminal)
        engine.process()

def initialize_game_engine():
    engine = Engine(components=(
        Position, Render, Information
    ))
    engine.add_system()

if __name__ == "__main__":
    terminal.open()
    terminal.set("input: filter=[keyboard,mouse]")
    engine = initialize_game_engine()
    sm = SceneManager(StartMenuScreen())
    sm.run(engine, terminal)
