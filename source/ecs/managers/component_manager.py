# component_manager.py

from source.ecs import components
from source.join import join as _join

class IncompatibleComponentForManagerError(Exception):
    pass

class DictComponentManager(dict):
    __slots__ = ["ctype"]
    def __init__(self, ctype):
        self.ctype = ctype
    def add(self, k, v):
        self[k] = v
    def join(self, *managers):
        for e in _join(self, *managers):
            yield e, (m[e] for m in managers)

#  364.2 KiB with this class
class ComponentManager:

    __slots__ = ["ctype", "components", "shared"]

    def __init__(self, ctype, dicttype=dict):
        self.ctype = ctype
        self.components = dicttype()
        self.shared = dict()

    def __str__(self):
        l = len(self.components.keys())
        return f"{self.__class__.__name__}(components={l})"

    def __len__(self):
        return len(self.components.keys())

    def __iter__(self):
        return iter(self.components.items())

    def __contains__(self, eid):
        return eid in self.components.keys()

    def exclude(self, other):
        for eid, component in self:
            if eid not in other:
                yield eid, component

    def add(self, entity_id: int, component: object) -> None:
        """
        Adds a key-value pair between an entity and the component to the
        component dictionary.
        """
        is_instance = isinstance(component, self.ctype)
        is_inherited = self.ctype in type(component).__bases__
        if not is_instance and not is_inherited:
            raise IncompatibleComponentForManagerError(f"""
    got: {component.__class__.__name__}
    expected: {self.ctype.__name__}
    Instance: {is_instance}
    Inherited: {is_inherited}"""
            )
        self.components[entity_id] = component

    def remove(self, eid: int) -> bool:
        """Removes a key-value pair from the component dictionary."""
        if eid in self.components.keys():
            del self.components[eid]
            return True
        return False

    def find(self, eid: int) -> object:
        """
        Returns the component value of an entity key that exists in the
        component dictionary. Returns None if not found.
        """
        if eid in self.components.keys():
            return self.components[eid]
        return None

    def values(self) -> object:
        for component in self.components.values():
            yield component


if __name__ == "__main__":
    from source.debug import dprint, gso
    from source.ecs.components import components

    c = ComponentManager(object)
    print(dprint(c))

    # print memory footprint
    # Total allocated size: 5.2 KiB
    import tracemalloc

    tracemalloc.start()
    managers = [ComponentManager(c) for c in components]
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("traceback")
    for stat in top_stats:
        print(stat)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
