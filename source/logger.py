# logger.py

"""Logger and Message class"""

import textwrap
from dataclasses import dataclass, field


@dataclass
class Message:
    string: str
    count: int = 0
    def __str__(self):
        count = f" (x{self.count})" if self.count > 0 else ''
        return f"{self.string}{count}"
    def strings(self, width):
        # if message length is less than width, will return one line
        # else returns multiple lines
        for s in textwrap.wrap(str(self), width):
            yield s

# singleton logger. unused but saved for reference
# class Logger:
#     instance = None
#     @dataclass
#     class _Logger:
#         last: str = None
#         messages: list = field(default_factory=list)
#         def add(self, message, count=0, lifetime=1):
#             if self.last == message:
#                 self.messages[-1].count += 1
#             else:
#                 self.messages.append(Message(message, 0, lifetime))
#                 self.last = message
#     def __new__(self):
#         if not Logger.instance:
#             Logger.instance = Logger._Logger()
#         return Logger.instance

@dataclass
class Logger:
    last_message_hash: int = None
    messages: list = field(default_factory=list)
    def add(self, message, repeatable=True):
        # repeatable prevents the count of same messages to increment
        hashed = hash(message)
        if self.last_message_hash == hashed:
            if repeatable:
                self.messages[-1].count += 1
        else:
            self.messages.append(Message(message, 0))
            self.last_message_hash = hashed

if __name__ == '__main__':
    l = Logger()
    l.add("you turn left")
    l.add("you turn right")
    l.add("you go straight")
    l.add("you go straight", repeatable=False)
    print('\n'.join(str(m) for m in l.messages))
