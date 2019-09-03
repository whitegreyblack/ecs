# demos\blob.py

"""Demo for the build_blob function in generate.py"""

import shutil

from source.generate import build_blob, string

if __name__ == "__main__":
    w, h = shutil.get_terminal_size()
    print(string(build_blob(w-1, w-2)))
