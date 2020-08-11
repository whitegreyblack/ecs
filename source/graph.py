# graph.py

""" `World Graph`

Creates a world graph of nodes holding an entity id


Overworld -> array of nodes MxN
City, Cave, Field, ..., etc. will make up the array
Each array node can then have any multiple number of children worlds

            + - - - - - - - overworld node (new::world node)
        . _ _ | . _ _ _ .     - neighbors = ne, n, nw, w, sw, s, se, e
       /|     |/|      /|     - parent = None since overworlds are top level
      . _ _ _ o _ _ _ . |     - child = world node (always)
     /| .    /| .    /| .
    . _ _ _ . _ _ _ . |
    | .     | .     | o - - - world node (new::dungeon node)
    |       |       |         - no neighbors
    .       .       .         - parent = overworld || dungeon node
                              - child = world node (always)
"""

from dataclasses import dataclass
from math import inf
from random import choice


class WorldGraph(dict):
    def __init__(self, graph: dict, start_id: id):
        self.update(graph)
        self.id = start_id
    @property
    def node(self):
        return self[self.id]
    def go_down(self):
        node = self[self.id]
        if not node:
            return False
        if node.child_id is None:
            return False
        self.id = node.child_id
        return True
    def go_up(self):
        node = self[self.id]
        if node.parent_id is None:
            return False
        self.id = node.parent_id
        return True

@dataclass
class Node:
    entity_id: int
    parent_id: int = None
    child_id: int = None

class WorldNode(Node):
    def __init__(
        self,
        entity_id: int,
        child_id: int = None,
        neighbors: dict = None
    ):
        super().__init__(entity_id, child_id=child_id)
        self.neighbors = neighbors if neighbors else {
            direction: None
                for direction in 'N NE E SE S SW W NW'.split()
        }
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
        classname = self.__class__.__name__
        eid = self.entity_id
        cid = self.child_id
        attributes = f"eid={eid}, cid={cid}, neighbors={neighbors}"
        return f"{self.__class__.__name__}({attributes})"

class DungeonNode(Node):
    def __init__(
        self,
        entity_id: int,
        parent_id: int = None,
        child_id: int = None
    ):
        super().__init__(entity_id, parent_id, child_id)

class DungeonMap(DungeonNode):
    def __init__(
        self,
        entity_id: int,
        dungeon: str,
        parent_id: int,
        child_id: int = None
    ):
        super().__init__(entity_id, parent_id, child_id)
        self.dungeon = dungeon

def find_child(graph, start_id, end_id):
    n = graph[start_id]
    if not n.child_id:
        return False
    # there exists a child
    while True:
        if end_id == n.child_id:
            return True
        n = graph.get(n.child_id, None)
        if not n:
            return False

def find_parent(graph, start_id, end_id):
    n = graph[start_id]
    if not n.parent_id:
        return False
    # there exists a parent
    while True:
        if end_id == n.parent_id:
            return True
        n = graph.get(n.parent_id, None)
        if not n:
            return False

def create_mst(graph):
    # Minimum spanning tree
    p, q = {}, {}
    for key in graph.keys():
        q[key] = inf
        p[key] = 0
    p[0], q[0] = 0, 0
    choices = [0, 1]
    while q:
        u = min(k for k in q.keys())
        for z in graph[u].keys():
            if z in q.keys() and 0 < graph[u][z] < q[z]:
                p[z] = u
                q[z] = graph[u][z]
        q.pop(u)
        if choice(choices) == 1 and q.keys():
            u = min(k for k in q.keys())
            for z in graph[u].keys():
                if z in q.keys() and 0 < graph[u][z] < q[z]:
                    p[z] = u
                    q[z] = graph[u][z]
    return p

if __name__ == "__main__":
    print(Node(3))
    print(WorldNode(4))
    print(DungeonNode(3, 5))
