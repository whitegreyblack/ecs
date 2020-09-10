# stack.py

class Stack:
    __slots__: list = ['items']
    def __init__(self, *items):
        self.items: list = [*items]
    def push(self, value: object):
        self.items.append(value)
    def pop(self):
        self.items.pop()
    def __len__(self):
        return len(self.items)
    @property
    def top(self):
        if self.items:
            return self.items[-1]
        return None
    def empty(self):
        self.items.clear()
