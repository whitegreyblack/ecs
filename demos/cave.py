# demos\cave.py

"""Demo for the build_cave function in generate.py"""

import shutil

from source.generate import build_cave, string

if __name__ == "__main__":
    w, h = shutil.get_terminal_size()
    print(string(build_cave(w-1, h-2)))
