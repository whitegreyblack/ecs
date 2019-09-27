# log_panel.py

"""Panel for Logs and Inner Message Panel. Log Panel is basically a wrapper"""

from .panel import Panel


class MessagePanel(Panel):
    __slots__ = ['terminal', 'logger', 'x', 'y', 'width', 'height']
    def __init__(self, terminal, logger, x, y, width, height):
        super().__init__(terminal, x, y, width, height, None)
        self.logger = logger

    def render(self):
        """
            Adds the maximum number of possible messages to the panel by
            adding messages in reverse order then rendering the messages
            by re-reversing the message list to get the correct order of
            events.
            If a string will take up more space than the remaining panel
            space then the string will not be added and the message list
            will stop appending new strings.
        """
        logs = []
        for message in reversed(self.logger.messages):
            # -2 accounts for the indentation: '> '
            strings = list(enumerate(message.strings(self.width - 2)))
            if len(strings) + len(logs) > self.height:
                break
            logs += strings
        logs.reverse()
        for y, (i, log) in enumerate(logs):
            self.terminal.addstr(self.y + y,
                                 self.x, 
                                 f"{'>' if i == 0 else ' '} {log}")

class LogPanel(Panel):
    __slots__ = "terminal x y width height title message_panel".split()
    def __init__(
            self, 
            terminal, 
            logger, 
            x, y, 
            width, 
            height, 
            title, 
            x_offset=2, 
            y_offset=1
    ):
        """Just a rectangle"""
        super().__init__(terminal, x, y, width, height, title)
        self.message_panel = MessagePanel(
            terminal,
            logger,
            x + x_offset,
            y + y_offset,
            width - x_offset * 2,
            height - y_offset * 2
            )
    
    def render(self):
        super().render()
        self.message_panel.render()
