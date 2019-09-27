# panel.py

"""Panel class and subclasses"""

import curses

from source.common import border, join


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

    def add_char(self, x, y, char, color=0):
        if not isinstance(char, str):
            char = str(char)
        if len(char) > 1:
            raise ValueError("Parameter char is not len(1)")
        if color > 0:
            color = curses.color_pair(color)
        self.terminal.add_char(self.x + x, self.y + y, char, color)

    def add_string(self, x, y, string, color=0):
        if not isinstance(string, str):
            string = str(string)
        if color > 0:
            color = curses.color_pair(color)
        self.terminal.addstr(self.y + y, self.x + x, string, color)

    def border(self):
        border(self.terminal, self.x, self.y, self.width - 1, self.height - 1)        

    def render(self):
        self.border()
        self.terminal.addstr(self.y, self.x+1, f"[{self.title}]")

class PlayerPanel(Panel):
    __slots__ = "terminal engine x y width height title".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.engine = engine
    def render(self):
        self.border()
        player = self.engine.player
        info = self.engine.infos.find(player)
        health = self.engine.healths.find(player)
        cur_hp = str(health.cur_hp)
        max_hp = f"/ {health.max_hp}"
        mana = self.engine.manas.find(player)
        cur_mp = str(mana.cur_mp)
        max_mp = f"/ {mana.max_mp}"
        equipment = self.engine.equipments.find(player)
        weapon = self.engine.weapons.find(equipment.hand)
        damage = weapon.damage_swing if weapon else 1
        armor = 0
        for eq_slot in (equipment.head, equipment.body, equipment.feet):
            eq = self.engine.armors.find(eq_slot)
            if eq:
                armor += eq.defense
        self.add_string(1, 1, info.name)
        self.add_string(1, 2, "HP: ")
        self.add_string(5, 2, cur_hp, 197)
        self.add_string(len(cur_hp) + 6, 2, max_hp, 125)
        self.add_string(1, 3, "MP: ")
        self.add_string(5, 3, cur_mp, 22)
        self.add_string(len(cur_mp) + 6 , 3, max_mp, 20)
        self.add_string(1, 5, f"DMG: {damage}")
        self.add_string(1, 6, f"DEF: {armor}")

class EnemyPanel(Panel):
    __slots__ = "terminal engine x y width height title".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.engine = engine        
