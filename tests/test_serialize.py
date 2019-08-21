# test_load.py

"""Try saving @dataclass classes with pickle"""

import pickle

from source.ecs.components import Position, Tile


def main():
    d = {
        0: Position(1, 2)
    }
    with open('data.pickle', 'wb') as f:
        pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)

    with open('data.pickle', 'rb') as f:
        data = pickle.load(f)
    print(data)

def load_saved_map():
    with open('source/saves/map_0.pickle', 'rb') as f:
        data = pickle.load(f)
        maps = pickle.load(f)
    print(data)
    print(maps)

def save_singleton_component():
    """Try to serialze a singleton class"""
    t = Tile()
    with open(f'tests/saves/singleton.pickle', 'wb') as f:
        pickle.dump(t, f, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    # main()
    load_saved_map()
    save_singleton_component()
