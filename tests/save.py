# singleton_save.py

"""Try to serialze a singleton class"""

import pickle
from source.ecs.components import Tile

if __name__ == "__main__":
    t = Tile()
    with open(f'tests/saves/singleton.pickle', 'wb') as f:
        pickle.dump(t, f, pickle.HIGHEST_PROTOCOL)
