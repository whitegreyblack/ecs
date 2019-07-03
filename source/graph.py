# graph.py

"""
Creates a world graph of nodes holding an entity id


Overworld -> array of nodes MxN
City, Cave, Field, ..., etc. will make up the array
Each array node can then have any multiple number of children worlds
"""

class Node:
    def __init__(self, entity_id: int, neighbors: dict=None):
        self.entity_id: int = entity_id
        self.neighbors: dict = neighbors if neighbors else dict()
    def __repr__(self):
        entity = f"entity_id={self.entity_id}"
        if self.neighbors:
            neighbors = {
                k: v for k, v in self.neighbors.items() if v is not None
            }
            # keypairs exist but values are none. set as empty dict
            if not neighbors:
                neighbors = dict()
        else:
            neighbors = self.neighbors
        attributes = f"{entity}, neighbors={neighbors}"
        return f"{self.__class__.__name__}({attributes})"

class OverworldNode(Node):
    def __init__(self, entity_id: int):
        super().__init__(entity_id, {
            direction: None
                for direction in 'N NE E SE S SW W NW'.split()
        })
        self.child_id: int = None
        # maps leading down will have 

class WorldNode(Node):
    def __init__(self, entity_id: int, parent_id: int):
        super().__init__(entity_id)
        self.parent_id: int = parent_id

if __name__ == "__main__":
    print(Node(3))
    print(OverworldNode(4))
    print(WorldNode(3, 5))
