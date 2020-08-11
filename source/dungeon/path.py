# path.py

import random


DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def ipath(direction, turn):
    yield DIRECTIONS[direction]

def _path(direction, turn):
    yield DIRECTIONS[(direction + (1 if turn else -1)) % len(DIRECTIONS)]

def lpath(direction, turn):
    for _ in range(2):
       yield from ipath(direction, turn)

def npath(direction, turn):
    yield from ipath(direction, turn)
    yield from _path(direction, turn)

def vpath(direction, turn):
    yield DIRECTIONS[direction]
    yield from _path(direction, turn)

def Lpath(direction, turn):
    yield from lpath(direction, turn)
    yield from _path(direction, turn)

def zpath(direction, turn):
    yield from ipath(direction, turn)
    yield from _path(direction, turn)
    yield from ipath(direction, turn)

def boxpath(direction, turn):
    yield from ipath(direction, turn)
    yield from _path(direction, turn)
    yield from ipath((direction + 2) % 4, not turn)
    yield from _path(direction, not turn)

def rectpath(direction, turn):
    for _ in range(2):
        yield from ipath(direction, turn)
    yield from _path(direction, turn)
    for _ in range(2):
        yield from ipath((direction + 2) % 4, not turn)
    yield from _path(direction, not turn)

def flagpath(direction, turn):
    yield from ipath(direction, turn)
    yield from boxpath(direction, turn)

paths = [
    boxpath,
    rectpath,
    flagpath,
    vpath,
    zpath,
    npath,
    lpath,
    Lpath
]

def random_inputs():
    direction = random.randint(0, 3)
    turn = random.randint(0, 1) == 0
    return direction, turn

def random_path():
    return random.choice(paths)(*random_inputs())

if __name__ == "__main__":
    for path in paths:
        x, y = 0, 0
        points = { (x, y) }
        for dx, dy in path(*random_inputs()):
            x += dx
            y += dy
            points.add((x, y))
        pl = list(points)
        pl.sort(key=lambda x: x[0])
        x0 = pl[0][0]
        x1 = pl[-1][0]
        pl.sort(key=lambda y: y[0])
        y0 = pl[0][1]
        y1 = pl[-1][1]
        print(x0, x1, y0, y1, points)
        img = [['.' for x in range(x1+x0+1)] for y in range(max(y1+y0+1, 1))]
        print(len(img), len(img[0]))
        for x, y in pl:
            try:
                img[y+y0][x+x0] = 'o'
            except IndexError:
                raise IndexError(f"{x+x0},{y+y0}")
        print('\n'.join(''.join(row) for row in img))

