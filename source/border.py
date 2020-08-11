# border.py

"""Holds border/box characters as a class"""

top_left = '┌'
horizontal = '─'
top_right = '┐'
bot_left = '└'
vertical = '│'
bot_right = '┘'

def border(a: int, b:int, x: int, y: int) -> tuple:
    """a, b = start point; x, y = end point"""
    for j in range(b, y):
        for i in range(a, x):
            if (i, j) == (a, b):
                char = top_left
            elif (i, j) == (x - 1, b):
                char = top_right
            elif (i, j) == (a, y - 1):
                char = bot_left
            elif (i, j) == (x - 1, y - 1):
                char = bot_right
            elif i == a or i == x - 1:
                char = vertical
            elif j == b or j == y - 1:
                char = horizontal
            else:
                continue
            yield i, j, char
