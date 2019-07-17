# gamescreen.py

"""Game screen class that renders and processes inputs for the main game"""

import curses

from source.astar import pathfind
from source.color import colors
from source.common import border, direction_to_keypress, eight_square, join
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
        self.map_panel_x = 0
        self.map_panel_y = 0
        # could use percentage? or min max based on map ratio?
        self.map_panel_width = 60
        self.map_panel_height = 19
        self.map_offset_x = 1
        self.map_offset_y = 1

        self.header_x = self.map_panel_x + self.map_offset_x
        self.header_y = self.map_panel_y + self.map_offset_y
        self.header_width = self.map_panel_width - self.map_offset_x * 2
        self.header_height = 1

        self.map_x = self.map_panel_x + self.map_offset_x
        self.map_y = self.header_y + 1
        # maximum bounds for map size; any larger and scroll is enabled TODO: scrolling
        self.map_width = max(self.map_panel_width - self.map_offset_x * 2, tilemap.width)
        self.map_height = max(self.map_panel_height - self.map_offset_y * 2, tilemap.height)
        
        # enemy panel border and coordinates
        self.enemy_panel_x = self.map_panel_width + 1
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

    def render_string(self, x, y, string):
        self.terminal.addstr(y, x, string)

    def render_char(self, x, y, character, color_pair=0):
        self.terminal.addch(y, x, character, color_pair)

    def render_fov(self):
        cast_light(self.engine)

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

    def render_enemy_panel(self):
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
        self.render_header()
        self.render_map()
        self.render_items()
        self.render_units()

    def render_header(self):
        health = self.engine.healths.find(self.engine.player)
        hp_string = f"hp:{health.cur_hp}/{health.max_hp}"
        mp_string = f"mp:0/0"
        eq_string = "['[[==/"
        header = f"{hp_string} {mp_string} {eq_string}"
        self.render_string(self.header_x, self.header_y, header)

    def render_map(self):
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
            self.engine.renders
        )
        for _, (visibility, position, render) in tiles:
            current_map_position = position.map_id == self.engine.world.id
            if current_map_position and visibility.level > 0:
                self.render_char(
                    position.x + self.map_x,
                    position.y + self.map_y,
                    render.char,
                    curses.color_pair(visibility.level)
                )

    def enemy_description(self, eid, render, info, health, position):
        return f"{eid}: {render.char} {info.name} {health.cur_hp}/{health.max_hp} ({position.x},{position.y})"

    def render_units(self):
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
        tiles = {
            (position.x, position.y): visibility
                for _, (position, visibility) in join(
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visibility.level > 1
        }
        # look for all positions not in tile positions and visibilities.
        # if their positions match and map is visible then show the unit
        enemy_count = 0
        for eid, health, position, render, info in units:
            visibility = tiles.get((position.x, position.y), None)
            # for (t, v) in tiles:
            if visibility:
                self.render_char(
                    self.map_x + position.x,
                    self.map_y + position.y,
                    render.char,
                    curses.color_pair(visibility.level)
                )
                non_player = eid != self.engine.player.id
                description_space = enemy_count < self.enemy_panel_height - 1
                if non_player and description_space:
                    description = self.enemy_description(eid, render, info, health, position)
                    self.render_string(
                        self.enemy_item_x + 1,
                        self.enemy_item_y + enemy_count,
                        description[:self.enemy_panel_width-1]
                    )
                    enemy_count += 1
            
        for eid, health, position, render, info in units:
            computer = eid != self.engine.player.id
            ai = self.engine.ais.find(eid=eid)
            if ai and ai.path:
                for x, y in ai.path[:len(ai.path)-1]:
                    self.render_char(
                        x + self.map_x,
                        y + self.map_y,
                        '.',
                        curses.color_pair(3)
                    )

    def render_items(self):
        items = join(
            self.engine.items,
            self.engine.positions,
            self.engine.renders,
        )
        tiles = {
            (position.x, position.y): visibility
                for _, (position, visibility) in join(
                    self.engine.positions, 
                    self.engine.visibilities
                )
                if visibility.level > 1
        }
        item_positions = set()
        for _, (_, position, render) in items:
            visibility = tiles.get((position.x, position.y), None)
            if visibility:
                self.render_char(
                    self.map_x + position.x,
                    self.map_y + position.y,
                    render.char,
                    curses.color_pair(visibility.level)
                )

    # def render_effect(self, x, y, effect):
    #     self.render_char(
    #         x + self.map_x_offset,
    #         y + self.map_y_offset,
    #         effect.char,
    #         curses.color_pair(1)
    #     )

    # def render_effects(self):
    #     for eid, effect in self.engine.effects:
    #         if effect.ticks > 0:
    #             entity = self.engine.entities.find(eid)
    #             position = self.engine.position.find(entity)
    #             movement = self.engine.movement.find(entity)
    #             x, y = position.x, position.y
    #             if movement:
    #                 x, y = x + movement.x, y + movement.y
    #             self.render_effect(x, y, effect, False)
    #             effect.ticks -= 1

    def render_log(self, log, ly, lx):
        self.terminal.addstr(ly, lx, str(log))
        log.lifetime -= 1

    def render_logs_panel(self):
        border(
            self.terminal, 
            self.logs_panel_x, 
            self.logs_panel_y, 
            self.logs_panel_width - 1,
            self.logs_panel_height
        )
        self.terminal.addstr(20, 1, '[log]')

        # logs = filter(lambda x: x.lifetime > 0, self.engine.logger.messages)
        logs = self.engine.logger.messages
        tilemap = self.engine.tilemaps.find(eid=self.engine.world.id)
        # only iterate slice of logs if it is larger than screen
        if len(logs) >= self.logs_items_height:
            logs = logs[len(logs) - self.logs_items_height - 1:]
        for y, log in enumerate(logs):
            log_y = self.logs_item_y + y
            self.render_log(log, log_y, self.logs_item_x)

    def redraw(self):
        self.terminal.refresh()

    def render(self):
        self.terminal.erase()
        self.render_fov()
        self.render_map_panel()
        self.render_enemy_panel()
        self.render_logs_panel()
        self.redraw()

    def process(self):
        return self.engine.turn_system.process()
