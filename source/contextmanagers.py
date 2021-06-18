from timeit import default_timer

# based off of code found @ https://gist.github.com/cgoldberg/2942781
class Timer(object):
    __slots__ = ["timer", "start", "secs", "ms"]

    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.secs = end - self.start
        self.ms = self.secs * 1000
