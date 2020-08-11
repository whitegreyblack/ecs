# entitymanager.py

"""Manager for entity objects"""

from dataclasses import dataclass


class EntityManager(object):

    __slots__ = ['next_id', 'ids', 'entity_ids', 'removed']
    
    def __init__(self) -> None:
        self.next_id: int = 0
        self.ids: set = set()
        self.removed: set = set()
        self.entity_ids: list = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(next_id={self.next_id})"

    def __iter__(self) -> int:
        for entity_id in self.entity_ids:
            yield entity_id

    def create(self) -> int:
        """Reserves an integer value to be used as the entity key."""
        entity_id = self.next_id
        self.next_id += 1
        # self.ids.add(entity_id)
        self.entity_ids.append(entity_id)
        return entity_id

    def add(self, entity_id: int) -> None:
        """
            Adds an entity_id value to the list of used entity key values. If
            the key is not already used then it set the next_id to the most
            appropriate next id value. If the key is already used then it will
            raise a ValueError exception.
        """
        if entity_id in self.ids:
            raise ValueError(f"Entity id({entity_id}) already exists")
        self.ids.add(entity_id)
        self.entity_ids.append(entity_id)
        self.find_next_id()

    def find_next_id(self) -> int:
        """Loops until a new id not in the set of known ids is found"""
        self.next_id = 0
        while self.next_id in self.ids:
            self.next_id += 1

    def remove(self, entity_id: int) -> None:
        """Moves id from known set of ids into a set of removed ids"""
        self.ids -= {entity_id}
        self.entity_ids.remove(entity_id)
        self.removed.add(entity_id)

if __name__ == "__main__":
    from source.debug import dprint
    manager = EntityManager()
    print(dprint(manager), '# check next_id value')
    entity = manager.create()
    print(dprint(entity))
    print(dprint(manager), '# verify next_id value incremented')

    e = manager.create()
    print(e)
    print(manager.next_id)

    try:
        manager.add(e)
    except ValueError:
        print(f'As expected: Value error raised when trying to add {e}')
