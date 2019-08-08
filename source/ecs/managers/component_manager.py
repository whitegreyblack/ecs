# componentmanager.py

"""Base class for component manager"""

from dataclasses import dataclass, field


class ComponentManager(object):

    __slots__ = ['ctype', 'components', 'shared']

    def __init__(self, ctype, dicttype=dict):
        self.ctype = ctype.__name__
        self.components = dicttype()
        self.shared = dict()

    def __str__(self):
        l = len(self.components.keys())
        return f"{self.__class__.__name__}(components={l})"

    def __iter__(self):
        return iter(self.components.items())

    def __contains__(self, eid):
        return eid in self.components.keys()

    def exclude(self, other):
        for eid, component in self:
            if eid not in other:
                yield eid, component

    def add(self, entity, component):
        if type(component).__name__ is not self.ctype:
            raise ValueError("Invalid component type added.")
        self.components[entity.id] = component

    def remove(self, entity=None, eid=None) -> bool:
        if entity is None and eid is None or (eid and eid < 0):
            raise Exception("need entity or eid")
        if entity and entity.id in self.components:
            del self.components[entity.id]
            return True
        if eid and eid in self.components.keys():
            del self.components[eid]
            return True
        return False

    def find(self, entity=None, eid=None):
        if entity is None and eid is None:
            raise Exception("need entity or eid")
        if entity is not None and entity.id in self.components.keys():
            return self.components[entity.id]
        if eid is not None and eid in self.components.keys():
            return self.components[eid]
        return None

if __name__ == "__main__":
    from util import dprint, gso
    c = ComponentManager()
    print(dprint(c))
