# map_panel.py

"""World and Map panels. World panel is a wrapper class for Map"""

import time

from source.common import join, join_drop_key, scroll
from source.raycast import cast_light

from .panel import Panel


class LevelPanel(Panel):
    __slots__ = "terminal engine x y width height".split()
    def __init__(self, terminal, engine, x, y, width, height):
        super().__init__(terminal, x, y, width, height, None)
        self.engine = engine
    def render(self):
        player = self.engine.positions.find(self.engine.player)
        tilemap = self.engine.tilemaps.find(player.map_id)
        # calculate camera bounds on scrolling map
        if tilemap.width < self.width:
            cam_x = 0
        else:
            cam_x = scroll(player.x, self.width, tilemap.width)
        x0, x1 = cam_x, self.width + cam_x
        if tilemap.height < self.height:
            cam_y = 0
        else:
            cam_y = scroll(player.y, self.height, tilemap.height)
        y0, y1 = cam_y, self.height + cam_y

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
                c = render.color if visibility.level > 1 else 240
                self.add_char(
                    position.x - cam_x,
                    position.y - cam_y,
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
                self.add_char(
                    position.x - cam_x,
                    position.y - cam_y,
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
        
        # if self.engine.mode is not GameMode.NORMAL:
        #     self.render_cursor(visible_tiles, player.map_id, cam_x, cam_y, x0, x1, y0, y1)

class MapPanel(Panel):
    __slots__ =  "terminal x y width height title level_panel".split()
    def __init__(self, terminal, engine, x, y, width, height, title):
        super().__init__(terminal, x, y, width, height, title)
        self.level_panel = LevelPanel(
            terminal, 
            engine, 
            x + 1, 
            y + 1, 
            width - 2, 
            height - 2
            )
    def render(self):
        super().render()
        self.level_panel.render()
