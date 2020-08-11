# panel.py

"""Panel class and subclasses"""

import textwrap

from source.border import border
from source.common import colorize, join


class Panel:
    __slots__ = ['terminal', 'x', 'y', 'width', 'height', 'title']
    def __init__(self, terminal, x, y, width, height, title):
        """Just a rectangle"""
        self.terminal = terminal
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title

    def add_string(self, x, y, string, color=None):
        if color:
            string = colorize(string, color)
        self.terminal.printf(self.x + x, self.y + y, string)

    def add_border(self):
        g = border(self.x, self.y, self.x + self.width, self.y + self.height)
        for i, j, c in g:
            self.terminal.printf(i, j, c)

    def render(self):
        self.add_border()
        self.terminal.printf(self.x + 1, self.y, f"[[{self.title}]]")

class PlayerPanel(Panel):
    __slots__ = "terminal engine x y width height title".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.engine = engine
    def render(self):
        super().render()
        c = colorize
        player = self.engine.player
        info = self.engine.infos.find(player)
        hp = self.engine.healths.find(player)
        mp = self.engine.manas.find(player)
        equipment = self.engine.equipments.find(player)
        weapon = self.engine.weapons.find(equipment.hand)
        damage = weapon.damage_swing if weapon else 1
        armor = 0
        for eq_slot in (equipment.head, equipment.body, equipment.feet):
            eq = self.engine.armors.find(eq_slot)
            if eq:
                armor += eq.defense
        self.terminal.printf(1, 1, textwrap.dedent(f"""
            {info.name}
            [0xE200+0] {c(hp.cur_hp, 'flame')} / {c(hp.max_hp, 'amber')}
            [0xE300+0] {c(mp.cur_mp, 'sky')} / {c(mp.max_mp, 'azure')}
            [0xE100+0] {damage} [0xE400+0] {armor}"""[1:]))

class EnemyPanel(Panel):
    __slots__ = "terminal engine x y width height title".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.engine = engine
    def render(self):
        super().render()
        c = colorize
        current_height = 0
        enemies = []
        for eid in self.engine.entities_in_view:
            if current_height >= self.height - 2:
                break
            gui = self.engine.renders.find(eid)
            hp = self.engine.healths.find(eid)
            info = self.engine.infos.find(eid)
            enemies.append("{} {} / {}".format(
                c(gui.char, gui.color),
                c(hp.cur_hp, 'flame'),
                c(hp.max_hp, 'amber')
            ))
            current_height += 1
        self.add_string(2, 1, '\n'.join(enemies))
