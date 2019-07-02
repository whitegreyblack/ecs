# componentmanager.py

"""Base class for component manager"""

from dataclasses import dataclass, field


class ComponentManager(object):

    __slots__ = ['ctype', 'components']

    def __init__(self, ctype):
        self.ctype = ctype.__name__
        self.components = dict()

    def __str__(self):
        l = len(self.components.keys())
        return f"{self.__class__.__name__}(components={l})"

    def __iter__(self):
        for k, v in self.components.items():
            yield k, v

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
        if not entity and not eid:
            raise Exception("need entity or eid")
        if entity and entity.id in self.components:
            del self.components[entity.id]
            return True
        if eid and eid in self.components.keys():
            del self.components[eid]
            return True
        return False

    def find(self, entity=None, eid=None):
        if not entity and not eid:
            raise Exception("need entity or eid")
        if entity and entity.id in self.components.keys():
            return self.components[entity.id]
        if eid and eid in self.components.keys():
            return self.components[eid]
        return None

if __name__ == "__main__":
    from util import dprint, gso
    c = ComponentManager()
    print(dprint(c))
