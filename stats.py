""" `memory notes`:
* Using Singleton Pattern on Tile: 
    total mem size is ~450.8 KiB with singleton
* Without:
    total mem size is ~481.2 KiB. 
    
* 30 KiB for a single map of tiles
* 428.3 KiB when using flyweight vs 549.8 KiB

* On startup before entering game: 365.9 KiB
* After new game and then quitting: 381.4 KiB
* Current when playing: ~436.9 KiB

* After removing ('#', '+') in block_movement paramater for a position component
  created during map_system:
    When playing a game: ~392.8 KiB

* After kill a single goblin unit: ~415.KiB.

* Before creating a function to yield components per eid from managers:
    common.py:61: size=69.1 KiB, count=201, average=352 B
    ~400.4 KiB | ~401.6 KiB
* After:
    common.py:62: size=115 KiB, count=1186, average=100 B
    ~438.5 KiB | ~458.5 KiB

* Setting dictionary k/v directly in component manager:
    self.components.update(((entity_id, component),))
    component_manager.py:40: size=100 KiB, count=6, average=16.7 KiB
    component_manager.py:40: size=101 KiB, count=7, average=14.4 KiB
    ~415.3 KiB

    self.components[entity_id] = component
    component_manager.py:39: size=100 KiB, count=6, average=16.7 KiB
    component_manager.py:39: size=101 KiB, count=7, average=14.4 KiB
    ~421.5 KiB

* Removed ids from entity_manager:
    ~403.1 KiB | ~402.2 KiB

* Join memory footprint reduce:
    Total allocated size: 348.3 KiB @ startup
    Total allocated size: 372.7 KiB @ 10 turns
"""