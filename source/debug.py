# util.py

"""Commonly used functions"""

from sys import getsizeof as gso

def dprint(obj):
    return f"{id(obj)} {hex(id(obj))} {gso(obj)} bytes {obj}"

def size(obj):
    try:
        class_name = obj.__name__
    except:
        class_name = obj.__class__.__name__
    return f"Size of {class_name}: {gso(obj)} bytes"

def count_objects(engine):
    """Debugging information and object counting for engine. Iterate through each component manager/shared cache."""
    from source.common import join

    def get_components(components):
        l = (list(filter(lambda x: x.classname() in components, engine.components)))
        return l

    messages = []
    count = [0, 0]
    for component in sorted(engine.components, key=lambda x: x.classname()):
        local = [0, 0]
        for i, cache_type in enumerate(('components', 'shared')):
            try:
                local[i] = len(getattr(engine, component.manager).components)
            except AttributeError as e:
                raise e(f"{component.manager} not found")
        messages.append(f"{component.manager}, {', '.join(map(str, count))}")
    messages.append(f"managed: {count[0]}, shared: {count[1]}")

    # environment entities
    messages.append(f"tiles: {get_components(set('tiles positions visibilities renders infos'.split()))}")
    
    # movable units
    messages.append(f"units: {get_components(set('healths positions infos renders'.split()))}")
    
    # items
    messages.append(f"items: {get_components(set('healths positions infos renders inventories'.split()))}")

    print("\n".join(messages))

if __name__ == "__main__":
    import dataclasses

    @dataclasses.dataclass
    class ComponentManger:
        components: dict = dataclasses.field(default_factory=dict)

    @dataclasses.dataclass
    class Engine:
        components: dict = dataclasses.field(default_factory=dict)
        tiles: dict = dataclasses.field(default_factory=ComponentManger)
        positions: dict = dataclasses.field(default_factory=ComponentManger)
        visibilities: dict = dataclasses.field(default_factory=ComponentManger)
        renders: dict = dataclasses.field(default_factory=ComponentManger)
        infos: dict = dataclasses.field(default_factory=ComponentManger)
        healths: dict = dataclasses.field(default_factory=ComponentManger)
        inventories: dict = dataclasses.field(default_factory=ComponentManger)

    e = Engine()
    count_objects(e)
