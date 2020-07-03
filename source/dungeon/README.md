# Dungeon Generation

Uses random room generation

To run the graph node minimap generator:
```
python minimap.py
```

To run the dungeon generator:
```
python dungeon.py
```

Files:
    config.py - common variables and shared utilities
    dungeon.py - produces a dungeon model with rooms, walls, doors, hallways, and floors
    ecs.py - mini ecs model and tests
    minimap.py - produces a dungeon model as a linked graph
    model.py - holds context variables
    output.py - print functions for 1d or 2d lists
    path.py - holds directions to draw each path type
    room.py - holds coordinates to draw each room type
