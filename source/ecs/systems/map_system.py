# map_system

"""Map system: not called every turn but on map change events"""

import pickle

from source.common import join
from source.ecs.components import (Information, Openable, Position, Render,
                                   Tile, TileMap, Visibility)
from source.graph import DungeonNode, WorldGraph
from source.maps import (add_boundry_to_matrix, cell_auto, flood_fill,
                         generate_poisson_array, replace_cell_with_stairs,
                         stringify_matrix, transform_random_array_to_matrix)

from .system import System


class MapSystem(System):
    def save_map(self, map_id):
        tilemap = self.engine.tilemaps.find(eid=map_id)
        tiles = {}
        for eid, tile in self.engine.tiles:
            group = [tile]
            group.append(self.engine.positions.find(eid=eid))
            group.append(self.engine.renders.find(eid=eid))
            group.append(self.engine.infos.find(eid=eid))
            group.append(self.engine.visibilities.find(eid=eid))
            openable = self.engine.openables.find(eid=eid)
            if openable:
                group.append(openable)
            tiles[eid] = group
        with open(f'source/saves/map_{map_id}.pickle', 'wb') as f:
            pickle.dump(tilemap, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(tiles, f, pickle.HIGHEST_PROTOCOL)
    
    def load_map(self, map_id):
        with open(f'source/saves/map_{map_id}.pickle', 'rb') as f:
            tilemap = pickle.load(f)
            tileinfo = pickle.load(f)
        world = self.engine.entities.find(map_id)
        self.engine.tilemaps.add(world, tilemap)
        for eid, components in tileinfo.items():
            try:
                t, p, r, i, v, o = components
            except:
                t, p, r, i, v = components
                o = None
            tile = self.engine.entities.find(eid)
            self.engine.tiles.add(tile, t)           
            self.engine.positions.add(tile, p)
            self.engine.renders.add(tile, r)
            self.engine.infos.add(tile, i)
            self.engine.visibilities.add(tile, v)
            if o:
                self.engine.openables.add(tile, o)
        
    def delete_map(self, map_id):
        # clear dictionaries to improve speedup    
        self.engine.tilemaps.remove(eid=map_id)
        for eid, tile in self.engine.tiles:
            self.engine.positions.remove(eid=eid)
            self.engine.renders.remove(eid=eid)
            self.engine.infos.remove(eid=eid)
        self.engine.visibilities.components.clear()
        self.engine.openables.components.clear()
        self.engine.tiles.components.clear()

    def generate_map(self, map_id=None, mapstring=None):
        # clear dictionaries to improve speedup
        if self.engine.world:
            self.save_map(self.engine.world.id)
            self.delete_map(self.engine.world.id)
        # this assumes map id is already generated by entity_manager.create()
        if map_id is not None:
            world = self.engine.entities.find(eid=map_id)
        else:
            world = self.engine.entities.create()
        # if given a specific mapstring use it instead of a random map
        if mapstring:
            dungeon = [[c for c in row] for row in mapstring.split('\n')]
            tilemap = TileMap(len(dungeon[0]), len(dungeon))
        else:
            random_array = generate_poisson_array(58, 17)
            no_stairs = transform_random_array_to_matrix(random_array, 58, 17, 3)
            no_stairs = add_boundry_to_matrix(no_stairs)
            for i in range(3):
                no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
            no_stairs = flood_fill(no_stairs)
            dungeon = replace_cell_with_stairs(no_stairs)
            tilemap = TileMap(58, 17)
        self.engine.tilemaps.add(world, tilemap)
        # add tiles and tile specific attribute components
        for y, row in enumerate(dungeon):
            for x, c in enumerate(row):
                tile = self.engine.entities.create()
                self.engine.tiles.add(tile, Tile())
                position = Position(
                    x, 
                    y,
                    map_id=world.id,
                    moveable=False, 
                    blocks_movement=c in ('#', '+')
                )
                self.engine.visibilities.add(tile, Visibility())
                self.engine.positions.add(tile, position)
                self.engine.renders.add(tile, Render(char=c))
                if c == '#':
                    self.engine.infos.add(tile, Information('wall'))
                elif c in ('/', '+'):
                    self.engine.infos.add(tile, Information('door'))
                    self.engine.openables.add(tile, Openable(opened=c=='/'))
                elif c == '<' or c == '>':
                    self.engine.infos.add(tile, Information('stairs'))
                elif c == '"':
                    self.engine.infos.add(tile, Information('grass'))
                elif c == '~':
                    self.engine.infos.add(tile, Information('water'))
                else:
                    self.engine.infos.add(tile, Information('floor'))
        # create world graph if ran the first time
        if not self.engine.world:
            self.engine.world = WorldGraph({
                world.id: DungeonNode(world.id, None)
            }, world.id)
        # update current map to save parent/child relationship
        else:
            self.engine.world.node.child_id = world.id
            current_map_id = self.engine.world.id
            self.engine.world.update({
                world.id: DungeonNode(world.id, current_map_id)
            })

    def regenerate_map(self, map_id):
        if self.engine.world:
            self.save_map(map_id)
            self.delete_map(map_id)
        self.load_map(self.engine.world.id)
