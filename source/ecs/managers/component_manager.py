# component_manager.py


#  364.2 KiB with this class
class ComponentManager(object):

    __slots__ = ['ctype', 'components', 'shared']

    def __init__(self, ctype, dicttype=dict):
        self.ctype = ctype
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

    def add(self, entity_id: int, component: object) -> None:
        """
            Adds a key-value pair between an entity and the component to the 
            component dictionary.
        """
        is_instance = isinstance(component, self.ctype)
        is_inherited = self.ctype in type(component).__bases__
        if not is_instance and not is_inherited:
            raise ValueError(
f"Ctype: {self.ctype} Instance: {is_instance}, Inherited: {is_inherited} Incoming: {type(component)}"
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
    managers = [
        ComponentManager(c)
            for c in components
    ]
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    for stat in top_stats:
        print(stat)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
