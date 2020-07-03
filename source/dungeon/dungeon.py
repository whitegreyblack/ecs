# room_builder.py

"""
Creates full rooms and hallways based off of the minimap.py graph builder demo
"""

import random

from config import MAX_ROOMS, DIFFICULTY_MULTIPLIER, MAX_RETRY, DIRECTIONS
from model import GraphContext, Point, Ruler
from room import RectRoomNode
from output import output

def build_rooms(difficulty):
    if not difficulty or difficulty < 1:
        difficulty = 1

    max_rooms = 10
    cur_retry = 0
    rooms = []
    room_mapping = dict()
    x_min = x_max = 0
    y_min = y_max = 0

    while cur_retry < MAX_RETRY:
        w = random.choice((7 * difficulty, 9 * difficulty))
        h = w // 3
        print(w, h)
        room = RectRoomNode(width=w, height=h)
        
        x_min -= room.width // 2
        x_max += room.width // 2
        y_min -= room.height // 2
        y_max += room.height // 2

        rid = len(rooms)
        rooms.append(room)
        room_mapping[rid] = { direction.name: -1 for direction in DIRECTIONS }
        break

    graph = [['.' 
                for x in range(x_max - x_min + 1)] 
                    for y in range(y_max - y_min + 1)]
    
    print(output(graph))

if __name__ == '__main__':
    import sys

    difficulty = 0
    if len(sys.argv) > 1:
        try:
            difficulty = int(sys.argv[1])
        except ValueError as e:
            raise e(f"Invalid paramater: {sys.argv[1]}")
        except Exception:
            raise
    
    build_rooms(difficulty)
