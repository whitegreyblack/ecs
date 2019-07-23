# gamescreen.py

"""Game screen class that renders and processes inputs for the main game"""

import curses
import random
import time

from source.astar import pathfind
from source.color import colors
from source.common import border, direction_to_keypress, eight_square, join, scroll
from source.ecs.components import Movement
from source.keyboard import valid_keypresses
from source.raycast import cast_light

from .screen import Screen


class GameScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.initialize_coordinates()
        self.entities = None
        self.entity_index = 0
        self.valid_keypresses.update(valid_keypresses)

    def initialize_coordinates(self):
        self.height, self.width = self.terminal.getmaxyx()

        tilemap = self.engine.tilemaps.find(eid=self.engine.world.id)
        # player info
        self.player_panel_x = 0
        self.player_panel_y = 0
        self.player_panel_width = 15
        self.player_panel_height = 18

        self.map_panel_x = self.player_panel_width + 1
        self.map_panel_y = 0
        self.map_panel_width = 50
        self.map_panel_height = 18
        self.map_offset_x = 1
        self.map_offset_y = 1
        self.map_x = self.map_panel_x + self.map_offset_x
        self.map_y = self.map_panel_y + self.map_offset_y # self.header_y + 1
        self.map_width = self.map_panel_width - 1
        self.map_height = self.map_panel_height -1

        # enemy panel border and coordinates
        self.enemy_panel_x = self.player_panel_width + self.map_panel_width + 2
        self.enemy_panel_y = 0
        self.enemy_panel_width = self.width - self.enemy_panel_x - 1
        self.enemy_panel_height = self.map_panel_height
        self.enemy_panel_offset_x = 1
        self.enemy_panel_offset_y = 1
        self.enemy_item_x = self.enemy_panel_x + self.enemy_panel_offset_x
        self.enemy_item_y = self.enemy_panel_y + self.enemy_panel_offset_y
        self.enemy_item_width = self.enemy_panel_width - self.enemy_panel_offset_x * 2
        self.enemy_items_height = self.enemy_panel_height - self.enemy_panel_offset_y * 2

        # log panel border and coordinates
        self.logs_panel_x = 0
        self.logs_panel_y = self.map_panel_height + 1
        self.logs_panel_width = self.width
        self.logs_panel_height = self.height - self.map_panel_height - 2
        self.logs_panel_offset_x = 2
        self.logs_panel_offset_y = 1
        self.logs_item_x = self.logs_panel_x + self.logs_panel_offset_x
        self.logs_item_y = self.logs_panel_y + self.logs_panel_offset_y
        self.logs_item_width = self.logs_panel_width - self.logs_panel_offset_x * 2
        self.logs_items_height = self.logs_panel_height - self.logs_panel_offset_y * 2

    def render_string(self, x, y, string, attr=0):
        self.terminal.addstr(y, x, string, attr)

    def render_char(self, x, y, character, attr=0):
        self.terminal.addch(y, x, character, attr)

    def render_fov(self):
        cast_light(self.engine)

    def render_player_panel_details(self, render, info, health) -> bool:
        self.render_string(
            self.player_panel_x + 1,
            self.player_panel_y + 1,
            info.name
        )
        self.render_string(
            self.player_panel_x + 1,
            self.player_panel_y + 2,
            "HP: ",
        )
        cur_hp = str(health.cur_hp)
        self.render_string(
            self.player_panel_x + 5,
            self.player_panel_y + 2,
            cur_hp,
            curses.color_pair(197)
        )
        self.render_string(
            self.player_panel_x + len(cur_hp) + 6,
            self.player_panel_y + 2,
            f"/ {health.max_hp}",
            curses.color_pair(125)
        )

    def render_player_panel(self):
        border(
            self.terminal,
            self.player_panel_x,
            self.player_panel_y,
            self.player_panel_width,
            self.player_panel_height
        )
        self.terminal.addstr(0, 1, '[info]')

    def render_inventory_panel(self):
        border(
            self.terminal, 
            self.inventory_x, 
            self.inventory_y, 
            self.inventory_width, 
            self.inventory_height
        )
        self.terminal.addstr(1, 2, '[equipment]')

        inventory = self.engine.inventories.find(self.engine.player)
        # self.terminal.addstr(1, 1, f"{inventory}")
        if not inventory.items:
            self.terminal.addstr(2, 2, 'empty')
        else:
            items = []
            for eid, (_, info) in join(self.engine.items, self.engine.infos):
                if eid in inventory.items:
                    items.append(info)
            for i, info in enumerate(items):
                self.render_string(
                    self.inventory_x + 1, 
                    self.inventory_y + 1 + i, 
                    f"{i+1}. {info.name}"
                )

    def render_enemy_panel_detail(self, enemy_count, render, info, health) -> bool:
        if enemy_count < self.enemy_panel_height - 1:
            # enemy character eg. goblin => <green>g</green>
            self.render_char(
                self.enemy_item_x + 1,
                self.enemy_item_y + enemy_count,
                render.char,
                curses.color_pair(colors.get(info.name, 240))
            )
            # enemy character current health
            self.render_string(
                self.enemy_item_x + 4,
                self.enemy_item_y + enemy_count,
                str(health.cur_hp),
                curses.color_pair(197)
            )
            # enemy character maximum health
            self.render_string(
                self.enemy_item_x + len(str(health.cur_hp)) + 5,
                self.enemy_item_y + enemy_count,
                f"/ {health.max_hp}",
                curses.color_pair(125)
            )
            return True
        return False

    def render_enemy_panel(self):
        """Initializes frame only. Content is filled by render_units"""
        border(
            self.terminal, 
            self.enemy_panel_x,
            self.enemy_panel_y, 
            self.enemy_panel_width,
            self.enemy_panel_height
        )
        self.render_string(
            self.enemy_panel_x + 1,
            self.enemy_panel_y,
            '[enemies]'
        )

    def render_map_panel(self):
        # calculate offsets on scrolling map
        position = self.engine.positions.find(self.engine.player)
        tilemap = self.engine.tilemaps.find(eid=position.map_id)
        if tilemap.width < self.map_width:
            cam_x = 0
        else:
            cam_x = scroll(position.x, self.map_width, tilemap.width)
        x0, x1 = cam_x, self.map_width + cam_x
        if tilemap.height < self.map_height:
            cam_y = 0
        else:
            cam_y = scroll(position.y, self.map_height, tilemap.height)
        y0, y1 = cam_y, self.map_height + cam_y

        self.render_map(position.map_id, cam_x, cam_y, x0, x1, y0, y1)

        tiles = {
            (position.x, position.y): visibility
                for _, (position, visibility) in join(
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visibility.level > 1
        }

        self.render_items(tiles, position.map_id, cam_x, cam_y, x0, x1, y0, y1)
        while True:
            self.render_units(tiles, position.map_id, cam_x, cam_y, x0, x1, y0, y1)
            if not self.engine.effects.components:
                break
            # render effects
            self.render_effects(tiles, position.map_id, cam_x, cam_y, x0, x1, y0, y1)
            self.engine.effects.components.clear()

    def render_map(self, map_id, cam_x, cam_y, x0, x1, y0, y1):
        border(
            self.terminal,
            self.map_panel_x,
            self.map_panel_y,
            self.map_panel_width,
            self.map_panel_height
        )
        tiles = join(
            self.engine.visibilities,
            self.engine.positions,
            self.engine.renders,
            self.engine.infos
        )
        for _, (visibility, position, render, info) in tiles:
            current_map_id = position.map_id == map_id
            visible = visibility.level > 0
            xbounds = x0 <= position.x < x1
            ybounds = y0 <= position.y < y1
            inbounds = xbounds and ybounds
            if current_map_id and visible and inbounds:
                if visibility.level == 2:
                    color = colors.get(info.name, 240)
                else:
                    color = 240
                self.render_char(
                    position.x + self.map_x - cam_x,
                    position.y + self.map_y - cam_y,
                    render.char,
                    curses.color_pair(color)
                )

    def render_units(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        units = [
            (eid, health, position, render, info)
                for eid, (health, position, render, info) in join(
                    self.engine.healths,
                    self.engine.positions, 
                    self.engine.renders,
                    self.engine.infos
                )
                if position.map_id == self.engine.world.id
        ]
        # look for all positions not in tile positions and visibilities.
        # if their positions match and map is visible then show the unit
        enemy_count = 0
        for eid, health, position, render, info in units:
            current_map_id = position.map_id == map_id
            visibility = tiles.get((position.x, position.y), None)
            inbounds = x0 <= position.x < x1 and y0 <= position.y < y1
            if visibility and inbounds:
                if visibility.level == 2:
                    color = colors.get(info.name, 0)
                else:
                    color = 0
                self.render_char(
                    self.map_x + position.x - cam_x,
                    self.map_y + position.y - cam_y,
                    render.char,
                    curses.color_pair(color)
                )
                # check if enemy needs to added to the panel
                non_player = eid != self.engine.player.id
                description_space = enemy_count < self.enemy_panel_height - 1
                if non_player:
                        enemy_count += int(self.render_enemy_panel_detail(
                            enemy_count, 
                            render, 
                            info, 
                            health
                        ))
                else:
                    self.render_player_panel_details(render, info, health)

    def render_items(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        items = join(
            self.engine.items,
            self.engine.positions,
            self.engine.renders,
            self.engine.infos
        )
        item_positions = set()
        for _, (_, position, render, info) in items:
            visibility = tiles.get((position.x, position.y), None)
            inbounds = x0 <= position.x < x1 and y0 <= position.y < y1
            if visibility and inbounds:
                color = colors.get(info.name, 0)
                self.render_char(
                    self.map_x + position.x - cam_x,
                    self.map_y + position.y - cam_y,
                    render.char,
                    curses.color_pair(color)
                )

    def render_effects(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        # eid, effect = self.engine.effects.

        for eid, effect in self.engine.effects.components.items():
            position = self.engine.positions.find(eid=effect.entity_id)
            render = self.engine.renders.find(eid=effect.entity_id)
            info = self.engine.infos.find(eid=effect.entity_id)
            visibility = tiles.get((position.x, position.y), None)
            inbounds = x0 <= position.x < x1 and y0 <= position.y < y1
            # only shows if inside the view area and space is lighted
            if visibility and inbounds:
                self.render_char(
                    self.map_x + position.x - cam_x,
                    self.map_y + position.y - cam_y,
                    effect.char
                )
                self.terminal.noutrefresh()
                curses.doupdate()
                time.sleep(.085)
                self.render_char(
                    self.map_x + position.x - cam_x,
                    self.map_y + position.y - cam_y,
                    render.char,
                    curses.color_pair(colors.get(info.name, 0))
                )
                self.terminal.noutrefresh()
                curses.doupdate()
                # time.sleep(.085)

    def render_log(self, log, ly, lx):
        self.terminal.addstr(ly, lx, str(log))
        # log.lifetime -= 1

    def render_logs_panel(self):
        border(
            self.terminal, 
            self.logs_panel_x, 
            self.logs_panel_y, 
            self.logs_panel_width - 1,
            self.logs_panel_height
        )
        self.terminal.addstr(self.logs_panel_y, self.logs_panel_x + 1, '[log]')

        # logs = filter(lambda x: x.lifetime > 0, self.engine.logger.messages)
        logs = self.engine.logger.messages
        tilemap = self.engine.tilemaps.find(eid=self.engine.world.id)
        # only iterate slice of logs if it is larger than screen
        if len(logs) >= self.logs_items_height:
            l = max(0, len(logs) - self.logs_items_height - 1)
            logs = logs[l:]
        for y, log in enumerate(logs):
            log_y = self.logs_item_y + y
            self.render_log(log, log_y, self.logs_item_x)

    def render(self):
        self.terminal.clear()
        self.render_fov()
        self.render_player_panel()
        self.render_enemy_panel()
        self.render_logs_panel()
        self.render_map_panel()

        # self.terminal.refresh()
        self.terminal.noutrefresh()
        curses.doupdate()
   
    def process(self):
        return self.engine.turn_system.process()
