# map_system

"""Map system: not called every turn but on map change events"""

import pickle
import random

from source.common import join
from source.description import env_char_to_name
from source.ecs.components import (Information, Item, Openable, Position,
                                   Render, Tile, TileMap, Visibility)
from source.generate import (add_boundry_to_matrix, array_to_matrix,
                             build_cave, cell_auto, flood_fill,
                             generate_poisson_array, matrix,
                             replace_cell_with_stairs, string)
from source.graph import DungeonNode, WorldGraph

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
        self.engine.tilemaps.add(map_id, tilemap)
        for tile, components in tileinfo.items():
            try:
                t, p, r, i, v, o = components
            except:
                t, p, r, i, v = components
                o = None
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
        if map_id is None:
            map_id = self.engine.entities.create()
        # if given a specific mapstring use it instead of a random map
        if mapstring:
            dungeon = [[c for c in row] for row in mapstring.split('\n')]
            tilemap = TileMap(len(dungeon[0]), len(dungeon))
        else:
            w, h = 58, 17
            # w, h = 80, 24
            # w, h = 180, 50
            random_array = generate_poisson_array(w, h)
            no_stairs = array_to_matrix(random_array, w, h, filterer=lambda x: x < 3 or x >= 8)
            no_stairs = add_boundry_to_matrix(no_stairs, bounds=1)
            for i in range(4):
                no_stairs = cell_auto(no_stairs, deadlimit=5+(i-5))
            no_stairs = flood_fill(no_stairs)
            dungeon = replace_cell_with_stairs(no_stairs)
            # dungeon = build_cave(w, h)
            print(string(dungeon))
            tilemap = TileMap(w, h)
        self.engine.tilemaps.add(map_id, tilemap)
        # add tiles and tile specific attribute components
        other_entities = []
        blocked = ('#', '+')
        for y, row in enumerate(dungeon):
            for x, c in enumerate(row):
                """ `per tile`:
                obj_id        -> instance (int)
                Tile()        -> instance (maybe enum(int) {Tile/Unit/Item})
                Position()    -> instance
                Visibility()  -> instance
                Render()      -> shared
                Information() -> shared
                """
                if c == ' ':
                    continue
                tile = self.engine.entities.create()
                # shared components
                self.engine.tiles.add(tile, Tile())
                i = self.engine.infos.shared[env_char_to_name[c]]
                self.engine.infos.add(tile, i)
                r = random.choice(self.engine.renders.shared[i.name])
                self.engine.renders.add(tile, r)
                if c in ('/', '+'):
                    # This is a unique case (possibly more in the future) in
                    # that this tile creates a map entity with Openable.
                    self.engine.openables.add(tile, Openable(opened=c=='/'))
                elif c == '"' and random.randint(0, 3) == 0:
                    # This is a unique case (possibly more in the future) in
                    # that this tile creates both a map and item entity:
                    flower = self.engine.entities.create()
                    self.engine.items.add(flower, Item('crafting'))
                    self.engine.positions.add(flower, Position(
                        x, y, 
                        map_id=world.id, 
                        movement_type=Position.MovementType.NONE, 
                        blocks_movement=False
                    ))
                    r = random.choice(self.engine.renders.shared['flower'])
                    self.engine.renders.add(flower, r)
                    self.engine.infos.add(flower, self.engine.infos.shared['flower'])
                # per instance components
                self.engine.visibilities.add(tile, Visibility())
                self.engine.positions.add(tile, Position(
                    x, 
                    y,
                    map_id=map_id,
                    movement_type=Position.MovementType.NONE,
                    blocks_movement=c in blocked
                ))
        # any objects found in the map that should have other properties will
        # be created as a different entity with non-map properties.
        for x, y, c in other_entities:
            if c == 'flower':
                flower = self.engine.entities.create()
                self.engine.items.add(flower, Item('crafting'))
                self.engine.positions.add(flower, Position(
                    x, y, 
                    map_id=world.id, 
                    movement_type=position.movement_type,
                    blocks_movement=False
                ))
                self.engine.renders.add(flower, self.engine.shared['flower'])
                self.engine.infos.add(flower, Information('flower'))
        # create world graph if ran the first time
        if not self.engine.world:
            self.engine.world = WorldGraph({
                map_id: DungeonNode(map_id)
            }, map_id)
        # update current map to save parent/child relationship
        else:
            self.engine.world.node.child_id = map_id
            current_map_id = self.engine.world.id
            self.engine.world.update({
                map_id: DungeonNode(
                    map_id, 
                    parent_id=current_map_id
                )
            })

    def regenerate_map(self, map_id):
        """
        Wrapper for load_map. Saves current map if it exists before 
        reading saved map data
        """
        if self.engine.world:
            self.save_map(map_id)
            self.delete_map(map_id)
        self.load_map(self.engine.world.id)
