# messenger.py

"""Logger and Message class"""

from dataclasses import dataclass, field


@dataclass
class Message:
    string: str
    count: int = 0
    lifetime: int = 1
    def __str__(self):
        count = f" (x{self.count})" if self.count > 0 else ''
        return f"{self.string}{count}"

@dataclass
class Logger:
    last: str = None
    messages: list = field(default_factory=list)
    def add(self, message, count=0, lifetime=1):
        if self.last == message:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(message, 0, lifetime))
            self.last = message
