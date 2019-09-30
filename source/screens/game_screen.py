# gamescreen.py

"""Game screen class that renders and processes inputs for the main game"""

import curses
import random
import time

from source.common import (
    GameMode, border, circle, diamond, direction_to_keypress, join,
    join_drop_key, join_on, scroll)
from source.ecs.components import (Effect, MeleeHitEffect, Movement, Position,
                                   RangeHitEffect, Spell, SpellEffect)
from source.pathfind import bresenhams, pathfind
from source.raycast import cast_light

from .log_panel import LogPanel
from .map_panel import MapPanel
from .panel import PlayerPanel, EnemyPanel
from .screen import Screen


class GameScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.initialize_panels()
        self.initialize_cursor()
        self.entities = None
        self.entity_index = 0
        self.valid_keypresses.update({
            'escape',
            # arrowkeys/keypad arrows
            'up-left', 'up', 'up-right',
            'left', 'center', 'right',
            'down-left', 'down', 'down-right',
            'c', # close door
            'e', # equipment
            'i', # inventory
            'o', # close door
            'l', # look
            'comma', # pickup
            'less-than', # move up stairs
            'greater-than', # move down stairs
            't', # throw missile,
            'tilde',
            'enter',
            'backtick',
        })

    def initialize_panels(self):
        height, width = self.terminal.getmaxyx()
        # player info
        player_panel = PlayerPanel(
            self.terminal, 
            self.engine, 
            0, 0, 16, 19, 
            'info'
        )
        # map info and player location
        map_panel = MapPanel(
            self.terminal,
            self.engine,
            player_panel.width,
            0, 50, 19,
            "map"
        )
        # enemy panel border and coordinates
        enemy_panel = EnemyPanel(
            self.terminal,
            self.engine,
            player_panel.width + map_panel.width,
            0,
            width - player_panel.width - map_panel.width,
            player_panel.height,
            "enemies"
        )
        logs_panel = LogPanel(
            self.terminal, 
            self.engine.logger,
            0,
            map_panel.height, 
            width,
            height - map_panel.height,
            'logs'
        )
        self.panels = [
            map_panel,
            player_panel,
            enemy_panel,
            logs_panel,
        ]

    def initialize_cursor(self):
        # initialize a cursor
        self.cursor = self.engine.entities.create()
        self.engine.positions.add(self.cursor, Position())

    def render_cursor(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        position = self.engine.positions.find(self.engine.cursor)
        x_offset = self.map_x - cam_x
        y_offset = self.map_y - cam_y
        if self.engine.mode in (GameMode.LOOKING, GameMode.DEBUG):
            self.render_char(position.x + x_offset, position.y + y_offset, 'X')
        elif self.engine.mode == GameMode.MAGIC:
            cursor = self.engine.cursors.find(self.engine.cursor)
            spellname = Spell.identify[cursor.using]
            render = self.engine.renders.shared[spellname][0]
            color = curses.color_pair(render.color)
            if spellname == 'fireball':
                for xx, yy in diamond():
                    x = position.x + xx
                    y = position.y + yy
                    if (x, y) not in tiles:
                        continue
                    self.render_char(x + x_offset, 
                                     y + y_offset, 
                                     render.char,
                                     color)
            elif spellname == 'crystal nova':
                 for xx, yy in circle():
                    x = position.x + xx
                    y = position.y + yy
                    if (x, y) not in tiles:
                        continue
                    self.render_char(x + x_offset, 
                                     y + y_offset, 
                                     render.char,
                                     color)
            else:
                # unhandled or single tile magic
                self.render_char(position.x + x_offset, position.y + y_offset, 'X')
        else:
            player = self.engine.positions.find(self.engine.player)
            path = pathfind(self.engine, player, position, pathfinder=bresenhams)
            x_offset = self.map_x - cam_x
            y_offset = self.map_y - cam_y
            for x, y in path[1:]:
                self.render_char(x + x_offset, y + y_offset, 'X')

    def render_items(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        item_positions = set()
        for _, (_, position, render, info) in join(
            self.engine.items,
            self.engine.positions,
            self.engine.renders,
            self.engine.infos
        ):
            current_map = position.map_id == self.engine.world.id
            visibility = (position.x, position.y) in tiles
            inbounds = x0 <= position.x < x1 and y0 <= position.y < y1
            if current_map and visibility and inbounds:
                try:
                    self.render_char(
                        self.map_x + position.x - cam_x,
                        self.map_y + position.y - cam_y,
                        render.char,
                        curses.color_pair(render.color)
                    )
                except:
                    print(position, render, info)
                    print(render.color)
                    raise

    def update_effects(self):
        self.engine.effects.components.clear()

    def render_melee_hit_effect(self, x, y, render, effect):
        self.render_char(x, y, effect.char, 0)
        self.terminal.noutrefresh()
        curses.doupdate()
        time.sleep(.045)
        color = curses.color_pair(render.color)
        self.render_char(x, y, render.char, color)
        self.terminal.noutrefresh()

    def render_range_hit_effect(self, x, y, ox, oy, render, effect, tiles):
        self.render_char(x+ox, y+oy, effect.char, 0)
        self.terminal.noutrefresh()
        curses.doupdate()
        time.sleep(.023)
        color = curses.color_pair(tiles[(x, y)].color)
        self.render_char(x+ox, y+oy, tiles[(x, y)].char, color)
        self.terminal.noutrefresh()
        curses.doupdate()
        time.sleep(.023)

    def render_spell_hit_effect(self, positions, previous, ox, oy, renders, tiles):
        for (x, y), render in zip(positions, renders):
            if (x, y) not in tiles:
                continue
            self.render_char(x + ox, y + oy, 
                             render.char, 
                             curses.color_pair(render.color))
        self.terminal.noutrefresh()
        curses.doupdate()
        time.sleep(.05)
        for (x, y) in positions:
            if (x, y) not in tiles:
                continue
            tile = tiles[(x, y)]
            self.render_char(x + ox, y + oy, tile.char, curses.color_pair(tile.color))
        self.terminal.noutrefresh() 
        curses.doupdate()
        # time.sleep(0.033)

    def render_effects(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        """
        Currently have the following effects:
            - attack animation
            - range animation
        Want:
            - spell animation
        """
        x_offset = self.map_x - cam_x
        y_offset = self.map_y - cam_y
        for eid, effect in self.engine.effects.components.items():
            position = self.engine.positions.find(effect.entity)
            render = self.engine.renders.find(effect.entity)
            info = self.engine.infos.find(effect.entity)
            # only shows if inside the view area and space is lighted
            if ((position.x, position.y) in tiles 
                and x0 <= position.x < x1 
                and y0 <= position.y < y1
            ):
                if isinstance(effect, MeleeHitEffect):
                    x = position.x + x_offset
                    y = position.y + y_offset
                    self.render_melee_hit_effect(x, y, render, effect)
                elif isinstance(effect, RangeHitEffect):
                    for x, y in effect.path[1:]:
                        self.render_range_hit_effect(
                            x,
                            y,
                            x_offset,
                            y_offset,
                            render,
                            effect,
                            tiles
                        )
                elif isinstance(effect, SpellEffect):
                    previous = None
                    for positions, renders in effect.ticks[1:]:
                        self.render_spell_hit_effect(
                            positions,
                            previous,
                            x_offset,
                            y_offset,
                            renders,
                            tiles
                        )
                        previous = positions

    def render(self):
        self.terminal.clear()
        self.terminal.erase()

        for panel in self.panels:
            panel.render()

        self.terminal.noutrefresh()
        curses.doupdate()
   
    def process(self):
        if self.engine.mode == GameMode.NORMAL:
            return self.engine.turn_system.process()
        else:
            return self.engine.look_system.process()
