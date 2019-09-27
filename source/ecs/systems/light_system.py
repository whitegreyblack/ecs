# light_system.py

from source.common import join, scroll
from source.raycast import cast_light

from .system import System


"""
    Maybe need a camera component?
"""

class LightingSystem(System):
    def process(self):
        # should only process the player entity on its turn
        g = join(self.engine.turns, self.engine.positions)
        for eid, (_, position) in g:
            if eid != self.engine.player:
                break
            tilemap = self.engine.tilemaps.find(position.map_id)
            camera = self.engine.cameras.find(eid)
            
            # map offsets if map is bigger than current camera viewport
            x0 = scroll(player.x, camera.width, tilemap.width)
            x1 = x0 + camera.width
            y0 = scroll(player.y, camera.height, tilemap.height)
            y1 = y0 + camera.height

            # sets tiles in range of unit to lighted
            # i.e. tile(X,Y).level > 0
            # they will be saved by the engine to be used during rendering
            cast_light(self.engine, x0, x1, y0, y1)
