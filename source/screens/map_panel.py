# map_panel.py

"""Map and Level panels. Map panel is a wrapper class for Level"""

import time

from source.common import (GameMode, circle, diamond, join, join_drop_key,
                           scroll)
from source.ecs.components import Spell
from source.raycast import cast_light

from .panel import Panel


class LevelPanel(Panel):
    __slots__ = "terminal engine x y width height cam_x cam_y".split()
    def __init__(self, terminal, engine, x, y, width, height):
        super().__init__(terminal, x, y, width, height, None)
        self.engine = engine
        self.cam_x = None
        self.cam_y = None

    def render(self):
        player = self.engine.positions.find(self.engine.player)
        tilemap = self.engine.tilemaps.find(player.map_id)
        # calculate camera bounds on scrolling map
        if tilemap.width < self.width:
            self.cam_x = 0
        else:
            self.cam_x = scroll(player.x, self.width, tilemap.width)
        x0, x1 = self.cam_x, self.width + self.cam_x
        if tilemap.height < self.height:
            self.cam_y = 0
        else:
            self.cam_y = scroll(player.y, self.height, tilemap.height)
        y0, y1 = self.cam_y, self.height + self.cam_y

        # do line of sight calculations
        cast_light(self.engine, x0, x1, y0, y1)

        start = time.time()
        # draw map first, then items, then units
        for visibility, position, render in join_drop_key(
            self.engine.visibilities,
            self.engine.positions,
            self.engine.renders
        ):
            if (visibility.level > 0
                and player.map_id == position.map_id
                and x0 <= position.x < x1 
                and y0 <= position.y < y1
            ):
                c = render.color if visibility.level > 1 else "darkest grey"
                self.add_string(
                    position.x - self.cam_x,
                    position.y - self.cam_y,
                    render.char,
                    c
                )

        self.engine.entities_in_view.clear()
        for eid, (health, position, render, info) in join(
            self.engine.healths,
            self.engine.positions,
            self.engine.renders,
            self.engine.infos
        ):
            if (position.map_id == self.engine.world.id
                and (position.x, position.y) in self.engine.tiles_in_view
                and x0 <= position.x < x1
                and y0 <= position.y < y1
            ):
                if self.engine.player != eid:
                    self.engine.entities_in_view.add(eid)
                self.add_string(
                    position.x - self.cam_x,
                    position.y - self.cam_y,
                    render.char,
                    render.color
                )

        # # draw items
        # self.render_items(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
        # while True:
        #     # draw units
        #     self.render_units(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
        #     if not self.engine.effects.components:
        #         break
        #     if time.time() - start > (1 / 23):
        #         self.engine.effects.components.clear()
        #         break
        #     # draw effects
        #     self.render_effects(tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
        #     self.update_effects()
        
        if self.engine.mode is not GameMode.NORMAL:
            # self.render_cursor(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)
            position = self.engine.positions.find(self.engine.cursor)
            if self.engine.mode in (GameMode.LOOKING, GameMode.DEBUG):
                self.add_string(
                    position.x - self.cam_x,
                    position.y - self.cam_y,
                    'X'
                )
            elif self.engine.mode == GameMode.MAGIC:
                cursor = self.engine.cursors.find(self.engine.cursor)
                spellname = Spell.identify[cursor.using]
                render = self.engine.renders.shared[spellname][0]
                if spellname == 'fireball':
                    for xx, yy in diamond():
                        x = position.x + xx
                        y = position.y + yy
                        if (x, y) not in self.engine.tiles_in_view:
                            continue
                        self.add_string(
                            x - cam_x,
                            y - cam_y,
                            render.char,
                            render.color
                        )

class MapPanel(Panel):
    __slots__ =  "terminal x y width height title level_panel".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.level_panel = LevelPanel(
            terminal,
            engine,
            x + 1, y + 1, width - 2, height - 2
        )
    def render(self):
        super().render()
        self.level_panel.render()
