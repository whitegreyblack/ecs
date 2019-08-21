# components_manager.py


class ComponentsManager(object):
    
    __slots__ = ['_dicttype', 'components', 'shared']

    def __init__(self, components, dicttype=dict):
        self._dicttype = dicttype
        self.components = {
            component_type.__name__: dicttype()
                for component_type in components
        }
        self.shared = dicttype()

    def __repr__(self):
        items = sorted(self.components.items(), key=lambda x: x[0])
        components = '\n  '.join(
            f"{key}: {'[]' if not values else list(values.keys())}"
                for key, values in items
        )
        return f"""
ComponentsManager: 
  {components}"""[1:]

    def add(self, entity_id: int, component: object) -> None:
        """
        Addds a key-value pair between an entity and the component to the
        component dictionary
        """
        t = component.__class__.__name__
        if t not in self.components:
            self.components[t] = self._dicttype()
        self.components[t][entity_id] = component

    def remove(self, entity_id: int, component_type: str) -> bool:
        if component_type not in self.components:
            raise ValueError(f"Cannot find {component_type} in component dictionary")
        if entity_id in self.components[component_type]:
            del self.components[entity_id]
            return True
        return False
    
    def find(self, entity_id: int, component_type: str) -> object:
        if component_type not in self.components:
            raise ValueError(f"Cannot find {component_type} in component dictionary")
        return self.components[component_type].get(entity_id)

if __name__ == "__main__":
    from source.ecs.components import components, Position
    c = ComponentsManager(components)
    c.add(1, Position(1, 1))
    print(c)

    # print memory footprint
    # Total allocated size: 2.4 KiB
    import tracemalloc
    tracemalloc.start()
    c = ComponentsManager(components)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    for stat in top_stats:
        print(stat)
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
