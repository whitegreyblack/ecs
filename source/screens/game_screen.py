# gamescreen.py

"""Game screen class that renders and processes inputs for the main game"""

import curses
import random
import time

from source.common import (
    GameMode, border, circle, diamond, direction_to_keypress, join,
    join_drop_key, join_on, scroll)
from source.ecs.components import (Effect, MeleeHitEffect, Movement, Position,
                                   RangeHitEffect, SpellEffect, Spell)
from source.pathfind import bresenhams, pathfind
from source.raycast import cast_light

from .screen import Panel, Screen


class GameScreen(Screen):
    def __init__(self, engine, terminal):
        super().__init__(engine, terminal)
        self.initialize_coordinates()
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

    def initialize_coordinates(self):
        self.height, self.width = self.terminal.getmaxyx()

        # player info
        self.player_panel = Panel(self.terminal, 0, 0, 15, 18, 'info')

        self.map_panel_x = self.player_panel.width + 1
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
        self.enemy_panel_x = self.player_panel.width + self.map_panel_width + 2
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

        # initialize a cursor
        self.cursor = self.engine.entities.create()
        self.engine.positions.add(self.cursor, Position())

    def render_string(self, x, y, string, attr=0):
        if not isinstance(string, str):
            string = str(string)
        self.terminal.addstr(y, x, string, attr)

    def render_char(self, x, y, character, attr=0):
        self.terminal.addch(y, x, character, attr)

    def render_fov(self):
        cast_light(self.engine)

    def render_player_panel_details(self, render, info, health) -> bool:
        # player name
        self.player_panel.add_string(1, 1, info.name)
        # player hp
        self.player_panel.add_string(1, 2, "HP: ")
        cur_hp = str(health.cur_hp)
        max_hp = f"/ {health.max_hp}"
        self.player_panel.add_string(5, 2, cur_hp, 197)
        self.player_panel.add_string(len(cur_hp) + 6, 2, max_hp, 125)
        # player mp
        mana = self.engine.manas.find(self.engine.player)
        cur_mp = str(mana.cur_mp)
        max_hp = f"/ {mana.max_mp}"
        self.player_panel.add_string(1, 3, "MP: ")
        self.player_panel.add_string(5, 3, cur_mp, 22)
        self.player_panel.add_string(len(cur_mp) + 6, 3, max_hp, 20)
        # player weapon damage
        equipment = self.engine.equipments.find(self.engine.player)
        weapon = self.engine.weapons.find(equipment.hand)
        damage = weapon.damage_swing if weapon else 1
        self.player_panel.add_string(1, 5, f"DMG: {damage}")
        # player armor stats
        armor = 0
        for eq_slot in (equipment.head, equipment.body, equipment.feet):
            eq = self.engine.armors.find(eq_slot)
            if eq:
                armor += eq.defense
        self.player_panel.add_string(1, 6, f"DEF: {armor}")

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
                curses.color_pair(render.color)
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
        player = self.engine.positions.find(self.engine.player)
        tilemap = self.engine.tilemaps.find(eid=player.map_id)
        if tilemap.width < self.map_width:
            cam_x = 0
        else:
            cam_x = scroll(player.x, self.map_width, tilemap.width)
        x0, x1 = cam_x, self.map_width + cam_x
        if tilemap.height < self.map_height:
            cam_y = 0
        else:
            cam_y = scroll(player.y, self.map_height, tilemap.height)
        y0, y1 = cam_y, self.map_height + cam_y
        # do line of sight calculations
        cast_light(self.engine, x0, x1, y0, y1)

        start = time.time()
        # draw map panel border
        self.render_map_border()

        # draw environment
        self.render_map(player.map_id, cam_x, cam_y, x0, x1, y0, y1)
        
        tiles = {
            (position.x, position.y): render
                for position, visibility, render in join_drop_key(
                    self.engine.positions,
                    self.engine.visibilities,
                    self.engine.renders
                )
                if visibility.level > 1
        }
        visible_tiles = set(tiles.keys())

        # draw items
        self.render_items(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
        while True:
            # draw units
            self.render_units(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
            if not self.engine.effects.components:
                break
            if time.time() - start > (1 / 23):
                self.engine.effects.components.clear()
                break
            # draw effects
            self.render_effects(tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
            self.update_effects()
        
        if self.engine.mode is not GameMode.NORMAL:
            self.render_cursor(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)

    def render_map_border(self):
        border(
            self.terminal,
            self.map_panel_x,
            self.map_panel_y,
            self.map_panel_width,
            self.map_panel_height
        )

    def render_map(self, map_id, cam_x, cam_y, x0, x1, y0, y1):
        x_offset = self.map_x - cam_x
        y_offset = self.map_y - cam_y
        
        for visibility, position, render in join_drop_key(
            self.engine.visibilities,
            self.engine.positions,
            self.engine.renders
        ):
            if (visibility.level > 0
                and map_id == position.map_id
                and x0 <= position.x < x1 
                and y0 <= position.y < y1
            ):
                c = render.color if visibility.level > 1 else 240
                self.render_char(
                    position.x + x_offset,
                    position.y + y_offset,
                    render.char,
                    curses.color_pair(c)
                )
        # self.render_char(x_offset, y_offset, curses.ACS_BOARD)
        # self.render_char(x_offset+1, y_offset, curses.ACS_BLOCK)
        # self.render_char(x_offset+2, y_offset, curses.ACS_CKBOARD)
        # self.render_char(x_offset+3, y_offset, curses.ACS_BULLET)

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

    def render_units(self, tiles, map_id, cam_x, cam_y, x0, x1, y0, y1):
        # look for all positions not in tile positions and visibilities.
        # if their positions match and map is visible then show the unit
        enemy_count = 0
        x_offset = self.map_x - cam_x
        y_offset = self.map_y - cam_y
        for eid, (health, position, render, info) in join(
            self.engine.healths,
            self.engine.positions, 
            self.engine.renders,
            self.engine.infos
        ):
            if (
                position.map_id == self.engine.world.id
                and (position.x, position.y) in tiles
                and x0 <= position.x < x1 
                and y0 <= position.y < y1
            ):
                # current_map_id = position.map_id == map_id
                color = render.color if (position.x, position.y) in tiles else 0
                self.render_char(
                    position.x + x_offset,
                    position.y + y_offset,
                    render.char,
                    curses.color_pair(color)
                )
                # check if enemy needs to added to the panel
                non_player = eid != self.engine.player
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

    def render_log(self, log, ly, lx):
        self.terminal.addstr(ly, lx, '> ' + str(log))
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

        logs = self.engine.logger.messages
        # only iterate slice of logs if it is larger than screen
        if len(logs) >= self.logs_items_height:
            l = max(0, len(logs) - self.logs_items_height - 1)
            logs = logs[l:]
        for y, log in enumerate(logs):
            log_y = self.logs_item_y + y
            self.render_log(log, log_y, self.logs_item_x)

    def render(self):
        self.terminal.clear()
        # self.render_fov()
        self.player_panel.render()
        # self.render_player_panel()
        self.render_enemy_panel()
        self.render_map_panel()
        self.render_logs_panel()

        self.terminal.noutrefresh()
        curses.doupdate()
   
    def process(self):
        if self.engine.mode == GameMode.NORMAL:
            return self.engine.turn_system.process()
        else:
            return self.engine.look_system.process()
