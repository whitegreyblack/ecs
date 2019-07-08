from dataclasses import dataclass, field

@dataclass
class Message:
    string: str
    lifetime: int = 1

@dataclass
class Logger:
    world: str = None
    header: str = ""
    messages: list = field(default_factory=list)
    def add(self, message, lifetime=1):
        self.messages.append(Message(message, lifetime))
